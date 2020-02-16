import os
from functools import wraps

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


def send_pre_message(func):
    @wraps(func)
    def decorated(message_from_user, *args, **kwargs):
        new_message = bot.send_message(message_from_user.chat.id, 'Processing...', parse_mode='markdown')
        return func(message_from_user, new_message, *args, **kwargs)

    return decorated


@bot.message_handler(commands=['list', 'lst'])
@send_pre_message
def handle_list_command(message_from_user, pre_message):
    bot.edit_message_text(chat_id=message_from_user.chat.id,
                          message_id=pre_message.message_id,
                          text=exchange_rate_helper.get_exchange_rates_list_message(),
                          parse_mode='markdown')


@bot.message_handler(regexp=r"^/\bexchange\s+(\d+\s+[a-zA-Z]{3}|\$\d+)\s+to\s+[a-zA-Z]{3}\b")
@send_pre_message
def handle_exchange_command(message_from_user, pre_message):
    message_text = utils.replace_and_split_by_regex(r"(/exchange|\s{2,})", message_from_user.text)
    target = message_text[-1].upper()
    amount = int(message_text[0].replace('$', ''))
    base = 'USD' if message_text[0].find('$') == 0 else message_text[1].upper()

    bot.edit_message_text(chat_id=message_from_user.chat.id,
                          message_id=pre_message.message_id,
                          text=exchange_rate_helper.exchange(base, target, amount),
                          parse_mode='markdown')


@bot.message_handler(regexp=r"^/\bhistory\s+[a-zA-Z]{3}/[a-zA-Z]{3}\s+for\s+\d+\s+days\b")
@send_pre_message
def handle_history_command(message_from_user, pre_message):
    message_text = utils.replace_and_split_by_regex(r"(/history|\s{2,})", message_from_user.text)
    base, target = message_text[0].upper().split('/')
    days = int(message_text[-2])

    start_at = utils.get_given_days_ago(days)
    end_at = utils.get_formatted_date()

    err, path_or_message = exchange_rate_helper.get_history_image(base, target, start_at, end_at, days)
    if err:
        bot.edit_message_text(chat_id=message_from_user.chat.id,
                              message_id=pre_message.message_id,
                              text=path_or_message,
                              parse_mode='markdown')
    else:
        with open(path_or_message, 'rb') as f:
            bot.send_photo(message_from_user.chat.id, f)
            bot.delete_message(chat_id=message_from_user.chat.id,
                               message_id=pre_message.message_id)
        os.remove(path_or_message)


@bot.message_handler(func=lambda x: True)
def handle_all_messages(message_from_user):
    help_message = "_/list_ or _/lst_ - get exchange rates for base *USD*\n" \
                   "_/exchange $XX to YYY_ or _/exchange XX YYY to YYY_ (where " \
                   "*XX* is amount and *YYY* is currency codes) - exchange from one to another\n" \
                   "_/history XXX/YYY for Z days_ (where *XXX/YYY* is base/target currencies and *Z* " \
                   "is amount of days) " \
                   "- get chart of last *Z* days"
    if message_from_user.text not in ['/start', '/help']:
        bot.send_message(message_from_user.chat.id, 'Unsupported Command')
    bot.send_message(message_from_user.chat.id, help_message, parse_mode='markdown')


@app.route(f'/{TOKEN}', methods=['POST'])
def get_updates():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "!", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
