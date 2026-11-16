from decimal import Decimal

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
)


class Alarmer:
    def __init__(
        self,
        bot: Bot,
        uid: int,
        chain: str,
        wallet: str,
        tx_hash: str,
        direction: str,
        value: Decimal
    ):
        self.bot = bot

        self.uid = uid
        self.chain = chain
        self.wallet = wallet

        self.tx_hash = tx_hash
        self.direction = direction
        self.value = value

        self.configure_explorer()

    def configure_explorer(self):
        if self.chain == "ETH":
            self.exp_url = "https://etherscan.io"
            self.exp_name = "EtherScan"
        elif self.chain == "BNB":
            self.exp_url = "https://bscscan.com"
            self.exp_name = "BscScan"
        elif self.chain == "GRAM":
            self.exp_url = "https://gram.org"
            self.exp_name = "GramOrg"
        elif self.chain == "SOL":
            self.exp_url = "https://explorer.solana.com"
            self.exp_name = "Solana Explorer"
        else:
            raise ValueError(
                f"Unsupported blockchain: {self.chain}"
            )

    def button_explorer(self):
        return f"{self.exp_url}/tx/{self.tx_hash}"

    def button_wallet(self):
        return f"{self.exp_url}/address/{self.wallet}"

    def button_message(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"🔎 {self.exp_name}",
                        url=self.button_explorer()
                    )
                ]
            ]
        )

    def build_message(self):
        if self.direction == "Sent":
            message_icon = "📤"
        elif self.direction == "Received":
            message_icon = "📥"
        elif self.direction == "Self-Transfer":
            message_icon = "🔄"
        else:
            raise ValueError(
                f"Unsupported transaction direction: {self.direction}"
            )

        return (
            f"<b>{message_icon} New transaction detected</b>\n"
            f"<blockquote>⛓️ <b>{self.chain}</b>\n"
            f"📌 Type: <b>{self.direction}</b>\n"
            f"💰 Amount: <code>{format(self.value, 'f')} "
            f"{self.chain}</code></blockquote>\n\n"
            f"<b>👛 Wallet</b>\n"
            f'<a href="{self.button_wallet()}">'
            f"{self.wallet[:6]}..."
            f"{self.wallet[-6:]}</a>\n\n"
            f"<b>🔗 Transaction hash</b>\n"
            f"<code>{self.tx_hash}</code>\n\n"
            f"<i>View full transaction details using the button below.</i>"
        )

    async def send(self):
        return await self.bot.send_message(
            chat_id=self.uid,
            text=self.build_message(),
            parse_mode=ParseMode.HTML,
            reply_markup=self.button_message(),
            link_preview_options=LinkPreviewOptions(
                is_disabled=True
            )
        )
