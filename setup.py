#!/usr/bin/env python3
"""
MindBridge Setup Script
This script helps set up the MindBridge mental wellness platform for development or production.
"""

import os
import sys
import subprocess
import secrets
import string

def generate_secret_key():
    """Generate a secure secret key for Django."""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for i in range(50))

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e.stderr}")
        return None

def create_env_file():
    """Create .env file if it doesn't exist."""
    if os.path.exists('.env'):
        print("📝 .env file already exists")
        return
    
    print("📝 Creating .env file...")
    secret_key = generate_secret_key()
    
    env_content = f"""# MindBridge Environment Configuration
# Generated automatically by setup script

# Core Django Settings
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=mindbridge_dev
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Optional: AI Features
# OPENAI_API_KEY=your-openai-api-key-here

# Optional: Error Tracking
# SENTRY_DSN=your-sentry-dsn-here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ .env file created successfully")

def setup_database():
    """Set up the database."""
    print("\n🗄️  Setting up database...")
    
    # Check if we can connect to PostgreSQL
    pg_check = run_command("pg_isready", "Checking PostgreSQL connection")
    
    if pg_check is None:
        print("⚠️  PostgreSQL not available. Using SQLite for development.")
        # Update .env to use SQLite
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('DB_NAME=mindbridge_dev', 'DB_NAME=db.sqlite3')
            
            with open('.env', 'w') as f:
                f.write(content)
    else:
        print("✅ PostgreSQL is available")
        # Create database if it doesn't exist
        run_command("createdb mindbridge_dev", "Creating database (ignore error if exists)")

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if os.path.exists('requirements.txt'):
        run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages")
    else:
        print("❌ requirements.txt not found")

def setup_django():
    """Set up Django application."""
    print("\n🚀 Setting up Django application...")
    
    # Make migrations
    run_command(f"{sys.executable} manage.py makemigrations", "Creating migrations")
    
    # Apply migrations
    run_command(f"{sys.executable} manage.py migrate", "Applying migrations")
    
    # Collect static files
    run_command(f"{sys.executable} manage.py collectstatic --noinput", "Collecting static files")

def create_superuser():
    """Create Django superuser."""
    print("\n👤 Creating superuser...")
    print("Please create an admin user for the Django admin interface:")
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'createsuperuser'], check=True)
        print("✅ Superuser created successfully")
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation skipped or failed")

def setup_frontend():
    """Set up frontend dependencies."""
    print("\n🎨 Setting up frontend...")
    
    # Check if Node.js is available
    node_check = run_command("node --version", "Checking Node.js")
    
    if node_check:
        npm_check = run_command("npm --version", "Checking npm")
        if npm_check:
            run_command("npm install", "Installing Node.js dependencies")
            run_command("npm run build", "Building frontend assets")
        else:
            print("⚠️  npm not available, skipping frontend build")
    else:
        print("⚠️  Node.js not available, skipping frontend setup")

def print_success_message():
    """Print success message with next steps."""
    print("\n" + "="*60)
    print("🎉 MindBridge setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Start the development server:")
    print("   python manage.py runserver")
    print("\n2. Visit your application:")
    print("   http://127.0.0.1:8000")
    print("\n3. Access the admin interface:")
    print("   http://127.0.0.1:8000/admin")
    print("\n4. For production deployment, see:")
    print("   docs/deployment.md")
    print("\n🔧 Optional next steps:")
    print("- Set up Redis for caching and real-time features")
    print("- Configure email settings for production")
    print("- Set up monitoring and logging")
    print("- Review security settings")
    print("\n🆘 Need help?")
    print("- Documentation: README.md")
    print("- Issues: https://github.com/yourusername/mindbridge/issues")
    print("- Email: support@mindbridge.com")

def main():
    """Main setup function."""
    print("🌟 Welcome to MindBridge Setup!")
    print("This script will help you set up the MindBridge mental wellness platform.")
    print("\n📋 Setup includes:")
    print("- Environment configuration")
    print("- Database setup")
    print("- Python dependencies")
    print("- Django application setup")
    print("- Frontend assets")
    print("\n" + "="*60)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create environment file
    create_env_file()
    
    # Install dependencies
    install_dependencies()
    
    # Setup database
    setup_database()
    
    # Setup Django
    setup_django()
    
    # Create superuser
    create_superuser()
    
    # Setup frontend
    setup_frontend()
    
    # Print success message
    print_success_message()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error message above and try again.")
        print("For help, visit: https://github.com/yourusername/mindbridge/issues")
        sys.exit(1)
