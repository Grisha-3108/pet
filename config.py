from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (BaseModel, 
                      computed_field, 
                      PostgresDsn, 
                      Field)


class Database(BaseModel):
    host: str = 'localhost'
    port: int = Field(ge=0, le=65535, default=5432)
    username: str = 'admin'
    password: str = 'admin'
    name: str = 'auth'
    sslmode: str = 'disable' #disable require verify-ca verify-full 
    isolation_level: str = 'READ COMMITTED' #or REPEATABLE READ or SERIALIZABLE

    @computed_field
    def async_connection(self) -> PostgresDsn:
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}'
    
    @computed_field
    def sync_connection(self) -> PostgresDsn:
        return f'postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}'
    

class AccessToken(BaseModel):
    access_token_expire: timedelta = timedelta(days=1)
    private_key: str = 'keys/private.pem'
    public_key: str = 'keys/public.pem'


class EmailServer(BaseModel):
    host: str = 'localhost'
    port: int = Field(ge=0, le=65535, default=587)
    username: str | None = None
    password: str | None = None
    starttls: bool = False
    use_tls: bool = True


class Settings(BaseSettings):
    db: Database = Database()
    auth_prefix: str = '/auth'
    token: AccessToken = AccessToken()
    email: EmailServer = EmailServer()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file='.env',
        env_prefix='AUTH__',
        env_nested_delimiter='__'
    )

settings = Settings()