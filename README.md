# Health Symptom Checker

A healthcare symptom analysis application that uses AI to provide educational information about possible conditions based on user symptoms. **This is for educational purposes only and is not a substitute for professional medical advice.**

## Features

- **Symptom Analysis**: Input symptoms and receive AI-powered analysis of possible conditions
- **RAG (Retrieval Augmented Generation)**: Uses Pinecone vector database for context-aware responses
- **Query History**: Stores and retrieves previous symptom queries
- **Modern UI**: Clean, responsive React frontend with Tailwind CSS
- **RESTful API**: Well-structured FastAPI backend with OOP principles

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for storing queries
- **Pinecone**: Vector database for RAG functionality
- **Google Gemini**: LLM for symptom analysis
- **Python 3.8+**

### Frontend
- **React 19**: UI library
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework

## Project Structure

```
Health_Symptom_Checker/
├── Backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── Routes/
│   │   └── symptom_routes.py   # Symptom analysis API routes
│   └── services/
│       ├── database_service.py # MongoDB service (OOP)
│       ├── llm_service.py      # Gemini LLM service (OOP)
│       └── pinecone_service.py # Pinecone RAG service (OOP)
├── Frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── components/
│   │   │   ├── SymptomForm.jsx    # Symptom input form
│   │   │   └── AnalysisResults.jsx # Results display
│   │   └── services/
│   │       └── api.js          # API service class
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- MongoDB Atlas account (or local MongoDB)
- Pinecone account
- Google Gemini API key

### Backend Setup

1. **Navigate to Backend directory**:
   ```bash
   cd Backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** in the Backend directory:
   ```env
   MONGO_URI=mongodb+srv://mattooshivam_db_user:ITnRrhYYWhLHn2Hs@healthsymptomchecker.d5oeexp.mongodb.net/
   GEMINI_KEY=AIzaSyDGQ-cLrZTTAXhJOFAyb0d6GplS3Aiuajg
   PINECONE_API=pcsk_nzkJF_SkFLu3fgv9EJAWZyXb2YPwHRFKvP69srPpck1XxgQHrUPqsQeJ3vSm6U5Xodckq
   PINECONE_INDEX=healthchecker
   ```

5. **Run the backend server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to Frontend directory**:
   ```bash
   cd Frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create `.env` file** in the Frontend directory (optional):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## API Endpoints

### POST `/api/symptoms/analyze`
Analyze symptoms and get probable conditions.

**Request Body**:
```json
{
  "symptoms": "I have been experiencing headaches, fever, and fatigue",
  "user_id": "optional_user_id"
}
```

**Response**:
```json
{
  "query_id": "507f1f77bcf86cd799439011",
  "symptoms": "I have been experiencing headaches, fever, and fatigue",
  "conditions": [
    "Common cold",
    "Influenza",
    "Viral infection"
  ],
  "recommendations": [
    "Rest and stay hydrated",
    "Monitor symptoms",
    "Consult a healthcare provider if symptoms worsen"
  ],
  "disclaimer": "This information is for educational purposes only..."
}
```

### GET `/api/symptoms/history`
Get query history.

**Query Parameters**:
- `user_id` (optional): Filter by user ID
- `limit` (optional, default: 10): Maximum number of queries

### GET `/api/symptoms/query/{query_id}`
Get a specific query by ID.

## Code Architecture

### Object-Oriented Design

The backend follows OOP principles with separate service classes:

- **DatabaseService**: Handles all MongoDB operations
- **LLMService**: Manages Gemini LLM interactions and response parsing
- **PineconeService**: Handles vector database operations for RAG

### Route Organization

Routes are organized in separate files within the `Routes/` folder:
- `symptom_routes.py`: All symptom-related endpoints

This keeps the codebase clean and maintainable.

## Important Disclaimers

⚠️ **This application is for EDUCATIONAL PURPOSES ONLY**

- This tool is NOT a substitute for professional medical advice, diagnosis, or treatment
- Always consult with a qualified healthcare provider for medical concerns
- Do not ignore professional medical advice or delay seeking it
- The information provided should not be used for diagnosing or treating health problems

## Development

### Running Tests

```bash
# Backend tests (if implemented)
cd Backend
pytest

# Frontend tests (if implemented)
cd Frontend
npm test
```

### Building for Production

```bash
# Frontend
cd Frontend
npm run build

# Backend
# Use a production ASGI server like Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License

This project is for educational purposes only.

## Contributing

This is an educational project. Contributions and improvements are welcome!

## Support

For issues or questions, please open an issue in the repository.


