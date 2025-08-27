#!/bin/bash

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin / admin123')
else:
    print('✅ Admin user already exists')
"

# Create demo user
echo "👤 Creating demo user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    User.objects.create_user('demo', 'demo@example.com', 'demo123')
    print('✅ Demo user created: demo / demo123')
else:
    print('✅ Demo user already exists')
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🎉 Build process completed!"
