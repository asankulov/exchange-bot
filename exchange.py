from http.client import HTTPSConnection

from utils import *

os.environ['work_dir'] = os.path.dirname(os.path.abspath(__file__))


class ExchangeRate:
    def __init__(self):
        self.api_resource = HTTPSConnection(host='api.exchangeratesapi.io')
        if not os.path.exists(os.path.join(os.environ['work_dir'], 'rates.json')):
            f = open(os.path.join(os.environ['work_dir'], 'rates.json'), 'w')
            data = self.get_exchange_rates_list_for_usd()
            save_json_to_file({'rates': data['rates'], 'timestamp': get_current_timestamp()}, f)

    def fetch(self, path):
        self.api_resource.request('GET', path)
        return self.api_resource.getresponse()

    def get_json_response(self, path):
        return json.loads(self.fetch(path).read())

    def get_exchange_rates_list_for_usd(self):
        return self.get_json_response('/latest?base=USD')

    def get_exchange_rates_for_base_and_symbol(self, base, to):
        return self.get_json_response(f'/latest?base={base}&symbols={to}')

    def get_exchange_rates_history(self, base, to, start_at, end_at):
        return self.get_json_response(f'/history?base={base}&symbols={to}&start_at={start_at}&end_at={end_at}')

    def get_exchange_rates_list_message(self):
        f = open(os.path.join(os.environ['work_dir'], 'rates.json'), 'r')
        data_loaded_from_file = json.loads(f.read())
        f.close()

        f = open(os.path.join(os.environ['work_dir'], 'rates.json'), 'w')
        expiration_time = 10 * 60 * 1000
        last_timestamp = int(data_loaded_from_file['timestamp'])
        current_timestamp = get_current_timestamp()

        if current_timestamp - last_timestamp < expiration_time:
            data_loaded_from_file['timestamp'] = current_timestamp
            save_json_to_file(data_loaded_from_file, f)

            return format_decimal_values(data_loaded_from_file['rates'])

        data_loaded_from_api = self.get_exchange_rates_list_for_usd()
        rates = data_loaded_from_api['rates']
        save_json_to_file({'rates': rates, 'timestamp': current_timestamp}, f)

        return format_decimal_values(rates)

    def exchange(self, base, target, amount):
        data_loaded_from_api = self.get_exchange_rates_for_base_and_symbol(base, target)
        if 'rates' in data_loaded_from_api:
            return convert_to_decimal_format(data_loaded_from_api['rates'][target] * amount)
        return 'Wrong format'

    def get_history_image_path(self, base, target, start_at, end_at, days):
        data_loaded_from_api = self.get_exchange_rates_history(base, target, start_at, end_at)
        rates = data_loaded_from_api['rates']
        if len(rates) == 0:
            return None

        x = []
        y = []
        for key in sorted(rates.keys()):
            x.append(datetime.datetime.strptime(key, '%Y-%m-%d').date())
            y.append(rates[key][target])

        return plot_and_save(x, y, target, f'{base} to {target} exchange rates in last {days} days')
