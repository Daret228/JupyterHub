import os
import socket
import sys
from subprocess import Popen
from jupyterhub.spawner import LocalProcessSpawner


class PythonServerSpawner(LocalProcessSpawner):
    """
    Создаем кастомный Spawner для запуска сервера на динамическом порту.
    """

    async def start(self):
        """
        Запускаем сервер
        """
        # Передаем имя пользователя через переменную окружения
        env = dict(os.environ, USER_NAME=self.user.name)

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
                ],
                env=env  # Передаем изменённое окружение
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
        """
        Останавливает запущенный сервер.
        """
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


# Добавляем текущую директорию в путь для поиска модулей(для передачи имени юзера)
sys.path.append(os.getcwd())

# Получаем конфигурацию JupyterHub
c = get_config()

# Отключаем добавление пользовательских постфиксов в маршрут
c.ConfigurableHTTPProxy.command = [
    'configurable-http-proxy', '--no-include-prefix'
]

# Указываем IP и порт, на котором будет работать JupyterHub
c.JupyterHub.ip = '0.0.0.0'  # Слушать на всех интерфейсах
c.JupyterHub.port = 8000  # Порт для JupyterHub

# Используем наш кастомный Spawner
c.JupyterHub.spawner_class = PythonServerSpawner

# Админы
c.Authenticator.admin_users = {'admin'}

# Аутентификация (сейчас тестовая, беспарольная)
c.Authenticator.allow_all = True
c.JupyterHub.authenticator_class = 'dummy'