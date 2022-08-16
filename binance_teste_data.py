#!/usr/local/bin/python3

from binance.client import Client
from binance.enums import *

import config


from lista_moedas import MOEDAS, get_all_coins, MOEDAS_2


from datetime import datetime, timedelta

client = Client(config.API_KEY, config.API_SECRET)


# PEGAR TODAS AS TRANSAÇÕES DO CLIENTE, CONFORME A LISTA DE MOEDAS:
def todas_transacoes():
    count = 1
    for moeda in MOEDAS:
        trades_hist = client.get_my_trades(symbol=moeda)
        for i in trades_hist:
            print(f"{count}) - {i}")
            count += 1
    for moeda in MOEDAS:
        try:
            trades_hist = client.get_margin_trades(symbol=moeda, isIsolated="TRUE")
            for i in trades_hist:
                print(f"{count}) - {i}")
                count += 1
        except Exception as e:
            print(f"Error ao gerar a conta para a moeda: {moeda}")


def todas_transacoes_moeda(moeda):
    operacoes_binance = {}
    count = 0
    trades_hist = client.get_my_trades(symbol=moeda)
    for i in trades_hist:
        count += 1
        tipo_operacao = "spot"
        dict_data = [i][0]
        symbol = dict_data["symbol"]
        coinstyle = "R$ " if "BRL" in symbol else "USD"
        id_trade = dict_data["id"]
        id_order = dict_data["orderId"]
        price = dict_data["price"]
        qty = dict_data["qty"]
        valor_total = dict_data["quoteQty"]
        comission = dict_data["commission"]
        comissionAsset = dict_data["commissionAsset"]
        time = dict_data["time"]
        isBuyer = dict_data["isBuyer"]
        isMaker = dict_data["isMaker"]
        isBestMatch = dict_data["isBestMatch"]
        time_format = format_date_outsideclass(time)
        cotacao_dolar = 5.50
        # cotacao_dolar = dolar_dict.get(time_format) if "USD" in moeda else 0
        valor_negociado_reais = (
            (round(float(price), 6) * (round(float(cotacao_dolar), 3)))
            if "USD" in moeda
            else price
        )
        total_reais = (
            (round(float(cotacao_dolar), 3) * round(float(valor_total), 2))
            if "USD" in moeda[-4:]
            else round(float(valor_total), 2)
        )
        tipo_t = "BUY" if isBuyer == True else "SELL"

        if comissionAsset == "BNB":
            comi_tax = 0.00075
        else:
            comi_tax = 0.001

        comi_total_reais = round(float(total_reais), 2) * comi_tax
        moeda = symbol
        moeda_operacao = coinstyle
        valor_negociado = f"{float(price):.5f}"
        valor_negociado_reais = f"{float(valor_negociado_reais):.5f}"
        tipo = tipo_t
        data = time_format
        data_original = time
        quantidade_negociada = f"{float(qty):.5f}"
        valor_total = f"{float(valor_total):.2f}"
        cotacao_dolar = (
            f"{float(cotacao_dolar):.3f}"  # Alterar para buscar query no django!!
        )
        # cotacao_dolar = CotacaoUsdtbrl.objects.filter(data=data)[0].cotacao
        comissao = f"{float(comission):.5f}"
        comissao_moeda = comissionAsset
        comi_tax = comi_tax
        comi_total_reais = f"{float(comi_total_reais):.2f}"
        id_order = id_order
        id_trader = id_trade
        tipo_operacao = tipo_operacao

        print(
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
            comi_tax,
            comi_total_reais,
            id_order,
            id_trader,
            tipo_operacao,
        )

    # try:
    #     trades_hist = client.get_margin_trades(symbol=moeda, isIsolated="TRUE")
    #     for i in trades_hist:
    #         print(f"{count}) - {i}")
    #         count += 1
    # except Exception as e:
    #     print(f"Error ao gerar a conta para a moeda: {moeda}")


# PEGAR TODOS OS PARES DE MOEDAS DA SELECT_CORRETORA
def pegar_todas_moedas():
    # moeda e cotacao atual:
    coins_list = client.get_all_tickers()

    count = 1
    for i in coins_list:
        print(f"{count}) - {i['symbol']}")
        count += 1


def format_date_outsideclass(date):
    not_formated_date = datetime.fromtimestamp(date / 1000)
    nd = not_formated_date + timedelta(days=0)
    format_date = nd.strftime("%Y-%m-%d")
    return format_date


def get_closed_day_ago(symbol):
    klines_c = client.get_historical_klines(
        symbol, Client.KLINE_INTERVAL_1DAY, "720 day ago UTC-3"
    )
    filt_klines_c = klines_c

    closes = []
    closes_to_stop = {}
    for kline in filt_klines_c:
        close = kline[4]
        closes.append(float(close))

    filt_klines_c_stop = klines_c[:-1]
    for kline in filt_klines_c_stop:
        close = kline[4]
        datas = format_date_outsideclass(kline[0])
        price_and_date = {}
        price_and_date["date"] = datas
        price_and_date["price"] = float(close)
        closes_to_stop[f"{datas}"] = float(close)
    return closes_to_stop


if __name__ == "__main__":
    # data = get_closed_day_ago("USDTBRL")
    # for k, v in data.items():
    #     print(f"Data: {k} - Valor: {v}")
    todas_transacoes_moeda("ACAUSDT")
