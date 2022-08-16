#!/usr/local/bin/python3
import json
from lista_moedas import MOEDAS
from collections import OrderedDict, Counter
from colors import bcolors
import pandas as pd


from datetime import datetime


def get_dolar_last_year():
    with open(
        f"/Users/marcelopata/Dropbox/Program/binance_data/USDTBRL_lastcotationsDolarBRL.json",
        "r",
    ) as dolar_json:
        dolar_dict = json.load(dolar_json)
        # for k, v in dolar_dict.items():
        #     print(k, v)
    return dolar_dict


# for date, price in i.items():
#     print(f'Data: {date} - Valor: {price}')
