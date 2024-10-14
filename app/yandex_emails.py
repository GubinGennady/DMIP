import imaplib  # Импортируем библиотеку для работы с IMAP-серверами
import email  # Импортируем модуль для работы с email-сообщениями
from email.header import decode_header  # Импортируем функцию для декодирования заголовков email
import os  # Импортируем модуль для работы с операционной системой (файловой системой)


# Функция для получения писем с Яндекс.Почты
def fetch_yandex_emails(login, password, save_dir="app/attachments/yandex"):
    username = login  # Логин пользователя
    password = password  # Пароль пользователя

    # Проверка, что логин и пароль не пустые
    if username is None or password is None:
        raise ValueError("Имя пользователя и пароль не должны быть None")  # Выбрасываем ошибку, если данные отсутствуют

    emails = []  # Инициализируем список для хранения писем

    try:
        # Подключаемся к IMAP-серверу Яндекса через SSL
        imap = imaplib.IMAP4_SSL("imap.yandex.ru")
        # Авторизуемся на сервере с использованием логина и пароля
        imap.login(username, password)

        # Выбор почтового ящика (в данном случае yandex)
        imap.select("yandex")

        # Выполняем поиск всех писем в yandex
        status, messages = imap.search(None, "ALL")
        # Получаем список ID писем
        email_ids = messages[0].split()

        # Проверяем, существует ли директория для сохранения вложений, и если нет, создаем её
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        # Проходим по каждому найденному письму
        for email_id in email_ids:
            # Получение письма по ID
            res, msg = imap.fetch(email_id, "(RFC822)")

            # Обрабатываем части сообщения
            for response_part in msg:
                if isinstance(response_part, tuple):
                    # Получаем само сообщение (письмо) из байтов
                    msg = email.message_from_bytes(response_part[1])

                    # Декодируем заголовок письма (тема)
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # Декодируем тему, если она в байтах
                        subject = subject.decode(encoding if encoding else 'utf-8')

                    # Получаем отправителя и дату отправки письма
                    from_ = msg.get("From")
                    date = msg.get("Date")

                    body = ""  # Инициализируем переменную для хранения тела письма
                    attachments = []  # Инициализируем список для хранения путей к вложениям

                    # Если письмо состоит из нескольких частей (например, текст и вложения)
                    if msg.is_multipart():
                        # Проходим по каждой части письма
                        for part in msg.walk():
                            content_type = part.get_content_type()  # Получаем тип содержимого
                            content_disposition = str(part.get("Content-Disposition"))

                            # Если это текстовое содержимое без вложений
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()  # Декодируем тело письма
                                except Exception as e:
                                    print(f"Ошибка при декодировании тела: {e}")
                            # Если это HTML-содержимое
                            elif content_type == "text/html":
                                try:
                                    html_content = part.get_payload(decode=True).decode()  # Декодируем HTML-контент
                                    body += html_content  # Добавляем его в тело письма
                                except Exception as e:
                                    print(f"Ошибка при декодировании HTML: {e}")

                            # Если это вложение
                            if "attachment" in content_disposition:
                                filename = part.get_filename()  # Получаем имя файла
                                if filename:
                                    # Декодируем имя файла, если оно закодировано
                                    filename = decode_header(filename)[0][0]
                                    if isinstance(filename, bytes):
                                        filename = filename.decode()

                                    # Определяем путь для сохранения файла
                                    file_path = os.path.join(save_dir, filename)
                                    # Сохраняем файл
                                    with open(file_path, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    # Добавляем путь к файлу в список вложений
                                    attachments.append(file_path)
                    else:
                        # Если письмо не многокомпонентное, просто получаем его тело
                        body = msg.get_payload(decode=True).decode()

                    # Добавляем данные о письме в список
                    emails.append({
                        "email_id": email_id.decode(),  # ID письма
                        "subject": subject,  # Тема письма
                        "from": from_,  # Отправитель
                        "date": date,  # Дата
                        "body": body,  # Тело письма
                        "attachments": attachments  # Вложения
                    })

    # Обработка ошибок IMAP
    except imaplib.IMAP4.error as e:
        print(f"Ошибка IMAP: {e}")

    # Закрываем соединение с сервером IMAP в любом случае
    finally:
        try:
            imap.close()  # Закрываем подключение
            imap.logout()  # Выходим из сессии
        except Exception as e:
            print(f"Ошибка при закрытии соединения: {e}")

    return emails  # Возвращаем список писем
