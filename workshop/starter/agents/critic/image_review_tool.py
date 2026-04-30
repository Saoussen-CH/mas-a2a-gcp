"""Multimodal image review tool. Loads image from GCS via Part.from_uri()."""
import os

from google import genai
from google.genai import types


def review_image(gcs_uri: str, concept_name: str, campaign_context: str) -> dict:
    """
    Review an image stored in GCS using Gemini multimodal.

    Vertex AI fetches the image from GCS server-side - no GCS credentials needed
    on the Critic container.

    Args:
        gcs_uri: GCS URI of the image (gs://bucket/path.png)
        concept_name: Name/label for this image concept
        campaign_context: Brief describing the campaign, brand voice, target audience

    Returns:
        {"status": "success", "concept_name": "...", "review": "..."}
        or {"status": "error", "concept_name": "...", "error": "..."}
    """
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    try:
        client = genai.Client(vertexai=True, project=project_id, location=location)

        # Infer mime type from the GCS URI extension
        ext = gcs_uri.rsplit(".", 1)[-1].lower() if "." in gcs_uri else "png"
        mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/png")
        image_part = types.Part.from_uri(file_uri=gcs_uri, mime_type=mime_type)

        prompt = f"""You are reviewing an AI-generated image for an Instagram campaign.

Campaign context: {campaign_context}
Concept name: {concept_name}

Evaluate this image on:
- Visual quality and composition
- Brand alignment and audience fit
- Instagram platform suitability
- Visual-copy alignment potential

Provide your review in this format:
- Score: X/10
- Status: APPROVED or NEEDS_REVISION
- What Works: [specific visual strengths]
- Issues: [specific problems if any]
- Suggestions: [concrete improvements if NEEDS_REVISION]
"""

        response = client.models.generate_content(
            model=model,
            contents=[image_part, prompt],
        )

        return {
            "status": "success",
            "concept_name": concept_name,
            "review": response.text,
        }

    except Exception as e:
        return {"status": "error", "concept_name": concept_name, "error": str(e)}
