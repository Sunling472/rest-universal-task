import logging
from functools import lru_cache
from dataclasses import dataclass

from environs import Env

LOG = logging.getLogger(__name__)


@dataclass
class DBConfig:
    username: str
    password: str
    host: str
    port: int
    database: str
    db_echo_log: bool

    def __post_init__(self) -> None:
        self.url: str = (
            'postgresql+asyncpg://{username}:{password}'
            '@{host}:{port}/{db}'.format(
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                db=self.database
            )
        )


@dataclass
class ApiConfig:
    title: str
    description: str
    api_v1: str
    debug: bool


@dataclass
class Config:
    db: DBConfig
    api: ApiConfig


@lru_cache()
def get_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        db=DBConfig(
            username=env.str('POSTGRES_USER'),
            password=env.str('POSTGRES_PASSWORD'),
            host=env.str('POSTGRES_HOST'),
            port=env.str('POSTGRES_PORT'),
            database=env.str('POSTGRES_DB'),
            db_echo_log=env.bool('DB_ECHO_LOG')
        ),
        api=ApiConfig(
            title=env.str('API_TITLE'),
            description=env.str('API_DESCRIPTION'),
            api_v1=env.str('API_V1_PATH'),
            debug=env.bool('DEBUG')
        )
    )
