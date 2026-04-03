from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, users, records, dashboard

# create all tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Backend API",
    description="A backend system for managing financial records with role based access control",
    version="1.0.0"
)

# register all routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(records.router, prefix="/records", tags=["Records"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])


@app.get("/")
def home():
    return {"message": "Finance Backend API is running"}