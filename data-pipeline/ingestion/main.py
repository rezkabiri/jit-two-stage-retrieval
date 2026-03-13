# data-pipeline/ingestion/main.py
import os
import json
import functions_framework
from google.cloud import storage
from google.cloud import discoveryengine_v1beta as discoveryengine
from .parser import extract_text, map_rbac_roles

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "rag-docs")

storage_client = storage.Client()
search_client = discoveryengine.DocumentServiceClient()

@functions_framework.cloud_event
def process_gcs_upload(cloud_event):
    """
    Triggered by a GCS upload (Eventarc or Cloud Storage trigger).
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    print(f"🔄 Processing new upload: gs://{bucket_name}/{file_name}")

    # 1. Download file content
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    file_content = blob.download_as_bytes()

    # 2. Extract Text
    content_text = extract_text(file_content, file_name)
    
    # 3. Map RBAC Metadata
    metadata = map_rbac_roles(file_name)
    print(f"🏷️ Assigned RBAC metadata: {json.dumps(metadata)}")

    # 4. Push to Vertex AI Search
    parent = search_client.branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        branch="default_branch"
    )

    # Use the file name (sanitized) as the document ID
    doc_id = file_name.replace("/", "_").replace(".", "_").lower()[:60]

    document = discoveryengine.Document(
        id=doc_id,
        content=discoveryengine.Document.Content(
            raw_content=content_text.encode("utf-8"),
            mime_type="text/plain"
        ),
        struct_data=metadata
    )

    try:
        request = discoveryengine.CreateDocumentRequest(
            parent=parent,
            document=document,
            document_id=doc_id
        )
        response = search_client.create_document(request=request)
        print(f"✅ Successfully indexed document: {response.name}")
    except Exception as e:
        print(f"❌ Error indexing document {doc_id}: {str(e)}")
