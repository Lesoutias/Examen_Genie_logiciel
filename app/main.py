from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import auth, users, vendeurs, taxes, paiements, signalements, stats

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Taxe App API",
    description="API for Market Tax Collection and Tracking System",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to the frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vendeurs.router)
app.include_router(taxes.router)
app.include_router(paiements.router)
app.include_router(signalements.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Taxe App API"}
