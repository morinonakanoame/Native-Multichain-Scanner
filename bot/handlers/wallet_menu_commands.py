from aiogram import (
    F,
    Router
)

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from aiomysql import Pool

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
    
@router.callback_query(F.data.startswith("action:track_action"))
async def handler_action_track(
    callback: CallbackQuery,
    state: FSMContext,
    pl: Pool
) -> None:
    uid = callback.from_user.id
    if callback.data == 'action:track_action':
        async with pl.acquire() as cnn:
            async with cnn.cursor() as cr:
                sql = "SELECT wallet FROM Table_1 WHERE uid = %s"
                values = (uid,)
                await cr.execute(sql, values)
                
                rows = await cr.fetchall()
                await cnn.commit()
        if len(rows) < 5:
            text = (
                "<b>⛓️ Select a blockchain</b>\n\n"
                "<blockquote>"
                "📌 Action: add a new wallet address\n"
                f"📊 Available slots: <code>{5 - len(rows)}</code> of <code>5</code>"
                "</blockquote>\n\n"
                "<i>Choose the network that contains the address you want to track.</i>"
            )
            answer = await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text='ETH',
                                callback_data="chain:button_for_eth"
                            ),
                            InlineKeyboardButton(
                                text='SOL',
                                callback_data="chain:button_for_sol"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text='BNB',
                                callback_data="chain:button_for_bnb"
                            ),
                            InlineKeyboardButton(
                                text='GRAM',
                                callback_data="chain:button_for_gram"
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
            )
            await state.update_data(action=answer.message_id)
        else:
            text = (
                "<b>🚫 Address limit reached</b>\n\n"
                "<blockquote>"
                f"👛 Tracked addresses: <code>{len(rows)}</code>\n"
                "📊 Maximum allowed: <code>5</code>"
                "</blockquote>\n\n"
                "<i>Remove one of your tracked addresses before adding a new one.</i>"
            )
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=build_button_to_back_menu()
            )
            await state.clear()
            
@router.callback_query(F.data.startswith("action:untrack_action"))
async def handler_action_track(
    callback: CallbackQuery,
    state: FSMContext,
    pl: Pool
) -> None:
    uid = callback.from_user.id
    async with pl.acquire() as cnn:
        async with cnn.cursor() as cr:
            sql = "SELECT wallet FROM Table_1 WHERE uid = %s"
            values = (uid,)
            await cr.execute(sql, values)
            rows = await cr.fetchall()
            await cnn.commit()
    if len(rows) == 1:
        i = "\n".join(
            row[0]
            for row in rows
        )
        text = (
            "<b>🗑️ Remove a tracked address</b>\n\n"
            "<blockquote>"
            f"👛 Saved addresses: <code>{len(rows)}</code>\n"
            "✉️ Next step: send the exact address you want to remove"
            "</blockquote>\n\n"
            "<i>You can copy the address from the Wallets section and send it here.</i>"
        )
        answer = await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.set_state("delete_wallet")
    elif len(rows) >= 2:
        text = (
            "<b>🗑️ Remove tracked addresses</b>\n\n"
            "<blockquote>"
            f"👛 Saved addresses: <code>{len(rows)}</code>\n"
            "✉️ To remove one: send its exact address\n"
            "🧹 To clear the list: use <b>Untrack All</b> below"
            "</blockquote>\n\n"
            "<i>You can copy an address from the Wallets section.</i>"
        )
        answer = await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🗑️ Remove All",
                            callback_data=f"action:untrack_all_action",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="‹ Back",
                            callback_data="button_to_main_menu"
                        )
                    ]
                ]
            )
        )
        await state.set_state("delete_wallet")
    else:
        text = (
            "<b>📭 No tracked addresses</b>\n\n"
            "<blockquote>"
            "👛 Saved addresses: <code>0</code>\n"
            "🗑️ There is currently nothing to remove"
            "</blockquote>\n\n"
            "<i>Add an address first, and it will appear in your tracking list.</i>"
        )
        answer = await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
        await state.update_data(action=answer.message_id)

@router.callback_query(F.data.startswith("action:list_action"))
async def handler_action_list(
    callback: CallbackQuery,
    pl: Pool
    ) -> None:
    uid = callback.from_user.id
    async with pl.acquire() as cnn:
        async with cnn.cursor() as cr:
            sql = "SELECT wallet, chain FROM Table_1 WHERE uid = %s"
            values = (uid,)
            await cr.execute(sql, values)
            rows = await cr.fetchall()
            await cnn.commit()
    if len(rows) < 1:
        await callback.message.edit_text(
            text=(
                "<b>📒 Your wallet list is empty</b>\n\n"
                "<blockquote>"
                "👛 Tracked addresses: <code>0</code>\n"
                "📊 Tracking status: <code>No active entries</code>"
                "</blockquote>\n\n"
                "<i>Add your first wallet from the main menu to start building the list.</i>"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
    else:
        wallet_rows = "\n".join(
            f"{number}. {wallet} - <code>{chain}</code>"
            for number, (wallet, chain) in enumerate(rows, start=1)
            )
        text = (
            "<b>📒 Your tracked wallets</b>\n\n"
            "<blockquote>"
            f"{wallet_rows}"
            "</blockquote>\n\n"
            f"<i>Total addresses: <code>{len(rows)}</code> of <code>5</code>.</i>"
        )
        await callback.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_button_to_back_menu()
        )
