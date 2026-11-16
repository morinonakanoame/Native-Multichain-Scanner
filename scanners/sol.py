from aiogram import Bot

from aiomysql import Pool
from decimal import Decimal

from alarmer import Alarmer

import aiohttp
import asyncio

import os

server = os.environ["sol_server"]
interval = 0.2

def normalize_value(value: int):
    if isinstance(value, int):
        return Decimal(value) / Decimal(10**9)
    else:
        return None
    
async def scanner(
    pl: Pool,
    bot: Bot
    ) -> str:    
    
    async with aiohttp.ClientSession(headers={
                                     "Content-Type": "application/json"
                                     }) as ssn:
        while True:
            async with pl.acquire() as cnn:
                async with cnn.cursor() as db:
                    sql = ("SELECT uid, wallet FROM Table_1 WHERE chain = %s")
                    chain = "SOL"
                    values = (chain,)
                    await db.execute(sql, values)
                    tracked_wallets = await db.fetchall()
                    await cnn.commit()
                    
                for uid, wallet in tracked_wallets:
                    if wallet is None:
                        continue
    
                    getSignature = { "jsonrpc": "2.0",
                                    "id": 1,
                                    "method": "getSignaturesForAddress",
                                    "params": [
                                    f"{wallet}",
                                    {
                                    "commitment": "finalized",
                                    "limit": 1
                                    }
                                ]
                            }        
                    try:
                        async with ssn.post(url=server,
                                            json=getSignature) as rqst:
                            if rqst.status == 200:
                                response = await rqst.json()
                                if "result" in response:
                                    signatures = response["result"]
                                    if len(signatures) == 0:
                                        continue
                                else:
                                    continue
                                
                                if "signature" in signatures[0]:
                                    last_signature = signatures[0]["signature"]
                                else:
                                    continue
                            else:
                                raise aiohttp.ServerConnectionError(
                                    f"Server returned HTTP {rqst.status} "
                                    "while fetching transaction signatures for "
                                    f"wallet {wallet}"
                                )
                    except aiohttp.ClientError as error:
                        print("Failed to fetch transaction signatures "
                              f"for wallet {wallet}: {error}")
                        continue
                    
                    request = {"jsonrpc": "2.0",
                               "id": 1,
                                "method": "getTransaction",
                                "params": [
                                f"{last_signature}",
                                {
                                    "commitment": "confirmed",
                                    "maxSupportedTransactionVersion": 1,
                                    "encoding": "jsonParsed"
                                    }
                                ]
                                }
                    try:
                        async with ssn.post(url=server,
                                            json=request) as rqst:
                            if rqst.status == 200:
                                response = await rqst.json()
                                if "result" in response:
                                    result = response['result']
                                    if result is None:
                                        continue
                                else:
                                    continue
                                
                                if "transaction" in result:
                                    transaction = result['transaction']
                                else:
                                    continue
                            else:
                                raise aiohttp.ServerConnectionError(
                                    f"Server returned HTTP {rqst.status} "
                                    f"while fetching transaction {last_signature}"
                                )
                    except aiohttp.ClientError as error:
                        print(f"Failed to fetch transaction "
                              f"{last_signature}: {error}")
                        continue
                    if "message" in transaction:
                        message = transaction["message"]
                        if "instructions" in message:
                            instructions = message["instructions"]
                            
                            async with cnn.cursor() as db:        
                                sql = ("SELECT 1 FROM Table_2 WHERE uid = %s AND wallet = %s AND hashs = %s")
                                values = (uid, wallet, last_signature)
                                await db.execute(sql, values)
                                saved_hash = await db.fetchone()
                                await cnn.commit()

                                if saved_hash is None:
                                    instruction = instructions[-1]
                                    if "parsed" in instruction:
                                        parsed = instruction["parsed"]
                                        if "info" in parsed:
                                            info = parsed["info"]
                        
                                            if info.get("source") == wallet and info.get("destination") == wallet:
                                                direction = "Self-Transfer"
                                                amount = normalize_value(info["lamports"])
                                            elif info.get("source") == wallet:
                                                direction = "Sent"
                                                amount = normalize_value(info["lamports"])
                                            elif info.get("destination") == wallet:
                                                direction = "Received"
                                                amount = normalize_value(info["lamports"])
                                            else:
                                                continue
                                            
                                            await Alarmer(
                                                bot=bot,
                                                uid=uid,
                                                chain=chain,
                                                wallet=wallet,
                                                tx_hash=last_signature,
                                                direction=direction,
                                                value=amount
                                            ).send()
                                            
                                            sql = ("INSERT INTO Table_2 (uid, wallet, hashs) VALUES (%s, %s, %s)")
                                            values = (uid, wallet, last_signature)
                                            await db.execute(sql, values)
                                            await cnn.commit()

                    await asyncio.sleep(interval)
