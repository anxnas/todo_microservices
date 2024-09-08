from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from pathlib import Path
from utils.database import get_user_locale, set_user_locale

LOCALES_DIR = Path(__file__).parent.parent / 'locales'

i18n = I18n(path=LOCALES_DIR, default_locale="en", domain="bot")
_ = i18n.gettext

class CustomI18nMiddleware(SimpleI18nMiddleware):
    async def get_locale(self, event, data):
        user_id = event.from_user.id if event.from_user else None
        if user_id:
            locale = await get_user_locale(user_id)
            # Принудительно обновляем локаль в i18n объекте
            self.i18n.current_locale = locale
            return locale
        return "en"

i18n_middleware = CustomI18nMiddleware(i18n)