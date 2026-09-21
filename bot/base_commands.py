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

def build_keyboards_to_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Track',
                    callback_data="action:track_row_action"
                ),
                InlineKeyboardButton(
                    text='Untrack',
                    callback_data="action:untrack_row_action"
                )
            ],
            [
                InlineKeyboardButton(
                    text='Wallets',
                    callback_data="action:untrack_all_rows_action"
                )
            ]
        ]
    )
        
    
@router.message(Command('start', prefix='/!.'))
async def handler_greet_message(
    msg: types.Message,
    state: FSMContext
) -> None:
    await state.clear()
    
    chat_id = msg.from_user.id
    await msg.bot.send_chat_action(
        action=ChatAction.TYPING,
        chat_id=chat_id
    )
    text = (f"<b>👋 Hello, this is a Tracker.</b>\n\n"
            f"🕵🏻 I can track wallets, let's get started!")
    action = await msg.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_keyboards_to_main_menu()
    )
    await state.update_data(
        action=action.message_id
    )

@router.callback_query(lambda menu: menu.data == "button_to_main_menu")
async def handler_back_menu_message(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    chat_id = call.from_user.id
    
    await call.bot.send_chat_action(
            action=ChatAction.TYPING,
            chat_id=chat_id
            )
        
    action = await state.get_data()
    msg = action.get('action')
    
    text = (f"<b>Hello, this is a Tracker.</b>\n\n"
            f"🕵🏻 I can track wallets, let's get started!")
                                 
    await call.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=build_keyboards_to_main_menu()
            )
