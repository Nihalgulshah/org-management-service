from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import SECRET_KEY, ALGORITHM, OrgCreate, OrgUpdate, LoginRequest, Token
from service import OrganizationService

app = FastAPI(title="Org Management Service")
service = OrganizationService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

# --- Auth Utilities ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        org_name: str = payload.get("sub")
        if org_name is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return org_name
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- Endpoints ---

@app.post("/org/create")
async def create_org(org: OrgCreate):
    # [cite: 7, 8]
    return await service.create_organization(org)

@app.get("/org/get")
async def get_org(organization_name: str):
    # [cite: 23, 24]
    return await service.get_organization(organization_name)

@app.post("/admin/login", response_model=Token)
async def login(creds: LoginRequest):
    # [cite: 46, 47]
    user = await service.authenticate_admin(creds.email, creds.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Return JWT with Org ID/Name [cite: 52, 54]
    access_token = create_access_token(data={"sub": user['organization_name']})
    return {"access_token": access_token, "token_type": "bearer", "org_name": user['organization_name']}

@app.put("/org/update")
async def update_org(data: OrgUpdate, current_org: str = Depends(get_current_admin)):
    # [cite: 30] Logic handles dynamic syncing of data
    # Note: We use the authenticated user's org to ensure they only update their own
    return await service.update_organization(current_org, data)

@app.delete("/org/delete")
async def delete_org(organization_name: str, current_org: str = Depends(get_current_admin)):
    # [cite: 40] Allow deletion for respective authenticated user only [cite: 44]
    if organization_name != current_org:
        raise HTTPException(status_code=403, detail="Not authorized to delete this organization")
    
    return await service.delete_organization(organization_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)