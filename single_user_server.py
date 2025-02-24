from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
import httpx  # Для отправки HTTP-запросов
import uvicorn

app = FastAPI()

# Адрес backend-сервера
BACKEND_URL = "http://localhost:8003"

# Адрес JupyterHub для проверки аутентификации
JUPYTERHUB_URL = "http://localhost:8000/hub/api"

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
        return Response(status_code=401, content="Unauthorized")

    try:
        # Проксируем запрос на backend-сервер
        async with httpx.AsyncClient() as client:
            backend_response = await client.request(
                method=request.method,
                url=f"{BACKEND_URL}{request.url.path}",
                headers={key: value for key, value in request.headers.items() if key != "host"},
                cookies=request.cookies,
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
    # Если файл запущен напрямую, используем порт по умолчанию (например, 8002)
    uvicorn.run(app, host="127.0.0.1", port=8002)