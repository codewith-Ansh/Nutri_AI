# NutriAI Backend - Phase 1

AI-Native Food Ingredient Insights API built with FastAPI

## Setup Instructions

1. **Create virtual environment**

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
text

2. **Install dependencies**

pip install -r requirements.txt
text

3. **Configure environment**

cp .env.example .env
Edit .env and add your API keys
text

4. **Run the server**

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
text

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Analysis
- `POST /api/analyze/text` - Analyze ingredient text
- `POST /api/analyze/image` - Analyze ingredient from image

### Chat
- `POST /api/chat` - Conversational ingredient analysis

## Tech Stack
- FastAPI 0.104+
- OpenAI GPT-4o-mini
- Tesseract OCR
- Redis for sessions
