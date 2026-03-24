# data-pipeline/ingestion/main.py
import os
import json
import logging
import functions_framework
from google.cloud import storage
from google.cloud import discoveryengine_v1beta as discoveryengine
from parser import extract_text, map_rbac_roles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
# ...
@functions_framework.cloud_event
def process_gcs_upload(cloud_event):
    """
    Triggered by a GCS upload (Eventarc or Cloud Storage trigger).
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    # Skip directory placeholders
    if file_name.endswith("/"):
        logger.info(f"📁 Skipping directory placeholder: {file_name}")
        return

    gcs_uri = f"gs://{bucket_name}/{file_name}"
    logger.info(f"🔄 Processing new upload: {gcs_uri}")

    # 1. Map RBAC Metadata
    # We still need to map roles based on the path
    metadata = map_rbac_roles(file_name)
    logger.info(f"🏷️ Assigned RBAC metadata for {file_name}: {json.dumps(metadata)}")

    # 2. Determine MIME Type
    mime_type = "text/plain"
    # ...
    # 3. Push to Vertex AI Search using URI
    # ...
    try:
        request = discoveryengine.CreateDocumentRequest(
            parent=parent,
            document=document,
            document_id=doc_id
        )
        response = search_client.create_document(request=request)
        logger.info(f"✅ Successfully indexed document from URI: {response.name}")
    except Exception as e:
        logger.error(f"❌ Error indexing document {doc_id}: {str(e)}", exc_info=True)
