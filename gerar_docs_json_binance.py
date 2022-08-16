#!/usr/local/bin/python3
import websocket, json, pprint, numpy
# import talib
import ssl
from binance.client import Client
from binance.enums import *

import config
from datetime import datetime, timedelta
import time

from email_yag import send_email_yag, trigger_send_mail
from colors import bcolors

from decimal import Decimal

from lista_moedas import MOEDAS, get_all_coins, MOEDAS_2


# from talib import MA_Type

from models import Trades, Balance
from dolar_prices_dict import get_dolar_last_year

from database import create_tables, add_usdtbrl_cotacao, search_usdtbrl
import database


# Defini se está comprado ou n
on_position = False
# defini se vai operar e receber mensagens
real_operation = True
# defini se vai operar, receber mensagens e Fazer Trades de verdade
real_trades = False
# defini se vai realizar ordens de Compra
real_trades_buiyng = False

# ativa ou desativa o envio de e-mails
on_send_mails = True


# Descomentar para alterar os símbolos
"""
TRADE_SYMBOL = "BTCUSDT"
TRADE_QUANTITY = 0.0002

TRADE_SYMBOL = "ETHUSDT"
TRADE_QUANTITY = 0.01

"""

TRADE_SYMBOL = "ADABRL"
TRADE_QUANTITY = 10

# Descomentar para alterar os símbolos
# """


# Parametros Binance

SOCKET = f"wss://stream.binance.com:9443/ws/{TRADE_SYMBOL.lower()}@kline_1m"
# SOCKET = f"wss://stream.binance.com:9443/ws/{TRADE_SYMBOL.lower()}@kline_2h"
client = Client(config.API_KEY, config.API_SECRET)
# Parametros Binance


closes = []
operations = []
test_operations = []
trades = []
closes_envio_email = []


def get_current_position(TRADE_SYMBOL):
    global on_position
    balance_one = Balance.get_balance(TRADE_SYMBOL)
    if float(balance_one.livre) > 0.00000 or float(balance_one.bloqueado) > 0.00000:
        on_position = True
        print(f"Estamos Comprados em: {TRADE_SYMBOL}")
        print(f"Posíção: {on_position}\n")
    else:
        on_position = False
        print(f"Ainda não estamos comprados em: {TRADE_SYMBOL}")
        print(f"Posição: {on_position}\n")


def get_orders(symbol):
    orders = client.get_all_orders(symbol=symbol)
    print(type(orders))
    for order in orders:
        # dict_or = orders['order']
        simbolo = order["symbol"]
        tipo = order["side"]
        preco = order["price"]
        time_order = Trades.format_date_outsideclass(order["time"])
        print(f"Moeda: {simbolo} - Tipo: {tipo} - Preço: {preco} - Data: {time_order}")
    return orders


def get_trades(symbol):
    global trades
    trades_exchange = client.get_my_trades(symbol=symbol)
    for trade in trades_exchange:
        simbolo = trade["symbol"]
        tipo = trade["isBuyer"]
        tipo_t = "BUY" if tipo == True else "SELL"
        preco = trade["price"]
        time_trade = Trades.format_date_outsideclass(trade["time"])
        quantidade = trade["qty"]

        total_pago = float(preco) * float(quantidade)
        # print(
        #     f"Moeda: {simbolo} - Tipo: {tipo_t} - Preço: {preco} - Qty: {quantidade} - Total Pago: {round((total_pago),2)} - Data: {time_trade}"
        # )
        trades.append(
            {
                "simbolo": simbolo,
                "tipo": tipo_t,
                "preco": preco,
                "quantidade": quantidade,
                "data": time_trade,
                "total": round((total_pago), 2),
            }
        )
    return trades


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    global operations
    try:
        print(f"{bcolors.VERDE}Sending order{bcolors.FIM}")
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
        )
        print(f"{bcolors.CBLUEBG2}{bcolors.AMARELO}{order}{bcolors.FIM}")
        try:
            simbolo = order["symbol"]
            order_id = order["orderId"]
            tipo = order["side"]
            executado = order["fills"][0]
            preco = executado["price"]
            quantidade = executado["qty"]
            comissao = executado["commission"]
            total = float(preco) * float(quantidade)
            operations.append(
                {
                    "simbolo": simbolo,
                    "id": order_id,
                    "tipo": tipo,
                    "preco": preco,
                    "quantidade": quantidade,
                    "comissao": comissao,
                    "total": total,
                }
            )
            print(
                f"Moeda: {simbolo} - Tipo: {tipo} - Preço: {preco} - Qty: {quantidade} - Comissao: {comissao} - Total USD: {total}"
            )
        except Exception as e:
            print(
                f"{bcolors.VERMELHO}Error salvando dados dicionario de operações: {e}{bcolors.FIM}"
            )
    except Exception as e:
        print(f"{bcolors.VERMELHO}Error: {e}{bcolors.FIM}")
        return False

    return True




