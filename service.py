import motor.motor_asyncio
from passlib.context import CryptContext
from fastapi import HTTPException, status
from models import MONGO_URI, DB_NAME, OrgCreate, OrgUpdate

# Setup DB and Hashing
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class OrganizationService:
    """
    Handles business logic for Organization Management.
    """
    
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    async def create_organization(self, data: OrgCreate):
        # 1. Validate organization name does not exist [cite: 13]
        existing_org = await db.organizations.find_one({"organization_name": data.organization_name})
        if existing_org:
            raise HTTPException(status_code=400, detail="Organization name already exists")

        # 2. Dynamic Collection Name [cite: 15]
        collection_name = f"org_{data.organization_name}"
        
        # 3. Create Admin User & Store Metadata in Master DB [cite: 17, 61]
        org_doc = {
            "organization_name": data.organization_name,
            "collection_name": collection_name,
            "admin_email": data.email,
            "admin_password": self.get_password_hash(data.password) # Hashed [cite: 68]
        }
        await db.organizations.insert_one(org_doc)

        # 4. Programmatically create the dynamic collection [cite: 64]
        # In Mongo, explicitly creating it is optional as it creates on first insert, 
        # but we can initialize it explicitly as requested.
        await db.create_collection(collection_name)
        
        return {"message": "Organization created successfully", "collection": collection_name}

    async def get_organization(self, name: str):
        # Fetch from Master DB [cite: 28]
        org = await db.organizations.find_one({"organization_name": name}, {"_id": 0, "admin_password": 0})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org

    async def update_organization(self, old_name: str, data: OrgUpdate):
        # Validate existence
        current_org = await db.organizations.find_one({"organization_name": old_name})
        if not current_org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # 1. Validate new name uniqueness if changed [cite: 37]
        if data.organization_name != old_name:
            conflict = await db.organizations.find_one({"organization_name": data.organization_name})
            if conflict:
                raise HTTPException(status_code=400, detail="New organization name already taken")
            
            # 2. Sync existing data to new Collection (Rename) [cite: 38]
            old_coll = current_org['collection_name']
            new_coll = f"org_{data.organization_name}"
            
            # MongoDB rename handles the "sync" efficiently
            try:
                await db[old_coll].rename(new_coll)
            except Exception as e:
                # Handle case where collection might not exist yet
                pass 

            # Update Metadata
            await db.organizations.update_one(
                {"organization_name": old_name},
                {"$set": {
                    "organization_name": data.organization_name,
                    "collection_name": new_coll,
                    "admin_email": data.email,
                    "admin_password": self.get_password_hash(data.password)
                }}
            )
            return {"message": "Organization updated and data synced to new collection"}
        
        # If name didn't change, just update details
        await db.organizations.update_one(
            {"organization_name": old_name},
            {"$set": {
                "admin_email": data.email,
                "admin_password": self.get_password_hash(data.password)
            }}
        )
        return {"message": "Organization details updated"}

    async def delete_organization(self, name: str):
        # Fetch metadata to find the collection
        org = await db.organizations.find_one({"organization_name": name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # 1. Handle deletion of relevant collections [cite: 45]
        try:
            await db.drop_collection(org['collection_name'])
        except:
            pass

        # 2. Delete metadata from Master DB
        await db.organizations.delete_one({"organization_name": name})
        return {"message": "Organization and associated data deleted"}

    async def authenticate_admin(self, email, password):
        # Validate credentials [cite: 51]
        user = await db.organizations.find_one({"admin_email": email})
        if not user or not self.verify_password(password, user['admin_password']):
            return False
        return user