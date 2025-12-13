# Quick Start Guide

## 🚀 Get Running in 3 Steps

### Step 1: Get Your API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy it

### Step 2: Configure Environment
Create `.env` file in project root:
```env
GEMINI_API_KEY=paste_your_key_here
```

### Step 3: Start the Application
```bash
docker-compose up --build
```

Wait 2-3 minutes for first-time setup, then:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Usage Flow

1. **Upload Exam**: Upload a solved exam (PDF/image/text)
2. **Parse**: Click "Parse Exam" to extract questions
3. **Submit Answers**: Enter student answers
4. **View Results**: See scores and explanations

## 🛠️ Troubleshooting

**Port in use?** Change ports in `docker-compose.yml`

**API errors?** Check `.env` file has correct `GEMINI_API_KEY`

**Build fails?** 
```bash
docker-compose down
docker-compose up --build --force-recreate
```

## 📚 More Info

- Full setup: [SETUP.md](./SETUP.md)
- Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Complete guide: [README.md](./README.md)

