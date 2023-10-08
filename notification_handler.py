import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import controller
import dao
import service
from multiprocessing import Process


class MyHandler(BaseHTTPRequestHandler):
    async def notify_users_by_group(self, group_name, day):
        result = controller.dao.get_ids_by_group(group_name)
        for id in result:
            try:
                await controller.bot.send_message(id, "Есть изменения")
                await controller.bot.send_photo(id, service.get_image_by_day(day))
            except:
                print(f"Не удалось отправить изменения пользователю {controller.dao.get_username_by_id(id)}")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # Обработка данных из тела POST-запроса
        data = body.decode('utf-8')
        data = json.loads(data)
        print(data)
        tasks_queue.append(lambda: asyncio.run(self.notify_users_by_group(data["groupName"], data)))
        # Отправляем ответ клиенту
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'success')

tasks_queue = []

def task_observer():
    print("Observing")
    while True:
        if tasks_queue != []:
            print("Task appeared")
            for func in tasks_queue:
                func()
                tasks_queue.remove(func)

def start_listening_port():
    # Создаем HTTP-сервер со своим обработчиком и указываем порт
    httpd = HTTPServer(("", 12234), MyHandler)
    print("listening port")
    # Запускаем сервер и прослушиваем порт до прерывания программы
    httpd.serve_forever()
