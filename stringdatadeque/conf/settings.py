from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "StringDataDeque"
    debug: bool = False
