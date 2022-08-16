#!/usr/local/bin/python3
import websocket, json, pprint, numpy
import ssl
from binance.client import Client
from binance.enums import *
import config
from datetime import datetime, timedelta
from email_yag import send_email_yag
from colors import bcolors

# import talib
# from talib import MA_Type


class BinanceTrades:
    def __init__(
        self,
        id_db,
        moeda,
        moeda_operacao,
        valor_negociado,
        valor_negociado_reais,
        tipo,
        data,
        data_original,
        quantidade_negociada,
        valor_total,
        cotacao_dolar,
        total_reais,
        comissao,
        comissao_moeda,
        id_order,
        id_trade,
    ):
        self.id_db = id_db
        self.moeda = moeda
        self.moeda_operacao = moeda_operacao
        self.valor_negociado = round(float(valor_negociado),5)
        self.valor_negociado_reais = round(float(valor_negociado_reais),5)
        self.tipo = tipo
        self.data = data
        self.data_original = data_original
        self.quantidade_negociada = round(float(quantidade_negociada),5)
        self.valor_total = valor_total
        self.cotacao_dolar = cotacao_dolar
        self.total_reais = round(float(total_reais),2)
        self.comissao = round(float(comissao),5)
        self.comissao_moeda = comissao_moeda
        self.id_order = id_order
        self.id_trade = id_trade

        # self.is_candle_closed = is_candle_closed
        # self.low_c = round(float(low_c), 5)
        # self.high_c = round(float(high_c), 5)
        # self.open_c = round(float(open_c), 5)
        # self.close_c = round(float(close_c), 5)

    def __str__(self):
        if self.tipo == 'BUY':
            return f"{bcolors.VERDE}{self.moeda} - Valor Negociado: {self.valor_negociado} {bcolors.FIM}"
        else:
            return f"{bcolors.VERMELHO}{self.moeda} - Valor Negociado: {self.valor_negociado} {bcolors.FIM}"
    
    @staticmethod
    def format_date(date):
        old_date = date
        format_date = old_date.strftime("%d/%m/%Y")
        format_date = format_date
        return format_date


