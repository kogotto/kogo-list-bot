from dotenv import load_dotenv
import os


def _read_secret(name: str) -> str | None:
    return os.getenv(name)


def _read_critical_secret(name: str) -> str:
    secret = _read_secret(name)
    if not secret:
        raise Exception(f'There is no {name} in env. See .env.example')
    return secret


def _read_db_name() -> str:
    return _read_critical_secret('KOGO_LIST_BOT_DB_NAME')


def _read_db_username() -> str:
    return _read_critical_secret('KOGO_LIST_BOT_DB_USERNAME')


def _read_db_password() -> str:
    return _read_critical_secret('KOGO_LIST_BOT_DB_PASSWORD')


def _read_db_host() -> str:
    return _read_critical_secret('KOGO_LIST_BOT_DB_HOST')


def load() -> None:
    load_dotenv()


def read_db_config():
    return {
        'database': _read_db_name(),
        'user': _read_db_username(),
        'password': _read_db_password(),
        'host': _read_db_host(),
    }


def read_token() -> str:
    return _read_critical_secret('KOGO_LIST_BOT_API_TOKEN')
