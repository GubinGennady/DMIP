from django.shortcuts import redirect
from django.views.generic import TemplateView

# Импортируем функции для получения писем из разных почтовых сервисов
from .mail_emails import fetch_mail_emails
from .gmail_emails import fetch_gmail_emails
from .yandex_emails import fetch_yandex_emails

# Импортируем модели EmailMessage, Title, User
from .models import EmailMessage
from .models import Title, User

# Для хеширования и проверки паролей
from django.contrib.auth.hashers import make_password, check_password


# Представление для регистрации
class RegView(TemplateView):
    template_name = 'app/reg.html'  # Шаблон для страницы регистрации

    def post(self, request):
        # Получаем email и пароли из POST-запроса
        email = self.request.POST.get('email')
        password1 = self.request.POST.get('password1')
        password2 = self.request.POST.get('password2')

        # Проверка, совпадают ли оба введённых пароля
        if password1 == password2:
            hash_password = make_password(password1)  # Хешируем пароль
            user = User()  # Создаём новый объект пользователя
            user.username = email  # Присваиваем email как имя пользователя
            user.password = hash_password  # Сохраняем хешированный пароль
            user.save()  # Сохраняем пользователя в базу данных
            return redirect('/app/auth')  # Перенаправляем на страницу аутентификации
        return redirect('/app')  # Если пароли не совпадают, перенаправляем на главную страницу


# Представление для аутентификации
class AuthView(TemplateView):
    template_name = 'app/auth.html'  # Шаблон для страницы аутентификации

    def post(self, request):
        # Получаем email и пароль из POST-запроса
        email = self.request.POST.get('email')
        password1 = self.request.POST.get('password1')

        # Проверяем, существует ли пользователь с данным email
        if User.objects.filter(username=email).exists():
            user_password = User.objects.filter(username=email).first()  # Получаем пользователя
            # Проверяем правильность пароля
            if check_password(password1, user_password.password):
                request.session['user'] = email  # Устанавливаем email пользователя в сессию
        return redirect('/app/list')  # Перенаправляем на список писем


# Представление для главной страницы
class IndexView(TemplateView):
    template_name = 'app/index.html'  # Шаблон для главной страницы

    # Дополнительный контекст для шаблона
    extra_context = {
        'title': 'Состояние загрузки',
        'fetch_yandex_emails': [],
        'fetch_gmail_emails': [],
        'fetch_mail_emails': []
    }

    # Проверка, авторизован ли пользователь, перед тем как обработать запрос
    def dispatch(self, request, *args, **kwargs):
        if 'user' not in request.session:
            return redirect('/app/auth')  # Если нет пользователя в сессии, перенаправляем на аутентификацию
        return super().dispatch(request, *args, **kwargs)

    # Получаем контекст для шаблона
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = EmailMessage.objects.all()  # Получаем все письма

        # Инициализируем переменные для хранения названий почтовых сервисов
        name_yandex = ''
        name_mail = ''
        name_gmail = ''

        # Проверяем наличие записей в таблице Title для каждого почтового сервиса
        if Title.objects.filter(name='Yandex').exists():
            name_yandex = Title.objects.filter(name='Yandex').first().name
        if Title.objects.filter(name='Gmail').exists():
            name_gmail = Title.objects.filter(name='Gmail').first().name
        if Title.objects.filter(name='Mail').exists():
            name_mail = Title.objects.filter(name='Mail').first().name

        # Добавляем названия почтовых сервисов в контекст
        context_data['title_yandex'] = name_yandex
        context_data['title_gmail'] = name_gmail
        context_data['title_mail'] = name_mail

        # Получаем текущего пользователя по email из сессии
        current_user = User.objects.filter(username=self.request.session['user']).first()

        # Инициализируем флаги для проверки успешной загрузки писем
        m1, m2, m3 = False, False, False

        # Пытаемся получить письма с Yandex
        try:
            yandex_list = fetch_yandex_emails(current_user.login_yandex, current_user.password_yandex)
            m1 = True
        except:
            m1 = False

        # Пытаемся получить письма с Gmail
        try:
            google_list = fetch_gmail_emails(current_user.login_gmail, current_user.password_gmail)
            m2 = True
        except:
            m2 = False

        # Пытаемся получить письма с Mail.ru
        try:
            mail_list = fetch_mail_emails(current_user.login_mail, current_user.password_mail)
            m3 = True
        except:
            m3 = False

        # Начальный ID для писем
        id = 1

        # Если письма с Yandex успешно загружены
        if m1:
            for ya in yandex_list:
                # Проверяем, существует ли письмо с данным ID, если нет — добавляем его
                if not EmailMessage.objects.filter(email_id=id).exists():
                    email = EmailMessage()
                    email.email_id = id
                    email.subject = ya['subject']
                    email.date_email = ya['date']
                    email.from_email = ya['from']
                    email.body = ya['body']
                    email.type = 'yandex'
                    email.user = current_user
                    email.attachments = ','.join(ya['attachments'])  # Сохраняем вложения
                    email.save()
                id += 1

        # Аналогично для писем с Gmail
        if m2:
            for go in google_list:
                if not EmailMessage.objects.filter(email_id=id).exists():
                    email = EmailMessage()
                    email.email_id = id
                    email.subject = go['subject']
                    email.date_email = go['date']
                    email.from_email = go['from']
                    email.body = go['body']
                    email.type = 'google'
                    email.attachments = ','.join(ya['attachments'])  # Сохраняем вложения
                    email.user = current_user
                    email.save()
                id += 1

        # Аналогично для писем с Mail.ru
        if m3:
            for ml in mail_list:
                if not EmailMessage.objects.filter(email_id=id).exists():
                    email = EmailMessage()
                    email.email_id = id
                    email.subject = ml['subject']
                    email.date_email = ml['date']
                    email.from_email = ml['from']
                    email.body = ml['body']
                    email.type = 'mail'
                    email.user = current_user
                    email.attachments = ','.join(ya['attachments'])  # Сохраняем вложения
                    email.save()
                id += 1

        # Добавляем количество писем по типам в контекст
        context_data['len_yandex'] = len(EmailMessage.objects.filter(type='yandex'))
        context_data['len_google'] = len(EmailMessage.objects.filter(type='google'))
        context_data['len_mail'] = len(EmailMessage.objects.filter(type='mail'))
        context_data['id_user'] = current_user.id  # ID текущего пользователя

        return context_data  # Возвращаем контекст для шаблона


# Представление для добавления данных пользователя
class Add(TemplateView):
    def post(self, request):
        # Получаем данные из POST-запроса
        data = self.request.POST
        # Получаем текущего пользователя
        user = User.objects.filter(username=request.session['user']).first()

        # Обновляем логины и пароли для почтовых сервисов, если они введены
        if data['login_yandex'] != '' and data['password_yandex'] != '':
            user.login_yandex = data['login_yandex']
            user.password_yandex = data['password_yandex']
        if data['login_gmail'] != '' and data['password_gmail'] != '':
            user.login_gmail = data['login_gmail']
            user.password_gmail = data['password_gmail']
        if data['login_mail'] != '' and data['password_mail'] != '':
            user.login_mail = data['login_mail']
            user.password_mail = data['password_mail']

        user.save()  # Сохраняем изменения
        return redirect('/app/list')  # Перенаправляем на список писем
