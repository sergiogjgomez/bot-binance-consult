from talib import EMA, RSI, MACD
import pandas_ta as ta
import numpy as np

class Indicators:

    def __init__(self, data):
        self.data = data

        self.close = data.get('Close')
        self.open = data.get('Open')
        self.high = data.get('High')
        self.low = data.get('Low')

    def ema(self, timeperiod: int = 15):
        return EMA(self.close, timeperiod).iloc[-1]

    def rsi(self, timeperiod: int = 14):
        return RSI(self.close, timeperiod).iloc[-1]

    def macd(self, fastperiod:int = 12, slowperiod:int = 26, signalperiod:int = 9):
        _macd, macdsignal, _ = MACD(self.close, fastperiod, slowperiod, signalperiod)

        return _macd.iloc[-1], macdsignal.iloc[-1]
    
    def adx(self):
        return ta.adx(self.high, self.low, self.close)['ADX_14']
    
    def macd_lazybeer(self):
        return ta.squeeze(self.high, self.low, self.close, lazybeer=True)['SQZ_20_2.0_20_1.5']
    
    def lazybear(self):
        length = 20
        mult = 2.0
        length_KC = 20
        mult_KC = 1.5

        # Calculo de Bandas Bollinguer 
        m_avg = self.close.rolling(window=length).mean()
        m_std = self.close.rolling(window=length).std(ddof=0) * mult
        self.data['upper_BB'] = m_avg + m_std
        self.data['lower_BB'] = m_avg - m_std

        # Calculo del rango verdadero
        self.data['tr0'] = abs(self.high - self.low)
        self.data['tr1'] = abs(self.high - self.close.shift())
        self.data['tr2'] = abs(self.low - self.close.shift())
        self.data['tr'] = self.data[['tr0', 'tr1', 'tr2']].max(axis=1)

        # Calculo del keltner channel 
        range_ma = self.data['tr'].rolling(window=length_KC).mean()
        self.data['upper_KC'] = m_avg + range_ma * mult_KC
        self.data['lower_KC'] = m_avg - range_ma * mult_KC

        # Calculo 
        highest = self.high.rolling(window=length_KC).max()
        lowest = self.low.rolling(window=length_KC).min()
        mean1 = (highest + lowest) / 2
        self.data['SQZ'] = self.close - (mean1 + m_avg) / 2 
        y = np.array(range(0, length_KC))
        func = lambda x : np.polyfit(y, x, 1)[0] * (length_KC - 1) + np.polyfit(y, x, 1)[1]
        self.data['SQZ'] = self.data['SQZ'].rolling(window=length_KC).apply(func, raw=True)

        return self.data['SQZ']

    def trading_latino(self):
        return self.ema(10), self.ema(55), self.adx(), self.lazybear()
