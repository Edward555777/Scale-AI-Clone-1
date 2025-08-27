# 🚀 Развертывание Scale AI Clone

## Вариант 1: Railway (Рекомендуется - Бесплатно)

### Шаги развертывания:

1. **Перейдите на Railway**: https://railway.app/
2. **Войдите через GitHub**
3. **Нажмите "New Project"**
4. **Выберите "Deploy from GitHub repo"**
5. **Выберите ваш репозиторий**: `Edward555777/Scale-AI-Clone-1`
6. **Railway автоматически определит Django проект**

### Настройка переменных окружения:

В Railway Dashboard добавьте эти переменные:

```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-app-name.railway.app
```

### Получение ссылки:

После развертывания Railway даст вам ссылку вида:
`https://your-app-name.railway.app`

---

## Вариант 2: Render (Бесплатно)

### Шаги развертывания:

1. **Перейдите на Render**: https://render.com/
2. **Войдите через GitHub**
3. **Нажмите "New +" → "Web Service"**
4. **Подключите ваш GitHub репозиторий**
5. **Настройте:**
   - **Name**: scale-ai-clone
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn scale_ai_platform.wsgi:application`

### Переменные окружения:

```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-app-name.onrender.com
```

---

## Вариант 3: Heroku (Платно)

### Шаги развертывания:

1. **Установите Heroku CLI**
2. **Выполните команды:**

```bash
# Логин в Heroku
heroku login

# Создайте приложение
heroku create your-app-name

# Добавьте PostgreSQL
heroku addons:create heroku-postgresql:mini

# Настройте переменные
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key

# Разверните
git push heroku main

# Запустите миграции
heroku run python manage.py migrate
```

---

## 🔗 После развертывания:

### Ваша публичная ссылка будет:
- **Railway**: `https://your-app-name.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **Heroku**: `https://your-app-name.herokuapp.com`

### Что можно делать:
✅ Регистрироваться и входить
✅ Создавать проекты аннотации
✅ Загружать файлы
✅ Аннотировать данные
✅ Экспортировать результаты

### Админ панель:
- URL: `https://your-domain.com/admin/`
- Логин: `admin`
- Пароль: `admin123`

---

## 🛠️ Локальная разработка:

```bash
# Клонировать
git clone https://github.com/Edward555777/Scale-AI-Clone-1.git

# Установить зависимости
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Запустить
python manage.py runserver
```

---

## 📞 Поддержка:

Если возникнут проблемы с развертыванием:
1. Проверьте логи в панели управления
2. Убедитесь, что все переменные окружения настроены
3. Проверьте, что база данных подключена
