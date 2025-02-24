import os
import socket
import sys
from subprocess import Popen
from jupyterhub.spawner import LocalProcessSpawner

# Добавляем текущую директорию в путь для поиска модулей
sys.path.append(os.getcwd())

# Получаем конфигурацию JupyterHub
c = get_config()

# Создаем кастомный Spawner для запуска single-user сервера (FastAPI) на динамическом порту
class PythonServerSpawner(LocalProcessSpawner):
    async def start(self):
        # Создаем сокет для поиска свободного порта
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))  # Привязываемся к случайному порту
            port = s.getsockname()[1]  # Получаем номер порта
        
        try:
            # Запускаем single-user сервер (FastAPI) на выбранном порту
            self.proc = Popen(
                [
                    "python3", "-m", "uvicorn", 
                    "single_user_server:app", 
                    "--host", "127.0.0.1", 
                    "--port", str(port)
                ]
            )
        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            self.log.error('У пользователя "%s" ошибка при старте сервера: %s', self.user.name, e)
            raise
        
        # Сохраняем PID процесса
        self.pid = self.proc.pid
        
        # Возвращаем IP и порт, на котором запущен сервер
        return '127.0.0.1', port
    
    async def stop(self, now=False):
        """Останавливает запущенный сервер"""
        if hasattr(self, 'proc') and self.proc:
            self.log.info('Остановка сервера пользователя "%s" (PID %d)', self.user.name, self.pid)
            self.proc.terminate()  # Отправляем SIGTERM
            try:
                self.proc.wait(timeout=5)  # Ждем завершения процесса
            except TimeoutError:
                self.log.warning('Принудительное завершение сервера пользователя "%s" (PID %d)', self.user.name, self.pid)
                self.proc.kill()  # Принудительное завершение, если процесс не закрылся
            finally:
                self.proc = None

# Настройка прокси для JupyterHub
# Отключаем добавление пользовательских постфиксов в маршрут
c.ConfigurableHTTPProxy.command = [
    'configurable-http-proxy', '--no-include-prefix'
]

# Указываем IP и порт, на котором будет работать JupyterHub
c.JupyterHub.ip = '0.0.0.0'  # Слушать на всех интерфейсах
c.JupyterHub.port = 8000  # Порт для JupyterHub

# Указываем JupyterHub использовать наш кастомный Spawner
c.JupyterHub.spawner_class = PythonServerSpawner

# Разрешаем аутентификацию для всех пользователей (без пароля)
c.Authenticator.allow_all = True

# Используем PAM аутентификацию
c.JupyterHub.authenticator_class = 'pam'