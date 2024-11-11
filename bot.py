"""Коммуникационный бот, который позволяет пользователям отправлять сообщения администратору.

Функциональность:
 • Принимает сообщения от пользователей и пересылает их администратору.
 • Ответы администратора пересылаются обратно соответствующему пользователю.

сервис клиента (пользователя) и адмистратора совещены в дном файле. 
"""


import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import logging


# Настройка логгирования. Данные хранятся в файле bot.log с уровнем логирования INFO. 
logging.basicConfig(
    filename = 'bot.log',  
    level = logging.INFO,  
    format = '%(asctime)s - %(levelname)s - %(message)s', 
)


# Конфигурация (константы)
HOST = '127.0.0.1'
USER_PORT = 8000
ADMIN_PORT = 8001

# Хранение сообщений
messages = {}


# Обработчик запросов от пользователей
class UserRequestHandler(BaseHTTPRequestHandler):
    """ Класс UserRequestHandler наследуется от BaseHTTPRequestHandler и имеет метод do_POST, 
    который обрабатывает POST-запросы от пользователей. 
    Он получает тело запроса, парсит его как JSON и извлекает идентификатор пользователя и
    само сообщение. Если эти поля отсутствуют, возвращается ошибка 400. 
    """
    
    def do_POST(self):
        logging.info(f'получено сообщение от пользователя')
        # Получаем длину данных запроса
        content_length = int(self.headers['Content-Length'])
        # Читаем данные из запроса
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data)

        user_id = message.get('user_id') # получаем user_id из полученного сообщения
        user_message = message.get('message') # получаем текст сообщения 

        if not user_id or not user_message:
            logging.error(f'ошибка получения данных user_id или user_message')
            self.send_response(400)
            self.end_headers()
            return

        # Сохраняем сообщение в память и отправляем на сервер администратора
        messages[user_id] = user_message
        logging.info(f'получено сообщение {user_id}: {user_message}')
        print(f'Message received from user {user_id}: {user_message}')

        # Отправляем ответ
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Message sent to admin')


# Обработчик запросов от администратора
class AdminRequestHandler(BaseHTTPRequestHandler):
    """  Класс AdminRequestHandler наследуется от BaseHTTPRequestHandler и имеет метод do_POST, 
    который обрабатывает POST-запросы от администратора. 
    Он получает тело запроса, парсит его как JSON и извлекает идентификатор пользователя и 
    ответ администратора. Если эти поля отсутствуют, возвращается ошибка 400.
    """
  
    def do_POST(self):
        logging.info(f'получено сообщение от администратора')
        # Получаем длину данных запроса
        content_length = int(self.headers['Content-Length'])
        # Читаем данные из запроса
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data)

        user_id = message.get('user_id')
        admin_response = message.get('response')

        if not user_id or not admin_response:
            logging.error(f'ошибка получения данных user_id или user_message')
            self.send_response(400)
            self.end_headers()
            return

        # Пересылаем ответ пользователю
        logging.info(f'Отправлено сообщение от администратора {user_id}: {admin_response}')
        print(f'Received response from admin for {user_id}: {admin_response}')
        if user_id in messages:
            del messages[user_id]  # Удаляем сообщение после ответа
            print(f'Sending response to {user_id}: {admin_response}')
        else:
            print(f'No message found for user_id: {user_id}')

        # Отправляем ответ
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Response sent to user')


# запуск сервиса пользователя
def run_user_server():
    httpd = HTTPServer((HOST, USER_PORT), UserRequestHandler)
    logging.info(f'Сервис пользователей запущен http://{HOST}:{USER_PORT}')
    print(f'User server running on http://{HOST}:{USER_PORT}')
    httpd.serve_forever()


# запуск сервиса администратора
def run_admin_server():
    httpd = HTTPServer((HOST, ADMIN_PORT), AdminRequestHandler)
    logging.info(f'Сервис администратора запущен http://{HOST}:{USER_PORT}')
    print(f'Admin server running on http://{HOST}:{ADMIN_PORT}')
    httpd.serve_forever()


if __name__ == "__main__":
    """ Этот блок отвечает за создание и запуск двух потоков. 
    Первый поток запускает функцию run_user_server, которая создает экземпляр HTTP-сервера 
    для обработки запросов от пользователей. 
    Второй поток запускает функцию run_admin_server, которая создает экземпляр HTTP-сервера 
    для обработки запросов от администратора. 
    Оба потока работают параллельно, обеспечивая работу двух серверов одновременно.
    """

    user_thread = threading.Thread(target=run_user_server)
    admin_thread = threading.Thread(target=run_admin_server)
    user_thread.start()
    admin_thread.start()