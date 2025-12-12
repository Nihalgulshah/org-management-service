from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "master_db"
SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"

# --- Pydantic Models ---

class OrgCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    org_name: str