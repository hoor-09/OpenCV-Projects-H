import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'focusguard-secret-key'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    SESSION_TYPE = 'filesystem'