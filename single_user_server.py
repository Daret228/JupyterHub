from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
import httpx 
import uvicorn
import os

app = FastAPI()

BACKEND_URL = "http://localhost:8003"
JUPYTERHUB_URL = "http://localhost:8000/hub/api"

async def get_user_info():
    """
    Проверяет аутентификацию пользователя и получает его имя из JupyterHub API.
    Возвращает имя пользователя или None.
    """
    username = os.getenv("USER_NAME")
    if username:
        print(f"Имя пользователя: {username}")
        return username
    else:
        print("Имя пользователя не установлено.")
    
    return "GG" 

    headers = request.headers
    
    try:
        async with httpx.AsyncClient() as client:
            
            response = await client.get(f"{JUPYTERHUB_URL}/user", headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                return user_data.get("name") 
            
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")

    return None


async def check_authentication(request: Request):
    """
    Проверяет аутентификацию пользователя, отправляя запрос в JupyterHub.
    Возвращает True, если аутентификация успешна, иначе False.
    """
    cookies = request.cookies
    if not cookies:
        return False

    try:
        async with httpx.AsyncClient() as client:
            # Отправляем GET-запрос в JupyterHub с куками пользователя
            response = await client.get(JUPYTERHUB_URL, cookies=cookies)
            
            # Если статус код 200, пользователь аутентифицирован
            if response.status_code == 200:
                return True
            else:
                return False
            
    except Exception as e:
        print(f"Ошибка при проверке аутентификации: {e}")
        return False

@app.middleware("http")
async def proxy_requests(request: Request, call_next):
    """
    Middleware для проксирования запросов на backend-сервер.
    """
    # Проверяем аутентификацию пользователя
    is_authenticated = await check_authentication(request)
    
    if not is_authenticated:
        # Если аутентификация не прошла, игнорируем запрос
        return Response(status_code=401, content="Unauthorized 1")
    
    # Получаем имя пользователя
    user_name = await get_user_info()
    
    if not user_name:
        return Response(status_code=401, content="Unauthorized 2")

    try:
        # Проксируем запрос на backend-сервер
        async with httpx.AsyncClient() as client:
            
            backend_response = await client.request(
                method=request.method,
                url=f"{BACKEND_URL}{request.url.path}",
                headers={**request.headers, "X-Forwarded-User": user_name},
                content=await request.body()
            )
            
            # Возвращаем ответ от backend-сервера
            return Response(
                content=backend_response.content,
                status_code=backend_response.status_code,
                headers=backend_response.headers
            )
            
    except Exception as e:
        print(f"Ошибка при проксировании запроса: {e}")
        return Response(status_code=500, content="Internal Server Error")

if __name__ == "__main__":
    # Если файл запущен напрямую, используем порт 8002
    uvicorn.run(app, host="127.0.0.1", port=8002)