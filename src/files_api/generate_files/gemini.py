# """Generate text, images, and audio from prompts using Google Gemini's API."""

# from typing import (
#     Literal,
#     Optional,
#     Tuple,
# )

# from aws_embedded_metrics import MetricsLogger
# from aws_embedded_metrics.storage_resolution import StorageResolution
# from google import genai
# from google.genai import types

# from files_api.monitoring.metrics import metrics_ctx

# SYSTEM_PROMPT = "You are an autocompletion tool that produces text files given constraints."


# async def get_text_chat_completion(prompt: str, gemini_client: Optional[genai.Client] = None) -> str:
#     """Generate a text chat completion from a given prompt."""
#     # get the Gemini client
#     client = gemini_client or genai.Client()

#     # get the completion
#     response = await client.aio.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             system_instruction=SYSTEM_PROMPT,
#             max_output_tokens=100,  # avoid burning your credits
#             temperature=1.0,
#         ),
#     )

#     metrics: MetricsLogger | None = metrics_ctx.get()
#     if metrics:
#         # Gemini response has usage_metadata with total_token_count
#         if response.usage_metadata and response.usage_metadata.total_token_count:
#             metrics.put_metric(
#                 key="GeminiTokensUsage",
#                 value=float(response.usage_metadata.total_token_count),
#                 unit="Count",
#                 storage_resolution=StorageResolution.STANDARD,
#             )
#     return response.text or ""


# async def generate_image(prompt: str, gemini_client: Optional[genai.Client] = None) -> bytes | None:
#     """Generate an image from a given prompt."""
#     # get the Gemini client
#     client = gemini_client or genai.Client()

#     # get image response from Gemini
#     response = await client.aio.models.generate_content(
#         model="gemini-2.5-flash-image",
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             response_modalities=["IMAGE"],
#             image_config=types.ImageConfig(
#                 aspect_ratio="1:1",
#             ),
#         ),
#     )

#     metrics: MetricsLogger | None = metrics_ctx.get()
#     if metrics:
#         metrics.put_metric(key="GeminiImageGeneratedCount", value=1, unit="Count")

#     # Extract the image data from the response
#     # Gemini returns inline_data with the image bytes
#     if response.parts:
#         for part in response.parts:
#             if part.inline_data is not None and part.inline_data.data:
#                 # Return the raw bytes
#                 return part.inline_data.data

#     return None


# async def generate_text_to_speech(
#     prompt: str,
#     gemini_client: Optional[genai.Client] = None,
#     response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3",
# ) -> Tuple[bytes, str]:
#     """
#     Generate text-to-speech audio from a given prompt.

#     Returns the audio content as bytes and the MIME type as a string.
#     """
#     # get the Gemini client
#     client = gemini_client or genai.Client()

#     # Map response format to MIME type
#     mime_type_map = {
#         "mp3": "audio/mpeg",
#         "opus": "audio/opus",
#         "aac": "audio/aac",
#         "flac": "audio/flac",
#         "wav": "audio/wav",
#         "pcm": "audio/pcm",
#     }

#     # get audio response from Gemini
#     response = await client.aio.models.generate_content(
#         model="gemini-2.5-flash-preview-tts",
#         contents=f"Say: {prompt}",
#         config=types.GenerateContentConfig(
#             response_modalities=["AUDIO"],
#             speech_config=types.SpeechConfig(
#                 voice_config=types.VoiceConfig(
#                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
#                         voice_name="Kore",
#                     )
#                 )
#             ),
#         ),
#     )

#     # Get the audio content as bytes
#     file_content_bytes: bytes = b""
#     file_mime_type: str = mime_type_map.get(response_format, "audio/wav")

#     # Extract audio data from response
#     if response.parts:
#         for part in response.parts:
#             if part.inline_data is not None and part.inline_data.data:
#                 file_content_bytes = bytes(part.inline_data.data)
#                 file_mime_type = part.inline_data.mime_type or file_mime_type
#                 break

#     metrics: MetricsLogger | None = metrics_ctx.get()
#     if metrics:
#         metrics.put_metric(key="GeminiTextToSpeechGeneratedCount", value=1, unit="Count")

#     return file_content_bytes, file_mime_type
