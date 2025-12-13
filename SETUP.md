# Setup Instructions

## Prerequisites

1. **Docker & Docker Compose**
   - Install Docker Desktop: https://www.docker.com/products/docker-desktop
   - Verify installation: `docker --version` and `docker-compose --version`

2. **Google Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key for use in environment variables

## Step-by-Step Setup

### 1. Clone/Download the Project

```bash
cd exam
```

### 2. Create Environment File

Create a `.env` file in the root directory:

```bash
# Windows (PowerShell)
New-Item -Path .env -ItemType File

# Linux/Mac
touch .env
```

Add the following content to `.env`:

```env
GEMINI_API_KEY=your_actual_api_key_here
OCR_LANGUAGE=en
MAX_FILE_SIZE_MB=10
```

**Important**: Replace `your_actual_api_key_here` with your actual Gemini API key.

### 3. Build and Start Services

```bash
docker-compose up --build
```

This command will:
- Build Docker images for backend and frontend
- Install all dependencies
- Start both services

**First build may take 5-10 minutes** (downloading dependencies and models).

### 4. Verify Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

### 5. Test the Application

1. Open http://localhost:3000 in your browser
2. Upload a sample exam file (PDF, image, or text)
3. Follow the step-by-step workflow

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use:

1. **Option 1**: Stop the conflicting service
2. **Option 2**: Modify ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "3001:3000"  # Change frontend port
     - "8001:8000"  # Change backend port
   ```

### Docker Build Fails

**Backend issues:**
```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend only
docker-compose build --no-cache backend
```

**Frontend issues:**
```bash
# Check frontend logs
docker-compose logs frontend

# Clear npm cache and rebuild
docker-compose build --no-cache frontend
```

### OCR Not Working

1. Ensure Tesseract is installed (handled by Dockerfile)
2. Check that images are clear and readable
3. Verify file format is supported (PDF, PNG, JPG, TXT)

### Gemini API Errors

1. Verify API key is correct in `.env`
2. Check API quota: https://makersuite.google.com/app/apikey
3. Ensure internet connectivity
4. Check backend logs: `docker-compose logs backend`

### Services Won't Start

```bash
# Stop all services
docker-compose down

# Remove volumes (if needed)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

## Development Mode

### Backend Development (Local)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development (Local)

```bash
cd frontend
npm install
npm start
```

## Production Deployment

For production deployment:

1. **Update CORS settings** in `backend/app/config.py`
2. **Set proper environment variables** (use secrets management)
3. **Use production builds**:
   ```bash
   # Frontend production build
   cd frontend
   npm run build
   
   # Use nginx or similar to serve static files
   ```
4. **Configure reverse proxy** (nginx, Apache, etc.)
5. **Set up SSL/TLS certificates**
6. **Use database** instead of in-memory storage

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `OCR_LANGUAGE` | Language for OCR (en, es, fr, etc.) | en |
| `MAX_FILE_SIZE_MB` | Maximum file upload size | 10 |
| `GEMINI_MODEL` | Gemini model to use | gemini-pro |

## Next Steps

- Read [README.md](./README.md) for usage instructions
- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Check [PROMPTS.md](./PROMPTS.md) for AI prompt details

