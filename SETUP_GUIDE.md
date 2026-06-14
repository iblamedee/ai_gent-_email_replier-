# Setup Guide

## Prerequisites

- **Python**: 3.13 or higher
- **Gmail Account**: With API access enabled
- **OpenRouter Account**: For LLM access
- **Docker** (optional): For Redis/Qdrant
- **Git**: For version control

## Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd email-auto-responser
```

### 2. Create Virtual Environment
```bash
# Using uv (recommended)
uv sync

# OR using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Using uv
uv sync

# Using pip
pip install -e .
```

**Dependencies**:
- `fastapi[standard]>=0.104.0` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `google-api-python-client>=2.170.0` - Gmail API
- `google-auth-oauthlib>=1.4.0` - OAuth2 authentication
- `langchain>=1.3.2` - LLM framework
- `langchain-openai>=1.2.2` - OpenAI integration
- `langchain-qdrant>=1.1.0` - Vector DB integration
- `python-dotenv>=0.9.9` - Environment variables
- `rq>=2.9.0` - Job queue
- `valkey>=6.1.1` - Redis client

### 4. Gmail API Setup

#### Step 4.1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Enter project name: "Email Auto-Responder"
4. Click "Create"

#### Step 4.2: Enable Gmail API
1. Search for "Gmail API"
2. Click "Gmail API" in results
3. Click "Enable"

#### Step 4.3: Create OAuth2 Credentials
1. Go to "Credentials" section
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Select "Desktop application"
4. Download JSON file
5. Save as `credentials.json` in project root

#### Step 4.4: Generate Access Token
```python
# Run this Python script once:
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

# This creates token.json automatically
```

### 5. Environment Variables

Create `.env` file in project root:
```bash
# OpenRouter LLM API Key
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional: OpenAI API Key (if using OpenAI instead)
OPENAI_API_KEY=your_openai_api_key
```

**Get OpenRouter API Key**:
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up / Log in
3. Go to API keys section
4. Create new API key
5. Copy and paste into `.env`

### 6. Vector Database Setup (Qdrant)

#### Option A: Docker (Recommended)
```bash
cd queue/
docker-compose up -d

# Verify it's running
curl http://localhost:6333/health
```

#### Option B: Local Installation
```bash
# Install Qdrant
pip install qdrant-client

# Or download from https://qdrant.io/documentation/quick-start/
```

#### Option C: Using Qdrant Cloud
1. Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create collection: `company-database`
3. Update connection URL in `features/retrivier/main.py`

### 7. Create Vector Database Collection

```python
# Run once to create collection:
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="company-database",
    vectors_config={
        "size": 384,  # Perplexity embedding size
        "distance": "Cosine"
    }
)

# Load your company knowledge base documents into this collection
# See features/vector-db_rag/main.py for details
```

## Running the Application

### Option 1: Web API (FastAPI)
```bash
# Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Access web interface
# Open browser to http://localhost:8000
```

### Option 2: CLI Interface
```bash
# Run interactive CLI
python main.py

# Follow prompts to process emails
```

### Option 3: Development with Jupyter
```bash
# Start Jupyter
jupyter notebook

# Open features/retrivier/main_1.ipynb
# Run cells to test retrieval and generation
```

## Directory Verification

After setup, verify your project structure:

```bash
# Should see these files
ls -la credentials.json token.json .env

# Gmail authentication ready
echo "Gmail setup: ✓"

# Vector DB running (if Docker)
docker ps | grep qdrant
echo "Qdrant setup: ✓"

# Dependencies installed
python -c "import fastapi, langchain, qdrant_client; print('Dependencies: ✓')"
```

## Configuration Files

### pyproject.toml
Contains all Python dependencies and project metadata.

**Key sections**:
- `[project]`: Project metadata
- `dependencies`: Package requirements
- `requires-python`: Python version requirement (>=3.13)

### Credentials Files

**credentials.json**: Gmail OAuth2 application credentials
- Downloaded from Google Cloud Console
- DO NOT commit to version control
- Added to `.gitignore`

**token.json**: Gmail user access token
- Generated after first authorization
- Stored in `.gitignore` for security
- Allows API calls on behalf of authenticated user

**.env**: Environment variables
- `OPENROUTER_API_KEY`: LLM provider authentication
- `OPENAI_API_KEY`: Optional, for embeddings
- Added to `.gitignore` for security

## Verification Checklist

- [ ] Python 3.13+ installed: `python --version`
- [ ] Virtual environment activated: `which python` shows venv path
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] Gmail API enabled in Google Cloud Console
- [ ] `credentials.json` present in project root
- [ ] `token.json` generated (first run of token generation script)
- [ ] `.env` file created with API keys
- [ ] Qdrant running: `curl http://localhost:6333/health`
- [ ] `company-database` collection created in Qdrant

## Troubleshooting

### Issue: "No module named 'features'"
**Solution**: Ensure you're in project root and virtual env is activated

### Issue: "Gmail API not enabled"
**Solution**: 
1. Go to Google Cloud Console
2. Search "Gmail API"
3. Click and select "Enable"

### Issue: "Invalid credentials"
**Solution**: 
1. Delete `token.json`
2. Re-run token generation script
3. Authorize the application in browser

### Issue: "Qdrant connection failed"
**Solution**:
```bash
# Check if Qdrant is running
docker ps
# If not running:
cd queue && docker-compose up -d
```

### Issue: "OpenRouter API key invalid"
**Solution**:
1. Log into OpenRouter dashboard
2. Verify API key is active
3. Check `.env` for typos
4. Restart the application

## Next Steps

1. **Upload Company Knowledge**: Add documents to Qdrant `company-database` collection
2. **Test Email Processing**: Send test emails and verify replies
3. **Customize UI**: Modify `templates/index.html` and `static/style.css`
4. **Deploy**: Use production ASGI server (Gunicorn, etc.)
5. **Monitor**: Set up logging and error tracking

## Development Tips

- Use `--reload` flag with Uvicorn for hot reloading during development
- Use Jupyter notebooks (`main_1.ipynb`) for testing features
- Check logs for debugging: `print()` statements and logging module
- Use FastAPI Swagger docs: `http://localhost:8000/docs`

## Security Considerations

- ✅ Never commit credentials to git
- ✅ Use environment variables for secrets
- ✅ Keep `.env` file in `.gitignore`
- ✅ Rotate API keys regularly
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for API endpoints
