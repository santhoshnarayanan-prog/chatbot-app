# MCUBE LUNA AI Chatbot

A professional AI-powered support chatbot with knowledge base integration, built with FastAPI and modern AI providers.

## Features

✨ **Core Features**
- 24/7 AI support chatbot
- Real-time chat interface
- Knowledge base integration with semantic search
- Document/PDF/DOCX upload support
- Website content crawling
- Automatic ticket creation with email notifications
- Multi-provider AI support (Groq, OpenAI)

🎯 **Technical Features**
- FastAPI backend with async support
- ChromaDB vector database for RAG
- SQLite for conversation storage
- Sentence transformers for embeddings
- CORS-enabled for multi-origin access
- Admin panel for knowledge management

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/chatbot-app.git
cd chatbot-app

# Setup backend
cd backend
python -m venv venv311
source venv311/bin/activate  # On Windows: venv311\Scripts\activate
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the app at: `http://localhost:8000`

## Project Structure

```
chatbot-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/              # API routes (chat, knowledge)
│   │   ├── services/            # Business logic
│   │   ├── models/              # Database models
│   │   └── db/                  # Database config
│   ├── requirements.txt
│   ├── Procfile                 # Render deployment
│   └── chroma_db/               # Vector database
├── frontend/
│   ├── index.html               # Chat UI
│   ├── admin.html               # Admin panel
│   ├── script.js                # Chat logic
│   └── style.css
└── README.md
```

## API Endpoints

### Chat
- `POST /chat/message` - Send message to bot
- `GET /chat/history` - Get conversation history

### Knowledge Base
- `POST /knowledge/upload` - Upload document
- `POST /knowledge/website` - Add website content
- `GET /knowledge/sources` - List knowledge sources
- `DELETE /knowledge/sources/{id}` - Delete knowledge source

### Health
- `GET /health` - Server health check
- `GET /docs` - Interactive API documentation

## Configuration

Create `.env` file in backend directory:

```env
# AI Provider (groq or openai)
AI_PROVIDER=groq

# Groq API Key (https://console.groq.com)
GROQ_API_KEY=your_key_here

# OpenAI API Key (optional, for AI_PROVIDER=openai)
OPENAI_API_KEY=your_key_here

# Email notifications (optional)
SMTP_SERVER=smtp.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
SUPPORT_EMAIL=support@yourcompany.com
```

## Deployment

### Deploy to Render (Free)

1. Push to GitHub
2. Go to https://render.com
3. Create new Web Service
4. Connect your GitHub repo
5. Configure:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Deploy!

Your app will be live at: `https://your-app-name.onrender.com`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## Development

### Run Tests
```bash
cd backend
pytest
```

### View API Docs
Open `http://localhost:8000/docs` in browser

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Uvicorn
- **AI:** Groq API, OpenAI API (optional)
- **Vector DB:** ChromaDB
- **Embeddings:** Sentence Transformers
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Database:** SQLite

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create a GitHub issue or contact the development team.

---

**Made with ❤️ by MCUBE Team**
