import os
from dotenv import load_dotenv

RUNNING_IN_AWS = os.getenv("AWS_EXECUTION_ENV") is not None

if not RUNNING_IN_AWS:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PALAGINA_USERNAME = os.getenv("PALAGINA_USERNAME")
PALAGINA_PASSWORD = os.getenv("PALAGINA_PASSWORD")
PALAGINA_LOGIN_URL = os.getenv("PALAGINA_LOGIN_URL")
PALAGINA_LISTA_CONFIG_URL = os.getenv("PALAGINA_LISTA_CONFIG_URL")
STATE_PATH = os.getenv("STATE_PATH", "palagina_state.json")
PALAGINA_CREATE_LOCK_NAME = os.getenv("PALAGINA_CREATE_LOCK_NAME", "palagina_nuovo_progetto_create")
LOCK_LEASE_SECONDS = int(os.getenv("LOCK_LEASE_SECONDS", "120"))
RELEASE_URL = os.getenv("RELEASE_URL", "http://127.0.0.1:8000/locks/release")