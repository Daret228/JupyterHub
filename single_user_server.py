# Импортируем необходимые модули
from fastapi import FastAPI, Request
from fastapi.responses import Response 
import httpx 
import uvicorn 
import os  
import re

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# URL backend-сервера и JupyterHub API
BACKEND_URL = "http://localhost:8003"
JUPYTERHUB_URL = "http://localhost:8000/hub/api"


async def get_user_info():
    """
    Проверяет аутентификацию пользователя и получает его имя из переменной окружения USER_NAME.
    Возвращает имя пользователя или None, если оно не установлено.
    """
    try:
        # Получаем имя пользователя из переменной окружения
        username = os.getenv("USER_NAME")  
        
        if username:
            print(f"Имя пользователя: {username}")
            # Проверка на латинсике и цифры
            if re.fullmatch(r'^[a-zA-Z0-9_-]+$', username):
                return username
            else:
                print('Неверный формат имени пользователя')
                return None
        else:
            print("Имя пользователя не установлено.")
            return None
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
    return None


async def check_authentication(request: Request):
    """
    Проверяет аутентификацию пользователя, отправляя запрос в JupyterHub API.
    Возвращает True, если аутентификация успешна, иначе False.
    """
    cookies = request.cookies 
    if not cookies:
        return False 

    try:
        async with httpx.AsyncClient() as client:
            # Отправляем GET-запрос в JupyterHub API с куками пользователя
            response = await client.get(JUPYTERHUB_URL, cookies=cookies)

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
        # Если аутентификация не прошла, возвращаем ошибку 401
        return Response(status_code=401, content="Authorization failed")

    # Проверяем получение имени пользователя
    user_name = await get_user_info()
    if not user_name:
        # Если имя пользователя не определено, возвращаем ошибку 401 
        return Response(status_code=401, content="Couldn't get the correct name")

    try:
        # Проксируем запрос на backend-сервер
        async with httpx.AsyncClient() as client:
            backend_response = await client.request(
                method=request.method,
                url=f"{BACKEND_URL}{request.url.path}", 
                # Добавляем заголовок с именем пользователя
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
        # В случае ошибки возвращаем 500 Internal Server Error 3
        return Response(status_code=500, content="Internal Server Error 3")


# Блок для запуска сервера, если скрипт запущен напрямую
if __name__ == "__main__":
    print("Запуск single сервера...") 
    # Если файл запущен напрямую, запускаем сервер на localhost:8002
    uvicorn.run(app, host="127.0.0.1", port=8002)