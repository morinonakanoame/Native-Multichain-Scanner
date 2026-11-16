from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

import aiomysql

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_"
    )
    
    host    : str
    port    : int 
    name    : str 
    user    : str 
    password: str
    
settings = Settings()
    
async def init_pl():
    return await aiomysql.create_pool(host=settings.host,
                                      port=settings.port,
                                      db=settings.name,
                                      password=settings.password,
                                      user=settings.user)
        
async def init_db(pl):
    async with pl.acquire() as cnn:
        async with cnn.cursor() as db:
            sql = """
                CREATE TABLE IF NOT EXISTS Table_1 (
                    id        INT AUTO_INCREMENT PRIMARY KEY,
                    uid       BIGINT             NOT NULL,
                    chain     TEXT               NOT NULL,
                    wallet    TEXT               NOT NULL
                )
            """
            values = ()
            await db.execute(sql, values)

            sql = """
                CREATE TABLE IF NOT EXISTS Table_2 (
                    id        INT AUTO_INCREMENT PRIMARY KEY,
                    uid       BIGINT             NOT NULL,
                    wallet    TEXT               NOT NULL,
                    hashs     TEXT               NOT NULL
                )
            """
            values = ()
            await db.execute(sql, values)
            await cnn.commit()
