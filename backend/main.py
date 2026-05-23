from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.trip import router as trip_router
from app.api.trip_debug import router as trip_debug_router

load_dotenv()

app = FastAPI(title="AI Travel Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):517\d",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip_router)
app.include_router(trip_debug_router)


@app.get("/")
def read_root() -> dict:
    return {"message": "AI Travel Assistant API is running"}
