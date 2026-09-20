from aiogram import (
    types,
    Router
)

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

from aiomysql import Pool

from keyboard.keyboards import build_button_to_back_menu

import aiomysql

router = Router()
    
def build_keyboards_with_chains() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Ethereum',
                        callback_data="button_for_eth"
                    ),
                    InlineKeyboardButton(
                        text='Solana',
                        callback_data="button_for_sol"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='Binance Chain',
                        callback_data="button_for_bnb"
                    ),
                    InlineKeyboardButton(
                        text='Gram',
                        callback_data="button_for_ton"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='‹ Back',
                        callback_data="button_to_main_menu"
                    )
                ],
            ]
        )   
    
@router.callback_query()
async def handler_actions_message(
    call: CallbackQuery,
    state: FSMContext,
    pl: Pool
) -> None:
    u_id = call.from_user.id
    if call.data == 'track_row_action':
        await call.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=u_id
            )
        
        action = await state.get_data()
        msg = action.get('action')
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s", (u_id,))
                
                rows = await cr.fetchall()
        if len(rows) < 3:
            text = f"Select blockchain which you need will use:"
            answer = await call.bot.edit_message_text(
                chat_id=u_id,
                message_id=msg,
                text=text,
                reply_markup=build_keyboards_with_chains()
            )
            await state.update_data(
                action=answer.message_id
            )
        else:
            text = 'You already added many addresses, will delete one of them!'
            await call.bot.edit_message_text(
                chat_id=u_id,
                message_id=msg,
                text=text,
                reply_markup=build_button_to_back_menu()
            )
            await state.clear()
    elif call.data == 'untrack_row_action':
        await call.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=u_id
            )
        
        action = await state.get_data()
        msg = action.get('action')
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s", (u_id,))
                rows = await cr.fetchall()
        if len(rows) > 0:
            i = "\n".join(
                row[0]
                for row in rows
            )
            text = f"Send me address which you wanna delete!"
            answer = await call.bot.edit_message_text(
                chat_id=u_id,
                message_id=msg,
                text=text,
                reply_markup=build_button_to_back_menu()
            )
            await state.update_data(
                action=answer.message_id
            )
        else:
            text = 'Right now you dont have addresses!'
            answer = await call.bot.edit_message_text(
                chat_id=u_id,
                message_id=msg,
                text=text,
                reply_markup=build_button_to_back_menu()
            )
            await state.update_data(
                action=answer.message_id
            )
    elif call.data == "untrack_all_rows_action":
        await call.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=u_id
            )
        action = await state.get_data()
        msg = action.get('action')
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s", (u_id,))
                
                rows = await cr.fetchall()
        if len(rows) < 1:
            text = "You haven't got adresses, will add them!"
            answer = await call.bot.edit_message_text(
                chat_id=u_id,
                message_id=msg,
                text=text,
                reply_markup=build_button_to_back_menu()
            )
            await state.update_data(
                action=answer.message_id
            )
        else:
            text = "Are you sure that wanna delete all addresses?"
            answer = await call.bot.edit_message_text(
                chat_id=u_id,
                message_id=msg,
                text=text,
                reply_markup=build_button_to_back_menu()
            )
            await state.update_data(
                action=answer.message_id
            ) 