def on_open(ws):
    create_tables()
    global on_position
    print("Conexão Iniciada!!\n")
    # info = client.get_exchange_info()
    # print(info)


    # <-------------- OBTER COTACAO DOLAR dos ultimos 365 dias e atualizar com o último fechamento!! ------------>
    dolar_dict = get_dolar_last_year()
    dolar_hist = Trades.get_closed_day_ago(symbol='USDTBRL')
    dolar_dict.update(dolar_hist)
    a_file = open(f"/Users/marcelopata/Dropbox/Program/binance_data/USDTBRL_lastcotationsDolarBRL.json", "w")
    a_file = json.dump(dolar_dict, a_file)
    
    with open(
        f"/Users/marcelopata/Dropbox/Program/binance_data/USDTBRL_lastcotationsDolarBRL.json",
        "r",
        ) as usdt_dict_prices:
        usdt_dict_prices_py = json.load(usdt_dict_prices)
        for k,v in usdt_dict_prices_py.items():
            data_dolar = k
            cotacao_dolar = v
            moeda = 'USDTBRL'
            transacoes_binance_db = database.search_usdtbrl(data_dolar)
            if transacoes_binance_db:
                pass
            else:
                add_usdtbrl_cotacao(moeda, data_dolar, cotacao_dolar)
                print(f"{bcolors.BOLD}{bcolors.VERDE}Transação Incluída com sucesso! {bcolors.FIM}")


    for moeda in MOEDAS:
        try:
            trades_hist = client.get_my_trades(symbol=moeda)
            a_file = open(f"/Users/marcelopata/Dropbox/Program/binance_data/teste_{moeda}_22092021.json", "w")
            a_file = json.dump(trades_hist, a_file)
            print(f"{bcolors.BOLD}{bcolors.VERDE}Json Gerado com successo: {moeda} {bcolors.FIM}")
        except Exception as e:
            print(f"{bcolors.BOLD}{bcolors.VERMELHO}problema em gerar o arquivo JSON de Margin Trade:  Moeda - {moeda} - {e} {bcolors.FIM}")
    
    for moeda in MOEDAS:
        try:
            margin_trades_hist = client.get_margin_trades(symbol=moeda, isIsolated='TRUE')
            if margin_trades_hist:
                m_file = open(f"/Users/marcelopata/Dropbox/Program/binance_data/teste_{moeda}_22092021_margin.json", "w")
                m_file = json.dump(margin_trades_hist, m_file)
                print(f"{bcolors.BOLD}{bcolors.VERDE}Json Gerado com successo: {moeda} {bcolors.FIM}")
        except Exception as e:
            print(f"{bcolors.BOLD}{bcolors.VERMELHO}problema em gerar o arquivo JSON de Margin Trade:  Moeda - {moeda} - {e} {bcolors.FIM}")
    
    #<------------- pegar histórico de todas as moedas da Binance ------------->
    # MOEDAS_DEF = get_all_coins()
    # count_moedas_com_histórico = 0
    # for moeda in MOEDAS_2:
    #     try:
    #         trades_hist = client.get_my_trades(symbol=moeda)
    #         if trades_hist:
    #             print(trades_hist)
    #             print(count_moedas_com_histórico)
    #             a_file = open(f"/Users/marcelopata/Dropbox/Program/binance_data/30092021_{moeda}_.json", "w")
    #             a_file = json.dump(trades_hist, a_file)
    #         else:
    #             print(f'{count_moedas_com_histórico} - Moeda sem histórico: {moeda}')
    #         count_moedas_com_histórico += 1
    #     except Exception as e:
    #         print(f'problema em gerar o arquivo JSON:  Moeda - {moeda} - {e}')
    #         # if 'oo much request weight used' in e:
    #         print(f"{bcolors.VERMELHO}Error: {e}{bcolors.FIM}")
    #         print(f'{bcolors.VERMELHO}Esperando 2 minutos até poder solicitar novamente: {e} {bcolors.CREDBG2}{bcolors.AMARELO}{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}{bcolors.FIM}')
    #         for i in range(120 , 0, -1):
    #             print(f'Faltando {i} Segundos')
    #             time.sleep(1)

    #<------------- FIM pegar histórico de todas as moedas da Binance ------------->
    try:
        get_current_position(TRADE_SYMBOL)
    except Exception as e:
        print(f"Error ao definir a posição ao abrir a conexão: {e}")
    try:
        balance = Balance.get_all_balance()
        for b in balance:
            print(b)
        print("\n")
    except:
        print(f"Sem Saldo na corretora")
    # info_symbol = client.get_symbol_info(TRADE_SYMBOL)
    # print(info_symbol)

    trades.clear()
    get_trades(TRADE_SYMBOL)
    if trades:
        for trade in trades:
            if "BUY" in trade["tipo"]:
                print(
                    f"{bcolors.VERDE}{trade['tipo']} | Moeda: {trade['simbolo']} - Preço: {trade['preco']} - Quantidade: {trade['quantidade']} - Data: {trade['data']} - Total: USD {trade['total']}{bcolors.FIM}"
                )
            else:
                print(
                    f"{bcolors.VERMELHO}{trade['tipo']} | Moeda: {trade['simbolo']} - Preço: {trade['preco']} - Quantidade: {trade['quantidade']} - Data: {trade['data']} - Total: USD {trade['total']}{bcolors.FIM}\n"
                )
        print("\n")
    trade_day = Trades.get_closed_day_ago(symbol=TRADE_SYMBOL)
    print(f"Closes: {len(trade_day)} | Mostrando somente últimos 25")
    print(trade_day[-25:])

    print("Tudo OK")


def on_close(ws):
    print("closed conection")


def on_message(ws, message):
    print(type(message))
    
    
    #close conection
    on_close(ws)





    # json_message = json.loads(message)
    # print(json_message)
    
    # trades_class = Trades.get_trades(message)
    # print(trades_class)
    


def on_error(ws, error):
    print(error)


ws = websocket.WebSocketApp(
    SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error
)

ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
