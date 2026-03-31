from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import secrets
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"

# Create the main app
app = FastAPI(title="Econnect VTC API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "client"  # client, driver, admin

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    role: str
    created_at: datetime

class DriverCreate(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str
    vehicle_model: str
    vehicle_plate: str

class DriverResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    phone: str
    role: str = "driver"
    vehicle_model: str
    vehicle_plate: str
    is_available: bool = True
    created_at: datetime

class BookingBase(BaseModel):
    pickup_address: str
    dropoff_address: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    pickup_date: str
    pickup_time: str
    transfer_type: str  # simple, retour, disposition
    notes: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    client_id: str
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    pickup_address: str
    dropoff_address: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    pickup_date: str
    pickup_time: str
    transfer_type: str
    notes: Optional[str] = None
    status: str  # pending, assigned, in_progress, completed, cancelled
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None

class AssignBooking(BaseModel):
    driver_id: str

class BookingStatusUpdate(BaseModel):
    status: str

class StatsResponse(BaseModel):
    total_bookings: int
    pending_bookings: int
    assigned_bookings: int
    completed_bookings: int
    total_clients: int
    total_drivers: int
    available_drivers: int

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Type de token invalide")
        user = await db.users.find_one({"id": payload["sub"]})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        user.pop("_id", None)
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def require_admin(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    return user

async def require_driver(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Accès chauffeur requis")
    return user

# ==================== EMAIL SERVICE ====================

async def send_notification_email(to_email: str, subject: str, html_content: str):
    """Send email notification via SendGrid"""
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    sender_email = os.environ.get('SENDER_EMAIL', 'noreply@econnect-vtc.com')
    
    if not sendgrid_key:
        logger.warning("SendGrid API key not configured, skipping email")
        return False
    
    try:
        message = Mail(
            from_email=sender_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

async def send_booking_notification_to_driver(driver: dict, booking: dict, client: dict):
    """Send notification to driver when a booking is assigned"""
    subject = f"🚗 Nouvelle course assignée - {booking['pickup_date']} à {booking['pickup_time']}"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #0A0A0A; color: #FAFAFA; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #141414; border-radius: 12px; padding: 30px; border: 1px solid #D4AF37;">
            <h1 style="color: #D4AF37; margin-bottom: 20px;">Nouvelle Course Assignée</h1>
            
            <h2 style="color: #FAFAFA;">Détails du client</h2>
            <p><strong>Nom:</strong> {client.get('name', 'N/A')}</p>
            <p><strong>Téléphone:</strong> {client.get('phone', 'N/A')}</p>
            <p><strong>Email:</strong> {client.get('email', 'N/A')}</p>
            
            <h2 style="color: #FAFAFA; margin-top: 20px;">Détails de la course</h2>
            <p><strong>📅 Date:</strong> {booking['pickup_date']}</p>
            <p><strong>⏰ Heure:</strong> {booking['pickup_time']}</p>
            <p><strong>📍 Départ:</strong> {booking['pickup_address']}</p>
            <p><strong>🏁 Arrivée:</strong> {booking['dropoff_address']}</p>
            <p><strong>Type:</strong> {booking['transfer_type']}</p>
            {f"<p><strong>Notes:</strong> {booking.get('notes', '')}</p>" if booking.get('notes') else ""}
            
            <div style="margin-top: 30px; padding: 20px; background: #D4AF37; border-radius: 8px; text-align: center;">
                <p style="color: #0A0A0A; font-weight: bold; margin: 0;">Connectez-vous à votre espace chauffeur pour confirmer</p>
            </div>
        </div>
    </body>
    </html>
    """
    await send_notification_email(driver['email'], subject, html_content)

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(user_data: UserCreate, response: Response):
    # Check if email exists
    existing = await db.users.find_one({"email": user_data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email.lower(),
        "name": user_data.name,
        "phone": user_data.phone,
        "password_hash": hash_password(user_data.password),
        "role": "client",  # Default role for registration
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user_doc)
    
    access_token = create_access_token(user_id, user_doc["email"], user_doc["role"])
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    
    return {
        "id": user_id,
        "email": user_doc["email"],
        "name": user_doc["name"],
        "phone": user_doc["phone"],
        "role": user_doc["role"]
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    user = await db.users.find_one({"email": credentials.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    access_token = create_access_token(user["id"], user["email"], user["role"])
    refresh_token = create_refresh_token(user["id"])
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "phone": user.get("phone"),
        "role": user["role"]
    }

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Déconnecté avec succès"}

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user

# ==================== CLIENT ROUTES ====================

@api_router.post("/bookings", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, request: Request):
    user = await get_current_user(request)
    
    booking_id = str(uuid.uuid4())
    booking_doc = {
        "id": booking_id,
        "client_id": user["id"],
        "client_name": user["name"],
        "client_email": user["email"],
        "client_phone": user.get("phone"),
        "pickup_address": booking.pickup_address,
        "dropoff_address": booking.dropoff_address,
        "pickup_lat": booking.pickup_lat,
        "pickup_lng": booking.pickup_lng,
        "dropoff_lat": booking.dropoff_lat,
        "dropoff_lng": booking.dropoff_lng,
        "pickup_date": booking.pickup_date,
        "pickup_time": booking.pickup_time,
        "transfer_type": booking.transfer_type,
        "notes": booking.notes,
        "status": "pending",
        "driver_id": None,
        "driver_name": None,
        "created_at": datetime.now(timezone.utc),
        "assigned_at": None
    }
    
    await db.bookings.insert_one(booking_doc)
    booking_doc.pop("_id", None)
    return BookingResponse(**booking_doc)

@api_router.get("/bookings/my", response_model=List[BookingResponse])
async def get_my_bookings(request: Request):
    user = await get_current_user(request)
    bookings = await db.bookings.find({"client_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [BookingResponse(**b) for b in bookings]

# ==================== DRIVER ROUTES ====================

@api_router.get("/driver/bookings", response_model=List[BookingResponse])
async def get_driver_bookings(request: Request):
    user = await require_driver(request)
    bookings = await db.bookings.find({"driver_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [BookingResponse(**b) for b in bookings]

@api_router.put("/driver/bookings/{booking_id}/status")
async def update_booking_status_driver(booking_id: str, status_update: BookingStatusUpdate, request: Request):
    user = await require_driver(request)
    
    booking = await db.bookings.find_one({"id": booking_id, "driver_id": user["id"]})
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    valid_statuses = ["in_progress", "completed"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Valeurs acceptées: {valid_statuses}")
    
    await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {"status": status_update.status}}
    )
    
    return {"message": "Statut mis à jour", "status": status_update.status}

@api_router.put("/driver/availability")
async def update_driver_availability(request: Request, is_available: bool = True):
    user = await require_driver(request)
    await db.users.update_one({"id": user["id"]}, {"$set": {"is_available": is_available}})
    return {"message": "Disponibilité mise à jour", "is_available": is_available}

# ==================== ADMIN ROUTES ====================

@api_router.get("/admin/stats", response_model=StatsResponse)
async def get_admin_stats(request: Request):
    await require_admin(request)
    
    total_bookings = await db.bookings.count_documents({})
    pending_bookings = await db.bookings.count_documents({"status": "pending"})
    assigned_bookings = await db.bookings.count_documents({"status": "assigned"})
    completed_bookings = await db.bookings.count_documents({"status": "completed"})
    total_clients = await db.users.count_documents({"role": "client"})
    total_drivers = await db.users.count_documents({"role": "driver"})
    available_drivers = await db.users.count_documents({"role": "driver", "is_available": True})
    
    return StatsResponse(
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        assigned_bookings=assigned_bookings,
        completed_bookings=completed_bookings,
        total_clients=total_clients,
        total_drivers=total_drivers,
        available_drivers=available_drivers
    )

@api_router.get("/admin/bookings", response_model=List[BookingResponse])
async def get_all_bookings(request: Request, status: Optional[str] = None):
    await require_admin(request)
    
    query = {}
    if status:
        query["status"] = status
    
    bookings = await db.bookings.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    return [BookingResponse(**b) for b in bookings]

@api_router.put("/admin/bookings/{booking_id}/assign")
async def assign_booking_to_driver(booking_id: str, assign_data: AssignBooking, request: Request):
    await require_admin(request)
    
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    driver = await db.users.find_one({"id": assign_data.driver_id, "role": "driver"})
    if not driver:
        raise HTTPException(status_code=404, detail="Chauffeur non trouvé")
    
    await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {
            "driver_id": driver["id"],
            "driver_name": driver["name"],
            "status": "assigned",
            "assigned_at": datetime.now(timezone.utc)
        }}
    )
    
    # Get client info
    client = await db.users.find_one({"id": booking["client_id"]})
    
    # Send email notification to driver
    await send_booking_notification_to_driver(driver, booking, client or {})
    
    return {"message": "Course assignée avec succès", "driver_name": driver["name"]}

@api_router.put("/admin/bookings/{booking_id}/status")
async def update_booking_status_admin(booking_id: str, status_update: BookingStatusUpdate, request: Request):
    await require_admin(request)
    
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    valid_statuses = ["pending", "assigned", "in_progress", "completed", "cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Valeurs acceptées: {valid_statuses}")
    
    await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {"status": status_update.status}}
    )
    
    return {"message": "Statut mis à jour", "status": status_update.status}

@api_router.get("/admin/drivers", response_model=List[DriverResponse])
async def get_all_drivers(request: Request):
    await require_admin(request)
    
    drivers = await db.users.find({"role": "driver"}, {"_id": 0, "password_hash": 0}).to_list(100)
    return [DriverResponse(**d) for d in drivers]

@api_router.post("/admin/drivers", response_model=DriverResponse)
async def create_driver(driver_data: DriverCreate, request: Request):
    await require_admin(request)
    
    # Check if email exists
    existing = await db.users.find_one({"email": driver_data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    driver_id = str(uuid.uuid4())
    driver_doc = {
        "id": driver_id,
        "email": driver_data.email.lower(),
        "name": driver_data.name,
        "phone": driver_data.phone,
        "password_hash": hash_password(driver_data.password),
        "role": "driver",
        "vehicle_model": driver_data.vehicle_model,
        "vehicle_plate": driver_data.vehicle_plate,
        "is_available": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(driver_doc)
    driver_doc.pop("_id", None)
    driver_doc.pop("password_hash", None)
    
    return DriverResponse(**driver_doc)

@api_router.delete("/admin/drivers/{driver_id}")
async def delete_driver(driver_id: str, request: Request):
    await require_admin(request)
    
    result = await db.users.delete_one({"id": driver_id, "role": "driver"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chauffeur non trouvé")
    
    return {"message": "Chauffeur supprimé"}

@api_router.get("/admin/clients", response_model=List[UserResponse])
async def get_all_clients(request: Request):
    await require_admin(request)
    
    clients = await db.users.find({"role": "client"}, {"_id": 0, "password_hash": 0}).to_list(100)
    return [UserResponse(**c) for c in clients]

# ==================== ROOT ROUTE ====================

@api_router.get("/")
async def root():
    return {"message": "Econnect VTC API", "version": "1.0.0"}

# Include router and setup
app.include_router(api_router)

# CORS Configuration
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[frontend_url, "http://localhost:3000", "https://driver-platform-28.preview.emergentagent.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STARTUP EVENTS ====================

@app.on_event("startup")
async def startup_event():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.bookings.create_index("id", unique=True)
    await db.bookings.create_index("client_id")
    await db.bookings.create_index("driver_id")
    await db.bookings.create_index("status")
    
    # Seed admin user
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@econnect-vtc.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    existing_admin = await db.users.find_one({"email": admin_email})
    if not existing_admin:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "name": "Administrateur",
            "phone": None,
            "password_hash": hash_password(admin_password),
            "role": "admin",
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(admin_doc)
        logger.info(f"Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing_admin["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}}
        )
        logger.info("Admin password updated")
    
    # Write test credentials
    credentials_path = Path("/app/memory/test_credentials.md")
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    credentials_path.write_text(f"""# Test Credentials

## Admin Account
- **Email**: {admin_email}
- **Password**: {admin_password}
- **Role**: admin

## Auth Endpoints
- POST /api/auth/register - Register new client
- POST /api/auth/login - Login
- POST /api/auth/logout - Logout
- GET /api/auth/me - Get current user

## Admin Endpoints
- GET /api/admin/stats - Dashboard stats
- GET /api/admin/bookings - All bookings
- PUT /api/admin/bookings/{{id}}/assign - Assign to driver
- GET /api/admin/drivers - All drivers
- POST /api/admin/drivers - Create driver
- DELETE /api/admin/drivers/{{id}} - Delete driver
- GET /api/admin/clients - All clients

## Driver Endpoints
- GET /api/driver/bookings - Driver's bookings
- PUT /api/driver/bookings/{{id}}/status - Update status
- PUT /api/driver/availability - Set availability

## Client Endpoints
- POST /api/bookings - Create booking
- GET /api/bookings/my - My bookings
""")
    logger.info("Test credentials written to /app/memory/test_credentials.md")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
