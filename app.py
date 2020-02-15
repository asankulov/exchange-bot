import datetime
import os

from flask import Flask, request
import telebot

import exchange
import utils

app = Flask(__name__)
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG', True)

TOKEN = os.environ['TOKEN']
WEBHOOK_BASE_URL = os.environ['WEBHOOK_BASE_URL']
webhook_url = f'{WEBHOOK_BASE_URL}/{TOKEN}'

bot = telebot.TeleBot(TOKEN)
bot.set_webhook(url=webhook_url)

exchange_rate_helper = exchange.ExchangeRate()

help_message = "_/list_ or _/lst_ - get exchange rates for base *USD*\n" \
               "_/exchange $XX to YYY_ or _/exchange XX YYY to YYY_ (where " \
               "*XX* is amount and *YYY* is currency codes) - exchange from one to another\n" \
               "_/history XXX/YYY for Z days_ (where *XXX/YYY* is base/target currencies and *Z* " \
               "is amount of days) " \
               "- get chart of last *Z* days"


@bot.message_handler(commands=['start', 'help'])
def handle_start_help_command(message):
    bot.send_message(message.chat.id, help_message, parse_mode='markdown')


@bot.message_handler(commands=['list', 'lst'])
def handle_list_command(message):
    bot.send_message(message.chat.id, exchange_rate_helper.get_exchange_rates_list_message(), parse_mode='markdown')
    # bot.send_message(message.chat.id, message.text.replace('/', ''))


@bot.message_handler(regexp=r"^/\bexchange\s+(\d+\s+[a-zA-Z]{3}|\$\d+)\s+to\s+[a-zA-Z]{3}\b")
def handle_exchange_command(message):
    message_text = utils.replace_and_split_by_regex(r"(/exchange|\s{2,})", message.text)
    target = message_text[-1].upper()

    if message_text[0].find('$') == 0:
        base = 'USD'
        amount = int(message_text[0].replace('$', ''))
    else:
        amount = int(message_text[0])
        base = message_text[1].upper()

    bot.send_message(message.chat.id, exchange_rate_helper.exchange(base, target, amount))


@bot.message_handler(regexp=r"^/\bhistory\s+[a-zA-Z]{3}/[a-zA-Z]{3}\s+for\s+\d+\s+days\b")
def handle_history_command(message):
    message_text = utils.replace_and_split_by_regex(r"(/history|\s{2,})", message.text)
    base, target = message_text[0].upper().split('/')
    today = datetime.date.today()
    days = int(message_text[-2])

    start_at = today - datetime.timedelta(days=days)
    start_at.strftime('%Y-%m-%d')
    end_at = today.strftime('%Y-%m-%d')

    img_path = exchange_rate_helper.get_history_image_path(base, target, start_at, end_at, days)
    with open(img_path, 'rb') as f:
        bot.send_photo(message.chat.id, f)
    os.remove(img_path)


@bot.message_handler(func=lambda x: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id, 'Unsupported Command')
    bot.send_message(message.chat.id, help_message, parse_mode='markdown')


@app.route(f'/{TOKEN}', methods=['POST'])
def get_updates():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "!", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
