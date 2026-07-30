import os

from dotenv import load_dotenv

load_dotenv()

class Settings:

    def __init__(self):
        self.user = os.getenv("db_user")
        self.user_host = os.getenv("db_host")
        self.user_password = os.getenv("db_pass")
        self.db_name = os.getenv("db_name")
        self.db_port = os.getenv("db_port","3306")