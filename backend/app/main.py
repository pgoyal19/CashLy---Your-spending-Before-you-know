from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models.database import User, Expense, Budget, Goal  # Import models to register them
from app.routes.auth import router as auth_router
from app.routes.finance import router as finance_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CashLy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(finance_router)


@app.get("/")
def root():
    return {"app": "CashLy", "status": "running"}

