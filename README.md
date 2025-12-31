# Nutri_AI

AI-powered food ingredient analysis platform using Google Gemini for intelligent nutritional insights with intent inference.

## Features

- **Ingredient Analysis**: Analyze food ingredients from text or images
- **AI-Powered Chat**: Conversational interface for nutrition questions
- **Intent Inference**: Automatically infer user goals, dietary preferences, and concerns
- **OCR Support**: Extract ingredients from product labels
- **Health Risk Assessment**: Get insights on ingredient health implications
- **Real-time Streaming**: Live AI responses with streaming support

## Tech Stack

- **Backend**: FastAPI + Google Gemini AI
- **Frontend**: React + TypeScript + Vite
- **AI**: Google Gemini 2.0 Flash
- **OCR**: Tesseract.js
- **Styling**: Tailwind CSS + shadcn/ui

## Run Locally

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google Gemini API key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your configuration:
   ```env
   # API Settings
   API_HOST=0.0.0.0
   API_PORT=8000
   DEBUG=true

   # Gemini LLM Settings
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp
   LLM_TEMPERATURE=0.7
   MAX_TOKENS=2048

   # Redis Settings (optional - uses in-memory for now)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   SESSION_EXPIRE_SECONDS=3600

   # Upload Settings
   MAX_UPLOAD_SIZE=10485760
   ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
   UPLOAD_DIR=./uploads

   # CORS Settings
   ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000,http://127.0.0.1:8080
   ```

5. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   The `.env` file should already contain:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:8080

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" 
4. Create a new API key
5. Copy the key and add it to your backend `.env` file

## API Endpoints

### Health Check
- `GET /api/health` - Basic health check
- `GET /api/health/llm` - LLM service health check

### Analysis
- `POST /api/analyze/text` - Analyze ingredient text
- `POST /api/analyze/image` - Analyze ingredient image

### Chat
- `POST /api/chat` - Non-streaming chat
- `POST /api/chat/stream` - Streaming chat (used by frontend)
- `GET /api/chat/{session_id}/history` - Get chat history

### Intent Inference (NEW)
- `POST /api/intent/infer` - Infer user intent from message
- `GET /api/intent/{session_id}` - Get stored intent for session

## Smoke Test

Once both backend and frontend are running, test these endpoints:

1. **Health Check**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Text Analysis**:
   ```bash
   curl -X POST http://localhost:8000/api/analyze/text \\
     -H "Content-Type: application/json" \\
     -d '{"text": "wheat flour, sugar, palm oil, salt"}'
   ```

3. **Chat**:
   ```bash
   curl -X POST http://localhost:8000/api/chat \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Is palm oil healthy?", "session_id": "test123"}'
   ```

4. **Intent Inference**:
   ```bash
   curl -X POST http://localhost:8000/api/intent/infer \\
     -H "Content-Type: application/json" \\
     -d '{"message": "I want to lose weight and avoid sugar", "ingredients": ["sugar", "corn syrup"]}'
   ```

5. **Frontend**: Visit http://localhost:8080 and try the chat interface

## Docker Setup (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./backend:/app
    
  frontend:
    build: ./frontend
    ports:
      - "8080:8080"
    depends_on:
      - backend
```

Run with:
```bash
GEMINI_API_KEY=your_key_here docker-compose up
```

## Migration Notes

This project has been migrated from OpenAI/Anthropic to Google Gemini:

- ✅ Removed `openai` and `anthropic` dependencies
- ✅ Added `google-genai` SDK
- ✅ Updated all LLM service calls to use Gemini
- ✅ Maintained API compatibility for frontend
- ✅ Added streaming support for real-time chat
- ✅ Added intent inference with validated JSON output
- ✅ No OpenAI/Anthropic references remain

## Development

- Backend auto-reloads on file changes with `--reload` flag
- Frontend hot-reloads automatically with Vite
- Check logs in terminal for debugging
- API documentation available at http://localhost:8000/docs

## Troubleshooting

1. **"Gemini API key not configured"**: Make sure you've set `GEMINI_API_KEY` in backend `.env`
2. **CORS errors**: Ensure frontend URL is in `ALLOWED_ORIGINS` in backend `.env`
3. **Port conflicts**: Change ports in `.env` files if 8000/8080 are in use
4. **Module not found**: Make sure you've activated the Python virtual environment