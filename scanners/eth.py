import aiohttp
import asyncio
import os

from decimal import Decimal

from aiogram import Bot
from aiomysql.pool import Pool

from web3 import Web3 as w

from alarmer import Alarmer

server = os.environ["eth_server"]
interval = 12
    
def normalize_address(address):
    if not isinstance(address, str):
        return None
    elif isinstance(address, str):
        return w.to_checksum_address(address)
    else:
        return None

async def scanner(
    pl: Pool,
    bot: Bot
):
    async with aiohttp.ClientSession(headers={
                                             "Content-Type": "application/json"
                                             }) as session:
        while True:
            block_number_request = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }

            try:
                async with session.post(
                    url=server,
                    json=block_number_request
                ) as rspc:
                    if rspc.status == 200:
                        rspc_data = await rspc.json()
                    elif rspc.status == 429:
                        raise asyncio.TimeoutError(
                            "Server rate limit exceeded while fetching "
                            "the latest block number (HTTP 429)"
                        )
                    elif rspc.status != 200:
                        raise aiohttp.ClientConnectionError(
                            f"Server returned HTTP {rspc.status} while "
                            "fetching the latest block number"
                        )
            except asyncio.TimeoutError as error:
                print(f"Could not fetch the latest block number: "
                      f"{error}")
                await asyncio.sleep(5)
                continue
            except aiohttp.ClientError as error:
                print(f"Request for the latest block number failed: "
                      f"{error}")
                continue

            if "result" not in rspc_data:
                continue

            block_number = rspc_data["result"]
            block_request = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [block_number, True],
                "id": 1
            }

            try:
                async with session.post(
                    url=server,
                    json=block_request
                ) as response:
                    if response.status == 200:
                        block_response_data = await response.json()
                    elif response.status == 429:
                        raise asyncio.TimeoutError(
                            f"Server rate limit exceeded while fetching "
                            f"block {block_number} (HTTP 429)"
                        )
                    elif response.status != 200:
                        raise aiohttp.ClientConnectionError(
                            f"Server returned HTTP {response.status} "
                            f"while fetching block {block_number}"
                        )
            except asyncio.TimeoutError as error:
                print(f"Could not fetch block {block_number}: "
                      f"{error}")
                await asyncio.sleep(5)
                continue
            except aiohttp.ClientError as error:
                print(f"Request for block {block_number} failed: "
                      f"{error}")
                continue

            if "result" not in block_response_data:
                continue
            block_data = block_response_data["result"]
            if "transactions" not in block_data:
                continue
            transactions = block_data["transactions"]

            async with pl.acquire() as cnn:
                async with cnn.cursor() as db:
                    sql = ("SELECT id, uid, wallet FROM Table_1 WHERE chain = %s")
                    chain = "ETH"
                    values = (chain,)
                    await db.execute(sql, values)
                    tracked_wallets = await db.fetchall()
                    await cnn.commit()

                    for transaction in transactions:
                        if "to" in transaction:
                            recipient_address = normalize_address(
                                transaction["to"]
                            )
                        if "from" in transaction:
                            sender_address = normalize_address(
                                transaction["from"]
                            )

                        for note_id, uid, wallet in tracked_wallets:
                            if recipient_address == wallet and sender_address == wallet:
                                direction = "Self-Transfer"
                            elif recipient_address == wallet:
                                direction = "Received"
                            elif sender_address == wallet:
                                direction = "Sent"
                            else:
                                continue

                            if "hash" not in transaction:
                                continue

                            transaction_hash = transaction["hash"]

                            sql = ("SELECT 1 FROM Table_2 WHERE uid = %s AND wallet = %s AND hashs = %s")
                            values = (uid, wallet, transaction_hash)
                            await db.execute(sql, values)
                            saved_hash = await db.fetchone()
                            await cnn.commit()

                            if saved_hash is None:
                                sql = ("INSERT INTO Table_2 (uid, wallet, hashs) VALUES (%s, %s, %s)")
                                values = (uid, wallet, transaction_hash)
                                await db.execute(sql, values)
                                await cnn.commit()
                            else:
                                continue
                            if "value" in transaction:
                                transaction_value = transaction["value"]
                                amount = (
                                    Decimal(int(transaction_value, 16))
                                    / Decimal(10**18)
                                )
                            else:
                                continue

                            await Alarmer(
                                bot=bot,
                                uid=uid,
                                chain=chain,
                                wallet=wallet,
                                tx_hash=transaction_hash,
                                direction=direction,
                                value=amount
                            ).send()

            await asyncio.sleep(interval)
