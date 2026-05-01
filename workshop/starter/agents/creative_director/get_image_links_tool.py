"""Image links tool: generates short-lived HTTPS URLs for GCS images."""
import os
import re
from datetime import timedelta


def get_image_links(gcs_uris: list[str]) -> dict:
    """
    Generate short-lived HTTPS links for GCS images so they can be opened in any browser.

    Call this once with all collected gcs_uri values before delivering the final campaign summary.

    Args:
        gcs_uris: List of GCS URIs (gs://bucket/path) from the Designer

    Returns:
        {"status": "success", "links": [{"concept": "...", "url": "https://..."}]}
        or {"status": "error", "error": "..."}
    """
    try:
        from google.cloud import storage as gcs
        import google.auth

        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        client = gcs.Client(project=project_id)

        # Detect credential type to choose signing method
        credentials, _ = google.auth.default()
        use_signed = hasattr(credentials, "service_account_email")

        links = []
        for uri in gcs_uris:
            without_prefix = uri[len("gs://"):]
            bucket_name, blob_path = without_prefix.split("/", 1)
            blob = client.bucket(bucket_name).blob(blob_path)

            # Extract a readable concept label from the blob path
            filename = blob_path.rsplit("/", 1)[-1]          # e.g. caption1_concept_a-ab12cd34.png
            concept = re.sub(r"-[0-9a-f]{8}\.[^.]+$", "", filename)  # strip uuid + ext

            if use_signed:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(hours=1),
                    method="GET",
                )
            else:
                # User ADC credentials can't sign - return public URL instead.
                # Requires the GCS bucket to have public read access.
                url = f"https://storage.googleapis.com/{bucket_name}/{blob_path}"

            links.append({"concept": concept, "url": url})

        return {"status": "success", "links": links, "signed": use_signed}

    except Exception as e:
        return {"status": "error", "error": str(e)}
