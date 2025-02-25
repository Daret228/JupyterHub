# 🚀 JupyterHub + FastAPI Backend  

Этот проект заменяет стандартный single-user сервер JupyterHub на FastAPI, используя кастомный Spawner.  

## 📌 Возможности  
- FastAPI backend вместо стандартного Jupyter single-user сервера.  
- Проксирование запросов через middleware.  
- Передача имени пользователя через заголовки.  
- Аутентификация через JupyterHub API.  

## 📂 Структура проекта  
```
📁 project  
│-- 📄 jupyterhub_config.py    # Конфигурация JupyterHub  
│-- 📄 backend.py              # Backend сервер (FastAPI)  
│-- 📄 single_user_server.py   # Single-user сервер (FastAPI)  
```

## 🔧 Установка и настройка  

### 1️⃣ Установить необходимые пакеты  
```bash
sudo apt update && sudo apt install -y npm nodejs python3-venv python3-pip
```

### 2️⃣ Установить `configurable-http-proxy` через npm  
```bash
npm install -g configurable-http-proxy
```

### 3️⃣ Установить Python-зависимости(можно в виртуальной среде)
```bash
pip install fastapi uvicorn httpx jupyterhub
```

### 4️⃣ Создать виртуальную среду (рекомендуется)  
```bash
python3 -m venv venv  
source venv/bin/activate  # Для Linux/macOS  
venv\Scripts\activate     # Для Windows  
```

### 5️⃣ Добавить `configurable-http-proxy` в PATH  
```bash
export PATH="$PATH:$(pwd)/node_modules/configurable-http-proxy/bin"
```

### 6️⃣ Запуск JupyterHub  
```bash
jupyterhub -f jupyterhub_config.py
```
и отдельно запустить `backend.py`
```bash
python3 backend.py
```

## 🔥 Использование  
После запуска:  
- JupyterHub доступен по `http://localhost:8000`.  
- Backend доступен по `http://localhost:8003`.  
- Single-user сервер проксирует запросы через middleware.  

## ✅ Проверка работы  
1. **Открыть JupyterHub**:  
   Перейдите в браузере по адресу [http://localhost:8000](http://localhost:8000).  
2. **Войти в систему**:  
   Введите любое имя пользователя (пароль не требуется, так как включен `dummy`-аутентификатор).  
3. **Запуск single-user сервера**:  
   После входа, сервер автоматически запустится.  
4. **Проверить backend**:  
   Откройте [http://localhost:8003](http://localhost:8003) и убедитесь, что отображается имя пользователя.   
5. **Завершение работы**:  
   В JupyterHub нажмите "Logout" и попробуйте снова зайти.  

## 🛠 Разработка и отладка  
Для тестирования backend можно запустить его отдельно:  
```bash
python backend.py
```

Для отладки single-user сервера:  
```bash
python single_user_server.py
```

В каждой из консолей на которых были запущены `jupyterhub` и `backend.py` соответственно выводятся логи

## 📚 Дополнительные ресурсы  
- 📖 Официальная документация JupyterHub: [JupyterHub Docs](https://docs.jupyter.org/en/latest/)

