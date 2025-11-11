"""FastAPI backend for RizzAI opening line generation.

This server provides an API endpoint for generating opening lines
based on uploaded images and profile descriptions.
"""

import io
from pathlib import Path

import torch
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from transformers import (
    Blip2ForConditionalGeneration,
    Blip2Processor,
)


app = FastAPI(
    title="RizzAI API",
    description="Generate opening lines from images and descriptions",
)

# Add CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OpeningLine(BaseModel):
    """Model for an opening line with generation parameters."""

    text: str
    kwargs: dict


class GenerateRequest(BaseModel):
    """Request model for generating opening lines with custom kwargs."""
    
    configs: list[dict]  # List of kwargs dictionaries for model.generate()


class GenerateResponse(BaseModel):
    """Response model for opening line generation."""

    opening_lines: list[OpeningLine]


# Global variables for model and processor
model = None
processor = None
device = None


def load_model():
    """Load the fine-tuned BLIP-2 model on startup."""
    global model, processor, device

    # Path to the fine-tuned model
    model_path = Path("..") / "models" / "final"
    
    # Check if model exists
    if not model_path.exists():
        print(f"Warning: Fine-tuned model not found at {model_path}")
        print("The API will still run but /generate will fail until model is available.")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model from {model_path} on {device}...")

    processor = Blip2Processor.from_pretrained(str(model_path))
    model = Blip2ForConditionalGeneration.from_pretrained(
        str(model_path),
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    
    if device == "cuda":
        model = model.to(device)
    
    model.eval()

    print("Model loaded successfully!")


@app.on_event("startup")
async def startup_event():
    """Load model when server starts."""
    load_model()


def generate_opening_line(
    image: Image.Image,
    profile_text: str,
    **generation_kwargs
) -> str:
    """Generate an opening line for a profile.

    Args:
        image: Profile image
        profile_text: Text description of the profile
        **generation_kwargs: Any kwargs to pass to model.generate()

    Returns:
        Generated opening line
    """
    if model is None or processor is None:
        raise RuntimeError("Model not loaded. Please ensure the model is trained and available.")
    
    # Create prompt
    prompt = f"Her profile: {profile_text}"

    # Process inputs
    dtype = torch.float16 if device == "cuda" else torch.float32
    inputs = processor(images=image, text=prompt, return_tensors="pt")
    
    # Move inputs to device
    inputs = {k: v.to(device, dtype=dtype) if v.dtype == torch.float32 else v.to(device) 
              for k, v in inputs.items()}

    # Generate
    with torch.no_grad():
        outputs = model.generate(**inputs, **generation_kwargs)

    # Decode
    generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()

    return generated_text


@app.post("/generate", response_model=GenerateResponse)
async def generate_lines(
    image: UploadFile = File(...),
    description: str = Form(...),
    configs: str = Form("[]"),  # JSON string of list of config dicts
):
    """Generate opening lines with custom generation parameters.

    Args:
        image: Uploaded profile image
        description: Text description of the profile
        configs: JSON string containing list of generation configs (kwargs for model.generate)

    Returns:
        List of opening lines generated with provided configurations
    """
    import json
    
    # Read and process image
    image_data = await image.read()
    pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")

    # Parse configs
    try:
        config_list = json.loads(configs)
    except json.JSONDecodeError:
        config_list = []
    
    # If no configs provided, use defaults
    if not config_list:
        config_list = [
            {"max_new_tokens": 80, "temperature": 0.9, "do_sample": True, "top_p": 0.9},
            {"max_new_tokens": 100, "temperature": 1.2, "do_sample": True, "top_p": 0.9},
            {"max_new_tokens": 120, "temperature": 1.5, "do_sample": True, "top_p": 0.9},
        ]

    # Generate opening lines with different parameters
    opening_lines = []
    
    for config in config_list:
        try:
            line = generate_opening_line(
                image=pil_image,
                profile_text=description,
                **config
            )
            opening_lines.append(OpeningLine(text=line, kwargs=config))
        except Exception as e:
            # If generation fails, add error message
            opening_lines.append(OpeningLine(
                text=f"Generation failed: {str(e)}", 
                kwargs=config
            ))

    return GenerateResponse(opening_lines=opening_lines)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RizzAI API",
        "status": "running",
        "device": device,
        "endpoints": {
            "generate": "/generate (POST) - Generate opening lines",
            "docs": "/docs - API documentation",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": device,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
