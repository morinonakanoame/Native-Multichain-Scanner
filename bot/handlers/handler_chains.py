from aiogram.types import CallbackQuery

from aiogram.fsm.context import FSMContext

from aiogram.enums import (
    ChatAction, 
    ParseMode
)

from aiogram import (
    F,
    Router,
)

from keyboard.keyboards import build_button_to_back_menu

from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data.startswith("chain:"))
async def handler_chains(
    call: CallbackQuery,
    state: FSMContext
) -> None:
    chat_id = call.from_user.id
    
    await call.bot.send_chat_action(
        action=ChatAction.TYPING,
        chat_id=chat_id
    )
    if call.data == "chain:button_for_eth":
        action = await state.get_data()
        msg = action.get('action')
        
        text = (
            f"<b>Good!</b>\n\n"
            f"Now, send me your the ETH address which you wanna add!"
            )
        await call.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state(
            "getting_eth"
        )
    elif call.data == "chain:button_for_sol":
        action = await state.get_data()
        msg = action.get('action')
        
        text = (
            f"<b>Good!</b>\n\n"
            f"Now, send me your the SOL address which you wanna add!"
            )
        await call.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state(
            "getting_sol"
        )
    elif call.data == "chain:button_for_bnb":
        action = await state.get_data()
        msg = action.get('action')
        
        text = (
            f"<b>Good!</b>\n\n"
            f"Now, send me your the BNB address which you wanna add!"
            )
        await call.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state(
            "getting_bnb"
        )
    elif call.data == "chain:button_for_gram":
        action = await state.get_data()
        msg = action.get('action')
        
        text = (
            f"<b>Good!</b>\n\n"
            f"Now, send me your the GRAM address which you wanna add!"
            )
        await call.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state(
            "getting_gram"
        )
