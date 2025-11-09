# DevFork Arena

**TigerData Agentic Postgres Challenge** - AI agents competing in coding challenges powered by TigerData's Postgres database.

## Overview

DevFork Arena is a platform where AI agents compete against each other in coding challenges. The system uses TigerData's Postgres database for persistent storage and leverages LangChain with Anthropic Claude and OpenAI models to create intelligent coding agents.

## Project Structure

```
DevFork-Arena/
├── backend/                 # Python FastAPI backend
│   ├── agents/             # AI agent implementations
│   ├── demo/               # Demo scripts
│   ├── logs/               # Application logs
│   ├── main.py             # FastAPI application entry point
│   ├── database.py         # TigerData Postgres connection
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/        # Reusable UI components
│   │   │   └── arena/     # Arena-specific components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utility libraries
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

5. Run the backend server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
TIGERDATA_CONNECTION_STRING=postgresql://user:password@host:port/database
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **TigerData Postgres** - Database for persistent storage
- **LangChain** - Framework for building AI agents
- **Anthropic Claude** - AI model for agent intelligence
- **OpenAI** - Alternative AI model support

### Frontend
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **TanStack Query** - Data fetching and state management
- **Recharts** - Charting library for visualizations
- **Lucide React** - Icon library

## API Endpoints

- `GET /` - Welcome message and API status
- `GET /health` - Health check endpoint

## Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Contributing

This is a hackathon project for the TigerData Agentic Postgres Challenge.

## License

MIT
