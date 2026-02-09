from authlib.integrations.starlette_client import OAuth
from core.config import settings

oauth = OAuth()

# Google OAuth
oauth.register(
    name='google',
    client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# VK OAuth
oauth.register(
    name='vk',
    client_id=settings.VK_OAUTH_CLIENT_ID,
    client_secret=settings.VK_OAUTH_CLIENT_SECRET,
    authorize_url='https://oauth.vk.com/authorize',
    #nosec
    access_token_url='https://oauth.vk.com/access_token',
    client_kwargs={'scope': 'email'}
)

# Telegram OAuth (через Bot API)
# Telegram использует другой подход - через бота и deep linking