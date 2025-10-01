#!/usr/bin/env python3
"""
Test simple para verificar que FastAPI funciona básicamente
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Crear app simple
app = FastAPI(
    title="Sistema de Gestión de Flota - TEST",
    description="Prueba básica de la API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Sistema de Gestión de Flota funcionando",
        "status": "OK",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test")
def test():
    return {
        "test": "passed",
        "message": "El servidor está funcionando correctamente"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)