class Trades:

    client = Client(config.API_KEY, config.API_SECRET)
    closes = []
    closes_to_stop = {}
    operations = []
    operations_test = []
    trades = []
    list_closes_after_buy = []

    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 76
    RSI_OVERSOLD = 30

    modalidade_compra = ""
    situacao_email_stop = (
        "<strong style='color:red'> Ainda não estamos comprados!!</strong>"
    )

    def __init__(
        self, symbol, time, candle, is_candle_closed, low_c, high_c, open_c, close_c
    ):
        self.symbol = symbol
        self.time = time
        self.candle = candle
        self.is_candle_closed = is_candle_closed
        self.low_c = round(float(low_c), 5)
        self.high_c = round(float(high_c), 5)
        self.open_c = round(float(open_c), 5)
        self.close_c = round(float(close_c), 5)

    def __str__(self):
        return f"{self.symbol} - Time: {self.format_date(self.time)} - Low: {self.low_c} - High: {self.high_c} - Open: {self.open_c} - Close: {self.close_c}"

    # def add_closes(self):
    #     if self.is_candle_closed is True:
    #         self.closes.append(self.close)
    #         print(f"Candle closed at: {round(float(self.candle_closed),2)}")
    #         print("\n")
    #         print(f"closes - {len(self.closes)}")
    #         print(self.closes)
    #     return self.closes

    @classmethod
    def get_trades(cls, message):
        json_message = json.loads(message)
        get_trades = cls(
            symbol=json_message["k"]["s"],
            time=json_message["E"],
            candle=json_message["k"],
            is_candle_closed=json_message["k"]["x"],
            low_c=json_message["k"]["l"],
            high_c=json_message["k"]["h"],
            open_c=json_message["k"]["o"],
            close_c=json_message["k"]["c"],
        )
        print(get_trades)
        return get_trades

    # KLINE_INTERVAL_2HOUR
    # KLINE_INTERVAL_1MINUTE
    # KLINE_INTERVAL_1DAY
    @staticmethod
    def get_closed_day_ago(symbol):
        klines_c = Trades.client.get_historical_klines(
            symbol, Client.KLINE_INTERVAL_1DAY, "360 day ago UTC-3"
        )
        filt_klines_c = klines_c
        for kline in filt_klines_c:
            close = kline[4]
            Trades.closes.append(float(close))

        filt_klines_c_stop = klines_c[:-1]
        for kline in filt_klines_c_stop:
            close = kline[4]
            datas = Trades.format_date_outsideclass(kline[0])
            price_and_date = {}
            price_and_date["date"] = datas
            price_and_date["price"] = float(close)
            Trades.closes_to_stop[f"{datas}"] = float(close)

        print(Trades.closes_to_stop)
        return Trades.closes_to_stop

    def get_fees(self, TRADE_SYMBOL):
        fees = self.client.get_trade_fee(symbol=TRADE_SYMBOL)
        taxs = fees["tradeFee"][0]
        maker = taxs["maker"]
        taker = taxs["taker"]
        self.fees = [maker, taker]
        return self.fees

    def format_date(self, date):
        not_formated_date = datetime.fromtimestamp(date / 1000)
        format_date = not_formated_date.strftime("%Y-%m-%d %H:%M:%S")
        self.format_date = format_date
        return self.format_date

    @staticmethod
    def format_date_outsideclass(date):
        not_formated_date = datetime.fromtimestamp(date / 1000)
        # format_date = not_formated_date.strftime("%Y-%m-%d %H:%M:%S")
        nd = not_formated_date + timedelta(days=1)
        format_date = nd.strftime("%Y-%m-%d")
        return format_date

    @staticmethod
    def format_date_outsideclass_resum(date):
        not_formated_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        format_date = not_formated_date.strftime("%d/%m/%Y - %H:%M:%S")
        return format_date

    # ---------------------------estratégias---------------------------

    def color_rsi(self, x):
        x = round(float(x), 2)
        if x < self.RSI_OVERSOLD:
            return f"Compra: {bcolors.VERDE}{x}{bcolors.FIM}"
        elif x > self.RSI_OVERBOUGHT:
            return f"Venda: {bcolors.VERMELHO}{x}{bcolors.FIM}"
        else:
            return x

    def get_rsi(self, rsi_period):
        np_closes = numpy.array(self.closes)
        rsi = talib.RSI(np_closes, rsi_period)
        print("Últimos 12 RSIS calculados até agora:")
        all_rsi = [self.color_rsi(x) for x in rsi[-12:]]
        for i in all_rsi:
            print(i)
        last_rsi = rsi[-1]
        print(
            f"{bcolors.VERDE}The Current RSI is:{bcolors.FIM} {self.color_rsi(last_rsi)}\n"
        )
        print(
            f"Compra se o RSI estiver abaixo de: {bcolors.VERDE}{self.RSI_OVERSOLD}{bcolors.FIM}"
        )
        print(
            f"Vende se o RSI estiver acima de: {bcolors.VERMELHO}{self.RSI_OVERBOUGHT}{bcolors.FIM}\n"
        )
        return last_rsi

    def get_last_last_rsi(self, rsi_period):
        np_closes = numpy.array(self.closes)
        rsi = talib.RSI(np_closes, rsi_period)
        last_last_rsi = rsi[-2]
        return last_last_rsi

    def get_sma(self, sma_period):
        np_closes = numpy.array(self.closes)
        sma = talib.EMA(np_closes, sma_period)
        print(f"médias móveis no momento: SMA - Periodo: {sma_period}")
        print(sma[-4:])
        last_sma = sma[-1]
        print(f"{bcolors.VERDE}The Current SMA is: {last_sma}{bcolors.FIM}")
        print("\n")
        return round(last_sma, 6)

    def get_last_last_sma(self, sma_period):
        np_closes = numpy.array(self.closes)
        sma = talib.SMA(np_closes, sma_period)
        print(f"médias móveis no momento: SMA - Periodo: {sma_period}")
        last_last_sma = sma[-2]
        print(f"{bcolors.VERDE}The Last SMA is: {last_last_sma}{bcolors.FIM}")
        print("\n")
        return round(last_last_sma, 6)

    def get_ema(self, ema_period):
        np_closes = numpy.array(self.closes)
        ema = talib.EMA(np_closes, ema_period)
        print(f"médias móveis no momento: EMA - Periodo: {ema_period}")
        print(ema[-4:])
        last_ema = ema[-1]
        print(f"{bcolors.VERDE}The Current EMA is: {last_ema}{bcolors.FIM}")
        print("\n")
        return round(last_ema, 6)

    def get_last_last_ema(self, ema_period):
        np_closes = numpy.array(self.closes)
        ema = talib.EMA(np_closes, ema_period)
        print(f"Penúltima médias móveis: EMA - Periodo: {ema_period}")
        last_last_ema = ema[-2]
        print(f"{bcolors.VERDE}The Last_Last EMA is: {last_last_ema}{bcolors.FIM}")
        print("\n")
        return round(last_last_ema, 6)

    def get_bbands(self):
        np_closes = numpy.array(self.closes)
        upper, middle, lower = talib.BBANDS(
            np_closes,
            timeperiod=5,
            nbdevup=2,
            nbdevdn=2,
            matype=talib.MA_Type.T3,
            # matype=0,
        )
        print("Ind.: matype=MA_Type.T3")
        last_lower = lower[-1]
        print(f"{bcolors.AZUL}The Current LOWER is: {last_lower}{bcolors.FIM}\n")

        last_middle = middle[-1]
        print(f"{bcolors.VERDE}The Current MIDDLE is: {last_middle}{bcolors.FIM}\n")

        last_upper = upper[-1]
        print(f"{bcolors.AZUL}The Current UPPER is: {last_upper}{bcolors.FIM}\n")
        print("\n")
        print(f"Lower: {last_lower} - Middle: {last_middle} - Upper: {last_upper}\n")

        return [round(last_lower, 6), round(last_middle, 6), round(last_upper, 6)]

    @staticmethod
    def ma_cross_up_buy(lower_ind, middle_ind, upper_ind):
        if lower_ind < middle_ind and upper_ind > middle_ind:
            print(
                f"{bcolors.VERDE}Compra pelas Médias Móveis cruzando pra cima!!{bcolors.FIM}"
            )
            Trades.modalidade_compra = "Compra pelas Médias Móveis cruzando pra cima!!"
            result = True
        else:
            result = False
        return result

    @staticmethod
    def ma_cross_down_sell(upper_ind, middle_ind, lower_ind):
        if upper_ind > middle_ind and lower_ind < middle_ind:
            print(
                f"{bcolors.VERMELHO}Venda pelas Médias Móveis cruzando pra Baixo!!{bcolors.FIM}"
            )
            Trades.modalidade_compra = "Venda pelas Médias Móveis cruzando pra Baixo!!"
            result = True
        else:
            result = False
        return result

    @staticmethod
    def rsi_cross_up_buy(last_rsi, definied_rsi):
        if last_rsi < definied_rsi:
            print(
                f"{bcolors.VERDE}Compra pelo RSI abaixo do prédefinido!!{bcolors.FIM}"
            )
            print(f"último RSI: {last_rsi} | RSI Pré-Definido: {definied_rsi}")
            Trades.modalidade_compra = f"Compra pelo RSI abaixo do prédefinido!!<br/>último RSI: {last_rsi} | RSI Pré-Definido: {definied_rsi}"
            result = True
        else:
            result = False
        return result

    @staticmethod
    def rsi_cross_down_sell(last_rsi, definied_rsi):
        if last_rsi > definied_rsi:
            print(f"{bcolors.VERDE}Venda pelo RSI upper do prédefinido!!{bcolors.FIM}")
            print(f"ültimo RSI: {last_rsi} | RSI Pré-Definido: {definied_rsi}")
            Trades.modalidade_compra = f"Venda pelo RSI upper do prédefinido!!<br/>último RSI: {last_rsi} | RSI Pré-Definido: {definied_rsi}"
            result = True
        else:
            result = False
        return result

    @staticmethod
    def stop_gain_sell(last_price, price_to_sell):
        if last_price >= price_to_sell:
            print(f"{bcolors.VERMELHO}Venda STOP GAIN!!{bcolors.FIM}")
            print(
                f"Stop Gain Atingido: {price_to_sell} | último fechamento que atingiu o STOP: {last_price}"
            )
            Trades.modalidade_compra = f"Venda STOP GAIN!! <br> Stop Gain Atingido: {price_to_sell} | último fechamento que atingiu o STOP: {last_price}"
            result = True
        else:
            result = False
        return result

    @staticmethod
    def stop_loss_sell(last_price, price_to_sell_loss):
        if last_price < price_to_sell_loss:
            print(f"{bcolors.VERMELHO}Venda STOP LOSS!!{bcolors.FIM}")
            print(
                f"Stop LOSS Atingido: {price_to_sell_loss} | último fechamento que atingiu o STOP: {last_price}"
            )
            Trades.modalidade_compra = f"Venda STOP LOSS!! <br> Stop LOSS Atingido: {price_to_sell_loss} | último fechamento que atingiu o STOP: {last_price}"
            result = True
        else:
            result = False
        return result

    def stop_gain_and_lost(self, buy_price, target_loss=3):

        if self.list_closes_after_buy:
            top_value = max(self.list_closes_after_buy)

        if self.list_closes_after_buy:
            dif_percent_price = round(float((top_value / buy_price - 1) * 100), 2)
            dif_percent_color_price = (
                f"{bcolors.VERDE}{dif_percent_price}{bcolors.FIM}"
                if dif_percent_price > 0
                else f"{bcolors.VERMELHO}{dif_percent_price}{bcolors.FIM}"
            )
            print(
                f"{bcolors.CVIOLETBG}{bcolors.AMARELO}Diferença Percentual:{bcolors.FIM} {dif_percent_color_price}"
            )

            if dif_percent_price >= target_loss:
                current_percentual_stop = (dif_percent_price * 0.7) / 100
                print(
                    f"Diferença Percentual maior que o limite de {target_loss}%: {dif_percent_price}%, podemos aumentar o stop para 70%, STOP: {round((current_percentual_stop * 100) ,2)}% resultado"
                )
                current_stop_operation = round(
                    float((buy_price * current_percentual_stop) + buy_price), 5
                )

                self.situacao_email_stop = f"Preço Compra: {buy_price} \n Diferença Percentual maior que o limite de {target_loss}%: {dif_percent_price}%, podemos aumentar o stop para 70%, STOP: {round((current_percentual_stop * 100) ,2)}% resultado \n Current Stop Operation: {current_stop_operation}"

                print(
                    f"{bcolors.CREDBG2}{bcolors.AMARELO}Current Stop Operation: {bcolors.FIM} {current_stop_operation}"
                )

            elif dif_percent_price > 2.5:
                print(
                    f"Diferença Percentual maior que o limite de 2,5% , podemos aumentar o stop para 0,7%"
                )
                current_stop_operation = round(
                    float((buy_price * 0.007) + buy_price), 5
                )

                self.situacao_email_stop = f"Preço Compra: {buy_price} \n Diferença Percentual: {dif_percent_price} maior que o limite de 2,5% , \n Current Stop Operation: {current_stop_operation}"

                print(
                    f"{bcolors.CREDBG2}{bcolors.AMARELO}Current Stop Operation: {bcolors.FIM} {current_stop_operation}"
                )

            elif dif_percent_price < target_loss:
                print("Diferença menor que o Limite")
                current_stop_operation = round(
                    float(((buy_price * (target_loss / 100)) - buy_price) * -1), 5
                )

                self.situacao_email_stop = f"Preço Compra: {buy_price} \n Diferença Percentual: {dif_percent_price} menos que o limite de {target_loss}, \n Current Stop Operation: {current_stop_operation}"

                print(
                    f"{bcolors.CREDBG2}{bcolors.AMARELO}Current Stop Operation: {bcolors.FIM} {current_stop_operation}"
                )
                if self.close_c < current_stop_operation:
                    print("Operacao Stopada por conta do stop loss")

        print("\n")
        print(f"Tamanho da Lista: {len(self.list_closes_after_buy)}")
        print(self.list_closes_after_buy[-100:])
        print("\n\n")
        print(top_value)
        print(self.list_closes_after_buy.index(top_value))
        print("\n\n")

        if self.close_c < current_stop_operation:
            print(
                f"{bcolors.CVIOLETBG}Venda pois fomos stopados na operação: último Fechamento {self.close_c} < Stop Operation: {current_stop_operation}{bcolors.FIM}"
            )
            resultado = True
            try:
                self.modalidade_compra = f"Venda STOP Operação!! <br> Stop Atingido: {current_stop_operation} | último fechamento que atingiu o STOP: {self.close_c}"
            except Exception as e:
                print(f"Erro na hora de criar a mensagem por e-mail: {e}")
        else:
            resultado = False

        return resultado


