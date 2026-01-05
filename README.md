# 🥗 Nutri_AI
**AI-Powered Food Ingredient Analysis Platform**

Nutri_AI is an intelligent food ingredient analysis platform that helps users understand ingredients, health risks, and nutritional trade-offs using Google Gemini.
It supports text, image, camera, and barcode inputs with context-aware multi-turn conversations.

---

🧠 Smart Ingredient Analysis  
Ingredient Detection: Identify ingredients from text, images, and camera input  
Health Risk Analysis: Explain potential health risks and sensitivities  
Nutritional Trade-offs: Highlight benefits vs drawbacks of ingredients  
Uncertainty Awareness: Clearly communicates uncertain or missing data  
Indian Food Context: Tailored analysis for Indian packaged and street foods  

💬 Conversational Intelligence  
Multi-Turn Conversations: Maintains chat context across follow-ups  
Intent Inference: Detects health, diet, curiosity, or safety intent  
Follow-up Awareness: Understands previous messages for better answers  
Structured Responses: Clear sections like verdict, risks, trade-offs  
Fallback Reasoning: Works even when AI response is unavailable  

📷 Multiple Input Methods  
Text Input: Manual ingredient or food name entry  
Image Upload: OCR-based ingredient extraction from labels  
Live Camera: Real-time ingredient analysis using camera  
Barcode Scan: Product lookup using OpenFoodFacts database  

🎨 Modern UI/UX  
Responsive Design: Works on mobile, tablet, and desktop  
Light / Dark Mode: User-friendly theme switching  
Streaming Responses: Real-time AI output rendering  
Insight Cards: Structured UI for risks, tips, and explanations  

🛠️ Technology Stack  

AI  
Google Gemini 2.5 Flash  
Reasoning-based responses  
Intent-aware analysis  
Uncertainty handling  

Backend  
FastAPI – Async backend  
Redis – Session storage  
JWT – Authentication  
Pydantic – Validation  
OpenFoodFacts – Barcode data  

Frontend  
React 18 + TypeScript  
Vite  
Tailwind CSS  
shadcn/ui  
Streaming UI  

🚀 Quick Start  

Backend  
cd backend  
pip install -r requirements.txt  
uvicorn app.main:app --reload  

Frontend  
cd frontend  
npm install  
npm run dev  

Access  
Frontend: http://localhost:3000  

📁 Project Structure  

Nutri_AI/  
├── README.md                  # Project documentation  
├── backend/                   # FastAPI backend  
│   ├── app/                   # Core application  
│   │   ├── api/routes/         # API routes  
│   │   │   ├── chat.py         # AI chat endpoints  
│   │   │   ├── analyze.py      # Food analysis logic  
│   │   │   ├── product.py      # Barcode lookup  
│   │   │   └── session.py      # Session handling  
│   │   ├── services/           # Business logic  
│   │   │   ├── gemini_service.py        # Gemini integration  
│   │   │   ├── reasoning_service_v2.py  # Reasoning engine  
│   │   │   ├── intent_service.py        # Intent detection  
│   │   │   └── jwt_service.py           # JWT handling  
│   │   ├── utils/              # Helper utilities  
│   │   │   ├── session_manager.py       # Redis sessions  
│   │   │   ├── uncertainty.py            # Uncertainty logic  
│   │   │   └── json_guard.py             # Safe JSON output  
│   │   └── models/             # Data models  
│   └── main.py                 # App entry point  
├── frontend/                   # React frontend  
│   ├── src/  
│   │   ├── components/         # UI components  
│   │   │   ├── ChatContainer.tsx        # Chat layout  
│   │   │   ├── ChatMessage.tsx          # Message UI  
│   │   │   ├── ChatInput.tsx            # Input handling  
│   │   │   ├── LiveCameraAnalyzer.tsx   # Camera analysis  
│   │   │   └── BarcodeScanner.tsx       # Barcode scanning  
│   │   ├── lib/                # Utilities  
│   │   │   ├── jwtService.ts            # Token logic  
│   │   │   └── aiUtils.ts               # AI helpers  
│   │   └── pages/              # App pages  
│   ├── package.json            # Frontend dependencies  
│   └── vite.config.ts          # Vite config  

🔒 Security Features  
JWT Authentication  
Session isolation  
Input validation  
Secure APIs  

📈 Performance Optimization  
Async APIs  
Redis caching  
Efficient OCR  
Optimized streaming  

🎯 Future Enhancements  
Mobile app  
Expanded food DB  
Diet-based insights  
Multi-language support  
Allergy profiles
