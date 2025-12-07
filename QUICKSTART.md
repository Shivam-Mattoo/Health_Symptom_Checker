# 🚀 Quick Start Guide - Authentication System

## Start the Application

### Terminal 1 - Backend
```powershell
cd Backend
.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

### Terminal 2 - Frontend
```powershell
cd Frontend
npm run dev
```

### Access
- 🌐 App: http://localhost:5173
- 📚 API Docs: http://localhost:8000/docs

---

## First Time Use

1. Visit http://localhost:5173
2. Click "Don't have an account? Sign up"
3. Enter your details:
   - Full Name
   - Email
   - Password (min 6 characters)
4. Click "Create Account"
5. You're automatically logged in! ✅

---

## Using the App

### Analyze Symptoms
1. Type your symptoms in the text box
2. Click "Analyze Symptoms"
3. Wait for AI analysis (includes LLM reasoning)
4. Results saved to your history automatically

### View History
1. Click "History" button in user profile (top of page)
2. See all your past analyses
3. Sorted by newest first
4. Color-coded severity badges

### Logout
1. Click "Logout" button in user profile
2. Redirects to login screen
3. Token cleared from browser

---

## API Examples (Testing)

### Register (Postman/curl)
```bash
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User"
}
```

### Login
```bash
POST http://localhost:8000/auth/login
Content-Type: application/x-www-form-urlencoded

username=test@example.com&password=password123
```

Response includes `access_token` - copy this for authenticated requests.

### Analyze (Protected)
```bash
POST http://localhost:8000/api/symptoms/analyze
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "symptoms": "I have a headache and fever"
}
```

---

## Troubleshooting

### "Could not validate credentials"
- **Cause:** Token expired or invalid
- **Fix:** Logout and login again

### Backend won't start
- **Check:** .env file has all required keys
- **Fix:** Ensure JWT_SECRET_KEY is set

### Frontend can't connect
- **Check:** Backend is running on port 8000
- **Fix:** Start backend first

### "Email already registered"
- **Cause:** Account exists
- **Fix:** Use different email or login

---

## Key Files

| File | Purpose |
|------|---------|
| `Backend/.env` | Configuration (includes JWT_SECRET_KEY) |
| `Backend/Routes/auth_routes.py` | Auth endpoints |
| `Backend/services/auth_service.py` | JWT logic |
| `Frontend/src/components/AuthForm.jsx` | Login/Register UI |
| `Frontend/src/services/api.js` | API calls |

---

## Database Collections

### `users`
Stores user accounts (email, hashed password, name)

### `symptom_history`
Stores symptom analyses per user with timestamps

---

## Security Notes

✅ **Passwords hashed** with bcrypt  
✅ **JWT tokens** expire in 7 days  
✅ **HTTPS ready** for production  
✅ **CORS configured** for local dev  

⚠️ **Never share your JWT_SECRET_KEY**  
⚠️ **Use HTTPS in production**

---

## Need More Help?

- 📖 Read `AUTHENTICATION.md` for detailed guide
- 📊 Read `IMPLEMENTATION_SUMMARY.md` for complete overview
- 🔍 Check FastAPI docs: http://localhost:8000/docs
- 🐛 Check terminal for error messages

---

**Happy Coding! 🎉**
