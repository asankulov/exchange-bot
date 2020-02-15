import datetime
import os
import json
import decimal
import re

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_current_timestamp():
    return int(datetime.datetime.now().timestamp())


def convert_to_decimal_format(value):
    return decimal.Decimal(value).quantize(decimal.Decimal('1.00')).to_eng_string()


def format_decimal_values(rates):
    message = ''
    for key, value in rates.items():
        message = message + f"_{key}_: *{convert_to_decimal_format(value)}*\n"
    return message


def save_json_to_file(data, f):
    f.write(json.dumps(data))
    f.close()


def replace_and_split_by_regex(pattern, string):
    return re.split(pattern=r'\s+', string=re.sub(pattern=pattern,
                                                  repl='',
                                                  string=string).strip())


def plot_and_save(x, y, y_label, title):
    plt.clf()
    plt.gca().set_title(title)
    plt.gca().set_ylabel(y_label)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(x, y, linestyle='-', color='tab:orange', marker='o', markerfacecolor='k')
    plt.gcf().autofmt_xdate()
    plt.gcf().tight_layout()

    for x, y in zip(x, y):
        label = "{:.5f}".format(y)

        plt.annotate(label,
                     (x, y),
                     textcoords="offset points",
                     xytext=(0, 5),
                     ha='center',
                     fontsize='x-small',
                     fontweight='bold',
                     color='k')

    img_path = os.path.join(os.environ['work_dir'], f'chart-{get_current_timestamp()}.png')
    plt.savefig(img_path)
    return img_path
