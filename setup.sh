#!/bin/bash
# Quick setup script for DeepProTeam Marketplace

echo "🚀 DeepProTeam Marketplace Setup"
echo "================================"

# Check Python version
python_version=$(python --version 2>&1)
echo "✓ Using: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔓 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📚 Installing dependencies..."
# pip install -r requirements.txt

# Create .env file if doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DJANGO_DEBUG=True
DB_NAME=marketplace
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
FRONTEND_URL=http://localhost:8000
DEFAULT_FROM_EMAIL=noreply@deepproteam.com
EOF
    echo "⚠️  Edit .env file before running in production!"
fi

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Initialize platform
echo "🎯 Initializing platform data..."
python manage.py init_platform

# Create superuser option
read -p "Create superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "Start development server with:"
echo "  python manage.py runserver"
echo ""
echo "Default admin credentials (if created):"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "API available at: http://localhost:8000/api/"
echo "Admin panel at: http://localhost:8000/admin/"
