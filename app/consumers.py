import base64
import os

# Устанавливаем модуль настроек Django для корректной работы приложения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Ensure correct path

import django

# Инициализируем Django
django.setup()

from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import EmailMessage, User
import json
from asgiref.sync import sync_to_async


# Класс WebSocket-консумера для Yandex-почты
class YourConsumer(AsyncWebsocketConsumer):

    # Метод, который вызывается при подключении WebSocket
    async def connect(self):
        await self.accept()  # Принимаем подключение

    @sync_to_async  # Синхронный метод для сохранения сообщений, обёрнутый в async для использования в асинхронном коде
    def save_message(self, d):
        # Если запрос данных — это список сообщений

        if d['data'] == 'list':
            id_user = d['id_user']
            # Ищем пользователя по ID
            current_user = User.objects.filter(id=id_user).first()
            id = int(d['id_yandex'])  # Получаем ID сообщения

            # Если ID сообщения 0, получаем последнее сообщение из Yandex
            if id == 0:
                emails = EmailMessage.objects.filter(type='yandex').filter(user=current_user).order_by(
                    '-email_id').first()
            else:
                # Иначе ищем предыдущее сообщение
                emails = EmailMessage.objects.filter(email_id=id - 1).filter(type='yandex').filter(
                    user=current_user).first()

            # Формируем HTML-ответ для отображения сообщений на фронтенде
            res = f''' <div class="card card-task">


                                            <div class="card-body">
                                                <div class="card-title">
                                                    <a href="#"><h6 data-filter-by="text" class="H6-filter-by-text">
                                                        <p id="id_block">''' + str(emails.email_id) + '''</p>
                                                        ''' + emails.subject + '''</h6></a><p>''' + emails.body + '''</p>
                                                    <span class="text-small">''' + emails.from_email + '''</span>
                                                </div>
                                                <div class="card-meta">

                                                    <div class="d-flex align-items-center">
                                                        <span>''' + emails.date_email + '''</span>
                                                    </div>

                                                </div>
                                            </div>
                                        </div>'''
            return res

    # Метод, который вызывается при получении данных через WebSocket
    async def websocket_receive(self, text_data):
        # Распаковываем данные и вызываем метод сохранения сообщений
        response = await self.save_message(json.loads(text_data['text']))
        # Отправляем результат обратно на фронтенд
        await self.send(text_data=json.dumps({"message": response}))

    # Метод для обработки отключения WebSocket
    async def disconnect(self, close_code):
        pass


# Класс WebSocket-консумера для Gmail
class WSGoogle(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Принимаем подключение

    @sync_to_async  # Метод сохранения сообщений для Gmail, аналогичный методу для Yandex
    def save_message(self, d):
        if d['data'] == 'list':
            id_user = d['id_user']
            current_user = User.objects.filter(id=id_user).first()
            id = int(d['id_google'])

            if id == 0:
                emails = EmailMessage.objects.filter(type='google').filter(user=current_user).order_by(
                    '-email_id').first()
            else:
                emails = EmailMessage.objects.filter(email_id=id - 1).filter(type='google').filter(
                    user=current_user).first()

            # Формируем HTML для Gmail
            res = f''' <div class="card card-task">
    
    
                                                   <div class="card-body">
                                                       <div class="card-title">
                                                           <a href="#"><h6 data-filter-by="text" class="H6-filter-by-text">
                                                               <p id="id_block_google">''' + str(emails.email_id) + '''</p>
                                                               ''' + emails.subject + '''</h6></a><p>''' + str(
                emails.body) + '''</p>
                                                           <span class="text-small">''' + emails.from_email + '''</span>
                                                       </div>
                                                       <div class="card-meta">
    
                                                           <div class="d-flex align-items-center">
                                                               <span>''' + emails.date_email + '''</span>
                                                           </div>
    
                                                       </div>
                                                   </div>
                                               </div>'''

            return res

    # Обработка получения данных через WebSocket
    async def websocket_receive(self, text_data):
        response = await self.save_message(json.loads(text_data['text']))
        await self.send(text_data=json.dumps({"message": response}))

    async def disconnect(self, close_code):
        pass


# Класс WebSocket-консумера для Mail.ru
class WSMail(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    @sync_to_async  # Метод сохранения сообщений для Mail.ru, аналогичный предыдущим
    def save_message(self, d):
        if d['data'] == 'list':
            id_user = d['id_user']
            current_user = User.objects.filter(id=id_user).first()
            id = int(d['id_mail'])

            if id == 0:
                emails = EmailMessage.objects.filter(type='mail').filter(user=current_user).order_by(
                    '-email_id').first()
            else:
                emails = EmailMessage.objects.filter(email_id=id - 1).filter(type='mail').filter(
                    user=current_user).first()

            # Формируем HTML для Mail.ru
            res = f''' <div class="card card-task">


                                                          <div class="card-body">
                                                              <div class="card-title">
                                                                  <a href="#"><h6 data-filter-by="text" class="H6-filter-by-text">
                                                                      <p id="id_block_mail">''' + str(
                emails.email_id) + '''</p>
                                                                      ''' + emails.subject + '''</h6></a><p>''' + str(
                emails.body) + '''</p>
                                                                  <span class="text-small">''' + emails.from_email + '''</span>
                                                              </div>
                                                              <div class="card-meta">

                                                                  <div class="d-flex align-items-center">
                                                                      <span>''' + emails.date_email + '''</span>
                                                                  </div>

                                                              </div>
                                                          </div>
                                                      </div>'''

            return res

    async def websocket_receive(self, text_data):
        response = await self.save_message(json.loads(text_data['text']))
        await self.send(text_data=json.dumps({"message": response}))

    async def disconnect(self, close_code):
        pass
