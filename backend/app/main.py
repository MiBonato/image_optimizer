from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import images

app = FastAPI(title="Image Optimizer API", version="0.1.0")

# CORS (autorise le front Vite en dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# Routes images
app.include_router(images.router)
