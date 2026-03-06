from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import SecretStr, computed_field, field_validator



class Setting(BaseSettings):
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: SecretStr
    ALGORITHM: str
    TOKEN_MINUTE: float
    ALLOWED_IPS: str


    @field_validator('ALLOWED_IPS', mode='after')
    @classmethod
    def ip_white_list(cls, value: str) -> list[str]:
        return [ip.strip() for ip in value.split(',')]



    @computed_field
    @property
    def db_url(self) -> str:
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}'
                f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')


    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')



settings = Setting()
