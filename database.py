import os
import datetime
import psycopg2
from config import DATABASE_URL_ELEPHANT

from dotenv import load_dotenv

mean_dict = os.getcwd().split("Program")[0]
data_json_dic = "Program/Curso-vue-macmini/curso-vuue/vueti-ap/src/data"
json_dest = mean_dict + data_json_dic + "/"


CREATE_NOTAS_TABLE = """CREATE TABLE IF NOT EXISTS tradesbinance (
    id SERIAL PRIMARY KEY,
    moeda VARCHAR(30),
    moeda_operacao VARCHAR(30),
    valor_negociado NUMERIC(12,5),
    valor_negociado_reais NUMERIC(12,5),
    tipo TEXT,
    data DATE,
    data_original NUMERIC (20,0),
    quantidade_negociada NUMERIC(20,5),
    valor_total NUMERIC(10,2),
    cotacao_dolar NUMERIC (4,2),
    total_reais NUMERIC (10,2),
    comissao NUMERIC (13,5),
    comissao_moeda VARCHAR(10),
    comi_tax NUMERIC (10,5),
    comi_total_reais NUMERIC (10,2),
    id_order NUMERIC,
    id_trade NUMERIC,
    tipo_operacao VARCHAR(30)
);"""

INSERT_NOTAS = """INSERT INTO tradesbinance 
( moeda, moeda_operacao, valor_negociado, valor_negociado_reais, tipo, data, data_original, quantidade_negociada, valor_total, cotacao_dolar, total_reais, comissao, comissao_moeda, comi_tax, comi_total_reais, id_order, id_trade, tipo_operacao) 
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s);
"""


SEARCH_NOTAS = "SELECT * FROM tradesbinance WHERE id_trade = %s "
# -----Formula para pegar tudo que foi comprado----##
# SUM_TIPO = "SELECT acao, SUM(quantidade_negociada) FROM notas WHERE tipo = 'C' GROUP BY acao;"


SELECT_ALL_TRADES = "SELECT * FROM tradesbinance ORDER BY data_original ASC;"
SELECT_ALL_TRADES_RANGE_DATE = (
    "SELECT * FROM tradesbinance WHERE data > '2021-09-01' ORDER BY data_original ASC;"
)


# <--------filtrando por data ---------------->
SELECT_ALL_TRADES = (
    "SELECT * FROM tradesbinance WHERE data > '2021-10-15' ORDER BY data_original ASC;"
)
SELECT_MOEDA_TRADES = "SELECT * FROM tradesbinance WHERE data > '2021-01-01' AND moeda LIKE (%s) and tipo_operacao = 'spot' ORDER BY data ASC;"
# <--------filtrando por data ---------------->

# SELECT_MOEDA_TRADES = (
#     "SELECT * FROM tradesbinance WHERE moeda LIKE (%s) ORDER BY data ASC;"
# )
SELECT_MOEDA_TRADES_DATES_RANGE = "SELECT * FROM tradesbinance WHERE data > '2021-09-01' AND moeda LIKE (%s) ORDER BY data ASC;"

SELECT_TRADES_BY_COIN = (
    "SELECT * FROM tradesbinance WHERE moeda LIKE '%ADA%'ORDER BY data ASC;"
)

CREATE_DOLAR_TABLE = """CREATE TABLE IF NOT EXISTS usdtbrl_binance (
    id SERIAL PRIMARY KEY,
    moeda VARCHAR(30),
    data DATE ,
    cotacao_dolar NUMERIC (5,3),
    UNIQUE (data)
);"""

INSERT_USDTBRL = """INSERT INTO usdtbrl_binance 
( moeda, data, cotacao_dolar)
VALUES (%s,%s,%s);
"""

SEARCH_USDTBRL = "SELECT * FROM usdtbrl_binance WHERE data = %s "

CREATE_MONTHYEAR_TABLE = """CREATE TABLE IF NOT EXISTS month_year (
    id SERIAL PRIMARY KEY,
    data DATE ,
    mes_numero VARCHAR,
    mes_escrito TEXT,
    year VARCHAR,
    UNIQUE (data)
);"""

INSERT_MONTHYEAR = """INSERT INTO month_year 
( data, mes_numero, mes_escrito, year)
VALUES (%s,%s,%s,%s);
"""

SEARCH_MONTHYAR = "SELECT * FROM month_year WHERE data = %s "

SELECT_ALL_MONTHYEAR = "SELECT * FROM month_year"

