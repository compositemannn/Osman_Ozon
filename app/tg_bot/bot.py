from aiogram import Bot
from app.infrastructure.config import settings 

bot = Bot(token=settings.TG_BOT_TOKEN)

async def send_return_notification(item_name: str, posting_number: str):
    text = (
        f"Возврат товара\n\n"
        f"Товар: {item_name}\n"
        f"Отправление: {posting_number}"
    )
    try:
        await bot.send_message(chat_id=settings.TG_CHAT_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        # чтобы вебхук Ozon не падал, если отвалился Telegram
        print(f"Ошибка отправки в ТГ: {e}")