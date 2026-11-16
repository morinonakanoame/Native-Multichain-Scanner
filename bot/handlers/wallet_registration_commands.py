from aiogram.types import (
    Message,
    CallbackQuery
)

from aiogram.fsm.context import FSMContext

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from aiogram.enums import (
    ChatAction, 
    ParseMode
)

from aiogram import (
    F,
    Router,
)

from validators import (
    valid_string_eth,
    valid_string_bnb,
    valid_string_sol,
    valid_string_ton
)

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiomysql import Pool

import asyncio

router = Router()

states = {
    "getting_eth": {
        "blockchain": "ETH"
    },
    "getting_bnb": {
        "blockchain": "BNB"
    },
    "getting_sol": {
        "blockchain": "SOL"
    },
    "getting_gram": {
        "blockchain": "GRAM"
    }
}


def build_button_to_back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='‹ Back',
                        callback_data="button_to_main_menu"
                    )
                ],
            ]
        )
@router.callback_query(F.data.startswith("chain:"))
async def handler_chains(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    if callback.data == "chain:button_for_eth":
        text = (
            "<b>📥 Add an ETH address</b>\n\n"
            "<blockquote>"
            "⛓️ Network: <code>ETH</code>\n"
            "📝 Required: a valid ETH wallet address"
            "</blockquote>\n\n"
            "<i>Send the address in your next message. It will be validated before being saved.</i>"
            )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='‹ Back',
                            callback_data="button_to_main_menu"
                            )
                        ],
                    ]
                )
            )
        await state.set_state("getting_eth")
    elif callback.data == "chain:button_for_bnb":
        text = (
            "<b>📥 Add a BNB address</b>\n\n"
            "<blockquote>"
            "⛓️ Network: <code>BNB</code>\n"
            "📝 Required: a valid BNB wallet address"
            "</blockquote>\n\n"
            "<i>Send the address in your next message. It will be validated before being saved.</i>"
            )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state("getting_bnb")
    elif callback.data == "chain:button_for_sol":
        text = (
            "<b>📥 Add a SOL address</b>\n\n"
            "<blockquote>"
            "⛓️ Network: <code>SOL</code>\n"
            "📝 Required: a valid SOL wallet address"
            "</blockquote>\n\n"
            "<i>Send the address in your next message. It will be validated before being saved.</i>"
            )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state("getting_sol")
    elif callback.data == "chain:button_for_gram":
        text = (
            "<b>📥 Add a GRAM address</b>\n\n"
            "<blockquote>"
            "⛓️ Network: <code>GRAM</code>\n"
            "📝 Required: a valid GRAM wallet address"
            "</blockquote>\n\n"
            "<i>Send the address in your next message. It will be validated before being saved.</i>"
            )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state("getting_gram")

