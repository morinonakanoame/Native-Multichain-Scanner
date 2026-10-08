from aiogram import (
    F,
    Router
)

from aiogram.enums import (
    ParseMode,
    ChatAction
)

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from aiomysql.pool import Pool

router = Router()

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
    
@router.message(StateFilter("delete_wallet"), F.text)
async def handler_delete_address_input(
    message: Message,
    state: FSMContext,
    pl: Pool,
) -> None:
    user_id = message.from_user.id
    wallet_address = message.text
    async with pl.acquire() as cnn:
        async with cnn.cursor() as cr:
            await cr.execute("SELECT wallet_id FROM Table_1 WHERE u_id = %s AND wallet_id = %s", (user_id, wallet_address))
            rows = await cr.fetchall()
            count = len(rows)
            if count == 1:
                await cr.execute("DELETE FROM Table_1 WHERE u_id = %s AND wallet_id = %s", (user_id, wallet_address))
                await cnn.commit()
    await message.bot.send_chat_action(
        action=ChatAction.TYPING,
        chat_id=user_id
    )
    if count == 0:
        text = (
            "<b>❌ Address not found</b>\n\n"
            "<blockquote>"
            f"📍 Address: <code>{wallet_address}</code>\n"
            "📊 Status: <code>Not tracked</code>"
            "</blockquote>\n\n"
            "<i>Check the address and send it again, or return to the main menu.</i>"
        )
        await message.answer(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
    elif count == 1:
        status = await message.answer(text="⏳")
        text = (
            "<b>✅ Address removed successfully</b>\n\n"
            "<blockquote>"
            f"📍 Address: <code>{wallet_address}</code>\n"
            "🗑️ Tracking status: <code>Removed</code>"
            "</blockquote>\n\n"
            "<i>This address is no longer included in your tracking list.</i>"
        )
        await status.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.clear()
    else:
        await state.set_state("confirm_delete_wallet")
        await state.update_data(wallet=wallet_address)
        
        status = await message.answer(text="⏳")
        text = (
            "<b>⚠️ Multiple matches found</b>\n\n"
            "<blockquote>"
            f"📍 Address: <code>{wallet_address}</code>\n"
            f"⛓️ Matching entries: <code>{count}</code>\n"
            "🗑️ Action: delete this address from every matching network"
            "</blockquote>\n\n"
            "<b>Do you want to continue?</b>\n"
            "<i>Choose an option below.</i>"
        )
        await status.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Yes",
                            callback_data=f"confirmed:button_yes",
                        ),
                        InlineKeyboardButton(
                            text="❌ No",
                            callback_data=f"confirmed:button_no",
                        ),
                    ]
                ]
            )
        )

@router.callback_query(StateFilter("confirm_delete_wallet"), F.data.startswith("confirmed:"))
async def handler_delete_matches_confirmation(
    callback: CallbackQuery,
    state: FSMContext,
    pl: Pool,
) -> None:
    if callback.data == "confirmed:button_yes":
        user_id = callback.from_user.id
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                wallet_address = await state.get_value("wallet")
                await cr.execute("DELETE FROM Table_1 WHERE u_id = %s AND wallet_id = %s", (user_id, wallet_address))
                deleted_count = cr.rowcount
                await cnn.commit()
        await callback.message.edit_text(text="⏳")
        text = (
            "<b>✅ Matching entries removed</b>\n\n"
            "<blockquote>"
            f"🗑️ Deleted entries: <code>{deleted_count}</code>\n"
            "📊 Tracking status: <code>Removed</code>"
            "</blockquote>\n\n"
            "<i>Use the button below to return to the main menu.</i>"
        )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.clear()
    elif callback.data == "confirmed:button_no":
        text = (
            "<b>↩️ Deletion cancelled</b>\n\n"
            "<blockquote>"
            "🔒 No entries were removed.\n"
            "📊 Your tracking list remains unchanged."
            "</blockquote>\n\n"
            "<i>You can safely return to the main menu.</i>"
        )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.clear()

@router.callback_query(F.data.startswith("action:untrack_all_action"))
async def handler_delete_all_confirmation(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    text = (
        "<b>⚠️ Delete all tracked addresses?</b>\n\n"
        "<blockquote>"
        "🗑️ Action: remove every saved address\n"
        "🔕 Result: all address tracking will be stopped\n"
        "💡 You can add the addresses again later"
        "</blockquote>\n\n"
        "<b>This action affects your entire tracking list.</b>\n"
        "<i>Do you want to continue?</i>"
    )
    await callback.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Yes",
                        callback_data=f"confirmed:button_yes",
                    ),
                    InlineKeyboardButton(
                        text="❌ No",
                        callback_data=f"confirmed:button_no",
                    ),
                ]
            ]
        )
    )
    await state.set_state("confirm_delete_all_wallet")
    
@router.callback_query(StateFilter("confirm_delete_all_wallet"))
async def handler_confirmation_delete_all(
    callback: CallbackQuery,
    state: FSMContext,
    pl: Pool
) -> None:
    if callback.data == "confirmed:button_yes":
        u_id = callback.from_user.id
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                await cr.execute("DELETE FROM Table_1 WHERE u_id = %s", (u_id,))
                deleted_count = cr.rowcount
                if deleted_count > 0:
                    await cnn.commit()
        await callback.message.edit_text(text="⏳")
        if deleted_count > 0:
            text = (
                "<b>✅ Tracking list cleared!</b>\n\n"
                "<blockquote>"
                f"🗑️ Deleted addresses: <code>{deleted_count}</code>\n"
                "📊 Saved addresses: <code>0</code>"
                "</blockquote>\n\n"
                "<i>You can add a new address from the main menu at any time.</i>"
            )
        else:
            text = (
                "<b>📭 Nothing to delete</b>\n\n"
                "<blockquote>"
                "👛 Tracked addresses: <code>0</code>\n"
                "🗑️ No changes were made to your list"
                "</blockquote>\n\n"
                "<i>Add an address first, and it will appear in your tracking list.</i>"
            )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.clear()
    elif callback.data == "confirmed:button_no":
        text = (
            "<b>↩️ Deletion cancelled!</b>\n\n"
            "<blockquote>"
            "🔒 No addresses were removed.\n"
            "📊 Your tracking list remains unchanged."
            "</blockquote>\n\n"
            "<i>Use the button below to return to the main menu.</i>"
        )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.clear()
