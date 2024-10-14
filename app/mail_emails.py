import imaplib  # Модуль для работы с IMAP-сервером
import email  # Модуль для разбора и обработки электронной почты
import os  # Модуль для работы с файловой системой
from email.header import decode_header  # Функция для декодирования заголовков писем


def fetch_mail_emails(username, password, save_dir="app/attachments/mail"):
    # Подключение к IMAP-серверу mail.ru
    imap = imaplib.IMAP4_SSL("imap.mail.ru")

    # Логинимся в почтовый ящик с использованием переданных имени пользователя и пароля
    imap.login(username, password)

    # Выбираем почтовый ящик (mail) для чтения писем
    imap.select("mail")

    # Ищем все письма в почтовом ящике
    status, messages = imap.search(None, "ALL")

    email_ids = messages[0].split()  # Получаем список идентификаторов писем
    emails = []  # Список для хранения информации о письмах

    # Проверяем, существует ли каталог для вложений, если нет — создаём его
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # Проходим по каждому письму
    for email_id in email_ids:
        # Получаем письмо по его ID
        res, msg = imap.fetch(email_id, "(RFC822)")

        # Ограничиваемся первыми 5 частями сообщения
        for response_part in msg[:5]:
            if isinstance(response_part, tuple):
                # Разбор содержимого письма
                msg = email.message_from_bytes(response_part[1])

                # Декодируем заголовок темы письма
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # Если заголовок в байтах, декодируем его
                    subject = subject.decode(encoding if encoding else 'utf-8')

                # Получаем отправителя и дату письма
                from_ = msg.get("From")
                date = msg.get("Date")

                # Инициализируем переменные для хранения тела письма и вложений
                body = ""
                attachments = []

                # Если письмо состоит из нескольких частей
                if msg.is_multipart():
                    # Проходим по каждой части письма
                    for part in msg.walk():
                        content_type = part.get_content_type()  # Получаем тип содержимого
                        content_disposition = str(part.get("Content-Disposition"))  # Получаем данные о вложении

                        # Обрабатываем текстовое содержимое (без вложений)
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                # Декодируем текстовое содержимое
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass

                        # Обрабатываем вложения
                        if "attachment" in content_disposition:
                            filename = part.get_filename()  # Получаем имя файла
                            if filename:
                                # Декодируем имя файла, если оно закодировано
                                filename = decode_header(filename)[0][0]
                                if isinstance(filename, bytes):
                                    filename = filename.decode()

                                # Сохраняем вложение в указанный каталог
                                file_path = os.path.join(save_dir, filename)
                                with open(file_path, "wb") as f:
                                    f.write(part.get_payload(decode=True))  # Записываем файл
                                attachments.append(file_path)  # Добавляем путь к файлу в список вложений
                else:
                    # Если письмо не многокомпонентное, просто получаем его содержимое
                    body = msg.get_payload(decode=True).decode()

                # Добавляем информацию о письме в список
                emails.append({
                    "email_id": email_id.decode(),  # ID письма
                    "subject": subject,  # Тема письма
                    "from": from_,  # Отправитель
                    "date": date,  # Дата отправления
                    "body": body,  # Тело письма
                    "attachments": attachments  # Вложения
                })

    # Закрываем соединение с сервером и выходим
    imap.close()
    imap.logout()

    return emails  # Возвращаем список писем
