import json
import os
from datetime import datetime
from http.client import HTTPSConnection

import utils

os.environ['work_dir'] = os.path.dirname(os.path.abspath(__file__))


class BadRequestException(Exception):
    pass


class ExchangeRate:
    def __init__(self):
        self.api_resource = HTTPSConnection(host='api.exchangeratesapi.io')
        if not os.path.exists(os.path.join(os.environ['work_dir'], 'rates.json')):
            f = open(os.path.join(os.environ['work_dir'], 'rates.json'), 'w')
            data = self.get_exchange_rates_response_for_usd()
            utils.save_json_to_file({'rates': data['rates'], 'timestamp': utils.get_current_timestamp()}, f)

    def fetch(self, path):
        self.api_resource.request('GET', path)
        response = self.api_resource.getresponse()
        if response.status == 400:
            response.close()
            raise BadRequestException
        return response.read()

    def get_json_response(self, path):
        return json.loads(self.fetch(path))

    def get_exchange_rates_response_for_usd(self):
        return self.get_json_response('/latest?base=USD')

    def get_exchange_rates_response_for_base_and_target(self, base, to):
        return self.get_json_response(f'/latest?base={base}&symbols={to}')

    def get_exchange_rates_history_response_for_base_and_target(self, base, to, start_at, end_at):
        return self.get_json_response(f'/history?base={base}&symbols={to}&start_at={start_at}&end_at={end_at}')

    def get_exchange_rates_list_message(self):

        data_loaded_from_file = utils.read_data_from_file_as_json(os.path.join(os.environ['work_dir'], 'rates.json'))

        expiration_time = 10 * 60 * 1000
        last_timestamp = int(data_loaded_from_file['timestamp'])
        current_timestamp = utils.get_current_timestamp()

        f = open(os.path.join(os.environ['work_dir'], 'rates.json'), 'w')

        if current_timestamp - last_timestamp < expiration_time:
            data_loaded_from_file['timestamp'] = current_timestamp
            utils.save_json_to_file(data_loaded_from_file, f)

            return utils.format_decimal_values(data_loaded_from_file['rates'])

        try:
            data_loaded_from_api = self.get_exchange_rates_response_for_usd()
        except BadRequestException:
            return 'Something went wrong.'

        rates = data_loaded_from_api['rates']
        utils.save_json_to_file({'rates': rates, 'timestamp': current_timestamp}, f)

        return utils.format_decimal_values(rates)

    def exchange(self, base, target, amount):
        try:
            data_loaded_from_api = self.get_exchange_rates_response_for_base_and_target(base, target)
            return utils.convert_to_decimal_format(data_loaded_from_api['rates'][target] * amount)
        except BadRequestException:
            return 'Wrong currency code.'

    def get_history_image(self, base, target, start_at, end_at, days):
        try:
            data_loaded_from_api = self.get_exchange_rates_history_response_for_base_and_target(base, target, start_at, end_at)
        except BadRequestException:
            return True, 'Wrong currency code.'

        rates = data_loaded_from_api['rates']
        if len(rates) == 0:
            return True, 'No exchange rate data is available for the selected currency.'

        x, y = [], []
        for key in sorted(rates.keys()):
            x.append(datetime.strptime(key, '%Y-%m-%d').date())
            y.append(rates[key][target])

        return False, utils.plot_and_save(x, y, target, f'{base} to {target} exchange rates in last {days} days')
