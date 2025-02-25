from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse 
import uvicorn  


# Создаем экземпляр приложения FastAPI
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware для логирования всех входящих запросов.
    Выводит информацию о методе запроса, URL и заголовках в консоль.
    """
    # Логируем метод запроса и URL
    print(f"\nПолучен запрос {request.method} для {request.url}")
    # Логируем заголовки запроса
    print(f"Заголовки: {request.headers}")

    # Передаем запрос дальше по цепочке middleware
    response = await call_next(request)
    return response


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def handle_get_request(request: Request, full_path: str):
    """
    Обработчик GET-запросов. Возвращает HTML-страницу с именем пользователя.
    Если имя пользователя не передано (например, пользователь не аутентифицирован),
    возвращается пустая страница.
    """
    # Получаем имя пользователя из заголовка "x-forwarded-user" DEFAULT = Неизвестный пользователь 
    user_name = request.headers.get("x-forwarded-user", "Неизвестный пользователь")
    print(f"Пользователь: {user_name}")

    # Формируем HTML-контент
    html_content = f"""
    <html>
        <head>
            <title>Backend Server</title>
        </head>
        <body>
            <h1>Привет, {user_name}!</h1>
            <p>Это сервер backend.</p>
            <a href="/hub/logout">LOGOUT</a>
            <a href="/hub/home">HOME</a>     
            <a href="/hub/api/user">SETTINGS</a>
        </body>
    </html>
    """
    # Возвращаем сформированный HTML-контент
    return HTMLResponse(content=html_content)


# Блок для запуска сервера, если скрипт запущен напрямую
if __name__ == "__main__":
    print("Запуск backend сервера...") 
    # Если файл запущен напрямую, запускаем сервер на localhost:8003
    uvicorn.run(app, host="0.0.0.0", port=8003)