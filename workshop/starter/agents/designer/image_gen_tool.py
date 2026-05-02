"""Gemini native image generation tool. Generates image, uploads to GCS, returns URI."""
import io
import os
import uuid

from google import genai
from google.adk.tools import ToolContext
from google.genai import types


async def generate_image(
    concept_name: str,
    image_prompt: str,
    aspect_ratio: str,
    tool_context: ToolContext,
) -> dict:
    """
    Generate an image with Gemini native image generation and upload it to GCS.

    Args:
        concept_name: Short identifier for this image concept (e.g. "post1_concept_a")
        image_prompt: Full image generation prompt string
        aspect_ratio: "1:1" for square (1080x1080) or "4:5" for portrait (1080x1350)

    Returns:
        {"status": "success", "gcs_uri": "gs://...", "concept_name": "..."}
        or {"status": "error", "error": "..."}
    """
    bucket_name = os.environ.get("GCS_IMAGES_BUCKET")
    if not bucket_name:
        return {"status": "error", "error": "GCS_IMAGES_BUCKET env var not set"}

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    # Use a dedicated image-capable model; separate from the text GEMINI_MODEL.
    # gemini-3.1-flash-image-preview does NOT support function calling, so it cannot
    # be used as an ADK agent - but calling it directly here is fine.
    image_model = os.environ.get(
        "GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview"
    )

    # Aspect ratio is not an API parameter for Gemini native generation - inject it
    # into the prompt so the model respects the desired Instagram format.
    aspect_hint = {
        "1:1": "square 1:1 aspect ratio (1080x1080)",
        "4:5": "portrait 4:5 aspect ratio (1080x1350)",
    }.get(aspect_ratio, f"{aspect_ratio} aspect ratio")
    prompt_with_aspect = f"{image_prompt}\n\nGenerate this as a {aspect_hint} image."

    try:
        # TODO 1: Create a genai.Client with vertexai=True, project, and location.
        # Call client.models.generate_content() with:
        #   - model=image_model
        #   - contents=prompt_with_aspect
        #   - config=types.GenerateContentConfig(
        #       response_modalities=["IMAGE", "TEXT"],
        #       http_options=types.HttpOptions(
        #           retry_options=types.HttpRetryOptions(
        #               attempts=5, exp_base=2, initial_delay=30,
        #               http_status_codes=[429, 500, 503, 504],
        #           ),
        #           timeout=180_000,
        #       ),
        #     )
        # Store the result in `response`.
        # Note: retry_options here is essential — image generation quota (DSQ) recovers
        # slowly, so initial_delay=30s gives the pool time to refill between attempts.

        # TODO 2: Extract image bytes from the response.
        # Iterate over response.candidates[0].content.parts.
        # Find the first part where part.inline_data is not None.
        # Set image_bytes = part.inline_data.data and mime_type = part.inline_data.mime_type or "image/png".
        # If no image_bytes found, return {"status": "error", "error": "Gemini returned no image data"}.
        image_bytes = None
        mime_type = "image/png"

        # TODO 3: Upload image_bytes to GCS and return the URI.
        # - Determine the file extension from mime_type ("jpg" if "jpeg" in mime_type else "png").
        # - Create a storage.Client and get the bucket (bucket_name).
        # - Build blob_name: f"campaign-images/{concept_name}-{uuid.uuid4().hex[:8]}.{ext}"
        # - Upload via blob.upload_from_file(io.BytesIO(image_bytes), content_type=mime_type).
        # - Build gcs_uri = f"gs://{bucket_name}/{blob_name}".
        gcs_uri = None

        # Save as ADK artifact so adk web renders the image inline when testing
        # the Designer directly. Silently skipped when no artifact service is
        # configured (e.g. Cloud Run deployment).
        if image_bytes and gcs_uri:
            ext = "jpg" if "jpeg" in mime_type else "png"
            try:
                artifact = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                await tool_context.save_artifact(f"{concept_name}.{ext}", artifact)
            except ValueError:
                pass

            return {"status": "success", "gcs_uri": gcs_uri, "concept_name": concept_name}

        return {"status": "error", "error": "Image generation incomplete - fill in the TODOs"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
