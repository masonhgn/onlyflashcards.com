"""WSGI entry point for Gunicorn"""
from app import app

application = app

if __name__ == "__main__":
    app.run()

