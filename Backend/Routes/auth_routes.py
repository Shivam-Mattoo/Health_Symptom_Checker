from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import timedelta

from models.user import UserCreate, UserLogin, User, Token, SymptomHistory
from services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from services.database_service import DatabaseService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    payload = auth_service.decode_token(token)
    email: str = payload.get("sub")
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = db_service.get_user_by_email(email)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(
        id=str(user_data["_id"]),
        email=user_data["email"],
        full_name=user_data["full_name"],
        created_at=user_data["created_at"],
        is_active=user_data.get("is_active", True)
    )

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    print(f"\n📝 Registration attempt for: {user_data.email}")
    
    # Check if user already exists
    existing_user = db_service.get_user_by_email(user_data.email)
    print(f"   Existing user check: {existing_user is not None}")
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    print(f"   Hashing password...")
    hashed_password = auth_service.get_password_hash(user_data.password)
    print(f"   Password hashed successfully")
    
    # Create user in database
    print(f"   Creating user in database...")
    user_id = db_service.create_user(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    print(f"   User created with ID: {user_id}")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Get created user
    user_doc = db_service.get_user_by_id(user_id)
    user = User(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=user_doc["created_at"],
        is_active=user_doc.get("is_active", True)
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password
    """
    print(f"\n🔐 Login attempt for: {form_data.username}")
    
    # Get user from database
    user_data = db_service.get_user_by_email(form_data.username)
    print(f"   User found: {user_data is not None}")
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    print(f"   Verifying password...")
    if not auth_service.verify_password(form_data.password, user_data["hashed_password"]):
        print(f"✗ Login failed: Invalid password\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(f"   Password verified")
    
    # Check if user is active
    if not user_data.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    user = User(
        id=str(user_data["_id"]),
        email=user_data["email"],
        full_name=user_data["full_name"],
        created_at=user_data["created_at"],
        is_active=user_data.get("is_active", True)
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@router.get("/history", response_model=list[SymptomHistory])
async def get_user_symptom_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get symptom analysis history for current user
    """
    history = db_service.get_user_history(current_user.id, limit=limit)
    
    return [
        SymptomHistory(
            id=str(h["_id"]),
            user_id=h["user_id"],
            symptoms=h["symptoms"],
            severity=h["severity"],
            conditions=h["conditions"],
            recommendations=h["recommendations"],
            created_at=h["created_at"],
            image_analysis=h.get("image_analysis")
        )
        for h in history
    ]
