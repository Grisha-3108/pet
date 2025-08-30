from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, computed_field, PostgresDsn


class Database(BaseModel):
    host: str = 'localhost'
    port: int = 5432
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



class Settings(BaseSettings):
    db: Database = Database()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file='.env',
        env_prefix='AUTH__',
        env_nested_delimiter='__'
    )

settings = Settings()
print(settings.db.sync_connection)