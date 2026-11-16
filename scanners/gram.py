import aiohttp
import asyncio
import base64
import os

from decimal import Decimal

from aiogram import Bot
from aiomysql import Pool

from tonsdk.utils import (
    Address, 
    InvalidAddressError
)

from alarmer import Alarmer

interval = 1.25
server = os.environ["gram_server"]

def normalize_address(wallet):
    if not wallet:
        return None

    try:
        return Address(wallet).to_string(
            is_user_friendly=False
        )
    except InvalidAddressError:
        return None


def friendly_wallet(wallet):
    if not wallet:
        return None

    try:
        return Address(wallet).to_string(
            is_user_friendly=True,
            is_url_safe=True,
            is_bounceable=False,
            is_test_only=False
        )
    except InvalidAddressError:
        return None


def normalize_hash(value):
    try:
        decoded_hash = base64.b64decode(value)
    except ValueError:
        return None

    if len(decoded_hash) == 32:
        hex_hash = decoded_hash.hex()

        if len(hex_hash) == 64:
            return hex_hash


def normalize_amount(amount):
    try:
        return Decimal(int(amount)) / Decimal(10**9)
    except ValueError, TypeError:
        return None


async def scanner(
    pool: Pool,
    bot: Bot
):
    async with aiohttp.ClientSession(headers={
                                             "X-API-Key": server
                                             }) as session:
        while True:
            async with pool.acquire() as cnn:
                async with cnn.cursor() as db:
                    sql = ("SELECT uid, wallet FROM Table_1 WHERE chain = %s")
                    chain = "GRAM"
                    values = (chain,)
                    await db.execute(sql, values)
                    tracked_wallets = await db.fetchall()
                    await cnn.commit()

                for uid, wallet in tracked_wallets:
                    wallet_address = normalize_address(wallet)
                    if wallet_address is None:
                        continue

                    request_params = {
                        "account": wallet_address,
                        "limit": 3,
                        "sort": "desc"
                    }
                    try:
                        async with session.get(url="https://toncenter.com/api/v3/transactions",
                                               params=request_params) as response:
                            if response.status == 200:
                                response_data = await response.json()
                            elif response.status == 429:
                                raise asyncio.TimeoutError(
                                    "Server rate limit exceeded while "
                                    f"fetching transactions for wallet {wallet_address} "
                                    "(HTTP 429)"
                                )
                            elif response.status != 200:
                                raise aiohttp.ClientConnectionError(
                                    f"Server returned HTTP {response.status} "
                                    "while fetching transactions for wallet "
                                    f"{wallet_address}"
                                )
                    except asyncio.TimeoutError as error:
                        print(f"Could not fetch transactions for wallet "
                            f"{wallet_address}: {error}")
                        await asyncio.sleep(5)
                        continue
                    except aiohttp.ClientError as error:
                        print(f"Transaction request failed for wallet "
                            f"{wallet_address}: {error}")
                        await asyncio.sleep(5)
                        continue

                    if "transactions" in response_data:
                        transactions = response_data["transactions"]

                    if isinstance(transactions, list):
                        async with cnn.cursor() as db:
                            for transaction in transactions:
                                if "hash" in transaction:
                                    encoded_hash = transaction["hash"]
                                    transaction_hash = normalize_hash(encoded_hash)
                                    
                                    if transaction_hash is not None:
                                        sql = ("SELECT 1 FROM Table_2 WHERE uid = %s AND wallet = %s AND hashs = %s")
                                        values = (uid, wallet_address, transaction_hash)
                                        await db.execute(sql, values)
                                        saved_hash = await db.fetchone()
                                        await cnn.commit()

                                        if saved_hash is None:
                                            if "in_msg" in transaction:
                                                incoming_message = transaction["in_msg"]
                                                if len(incoming_message) > 1:
                                                    incoming_source = normalize_address(
                                                        incoming_message["source"]
                                                    )
                                                    incoming_destination = normalize_address(
                                                        incoming_message["destination"]
                                                    )
                                                    incoming_amount = normalize_amount(
                                                        incoming_message["value"]
                                                    )

                                                    if incoming_source == wallet_address and incoming_destination == wallet_address:
                                                        direction = "Self-Transfer"
                                                    elif incoming_source != wallet_address and incoming_destination == wallet_address:
                                                        direction = "Received"
                                                    amount = incoming_amount

                                            if "out_msgs" in transaction:
                                                outgoing_messages = transaction["out_msgs"]
                                                if len(outgoing_messages) > 0:
                                                    outgoing_source = normalize_address(
                                                        outgoing_messages[0]["source"]
                                                    )
                                                    outgoing_destination = normalize_address(
                                                        outgoing_messages[0]["destination"]
                                                    )
                                                    outgoing_amount = normalize_amount(
                                                        outgoing_messages[0]["value"]
                                                    )

                                                    if outgoing_source == wallet_address and outgoing_destination != wallet_address:
                                                        direction = "Sent"
                                                    elif outgoing_destination == wallet_address and outgoing_source == wallet_address:
                                                        continue
                                                    amount = outgoing_amount

                                            await Alarmer(
                                                bot=bot,
                                                uid=uid,
                                                chain=chain,
                                                wallet=friendly_wallet(wallet_address),
                                                tx_hash=transaction_hash,
                                                direction=direction,
                                                value=amount
                                            ).send()

                                            sql = ("INSERT INTO Table_2 (uid, wallet, hashs) VALUES (%s, %s, %s)")
                                            values = (uid, wallet_address, transaction_hash)
                                            await db.execute(sql, values)
                                            await cnn.commit()

                    await asyncio.sleep(interval)
