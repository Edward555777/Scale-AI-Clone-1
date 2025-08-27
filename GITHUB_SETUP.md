# 🚀 Настройка GitHub репозитория

## Шаги для загрузки проекта на GitHub:

### 1. Создайте репозиторий на GitHub:
- Перейдите на https://github.com/
- Нажмите "New repository"
- Название: `scale-ai-clone`
- Описание: `Data Annotation Platform - Scale AI Clone`
- Сделайте его Public
- НЕ инициализируйте с README (у нас уже есть)

### 2. Выполните эти команды в терминале:

```bash
# Добавьте удаленный репозиторий (замените YOUR_USERNAME на ваше имя пользователя)
git remote add origin https://github.com/YOUR_USERNAME/scale-ai-clone.git

# Переименуйте ветку в main (современный стандарт)
git branch -M main

# Загрузите код на GitHub
git push -u origin main
```

### 3. После загрузки ваш проект будет доступен по ссылке:
`https://github.com/YOUR_USERNAME/scale-ai-clone`

## 🔗 Постоянные ссылки на проект:

- **GitHub репозиторий**: https://github.com/YOUR_USERNAME/scale-ai-clone
- **Документация**: https://github.com/YOUR_USERNAME/scale-ai-clone/blob/main/README.md
- **Issues**: https://github.com/YOUR_USERNAME/scale-ai-clone/issues

## 📋 Что включено в репозиторий:

✅ Полный Django проект
✅ Все модели и представления
✅ Шаблоны и статические файлы
✅ Документация (README.md)
✅ Requirements.txt
✅ .gitignore для Python/Django

## 🎯 Следующие шаги:

1. Загрузите код на GitHub
2. Настройте GitHub Pages (опционально)
3. Добавьте CI/CD (GitHub Actions)
4. Настройте автоматическое развертывание
