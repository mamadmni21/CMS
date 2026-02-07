import os

class Config:
    # 1. Remove the ?ssl_mode=... from the end of the URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'mysql+pymysql://avnadmin:AVNS_2tMx7wZmnAwBTYDM8zr@mysql-25d48b51-sepuh-cms-26.a.aivencloud.com:14721/cms_2025')
    
    # 2. Add this specific dictionary for Aiven's SSL requirement
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "ssl": {
                "ca": None  # This tells PyMySQL to use SSL without a specific file
            }
        }
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
