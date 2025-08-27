#!/usr/bin/env python
"""
Database initialization script for Scale AI Clone
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scale_ai_platform.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import execute_from_command_line

def init_database():
    """Initialize the database with required data"""
    print("🚀 Initializing Scale AI Clone database...")
    
    # Run migrations
    print("📦 Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✅ Migrations created successfully")
    except Exception as e:
        print(f"⚠️ Warning creating migrations: {e}")
    
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations applied successfully")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        return
    
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        print("👤 Creating admin user...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Admin user created: admin / admin123")
    else:
        print("✅ Admin user already exists")
    
    # Create demo user if it doesn't exist
    if not User.objects.filter(username='demo').exists():
        print("👤 Creating demo user...")
        User.objects.create_user(
            username='demo',
            email='demo@example.com',
            password='demo123'
        )
        print("✅ Demo user created: demo / demo123")
    else:
        print("✅ Demo user already exists")
    
    print("🎉 Database initialization complete!")

if __name__ == '__main__':
    init_database()
