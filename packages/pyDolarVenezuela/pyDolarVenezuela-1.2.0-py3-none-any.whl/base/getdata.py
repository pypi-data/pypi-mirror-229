import json
from request import ask
from functionstime import get_time_zone
from util import _convert_specific_format
from util import ExchangeMonitor

def get_exchange_rate(types: list, country: str = 've'):
    url = ExchangeMonitor + "/ajax/widget-unique"
    all_monitors = {}
    all_monitors = {'datetime': get_time_zone()}
    
    for type in types:
        params = {
            "country": country,
            "type": type
        }
        response = ask(url, params=params)
        dataJson = json.loads(response)

        price = str(dataJson['price']).replace(',', '.')
        price = price.replace('.', '', 1) if price.count('.') == 2 else price
        change = f"{dataJson['percent']}" if dataJson['symbol'] == 'neutral' else f"{dataJson['percent']}"
        data = {
            "title": dataJson['name'],
            "price": price,
            "change": change
        }

        all_monitors[_convert_specific_format(dataJson['name'])] = data
        
    return all_monitors