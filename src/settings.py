from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


load_dotenv()


class Settings(BaseSettings):
    sqlalchemy_database_uri: str

    openai_api_key: str

    redis_uri: str

    pinecone_api_key: str
    pinecone_index_name: str
    pinecone_env_name: str

    jwt_secret_key: str
    jwt_algorithm: str

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()
