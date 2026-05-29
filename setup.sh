#!/bin/bash
set -e

echo "=== Nexus Social — Setup ==="
echo ""

# Install dependencies
pip install django pillow

# Set up database
python manage.py makemigrations core
python manage.py migrate

# Create superuser
echo ""
echo "Creating admin user..."
echo "from core.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@nexus.com', 'admin123')" | python manage.py shell

# Seed demo data
python manage.py seed_demo

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Demo accounts:"
echo "  alice_chen  / demo1234"
echo "  dev_marcus  / demo1234"
echo "  travel_sofia / demo1234"
echo "  james_photo  / demo1234"
echo "  admin        / admin123 (admin panel)"
echo ""
echo "Run the server:"
echo "  python manage.py runserver"
echo ""
echo "Then open: http://127.0.0.1:8000"
echo ""
echo "Optional — AI recommendations:"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
echo "  python manage.py runserver"
