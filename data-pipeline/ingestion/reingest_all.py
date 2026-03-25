import os
import json
import logging
import argparse
from google.cloud import storage
from google.cloud import discoveryengine_v1beta as discoveryengine
from parser import map_rbac_roles

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def reingest_bucket(project_id, bucket_name, data_store_id, location="global"):
    """
    Iterates through a GCS bucket and indexes all files into Vertex AI Search.
    """
    storage_client = storage.Client(project=project_id)
    search_client = discoveryengine.DocumentServiceClient()

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    parent = search_client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch"
    )

    count = 0
    success = 0
    
    logger.info(f"🚀 Starting full re-ingestion from bucket: gs://{bucket_name}")
    logger.info(f"🎯 Target Data Store: {data_store_id}")

    for blob in blobs:
        file_name = blob.name
        
        # Skip directory placeholders
        if file_name.endswith("/"):
            continue

        count += 1
        gcs_uri = f"gs://{bucket_name}/{file_name}"
        
        # 1. Map RBAC Metadata
        metadata = map_rbac_roles(file_name)
        
        # 2. Determine MIME Type
        mime_type = "text/plain"
        if file_name.lower().endswith(".pdf"):
            mime_type = "application/pdf"
        elif file_name.lower().endswith(".md"):
            mime_type = "text/markdown"
        elif file_name.lower().endswith(".txt"):
            mime_type = "text/plain"

        # Use the file name (sanitized) as the document ID
        doc_id = file_name.replace("/", "_").replace(".", "_").lower()[:60]

        document = discoveryengine.Document(
            id=doc_id,
            content=discoveryengine.Document.Content(
                uri=gcs_uri,
                mime_type=mime_type
            ),
            struct_data=metadata
        )

        try:
            request = discoveryengine.CreateDocumentRequest(
                parent=parent,
                document=document,
                document_id=doc_id
            )
            search_client.create_document(request=request)
            logger.info(f"✅ Indexed: {file_name}")
            success += 1
        except Exception as e:
            logger.error(f"❌ Failed to index {file_name}: {str(e)}")

    logger.info(f"🏁 Re-ingestion complete. Processed: {count}, Successful: {success}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-ingest all documents from a GCS bucket into Vertex AI Search.")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--bucket", required=True, help="GCS Bucket Name")
    parser.add_argument("--datastore", required=True, help="Vertex AI Data Store ID")
    parser.add_argument("--location", default="global", help="Vertex AI Location (default: global)")

    args = parser.parse_args()
    reingest_bucket(args.project, args.bucket, args.datastore, args.location)