class Balance:
    def __init__(self, moeda, livre, bloqueado):
        self.moeda = moeda
        self.livre = livre
        self.bloqueado = float(bloqueado)

    def __str__(self):
        if self.bloqueado > 0.00000000:
            return f"Moeda: {self.moeda} \t| Saldo: {self.livre} \t| Em Ordem: {self.bloqueado}"
        else:
            return f"Moeda: {self.moeda} \t| Saldo: {self.livre}"

    @classmethod
    def get_balance(cls, TRADE_SYMBOL):
        only_coin = TRADE_SYMBOL[:3]
        balance = Trades.client.get_asset_balance(asset=only_coin)
        return cls(balance["asset"], balance["free"][:-3], balance["locked"])

    @classmethod
    def get_all_balance(cls):
        account = Trades.client.get_account()
        balances = account["balances"]
        return [
            cls(balance["asset"], balance["free"], balance["locked"])
            for balance in balances
            if float(balance["free"]) > 0.00000000
            or float(balance["locked"]) > 0.00000000
        ]


# {
#   "e": "kline",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "k": {
#     "t": 123400000, // Kline start time
#     "T": 123460000, // Kline close time
#     "s": "BNBBTC",  // Symbol
#     "i": "1m",      // Interval
#     "f": 100,       // First trade ID
#     "L": 200,       // Last trade ID
#     "o": "0.0010",  // Open price
#     "c": "0.0020",  // Close price
#     "h": "0.0025",  // High price
#     "l": "0.0015",  // Low price
#     "v": "1000",    // Base asset volume
#     "n": 100,       // Number of trades
#     "x": false,     // Is this kline closed?
#     "q": "1.0000",  // Quote asset volume
#     "V": "500",     // Taker buy base asset volume
#     "Q": "0.500",   // Taker buy quote asset volume
#     "B": "123456"   // Ignore
#   }
# }


# #Historico get_1_day_ago
# """"
# [
#   [
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Ignore.
#   ]
# ]
# """"
