from aiogram import Router

from bot.base_commands import router as menu_router
from bot.handlers.menu_commands import router as wallet_menu_router
from bot.handlers.registration_commands import router as wallet_add_router
from bot.handlers.delete_commands import router as wallet_delete_router

router = Router()

router.include_routers(
    menu_router,
    wallet_menu_router,
    wallet_add_router,
    wallet_delete_router
)
