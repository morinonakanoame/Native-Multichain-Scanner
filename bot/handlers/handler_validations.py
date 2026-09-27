from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.enums import (
    ChatAction, 
    ParseMode
)

from aiogram import (
    F,
    types,
    Router,
)

from keyboard.keyboards import build_button_to_back_menu
from validators.eth import valid_string_eth
from validators.bnb import valid_string_bnb
from validators.sol import valid_string_sol
from validators.ton import valid_string_ton

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiomysql import Pool

import aiomysql
import asyncio

router = Router()

@router.message(StateFilter("getting_eth"), F.text)
async def handler_eth_registration(
    message: Message,
    pl: Pool
)-> None:
    chat_id = message.from_user.id
    string = message.text
    
    msg = await message.answer(
        text="⌛️"
    )
    blockchain = 'eth'
    validation = await asyncio.to_thread(
        valid_string_eth,
        string
        )
    if validation is False:
        text = (
            f"<b>❌ The address obtained does not exist.</b>\n\n"
            f"Try another one or enter the correct one."
        )
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
    elif validation is True:
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s AND blockchain = %s AND wallet_id = %s", (chat_id, blockchain, string))
                result = await cr.fetchone()
                if result is None:
                    await cr.execute("""INSERT INTO Table_1 (u_id, blockchain, wallet_id) VALUES (%s, %s, %s)""", (chat_id, blockchain, string))
                    await cnn.commit()
            
                    text = (
                        f"<b>✅ Well!</b>\n\n"
                        f"You are now tracking the address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )
                else:
                    text = ( 
                        f"❗️ You are already tracking this address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )   
                    
@router.message(StateFilter("getting_bnb"), F.text)
async def handler_bnb_registration(
    message: Message,
    state: FSMContext,
    pl: Pool
) -> None:
    chat_id = message.from_user.id
    string = message.text
    
    msg = await message.answer(
        text="⌛️"
    )
    blockchain = "bnb"
    validation = await asyncio.to_thread(
        valid_string_bnb,
        string
    )
    if validation is False:
        text = (
            f"<b>❌ The address obtained does not exist.</b>\n\n"
            f"Try another one or enter the correct one."
        )
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
    elif validation is True:
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s AND blockchain = %s AND wallet_id = %s", (chat_id, blockchain, string))
                result = await cr.fetchone()
                if result is None:
                    await cr.execute("""INSERT INTO Table_1 (u_id, blockchain, wallet_id) VALUES (%s, %s, %s)""", (chat_id, blockchain, string))
                    await cnn.commit()
                    
                    text = (
                        f"<b>✅ Well!</b>\n\n"
                        f"You are now tracking the address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )
                else:
                    text = ( 
                        f"❗️ You are already tracking this address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )

@router.message(StateFilter("getting_sol"))
async def handler_sol_registration(
    message: Message,
    state: FSMContext,
    pl: Pool
) -> None:
    chat_id = message.from_user.id
    string = message.text
    
    msg = await message.answer(
        text="⌛️"
    )
    blockchain = "sol"
    validation = await asyncio.to_thread(
        valid_string_sol,
        string
    )
    if validation is False:
        text = (
            f"<b>❌ The address obtained does not exist.</b>\n\n"
            f"Try another one or enter the correct one."
        )
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
    elif validation is True:
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s AND blockchain = %s AND wallet_id", (chat_id, blockchain, string))
                result = await cr.fetchone()
                if result is None:
                    await cr.execute("""INSERT INTO Table_1 (u_id, blockchain, wallet_id) VALUES (%s, %s, %s)""", (chat_id, blockchain, string))
                    await cnn.commit()
                    
                    text = (
                        f"<b>✅ Well!</b>\n\n"
                        f"You are now tracking the address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )
                else:
                    text = ( 
                        f"❗️ You are already tracking this address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )
                    
@router.message(StateFilter("getting_gram"))
async def handler_gram_registration(
    message: Message,
    state: FSMContext,
    pl: Pool
) -> None:
    chat_id = message.from_user.id
    string = message.text
    
    msg = await message.answer(
        text="⌛️"
    )
    blockchain = "gram"
    validation = await asyncio.to_thread(
        valid_string_ton,
        string
    )
    if validation is False:
        text = (
            f"<b>❌ The address obtained does not exist.</b>\n\n"
            f"Try another one or enter the correct one."
        )
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
    elif validation is True:
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s AND blockchain = %s and wallet_id = %s", (chat_id, blockchain, string))
                result = await cr.fetchone()
                if result is None:
                    await cr.execute("""INSERT INTO Table_1 (u_id, blockchain, wallet_id) VALUES (%s, %s, %s)""", (chat_id, blockchain, string))
                    await cnn.commit()
                    
                    text = (
                        f"<b>✅ Well!</b>\n\n"
                        f"You are now tracking the address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )
                else:
                    text = ( 
                        f"❗️ You are already tracking this address!"
                    )
                    await msg.edit_text(
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_button_to_back_menu()
                    )