@router.message(StateFilter(*states), F.text)
async def handler_registration(
    message: Message,
    state: FSMContext,
    pl: Pool
)-> None:
    uid = message.from_user.id
    status = await state.get_state()
    if status == "getting_eth":
        wallet_address = message.text
        validation = await asyncio.to_thread(
            valid_string_eth,
            wallet_address
            )   
        await message.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=uid
            )
        if validation is False:
            status_message = await message.answer(text="⌛️")
            text = (
                "<b>❌ Address validation failed</b>\n\n"
                "<blockquote>"
                "⛓️ Network: <code>ETH</code>\n"
                "📊 Status: <code>Invalid address</code>"
                "</blockquote>\n\n"
                "<i>Check that the address is complete and belongs to ETH, then send it again.</i>"
            )
            await status_message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=build_button_to_back_menu()
            )
        elif validation is True:
            if 'getting_eth' in states:
                getting_eth = states['getting_eth']
            if 'blockchain' in getting_eth:
                blockchain = getting_eth['blockchain'] 
            async with pl.acquire() as cnn:
                async with cnn.cursor() as cr:
                    sql = "SELECT wallet FROM Table_1 WHERE uid = %s AND chain = %s AND wallet = %s"
                    values = (uid, blockchain, wallet_address)
                    await cr.execute(sql, values)
                    result = await cr.fetchone()
                    await cnn.commit()
                    status_message = await message.answer(text="⌛️")
                    if result is None:
                        sql = "INSERT INTO Table_1 (uid, chain, wallet) VALUES (%s, %s, %s)"
                        values = (uid, blockchain, wallet_address)
                        await cr.execute(sql, values)
                        await cnn.commit()
                        text = (
                            "<b>✅ Address added successfully</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Tracking status: <code>Active</code>"
                            "</blockquote>\n\n"
                            "<i>The address is now available in Wallets and can be removed at any time.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
                    else:
                        text = (
                            "<b>⚠️ Address already tracked</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Status: <code>Already saved</code>"
                            "</blockquote>\n\n"
                            "<i>No duplicate entry was created. You can manage this address in Wallets.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )   
                        await state.clear()
    elif status == "getting_bnb":
        wallet_address = message.text
        validation = await asyncio.to_thread(
            valid_string_bnb,
            wallet_address
        )
        await message.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=uid
            )
        if validation is False:
            status_message = await message.answer(text="⌛️")
            text = (
                "<b>❌ Address validation failed</b>\n\n"
                "<blockquote>"
                "⛓️ Network: <code>BNB</code>\n"
                "📊 Status: <code>Invalid address</code>"
                "</blockquote>\n\n"
                "<i>Check that the address is complete and belongs to BNB, then send it again.</i>"
            )
            await status_message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=build_button_to_back_menu()
            )
        elif validation is True:
            if 'getting_bnb' in states:
                getting_bnb = states['getting_bnb']
            if 'blockchain' in getting_bnb:
                blockchain = getting_bnb['blockchain'] 
            async with pl.acquire() as cnn:
                async with cnn.cursor() as cr:
                    sql = "SELECT wallet FROM Table_1 WHERE uid = %s AND chain = %s AND wallet = %s"
                    values = (uid, blockchain, wallet_address)
                    await cr.execute(sql, values)
                    result = await cr.fetchone()
                    await cnn.commit()
                    
                    status_message = await message.answer(text="⌛️")
                    if result is None:
                        sql = "INSERT INTO Table_1 (uid, chain, wallet) VALUES (%s, %s, %s)"
                        values = (uid, blockchain, wallet_address)
                        await cr.execute(sql, values)
                        await cnn.commit()
                        text = (
                            "<b>✅ Address added successfully</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Tracking status: <code>Active</code>"
                            "</blockquote>\n\n"
                            "<i>The address is now available in Wallets and can be removed at any time.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
                    else:
                        text = (
                            "<b>⚠️ Address already tracked</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Status: <code>Already saved</code>"
                            "</blockquote>\n\n"
                            "<i>No duplicate entry was created. You can manage this address in Wallets.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
    elif status == "getting_sol":
        wallet_address = message.text
        validation = await asyncio.to_thread(
            valid_string_sol,
            wallet_address
        )
        await message.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=uid
            )
        if validation is False:
            status_message = await message.answer(text="⌛️")
            text = (
                "<b>❌ Address validation failed</b>\n\n"
                "<blockquote>"
                "⛓️ Network: <code>SOL</code>\n"
                "📊 Status: <code>Invalid address</code>"
                "</blockquote>\n\n"
                "<i>Check that the address is complete and belongs to SOL, then send it again.</i>"
            )
            await status_message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=build_button_to_back_menu()
            )
        elif validation is True:
            if 'getting_sol' in states:
                getting_sol = states['getting_sol']
            if 'blockchain' in getting_sol:
                blockchain = getting_sol['blockchain'] 
            async with pl.acquire() as cnn:
                async with cnn.cursor() as cr:
                    sql = "SELECT wallet FROM Table_1 WHERE uid = %s AND chain = %s AND wallet = %s"
                    values = (uid, blockchain, wallet_address)
                    await cr.execute(sql, values)
                    result = await cr.fetchone()
                    await cnn.commit()
                    
                    status_message = await message.answer(text="⌛️")
                    if result is None:
                        sql = "INSERT INTO Table_1 (uid, chain, wallet) VALUES (%s, %s, %s)"
                        values = (uid, blockchain, wallet_address)
                        await cr.execute(sql, values)
                        await cnn.commit()
                        text = (
                            "<b>✅ Address added successfully</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Tracking status: <code>Active</code>"
                            "</blockquote>\n\n"
                            "<i>The address is now available in Wallets and can be removed at any time.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
                    else:
                        text = (
                            "<b>⚠️ Address already tracked</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Status: <code>Already saved</code>"
                            "</blockquote>\n\n"
                            "<i>No duplicate entry was created. You can manage this address in Wallets.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
    elif status == "getting_gram":
        wallet_address = message.text
        validation = await asyncio.to_thread(
            valid_string_ton,
            wallet_address
        )
        await message.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=uid
            )
        if validation is False:
            status_message = await message.answer(text="⌛️")
            text = (
                "<b>❌ Address validation failed</b>\n\n"
                "<blockquote>"
                "⛓️ Network: <code>GRAM</code>\n"
                "📊 Status: <code>Invalid address</code>"
                "</blockquote>\n\n"
                "<i>Check that the address is complete and belongs to GRAM, then send it again.</i>"
            )
            await status_message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=build_button_to_back_menu()
            )
        elif validation is True:
            if 'getting_gram' in states:
                getting_gram = states['getting_gram']
            if 'blockchain' in getting_gram:
                blockchain = getting_gram['blockchain'] 
            async with pl.acquire() as cnn:
                async with cnn.cursor() as cr:
                    sql = "SELECT wallet FROM Table_1 WHERE uid = %s AND chain = %s AND wallet = %s"
                    values = (uid, blockchain, wallet_address)
                    await cr.execute(sql, values)
                    result = await cr.fetchone()
                    await cnn.commit()
                    
                    status_message = await message.answer(text="⌛️")
                    if result is None:
                        sql = "INSERT INTO Table_1 (uid, chain, wallet) VALUES (%s, %s, %s)"
                        values = (uid, blockchain, wallet_address)
                        await cr.execute(sql, values)
                        await cnn.commit()
                        text = (
                            "<b>✅ Address added successfully</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Tracking status: <code>Active</code>"
                            "</blockquote>\n\n"
                            "<i>The address is now available in Wallets and can be removed at any time.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
                    else:
                        text = (
                            "<b>⚠️ Address already tracked</b>\n\n"
                            "<blockquote>"
                            f"⛓️ Network: <code>{blockchain}</code>\n"
                            f"📍 Address: <code>{wallet_address}</code>\n"
                            "📊 Status: <code>Already saved</code>"
                            "</blockquote>\n\n"
                            "<i>No duplicate entry was created. You can manage this address in Wallets.</i>"
                        )
                        await status_message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=build_button_to_back_menu()
                        )
                        await state.clear()
