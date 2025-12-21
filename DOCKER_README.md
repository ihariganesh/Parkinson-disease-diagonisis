# Docker Setup for Parkinson Care Application

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Run the Application

1. **Set up environment variables**
   ```bash
   # Create .env file in the root directory
   cp .env.example .env
   
   # Edit .env and add your API keys:
   # GROQ_API_KEY=your_groq_api_key
   # GEMINI_API_KEY=your_gemini_api_key (optional)
   # SECRET_KEY=your-secret-key-here
   ```

2. **Build and run containers**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Mode

Run with hot-reload:
```bash
docker-compose up
```

### Production Mode

Build optimized images:
```bash
docker-compose -f docker-compose.yml up -d
```

## Commands

**Start services**
```bash
docker-compose up -d
```

**Stop services**
```bash
docker-compose down
```

**View logs**
```bash
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend
```

**Rebuild containers**
```bash
docker-compose up --build
```

**Remove all containers and volumes**
```bash
docker-compose down -v
```

## Container Details

### Backend Container
- **Image**: Python 3.13-slim
- **Port**: 8000
- **Volumes**: 
  - `./backend/uploads` - Uploaded medical files
  - `./backend/models` - Pre-trained ML models
  - `./backend/parkinson_dev.db` - SQLite database

### Frontend Container
- **Image**: Node 20 Alpine + Nginx
- **Port**: 80
- **Build**: Multi-stage build (Node for building, Nginx for serving)

## Environment Variables

Required in `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your-secret-key-here
ENABLE_GEMINI=false
AUDIO_FAST_MODE=true
```

## Persistent Data

Data persisted across container restarts:
- Database: `parkinson_dev.db`
- Uploaded files: `backend/uploads/`
- ML models: `backend/models/`

## Troubleshooting

**Backend won't start**
```bash
docker-compose logs backend
# Check for missing models or API keys
```

**Frontend can't connect to backend**
- Verify `VITE_API_BASE_URL` in docker-compose.yml
- Check backend container is running: `docker ps`

**Database issues**
```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

## Deployment

For production deployment, consider:
1. Use PostgreSQL instead of SQLite
2. Add SSL/TLS certificates
3. Use environment-specific `.env` files
4. Set up proper logging and monitoring
5. Use Docker secrets for sensitive data

## Notes

- Models must be present in `backend/models/` directory
- First run may take longer due to image building
- Frontend uses Nginx for production-grade serving
- Backend uses Uvicorn ASGI server
