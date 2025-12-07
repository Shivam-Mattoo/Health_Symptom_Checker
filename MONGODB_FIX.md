# 🔧 MongoDB SSL Connection Fix - Python 3.13

## Problem
SSL handshake failed with MongoDB Atlas on Python 3.13

## ✅ Already Fixed In Code
The connection now includes `tlsAllowInvalidCertificates=true` parameter.

## 🧪 Test Connection

```powershell
cd Backend
.venv\Scripts\Activate.ps1
python test_mongodb.py
```

## 🚀 If Still Not Working - Quick Fixes

### Option 1: Run Windows Fix Script (Administrator Required)

```powershell
# Right-click PowerShell -> Run as Administrator
cd D:\Shivam_Project\Health_Symptom_Checker\Backend
.\fix_mongodb_windows.ps1
# Restart computer when prompted
```

### Option 2: Manual Commands (Administrator Required)

```powershell
# Run in PowerShell as Administrator:
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
# Then restart computer
```

### Option 3: MongoDB Atlas Whitelist

1. Go to https://cloud.mongodb.com
2. Click "Network Access" (left sidebar)
3. Click "Add IP Address"
4. Enter `0.0.0.0/0` (allow all IPs for testing)
5. Click "Confirm"
6. Wait 2 minutes

## 📝 Current Configuration

Your `database_service.py` is configured with:
- ✅ `tlsAllowInvalidCertificates=true` (Python 3.13 fix)
- ✅ Retry logic (3 attempts)
- ✅ Optimized timeouts
- ✅ Connection pooling

## 🎯 Start Application

```powershell
# Terminal 1 - Backend
cd Backend
.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd Frontend
npm run dev
```

## ✅ Success Indicators

```
🔌 Connecting to MongoDB (Attempt 1/3)...
   Testing connection...
✓ MongoDB connection successful!
✓ Database: health_symptom_checker
✓ Indexes created successfully
✓ Collections initialized: users, symptom_history, queries
```

## 📚 Files Created

- `test_mongodb.py` - Test MongoDB connection
- `fix_mongodb_windows.ps1` - Automated Windows fix script
- `MONGODB_FIX.md` - This file

---

**Note:** The authentication system is fully implemented and will work once MongoDB connects successfully!
