from aiogram import (
    types,
    Router
)

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from aiogram.enums import (
    ChatAction, 
    ParseMode
)

from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router() 
        
@router.message(Command('start', prefix='/!.'))
async def handler_greet_message(
    message: types.Message,
    state: FSMContext
) -> None:
    await state.clear()
    
    uid = message.from_user.id
    await message.bot.send_chat_action(
        action=ChatAction.TYPING,
        chat_id=uid
    )
    text = (
        "<b>👋 Welcome to Wallet Tracker</b>\n\n"
        "<blockquote>"
         "⛓️ Supported networks: <code>4</code>\n"
        "👛 Wallet limit: <code>5 addresses</code>\n"
        "🔔 Service: activity monitoring for saved wallets"
        "</blockquote>\n\n"
        "<i>Choose an action below to manage your tracking list.</i>"
        )
    action = await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='➕ Add',
                        callback_data="action:track_action"
                    ),
                    InlineKeyboardButton(
                        text='🗑️ Remove',
                        callback_data="action:untrack_action"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='📒 My Wallets',
                        callback_data="action:list_action"
                    )
                ]
            ]
        )
    )
    await state.update_data(action=action.message_id)

@router.callback_query(lambda menu: menu.data == "button_to_main_menu")
async def handler_back_menu_message(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    await state.clear()
    text = (
        "<b>🏠 Welcome to back a main menu of Tracker!</b>\n\n"
        "<blockquote>"
        "⛓️ Supported networks: <code>4</code>\n"
        "👛 Wallet limit: <code>5 addresses</code>\n"
        "🔔 Service: activity monitoring for saved wallets"
        "</blockquote>"
        "\n\n<i>Choose an action below to manage your tracking list.</i>"
        )
    action = await callback.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='➕ Add',
                        callback_data="action:track_action"
                    ),
                    InlineKeyboardButton(
                        text='🗑️ Remove',
                        callback_data="action:untrack_action"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='📒 My Wallets',
                        callback_data="action:list_action"
                    )
                ]
            ]
        )
        )
    await state.update_data(action=action.message_id)
