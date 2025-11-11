# RizzAI Backend

FastAPI backend server for the RizzAI opening line generator.

## Features

- 🚀 FastAPI-based REST API
- 🤖 BLIP-2 model with LoRA fine-tuning
- 🎯 Generates 3 opening lines with different temperature parameters
- 💾 8-bit quantization for memory efficiency
- 🔥 GPU support (CUDA) with CPU fallback

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure the fine-tuned model is available:
   - The model should be in `../blip2_rizz_finetuned/`
   - If not, train the model first using `../blip2/train_blip2.py`

## Running the Server

Start the server:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

### POST /generate
Generate 3 opening lines from an image and description.

**Request:**
- `image`: Image file (multipart/form-data)
- `description`: Profile description text

**Response:**
```json
{
  "opening_lines": [
    {
      "text": "Generated opening line...",
      "temperature": 0.9,
      "max_tokens": 80
    },
    {
      "text": "Another opening line...",
      "temperature": 1.2,
      "max_tokens": 100
    },
    {
      "text": "Creative opening line...",
      "temperature": 1.5,
      "max_tokens": 120
    }
  ]
}
```

### GET /health
Check server health and model status.

## Configuration

The backend uses:
- **Base Model:** Salesforce/blip2-opt-2.7b
- **Fine-tuned Adapter:** ../blip2_rizz_finetuned/
- **Quantization:** 8-bit for memory efficiency
- **Device:** Automatic (CUDA if available, else CPU)

## Notes

- First request may be slow as the model loads into memory
- GPU recommended for faster inference
- Model requires ~6GB of memory with 8-bit quantization
