# Deployment Guide for DigitalOcean

## Prerequisites
- DigitalOcean Droplet (Ubuntu 20.04 or 22.04 recommended)
- MongoDB installed and running (or MongoDB Atlas connection string)
- Domain name (optional)

## Step-by-Step Deployment

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install MongoDB (if using local MongoDB)
# Or skip this if using MongoDB Atlas
sudo apt install mongodb -y
```

### 2. Create Application User

```bash
# Create a non-root user for the application
sudo adduser --disabled-password --gecos "" appuser

# Add user to sudo group (optional)
sudo usermod -aG sudo appuser

# Switch to appuser
su - appuser
```

### 3. Clone/Copy Your Application

```bash
# If using Git
git clone <your-repo-url> onlyflashcards
cd onlyflashcards

# OR manually copy your files via SCP:
# From your local machine:
# scp -r /path/to/onlyflashcards.com/* appuser@your-server-ip:/home/appuser/onlyflashcards/
```

### 4. Set Up Python Virtual Environment

```bash
cd ~/onlyflashcards  # or wherever you cloned it

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add your configuration:
```
SECRET_KEY=your-secure-secret-key-here-generate-one-with-openssl-rand-hex-32
MONGODB_URI=mongodb://localhost:27017/
# OR for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=flashcard_app
```

Generate a secure secret key:
```bash
openssl rand -hex 32
```

### 6. Test Your Application Locally

```bash
# Make sure MongoDB is running (if using local MongoDB)
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Test the app
python app.py
# Or with Gunicorn:
gunicorn -c gunicorn_config.py wsgi:app
```

### 7. Create Systemd Service

```bash
# Switch back to root or use sudo
sudo nano /etc/systemd/system/onlyflashcards.service
```

Add the following content:

```ini
[Unit]
Description=OnlyFlashcards Flask Application
After=network.target

[Service]
User=appuser
Group=appuser
WorkingDirectory=/home/appuser/onlyflashcards
Environment="PATH=/home/appuser/onlyflashcards/venv/bin"
ExecStart=/home/appuser/onlyflashcards/venv/bin/gunicorn -c gunicorn_config.py wsgi:app

Restart=always

[Install]
WantedBy=multi-user.target
```

### 8. Enable and Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable onlyflashcards

# Start the service
sudo systemctl start onlyflashcards

# Check status
sudo systemctl status onlyflashcards

# View logs
sudo journalctl -u onlyflashcards -f
```

### 9. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Enable firewall
sudo ufw enable
```

### 10. Set Up Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/onlyflashcards
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/onlyflashcards /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 11. Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot will automatically configure Nginx and set up auto-renewal
```

### 12. Update Nginx Config for HTTPS (if using SSL)

Nginx will be automatically updated by Certbot, but here's a reference:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Useful Commands

### Service Management
```bash
# Restart the application
sudo systemctl restart onlyflashcards

# Stop the application
sudo systemctl stop onlyflashcards

# View logs
sudo journalctl -u onlyflashcards -f

# View last 100 lines of logs
sudo journalctl -u onlyflashcards -n 100
```

### Application Updates
```bash
# Pull latest code (if using Git)
cd ~/onlyflashcards
git pull

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart the service
sudo systemctl restart onlyflashcards
```

### MongoDB (if using local MongoDB)
```bash
# Start MongoDB
sudo systemctl start mongodb

# Stop MongoDB
sudo systemctl stop mongodb

# Check MongoDB status
sudo systemctl status mongodb

# Enable MongoDB on boot
sudo systemctl enable mongodb
```

## Troubleshooting

### Application not starting
```bash
# Check service status
sudo systemctl status onlyflashcards

# Check logs for errors
sudo journalctl -u onlyflashcards -n 50

# Check if port 5000 is in use
sudo netstat -tulpn | grep 5000
```

### Permission issues
```bash
# Make sure appuser owns the application directory
sudo chown -R appuser:appuser /home/appuser/onlyflashcards
```

### MongoDB connection issues
```bash
# Test MongoDB connection
mongo --eval "db.version()"

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

## Production Checklist

- [ ] Changed SECRET_KEY in .env to a secure random value
- [ ] MongoDB is accessible and connection string is correct
- [ ] Firewall is configured
- [ ] Nginx is configured as reverse proxy
- [ ] SSL certificate is installed (Let's Encrypt)
- [ ] Application service is running and enabled on boot
- [ ] Logs are being monitored
- [ ] Backup strategy for database is in place

