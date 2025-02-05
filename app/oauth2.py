from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from httpx import AsyncClient
from . import models, database, security
from .oauth2_config import settings

router = APIRouter()

@router.get("/login/google")
async def login_google():
    """Inicia el flujo de autenticación con Google"""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
    }
    return {"url": f"{GOOGLE_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"}

@router.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(database.get_db)):
    """Maneja la respuesta de Google"""
    async with AsyncClient() as client:
        # Obtener token
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
        )
        token_data = token_response.json()
        
        # Obtener información del usuario
        user_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_data = user_response.json()

        # Crear o actualizar usuario
        db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
        if not db_user:
            db_user = models.User(
                email=user_data["email"],
                name=user_data["name"],
                username=user_data["email"].split("@")[0],
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # Generar token JWT
        access_token = security.create_access_token(data={"sub": db_user.username})
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login/github")
async def login_github():
    """Inicia el flujo de autenticación con GitHub"""
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email",
    }
    return {"url": f"{GITHUB_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"}

@router.get("/auth/github/callback")
async def github_callback(code: str, db: Session = Depends(database.get_db)):
    """Maneja la respuesta de GitHub"""
    async with AsyncClient() as client:
        # Obtener token
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"}
        )
        token_data = token_response.json()
        
        # Obtener información del usuario
        user_response = await client.get(
            GITHUB_USERINFO_URL,
            headers={
                "Authorization": f"Bearer {token_data['access_token']}",
                "Accept": "application/json"
            }
        )
        user_data = user_response.json()

        # Crear o actualizar usuario
        db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
        if not db_user:
            db_user = models.User(
                email=user_data["email"],
                name=user_data["name"] or user_data["login"],
                username=user_data["login"],
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # Generar token JWT
        access_token = security.create_access_token(data={"sub": db_user.username})
        return {"access_token": access_token, "token_type": "bearer"}