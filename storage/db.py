from aiomysql import Pool

import aiomysql
    
host = '127.0.0.1'
port = 3306
db = 'TrackBase'
user='me'
password='meme1234'

async def init_pl() -> None:
    return await aiomysql.create_pool(
        host=host,
        port=port,
        db=db,
        password=password,
        user=user
        )
        
async def init_db(
    pl: Pool
) -> Pool:
    async with pl.acquire() as cnn:
        async with cnn.cursor() as cr:
            await cr.execute("""
                                CREATE TABLE IF NOT EXISTS Table_1 (
                                    num               INT         AUTO_INCREMENT    PRIMARY KEY,
                                    u_id              BIGINT                           NOT NULL,
                                    wallet_id         TEXT                             NOT NULL
                                    )
                                    """)
            await cr.execute("""
                                CREATE TABLE IF NOT EXISTS Table_2 (
                                    num               INT         AUTO_INCREMENT    PRIMARY KEY,
                                    u_id              BIGINT                           NOT NULL,
                                    hashs             TEXT                             NOT NULL
                                    )
                                    """)
            await cnn.commit()
            await cr.close()
