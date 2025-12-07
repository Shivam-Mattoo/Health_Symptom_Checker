# Authentication System - Setup Guide

## Overview
This application now includes a complete JWT-based authentication system with session management and user history tracking.

## Features Implemented

### Backend
✅ **JWT Authentication**
- Token-based authentication with 7-day expiration
- Password hashing using bcrypt
- Secure token validation middleware

✅ **Database Collections**
- `users` - User accounts with email, password, and profile info
- `symptom_history` - User-specific symptom analysis history
- Indexed for performance

✅ **API Endpoints**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info
- `GET /auth/history` - Get user's symptom history
- `POST /api/symptoms/analyze` - Analyze symptoms (requires auth)

### Frontend
✅ **Authentication UI**
- Beautiful login/register form with animations
- User profile display with logout
- Session persistence using localStorage
- Automatic token validation on app load

✅ **History Management**
- View past symptom analyses
- Filtered by authenticated user
- Beautiful modal with severity badges
- Date formatting and condition grouping

## Environment Variables

Add to your `.env` file in the Backend directory:

```env
# Existing variables
MONGO_URI=your_mongodb_connection_string
GEMINI_KEY=your_gemini_api_key
PINECONE_API=your_pinecone_api_key
PINECONE_INDEX=healthchecker

# New Authentication Variable
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

**Important:** Generate a secure JWT secret key:
```bash
# On Windows PowerShell:
-join ((65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Or use any random 32+ character string
```

## Installation

### Backend Dependencies
```bash
cd Backend
pip install python-jose[cryptography] passlib[bcrypt] python-dateutil
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Frontend (No new dependencies needed)
All authentication components use existing React and Tailwind setup.

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: string (unique, indexed),
  hashed_password: string,
  full_name: string,
  created_at: datetime,
  is_active: boolean
}
```

### Symptom History Collection
```javascript
{
  _id: ObjectId,
  user_id: string (indexed),
  symptoms: string,
  severity: string,
  conditions: [string],
  recommendations: [string],
  image_analysis: string (optional),
  created_at: datetime (indexed)
}
```

## API Usage Examples

### Register New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### Analyze Symptoms (Authenticated)
```bash
curl -X POST http://localhost:8000/api/symptoms/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "symptoms": "I have a headache and fever"
  }'
```

### Get History
```bash
curl -X GET http://localhost:8000/auth/history?limit=20 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt with salt
2. **JWT Tokens**: Signed tokens with expiration (7 days)
3. **Token Validation**: All protected routes verify JWT signature
4. **HTTPS Ready**: Use environment variables for production secrets
5. **CORS Protection**: Configured for specific origins

## Frontend Components

### AuthForm.jsx
- Toggle between login/register
- Form validation
- Error handling
- Stores token in localStorage

### UserProfile.jsx
- Displays logged-in user info
- Logout button
- Access to history modal

### HistoryModal.jsx
- Fetches user's symptom history
- Beautiful card layout
- Severity color coding
- Date formatting

## Running the Application

1. **Start Backend:**
```bash
cd Backend
.venv\Scripts\Activate.ps1  # Activate virtual environment
uvicorn main:app --reload --port 8000
```

2. **Start Frontend:**
```bash
cd Frontend
npm run dev
```

3. **Access Application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## User Flow

1. User visits app → Sees login/register form
2. Register/Login → Receives JWT token
3. Token stored in localStorage
4. User profile appears at top
5. Analyze symptoms → Saved to user's history
6. View history → See all past analyses
7. Logout → Clears token and session

## Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Token persists on page refresh
- [ ] Analyze symptoms while authenticated
- [ ] View symptom history
- [ ] Logout clears session
- [ ] Protected routes require authentication
- [ ] Invalid tokens are rejected

## Troubleshooting

**Issue: "Could not validate credentials"**
- Token expired (7 days)
- Token invalid or tampered
- Solution: Logout and login again

**Issue: "Email already registered"**
- User with that email exists
- Solution: Use different email or login

**Issue: MongoDB connection failed**
- Check MONGO_URI in .env
- Ensure MongoDB cluster is accessible
- Check IP whitelist in MongoDB Atlas

**Issue: JWT_SECRET_KEY missing**
- Add JWT_SECRET_KEY to .env file
- Restart backend server

## Production Deployment

1. Generate strong JWT secret (32+ characters)
2. Use HTTPS for all connections
3. Set secure CORS origins
4. Enable rate limiting
5. Add refresh token mechanism (optional)
6. Monitor failed login attempts
7. Implement password reset flow (future)

## Future Enhancements

- [ ] Password reset via email
- [ ] Email verification
- [ ] Refresh token mechanism
- [ ] OAuth2 social login (Google, Facebook)
- [ ] Two-factor authentication (2FA)
- [ ] Password strength meter
- [ ] Account settings page
- [ ] Export history to PDF
- [ ] Share analysis with doctors

---

**Created:** December 2025  
**Backend:** FastAPI + JWT + MongoDB  
**Frontend:** React + Tailwind CSS
