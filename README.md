# Health Symptom Checker

A healthcare symptom analysis application that uses AI to provide educational information about possible conditions based on user symptoms. **This is for educational purposes only and is not a substitute for professional medical advice.**

## 📌 Problem Statement
The objective of this project is to build an AI-powered healthcare tool that accepts user symptoms and returns **possible medical conditions**, **severity analysis**, and **recommended next steps**.  
This project is designed to help users better understand their symptoms using LLMs, RAG, and analytics.  

## 🎥 Demo Video

Click below to watch the full project demo:

👉 **Demo Video:** https://drive.google.com/file/d/1oYxMgrRsP5VKv8cJ6z1gr2wxuGiwGVNd/view?usp=drive_link

This video covers:
- Full frontend walkthrough  
- Backend FastAPI processing  
- RAG + Pinecone + Gemini pipeline  
- Severity & condition analysis  
- Recommended action steps  
- Visual charts and analytics  


## Features

- **Symptom Analysis**: Input symptoms and receive AI-powered analysis of possible conditions
- **RAG (Retrieval Augmented Generation)**: Uses Pinecone vector database for context-aware responses
- **Query History**: Stores and retrieves previous symptom queries
- **Modern UI**: Clean, responsive React frontend with Tailwind CSS
- **RESTful API**: Well-structured FastAPI backend with OOP principles

## UI Implementation and Results

Below are screenshots of the Health Symptom Checker in action: input UI, progress state, result cards, severity/likelihood charts, and recommended actions.

### Fig 1 — User Information (Logged-in User)
<p align="center">
  <img src="https://github.com/user-attachments/assets/bc3a8051-64e0-4c4e-8a88-895e9ec12ea1" width="100%">
</p>

*Shows the authenticated user details at the top of the application.*


### Fig 2 — Main User Interface (Symptom Input Options)

<p align="center">
 <img width="1782" height="917" alt="Screenshot 2025-12-07 172049" src="https://github.com/user-attachments/assets/6f659c5f-19be-40a8-91a7-fd0bff48a230" />
</p>

*This screen allows the user to begin the health analysis by choosing one of three input methods — **Text Input**, **Image Upload**, or **PDF Document**. It serves as the primary entry point for providing symptoms that the system will analyze.*


### Fig 3 — Symptom Input and Real-Time Analysis Progress

<p align="center">
  <img width="1465" height="826" alt="Screenshot 2025-12-07 172232" src="https://github.com/user-attachments/assets/08962ee8-5568-4c87-b1f3-5e151e889fbe" />

</p>

*This screen shows the user entering symptoms in text format. After clicking **Analyze Symptoms**, the system begins processing the input using AI and displays a real-time progress indicator, informing the user that symptom analysis is underway.*

### Fig 4 — Severity Assessment and Symptom Summary

<p align="center">
  <img width="1919" height="753" alt="Screenshot 2025-12-07 172305" src="https://github.com/user-attachments/assets/2dc60163-203b-4dcf-9c6c-9f37993d7319" />
</p>

*This screen displays the symptoms reported by the user followed by an AI-generated **severity assessment**. The system categorizes the condition as Mild, Moderate, or Severe and provides an alert level percentage along with a brief explanation of what the severity rating means.*


### Fig 5 — Generated Possible Medical Conditions (Ranked by Likelihood )

<p align="center">
<img width="1910" height="922" alt="Screenshot 2025-12-07 172316" src="https://github.com/user-attachments/assets/bde16583-a107-4e1e-9ed1-bacdbd9ff43c" />
<img width="1916" height="571" alt="Screenshot 2025-12-07 172327" src="https://github.com/user-attachments/assets/7604e716-0a6e-43de-93df-6441b4feaf9c" />

</p>

*This section displays the top potential medical conditions identified by the AI based on the user’s symptoms. Each condition is ranked and includes a likelihood percentage along with a short explanation. These results are educational suggestions only and not a medical diagnosis.*

### Fig 6 — Recommended Action Steps Based on Symptom Analysis

<p align="center">
  <img width="1919" height="1023" alt="Screenshot 2025-12-07 172335" src="https://github.com/user-attachments/assets/39d3cc67-9807-489b-a33d-43e92d3c41ec" />
  <img width="1919" height="609" alt="Screenshot 2025-12-07 172345" src="https://github.com/user-attachments/assets/ef55ca03-607b-446b-a7d8-eebcc0ac7356" />
</p>

*This section shows the AI-generated recommended action steps to help the user manage their symptoms. Each action is assigned a priority level, indicating its urgency and importance. The steps include explanations under “Why this matters” to help users understand the reasoning behind each recommendation.*

### Fig 7 — Visual Analytics & Charts for Condition Likelihood

<p align="center">
  <img width="1919" height="1022" alt="Screenshot 2025-12-07 172357" src="https://github.com/user-attachments/assets/97f51b52-8cca-4b6e-a1ce-4996a26f6c44" />
</p>

*This section provides visual insights through analytics charts. The **Likelihood Bar Chart** displays how strongly the user’s symptoms match each potential condition, while the **Pie Chart** shows the proportional distribution of these likelihoods. These visualizations help users quickly understand the analysis results at a glance.*






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
  

## 🎯 Why These Technologies?

### 🟩 FastAPI (Backend)
Fast, modern Python framework with:
- Async performance  
- Auto-generated `/docs`  
- Cleaner structure than Flask  
- Ideal for AI applications  

---

### 🟦 MongoDB (Database)
Used because:
- Flexible NoSQL JSON-like structure  
- Perfect for AI outputs (dynamic fields)  
- Scales easily  
- Stores user history & previous results  

---

### 🟪 Pinecone (Vector Database)
Needed for RAG because:
- Stores embeddings  
- Retrieves medically relevant context  
- Works perfectly with Gemini embeddings  
- Solves token-limit issues for large text/PDF input  

---

### 🧠 Retrieval Augmented Generation (RAG)
We used RAG because:
- Gemini alone cannot handle very long input  
- RAG breaks text into chunks → embeds → retrieves  
- Improves accuracy dramatically  
- Prevents token overflow  
- Critical for image & PDF uploads  

---

### 🟧 Google Gemini (LLM)
Used because:
- Understands symptoms accurately  
- Generates severity, conditions, actions  
- Supports embeddings  
- Supports images and PDFs  

---

### ✔ Combined Power: MongoDB + Pinecone
- MongoDB → stores **user data & history**  
- Pinecone → stores **vector embeddings**  
Both form a complete medical RAG pipeline.

---


## 🔄 System Workflow

1. User enters symptoms (Text / Image / PDF)  
2. Backend extracts text  
3. RAG pipeline retrieves relevant medical information  
4. Gemini generates severity, conditions, recommendations  
5. Charts and results rendered on frontend  
6. History saved to MongoDB  

---

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
## 🔑 Where to Get API Keys

| Service | How to Get Key |
|---------|----------------|
| **MongoDB URI** | Go to https://cloud.mongodb.com → Create free cluster → Database → Connect → Choose “Connect your application” → Copy connection string |
| **Gemini API Key** | Visit https://aistudio.google.com/ → Go to “Get API Key” → Generate new API key |
| **Pinecone API Key** | Visit https://app.pinecone.io/ → API Keys → Create API Key |
| **Pinecone Index Name** | Go to Pinecone Dashboard → Indexes → Create Index → Use that index name |


Create your `.env` file inside `/Backend`:

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
   MONGO_URI=your_mongo_uri_here
   GEMINI_KEY=your_gemini_key_here
   PINECONE_API=your_pinecone_api_key_here
   PINECONE_INDEX=your_index_name

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


