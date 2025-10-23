"""FastAPI backend for RizzAI opening line generation.

This server provides an API endpoint for generating opening lines
based on uploaded images and profile descriptions.
"""

import io
import os

import torch
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from PIL import Image
from pydantic import BaseModel
from transformers import (
    BitsAndBytesConfig,
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
    temperature: float
    max_tokens: int


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

    base_model_name = "Salesforce/blip2-opt-2.7b"
    adapter_path = "../models/blip2_rizz_finetuned"

    # Check if adapter exists
    if not os.path.exists(adapter_path):
        raise RuntimeError(
            f"Fine-tuned model not found at {adapter_path}. "
            "Please train the model first or update the path."
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model on {device}...")

    processor = Blip2Processor.from_pretrained(base_model_name)

    # Configure quantization for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
    )

    model = Blip2ForConditionalGeneration.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map={"": 0} if device == "cuda" else None,
    )

    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    print("Model loaded successfully!")


@app.on_event("startup")
async def startup_event():
    """Load model when server starts."""
    # load_model()


def generate_opening_line(
    image: Image.Image,
    profile_text: str,
    temperature: float = 1.0,
    max_new_tokens: int = 100,
) -> str:
    """Generate an opening line for a profile.

    Args:
        image: Profile image
        profile_text: Text description of the profile
        temperature: Sampling temperature (higher = more creative)
        max_new_tokens: Maximum number of tokens to generate

    Returns:
        Generated opening line
    """
    # Create prompt
    prompt = f"{profile_text}\n\nQuestion: What is the best flirting opening line to start a conversation with her on Tinder? Answer:"

    # Process inputs
    dtype = torch.float16 if device == "cuda" else torch.float32
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(
        device, dtype=dtype
    )

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
            num_beams=4,
            repetition_penalty=1.2,
        )

    # Decode
    generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[
        0
    ].strip()

    return generated_text


@app.post("/generate", response_model=GenerateResponse)
async def generate_lines(
    image: UploadFile = File(...),
    description: str = Form(...),
):
    """Generate 3 opening lines with different parameters.

    Args:
        image: Uploaded profile image
        description: Text description of the profile

    Returns:
        List of 3 opening lines with different generation parameters
    """
    # Read and process image
    image_data = await image.read()
    pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")

    # Generate 3 opening lines with different parameters
    opening_lines = []

    # Line 1: Balanced creativity
    # line1 = generate_opening_line(
    #     image=pil_image,
    #     profile_text=description,
    #     temperature=0.9,
    #     max_new_tokens=80,
    # )
    line1 = "Your smile is contagious! What's the secret to keeping it so bright?"

    opening_lines.append(OpeningLine(text=line1, temperature=0.9, max_tokens=80))

    # Line 2: More creative
    # line2 = generate_opening_line(
    #     image=pil_image,
    #     profile_text=description,
    #     temperature=1.2,
    #     max_new_tokens=100,
    # )
    line2 = "If you were a fruit, you'd be a fineapple! What's your favorite way to unwind after a long day?"
    opening_lines.append(OpeningLine(text=line2, temperature=1.2, max_tokens=100))

    # # Line 3: Most creative
    # line3 = generate_opening_line(
    #     image=pil_image,
    #     profile_text=description,
    #     temperature=1.5,
    #     max_new_tokens=120,
    # )
    line3 = "Are you made of copper and tellurium? Because you're Cu-Te! What's the most adventurous thing you've ever done?"
    opening_lines.append(OpeningLine(text=line3, temperature=1.5, max_tokens=120))

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
