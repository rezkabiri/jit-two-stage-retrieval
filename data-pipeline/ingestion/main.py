# data-pipeline/ingestion/main.py
import os
import json
import functions_framework
from google.cloud import storage
from google.cloud import discoveryengine_v1beta as discoveryengine
from parser import extract_text, map_rbac_roles

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

    # Skip directory placeholders
    if file_name.endswith("/"):
        print(f"📁 Skipping directory placeholder: {file_name}")
        return

    gcs_uri = f"gs://{bucket_name}/{file_name}"
    print(f"🔄 Processing new upload: {gcs_uri}")

    # 1. Map RBAC Metadata
    # We still need to map roles based on the path
    metadata = map_rbac_roles(file_name)
    print(f"🏷️ Assigned RBAC metadata: {json.dumps(metadata)}")

    # 2. Determine MIME Type
    mime_type = "text/plain"
    if file_name.lower().endswith(".pdf"):
        mime_type = "application/pdf"
    elif file_name.lower().endswith(".md"):
        mime_type = "text/markdown"
    elif file_name.lower().endswith(".txt"):
        mime_type = "text/plain"

    # 3. Push to Vertex AI Search using URI
    parent = search_client.branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        branch="default_branch"
    )

    # Use the file name (sanitized) as the document ID
    doc_id = file_name.replace("/", "_").replace(".", "_").lower()[:60]

    # Use the URI field which is highly stable across SDK versions
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
        response = search_client.create_document(request=request)
        print(f"✅ Successfully indexed document from URI: {response.name}")
    except Exception as e:
        print(f"❌ Error indexing document {doc_id}: {str(e)}")
