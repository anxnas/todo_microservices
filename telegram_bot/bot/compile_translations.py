from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

with open('locales/en/LC_MESSAGES/bot.po', 'rb') as po_file:
    catalog = read_po(po_file)

with open('locales/en/LC_MESSAGES/bot.mo', 'wb') as mo_file:
    write_mo(mo_file, catalog)

with open('locales/ru/LC_MESSAGES/bot.po', 'rb') as po_file:
    catalog = read_po(po_file)

with open('locales/ru/LC_MESSAGES/bot.mo', 'wb') as mo_file:
    write_mo(mo_file, catalog)