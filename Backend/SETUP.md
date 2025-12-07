# Backend Setup Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file** in the Backend directory with your credentials:
   ```env
   MONGO_URI=mongodb+srv://mattooshivam_db_user:ITnRrhYYWhLHn2Hs@healthsymptomchecker.d5oeexp.mongodb.net/
   GEMINI_KEY=AIzaSyDGQ-cLrZTTAXhJOFAyb0d6GplS3Aiuajg
   PINECONE_API=pcsk_nzkJF_SkFLu3fgv9EJAWZyXb2YPwHRFKvP69srPpck1XxgQHrUPqsQeJ3vSm6U5Xodckq
   PINECONE_INDEX=healthchecker
   ```

3. **Run the server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## Important Notes

### Embedding Model
The current implementation uses a simple hash-based embedding for Pinecone. For production use, you should integrate a proper embedding model such as:
- OpenAI's `text-embedding-ada-002`
- Sentence Transformers (e.g., `sentence-transformers/all-MiniLM-L6-v2`)
- Cohere embeddings
- Google's Universal Sentence Encoder

To use a proper embedding model, update the `generate_embedding` method in `services/pinecone_service.py`.

### Database
The application uses MongoDB Atlas. Make sure your connection string is correct and the database is accessible.

### Pinecone Index
The Pinecone index will be created automatically if it doesn't exist. The default dimension is 1536. If you use a different embedding model, update the dimension accordingly.


