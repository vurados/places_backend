from fastapi import APIRouter, Depends, HTTPException, Request
from authlib.integrations.starlette_client import OAuthError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.oauth import oauth
from app.services.auth_service import create_access_token

router = APIRouter()

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_auth(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Создаем или обновляем пользователя
        # ... аналогично oauth_login из предыдущего кода ...
        
        return {"message": "Google auth successful", "user_info": user_info}
    
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/vk")
async def vk_login(request: Request):
    redirect_uri = request.url_for('vk_auth')
    return await oauth.vk.authorize_redirect(request, redirect_uri)

@router.get("/vk/callback")
async def vk_auth(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.vk.authorize_access_token(request)
        # VK возвращает данные по-другому, нужно обработать
        # ... обработка VK данных ...
        
        return {"message": "VK auth successful"}
    
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=str(error))