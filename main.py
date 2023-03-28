from binance.spot import Spot
import pandas as pd

import utils.config as config
from utils.strategy import Indicators
from utils.errors import limit_error


class BotBinance:
    '''
    Bot para binance que permite automatizar las compras y ventas en el mercado Spot.
    '''

    __api_key = config.API_KEY
    __api_secret = config.API_SECRET_KEY
    binance_client = Spot(api_key=__api_key, api_secret=__api_secret)

    def __init__(self, pair: str, interval: str):
        '''
        Args:
            pair (str): the trading pair
            interval (str): the interval of candle, e.g 1s, 1m, 5m, 1h, 1d, etc.
        '''
        self.pair = pair.upper()
        self.interval = interval
        self.symbol = self.pair.removesuffix("USDT")

    def _request(self, method: str, parameters: dict = None):
        try:
            response = getattr(self.binance_client, method)
            return response() if parameters is None else response(**parameters)
        except: 
            print(f'El método: {method} ha fallado.\nParametros: {parameters}\n\n')
        
        
    def binance_account(self) -> dict:
        '''
        Devuelve las metricas y balances asociados a la cuenta
        '''
        return self._request('account')

    def cryptocurrencies(self) -> list[dict]:
        '''
        Devuelve una lista con todas las criptomodenas en la cuenta 
        que tengan un saldo positivo
        '''
        return [crypto for crypto in self.binance_account().get("balances") if float(crypto.get("free")) > 0]
    
    def symbol_price(self, pair: str = None):
        '''
        Devuelve el precio actual para un determinado par cripto

        Arg:
            pair (str): par cripto a determinar el precio
        '''
        pair = self.pair if pair is None else pair

        return float(self._request('ticker_price', {'symbol': pair.upper()}).get('price'))
    
    def candlesticks(self, limit: int = 200) -> pd.DataFrame:
        '''
        Devuelve la información de la vela
        '''
        candle = pd.DataFrame(self._request('klines', {'symbol': self.pair,
                                                       'interval': self.interval,
                                                       'limit': limit
                                                       }),
                              columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'],
                              dtype=float)
        
        return candle[['Open time', 'Close time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    

if __name__ == '__main__':

    pair : str = input('\nIntroduce el par que deseas evaluar (ejemplo: btcusdt): ')
    interval : str = input('Introduce el intervalo de la vela japones (ejemplo: 4h): ')
    limit_consult = input('Por defecto se recopila 200 velas, deseas modificarlo? (Y/N): ')
    limit_consult = limit_consult.upper()

    if limit_consult == 'Y':
        limit = limit_error('Introduce la cantidad de velas que quieres recopilar (max 500): ')
    else:
        limit = 200


    while limit > 500 or limit < 0:
        limit = limit_error('Limite inválido! Por favor ingrese un limite correcto (número entero entre 0 y 500): ')

    try: 
            
        bot = BotBinance(pair, interval)
        indicador = Indicators(bot.candlesticks(limit=200))
        ema10, ema55, adx, lazybear = indicador.trading_latino()

        print('\nIndicadores:\n')
        print(f'EMA10: {ema10:.3f}\nEMA55: {ema55:.3f}\nADX: {adx.iloc[-1]:.3f}\nLAZYBEAR: {lazybear.iloc[-1]:.3f}\n')

        
        actual_price = bot.symbol_price()

        if (actual_price > ema10 and
            actual_price > ema55 and 
            adx.iloc[-1] > adx.iloc[-2] and 
            lazybear[-1] > lazybear[-2] and 
            adx.iloc[-1] > 25 and 
            ema10 > ema55):

            print(f'Condiciones para la alza del par {bot.pair}\n')

        else:
            print(f'No hay condiciones significativas para la alza del par {bot.pair}\n')
    
    except:
        print('ERROR! Par o Intervalo incorrecto, por favor vuelve a intentarlo')