nd = "Desktop"

MAKE_JSON_FILE = f"""
COPY (
SELECT array_to_json(array_agg(tradesbinance ORDER BY data_original ASC), FALSE)
FROM tradesbinance
) to '{json_dest}file.json'
"""


# < ------------------------------------- ########### ------------------------------------------->


SELECT_ALL_NOTAS = "SELECT * FROM notas ORDER BY data ASC;"

# formula para filtrar os saldos no DBm ordem crescente de maior quantidade de ação.

SELECT_ACOES_SALDOS = """
SELECT acao, 
SUM(quantidade_negociada) as soma_acoes_compradas,
corretora, 
RANK() OVER(ORDER BY SUM(quantidade_negociada) DESC)
FROM notas as n
GROUP BY  acao, corretora
HAVING SUM(quantidade_negociada) > 0 
ORDER BY soma_acoes_compradas DESC;
"""

SELECT_ACOES_SALDOS_USER = """
SELECT acao,
SUM(quantidade_negociada) as soma_acoes_compradas,
corretora, 
usuario,
RANK() OVER(ORDER BY SUM(quantidade_negociada) DESC)
FROM notas as n
GROUP BY  acao, corretora, usuario
HAVING SUM(quantidade_negociada) > 0 
ORDER BY soma_acoes_compradas DESC;
"""


SELECT_EMPRESAS_NEGOCIADAS = "SELECT acao from notas GROUP BY acao;"
SELECT_CORRETORA = "SELECT corretora from notas GROUP BY corretora;"
SELECT_USUARIO = "SELECT usuario from notas GROUP BY usuario;"


# ------------------------------------CONEXAO NO BANCO DE DADOS------------------------------------------------>>>>>>
"""
# Elephant URL CONECTION
DATABASE_URL = DATABASE_URL_ELEPHANT
connection = psycopg2.connect(DATABASE_URL)

"""

# """ LOCAL CONECTION
connection = psycopg2.connect(
    host="localhost", database="opera_binance", user="postgres", password="mopmop"
)
# """

CALENDARIO_MESES = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Março",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}


def make_json_file():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(MAKE_JSON_FILE)


def create_tables():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_NOTAS_TABLE)
            cursor.execute(CREATE_DOLAR_TABLE)
            cursor.execute(CREATE_MONTHYEAR_TABLE)


def add_notas(
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
    id_trade,
    tipo_operacao,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_NOTAS,
                (
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
                    id_trade,
                    tipo_operacao,
                ),
            )


def search_notas(
    id_trade,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                SEARCH_NOTAS,
                (id_trade,),
            )
            return cursor.fetchone()


def search_monthyear(
    data,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                SEARCH_MONTHYAR,
                (data,),
            )
            return cursor.fetchone()


def add_monthyear(
    data,
    mes_numero,
    mes_escrito,
    year,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_MONTHYEAR,
                (
                    data,
                    mes_numero,
                    mes_escrito,
                    year,
                ),
            )


def select_all_monthyear():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_MONTHYEAR)
            return cursor.fetchall()


def add_usdtbrl_cotacao(
    moeda,
    data,
    cotacao_dolar,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_USDTBRL,
                (
                    moeda,
                    data,
                    cotacao_dolar,
                ),
            )


def search_usdtbrl(
    data,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                SEARCH_USDTBRL,
                (data,),
            )
            return cursor.fetchone()


def select_all_trades():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_TRADES)
            return cursor.fetchall()


def select_moeda_trades(
    moeda,
):
    with connection:
        with connection.cursor() as cursor:
            like_pattern = f"%{moeda}%"
            cursor.execute(SELECT_MOEDA_TRADES, (like_pattern,))
            return cursor.fetchall()


def select_all_notas():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_NOTAS)
            return cursor.fetchall()


def select_saldo_acoes():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ACOES_SALDOS)
            return cursor.fetchall()


def select_saldo_acoes_user():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ACOES_SALDOS_USER)
            return cursor.fetchall()


def select_empresas_negociadas():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_EMPRESAS_NEGOCIADAS)
            return cursor.fetchall()


def select_corretora():
    with connection:
        with connection.cursor() as cursor:
            corretoras = cursor.execute(SELECT_CORRETORA)
            return cursor.fetchall()


def select_usuario():
    with connection:
        with connection.cursor() as cursor:
            corretoras = cursor.execute(SELECT_USUARIO)
            return cursor.fetchall()
