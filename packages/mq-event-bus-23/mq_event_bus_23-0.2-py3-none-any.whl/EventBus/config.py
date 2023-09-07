from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseSettings, validator

ENV_FILEPATH = Path(__file__).parent.parent.parent.joinpath(".env.example")


class RabbitmqConfig(BaseSettings):
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    AMPQ_URI: Optional[str] = None

    @validator("AMPQ_URI", pre=True)
    def assemble_ampq_connection(
            cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return "ampq://{{user}}:{{password}}@{{host}}:{{port}}/" \
            .replace('{{user}}', values.get('RABBITMQ_USER')) \
            .replace('{{password}}', values.get('RABBITMQ_PASSWORD')) \
            .replace('{{host}}', values.get('RABBITMQ_HOST')) \
            .replace('{{port}}', values.get('RABBITMQ_PORT'))

    class Config:
        case_sensitive = True
        env_file = "../.env"


def get_rabbitmq_config() -> RabbitmqConfig:
    return RabbitmqConfig()
