#!/usr/local/bin/python3
import json
from lista_moedas import MOEDAS, MOEDAS_2
from collections import OrderedDict, Counter
from colors import bcolors
import pandas as pd
import locale

locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")


from datetime import datetime
from dolar_prices_dict import get_dolar_last_year

from database import create_tables, add_notas, search_notas
from database import search_monthyear, add_monthyear, make_json_file
import database


def format_date_outsideclass(date):
    not_formated_date = datetime.fromtimestamp(date / 1000)
    # format_date = not_formated_date.strftime("%d/%m/%Y")
    format_date = not_formated_date.strftime("%Y-%m-%d")
    # format_date = not_formated_date.strftime("%Y-%m-%d %H:%M:%S")
    format_date = format_date
    return format_date


operacoes_binance = {}

dolar_dict = get_dolar_last_year()
print(dolar_dict.get("2021-09-21"))

saldos = {}
order_id = []
trade_id = []
count = 0
lista_meses = []

# ---------------------------------- GERANDO SOB OS ARQUIVOS TRADE NORMAL ----------------------------------#
for moeda in MOEDAS:
    compra = 0
    venda = 0
    comi_moeda = 0
    comi_bnb = 0
    comissoes = []
    try:
        coinstyle = "R$ " if "BRL" in moeda else "USD"
        with open(
            f"/Users/marcelopata/Dropbox/Program/binance_data/teste_{moeda}_22092021.json",
            "r",
        ) as pata_read_first:
            dict_file = json.load(pata_read_first)
            for i in dict_file:
                # print(i)
                tipo_operacao = 'spot'
                dict_data = [i][0]
                symbol = dict_data["symbol"]
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
                cotacao_dolar = dolar_dict.get(time_format) if "USD" in moeda else 0
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
                if tipo_t == "BUY":
                    compra += round(float(qty), 5)
                else:
                    venda += round(float(qty), 5)

                if comissionAsset == "BNB":
                    comi_bnb += round(float(comission), 5)
                else:
                    comi_moeda += round(float(comission), 5)
                
                if comissionAsset == "BNB":
                    comi_tax = 0.00075
                else:
                    comi_tax = 0.001
                comi_total_reais = round(float(total_reais), 2) * comi_tax
                comissoes.append({comissionAsset: round(float(comission), 8)})
                order_id.append(id_order)
                trade_id.append(id_trade)
                lista_meses.append(time_format[:7])
                operacoes_binance.update(
                    {
                        count: {
                            "moeda_sym": symbol,
                            "moeda_operacao": coinstyle,
                            "valor": f"{float(price):.5f}",
                            "valor_reais": f"{float(valor_negociado_reais):.5f}",
                            "tipo": tipo_t,
                            "data": time_format,
                            "data_original": time,
                            "quantidade": f"{float(qty):.5f}",
                            "total": f"{float(valor_total):.2f}",
                            "cot_usd": f"{float(cotacao_dolar):.3f}",
                            "total_reais": f"{float(total_reais):.2f}",
                            "comissao": f"{float(comission):.5f}",
                            "comissao_moeda": comissionAsset,
                            "comi_tax": comi_tax,
                            "comi_total_reais": f"{float(comi_total_reais):.2f}",
                            "id_order": id_order,
                            "id_trade": id_trade,
                            "tipo_operacao": tipo_operacao,
                        }
                    }
                )
                count += 1
            saldo_moedas = compra - venda
            saldos.update(
                {
                    moeda: {
                        "compra": round(float(compra), 5),
                        "venda": round(float(venda), 5),
                        "saldo": saldo_moedas,
                        f"comissao {moeda}": comi_moeda,
                        "comi_bnb": comi_bnb,
                        "comissoes": comissoes,
                    }
                }
            )
    except Exception as e:
        pass
        # print(f"Problema em ler o arquivo da Moeda {moeda}:  {e}")

# ---------------------------------- GERANDO SOB OS ARQUIVOS TRADE NORMAL ----------------------------------#

print(f'COntagem eim: {count}')
# ---------------------------------- GERANDO SOB OS ARQUIVOS DE MARGIN ----------------------------------#
for moeda in MOEDAS:
    compra = 0
    venda = 0
    comi_moeda = 0
    comi_bnb = 0
    comissoes = []
    try:
        coinstyle = "R$ " if "BRL" in moeda else "USD"
        with open(
            f"/Users/marcelopata/Dropbox/Program/binance_data/teste_{moeda}_22092021_margin.json",
            "r",
        ) as pata_read_first:
            dict_file = json.load(pata_read_first)
            print(dict_file)
            for i in dict_file:
                # print(i)
                tipo_operacao = 'margem'
                dict_data = [i][0]
                symbol = dict_data["symbol"]
                id_trade = dict_data["id"]
                id_order = dict_data["orderId"]
                price = dict_data["price"]
                qty = dict_data["qty"]
                valor_total = (round(float(price), 6)) * (round(float(qty), 6))
                comission = dict_data["commission"]
                comissionAsset = dict_data["commissionAsset"]
                time = dict_data["time"]
                isBuyer = dict_data["isBuyer"]
                isMaker = dict_data["isMaker"]
                isBestMatch = dict_data["isBestMatch"]

                time_format = format_date_outsideclass(time)
                cotacao_dolar = dolar_dict.get(time_format) if "USD" in moeda else 0
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
                if tipo_t == "BUY":
                    compra += round(float(qty), 5)
                else:
                    venda += round(float(qty), 5)

                if comissionAsset == "BNB":
                    comi_bnb += round(float(comission), 5)
                else:
                    comi_moeda += round(float(comission), 8)

                if comissionAsset == "BNB":
                    comi_tax = 0.00075
                else:
                    comi_tax = 0.001
                comi_total_reais = round(float(total_reais), 2) * comi_tax

                comissoes.append({comissionAsset: round(float(comission), 8)})
                order_id.append(id_order)
                trade_id.append(id_trade)
                lista_meses.append(time_format[:7])
                try:
                    operacoes_binance.update(
                        {
                            count: {
                                "moeda_sym": symbol,
                                "moeda_operacao": coinstyle,
                                "valor": f"{float(price):.5f}",
                                "valor_reais": f"{float(valor_negociado_reais):.5f}",
                                "tipo": tipo_t,
                                "data": time_format,
                                "data_original": time,
                                "quantidade": f"{float(qty):.5f}",
                                "total": f"{float(valor_total):.2f}",
                                "cot_usd": f"{float(cotacao_dolar):.3f}",
                                "total_reais": f"{float(total_reais):.2f}",
                                "comissao": f"{float(comission):.5f}",
                                "comissao_moeda": comissionAsset,
                                "comi_tax": comi_tax,
                                "comi_total_reais": f"{float(comi_total_reais):.2f}",
                                "id_order": id_order,
                                "id_trade": id_trade,
                                "tipo_operacao": tipo_operacao,
                            }
                        }
                    )
                    print(f'Dict atualizado com sucesso!!!')
                except Exception as e:
                    print(f'Erro ao atualizar dict: {e}')
                count += 1
            saldo_moedas = compra - venda
            saldos.update(
                {
                    moeda: {
                        "compra": round(float(compra), 5),
                        "venda": round(float(venda), 5),
                        "saldo": saldo_moedas,
                        f"comissao {moeda}": comi_moeda,
                        "comi_bnb": comi_bnb,
                        "comissoes": comissoes,
                    }
                }
            )
    except Exception as e:
        print(f"Problema em ler o arquivo da Moeda de Margin {moeda}:  {e}")


# ---------------------------------- GERANDO SOB OS ARQUIVOS DE MARGIN ----------------------------------#


print("\n\n\n\n\n")
print(len(trade_id))
print(len(set(trade_id)))
print(len(order_id))
print(len(set(order_id)))
# for k,v in operacoes_binance.items():
#     print(v)


ordered = OrderedDict(sorted(operacoes_binance.items(), key=lambda t: t[1]["data"]))

for k,v in ordered.items():
    print(v)
# pd.set_option('display.max_rows', None)
# df = pd.DataFrame(ordered)
# df = df.T
# sum_id_order = df.groupby('id_order', as_index=False)['valor','quantidade','total'].sum()
# print(sum_id_order)


calendario_ano_meses = {
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

new_lista_meses = list(set(lista_meses))
new_lista_meses.sort()


create_tables()
for i in new_lista_meses:
    format_date = f"{i}-01"
    mes_numero = i[-2:]
    ano = i[:4]
    print(mes_numero)
    mes_escrito = calendario_ano_meses.get(mes_numero)
    print(mes_escrito)
    month_meses_db = database.search_monthyear(format_date)
    if month_meses_db:
        print("data já incluida")
    else:
        add_monthyear(format_date, mes_numero, mes_escrito, ano)


count_total_operations = 1
with open(
    f"/Users/marcelopata/Dropbox/Program/binance_data/resultados_22092021.txt", "w"
) as wr_file:
    for data_dict in new_lista_meses:
        mes_name = data_dict[5:]
        year_name = data_dict[:4]
        print(
            f"{bcolors.CVIOLETBG}{bcolors.AMARELO} {calendario_ano_meses.get(mes_name)} | {year_name}{bcolors.FIM}\n"
        )
        wr_file.write(f"{calendario_ano_meses.get(mes_name)} | {year_name}\n\n")
        total_compra_brl = 0
        total_venda_brl = 0

        total_compra_usd = 0
        total_venda_usd = 0

        total_compra_usd_brl = 0
        total_venda_usd_brl = 0

        lista_moedas_mes = []
        lista_moedas_mes_compra = []

        media_venda_por_moeda = {}
        media_compra_por_moeda = {}


        for k, v in ordered.items():
            id_trader = v["id_trade"]
            moeda = v["moeda_sym"]
            coinstyle = "R$ " if "BRL" in moeda else "USD"
            moeda_operacao = v["moeda_operacao"]
            valor_negociado = v["valor"]
            valor_reais = v["valor_reais"]
            tipo = v["tipo"]
            data = v["data"]
            data_original = v["data_original"]
            quantidade_negociada = v["quantidade"]
            valor_total = v["total"]
            valor_total_format = f"{coinstyle} {locale.currency(round(float(valor_total), 2), grouping=True, symbol=None)}"
            cotacao_dolar = v["cot_usd"]
            comissao = v["comissao"]
            comissao_moeda = v["comissao_moeda"]
            id_order = v["id_order"]
            tipo_operacao = v["tipo_operacao"]
            comi_tax = v['comi_tax']
            comi_total_reais = v['comi_total_reais']

            total_reais = round(float(v["total_reais"]), 2)
            total_reais_format = locale.currency(
                total_reais, grouping=True, symbol=None
            )
            if data_dict == v["data"][:7]:
                new_date = datetime.strptime(v["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                if v["tipo"] == "SELL":
                    lista_moedas_mes.append(moeda)
                    print(
                        f'{bcolors.VERMELHO}{v["moeda_sym"]} {v["valor"]} - Quantidade total: {v["quantidade"]} \tValor Total: {valor_total_format} \t\t{new_date}\tComissao: {v["comissao"]}\t \tComissao Moeda: {v["comissao_moeda"]}\t ID Order: {v["id_order"]}\t ID Trade: {v["id_trade"]}\t\t Cambio: {v["cot_usd"]}\t\t Total: R$ {total_reais_format}{bcolors.FIM} - TAX: {comi_tax} - COMIR$: {comi_total_reais}'
                    )
                    wr_file.write(
                        f'{v["moeda_sym"]}\t {v["valor"]} \t\t- Quantidade total: {v["quantidade"]} \tValor Total: {v["total"]} \t\t{v["tipo"]} {new_date}\tComissão: {v["comissao"]}\t \tComissão Moeda: {v["comissao_moeda"]}\t\tID Order: {v["id_order"]}\t ID Trade: {v["id_trade"]}\t\t Cambio: {v["cot_usd"]}\t\t Total: R$ {total_reais_format}\n'
                    )
                    if "USD" in valor_total_format:
                        total_venda_usd_brl += round(float(v["total_reais"]), 2)
                        total_venda_usd += round(float(v["total"]), 2)
                    else:
                        total_venda_brl += round(float(v["total_reais"]), 2)

                    if media_venda_por_moeda.get(moeda):
                        update_value_dict = [
                            float(media_venda_por_moeda.get(moeda)[0])
                            + round(float(total_reais), 2),
                            float(media_venda_por_moeda.get(moeda)[1])
                            + round(float(quantidade_negociada), 5),
                        ]
                        up_dict_venda = {moeda: update_value_dict}
                        media_venda_por_moeda.update(up_dict_venda)
                    if media_venda_por_moeda.get(moeda) == None:
                        media_venda_por_moeda[f"{moeda}"] = [
                            round(float(total_reais), 2),
                            round(float(quantidade_negociada), 5),
                        ]

                else:
                    lista_moedas_mes_compra.append(moeda)
                    print(
                        f'{bcolors.VERDE}{v["moeda_sym"]} {v["valor"]} - Quantidade total: {v["quantidade"]} \tValor Total: {valor_total_format} \t\t {new_date}\tComissao: {v["comissao"]}\t \tComissao Moeda: {v["comissao_moeda"]}\t ID Order: {v["id_order"]}\t ID Trade: {v["id_trade"]}\t\t Cambio: {v["cot_usd"]}\t\t Total: R$ {total_reais_format}{bcolors.FIM} TAX: {comi_tax} - COMIR$: {comi_total_reais}'
                    )
                    wr_file.write(
                        f'{v["moeda_sym"]}\t {v["valor"]} \t\t- Quantidade total: {v["quantidade"]} \tValor Total: {v["total"]} \t\t{v["tipo"]} {new_date}\tComissão: {v["comissao"]}\t \tComissão Moeda: {v["comissao_moeda"]}\t\tID Order: {v["id_order"]}\t ID Trade: {v["id_trade"]}\t\t Cambio: {v["cot_usd"]}\t\t Total: R$ {total_reais_format}\n'
                    )
                    if "USD" in valor_total_format:
                        total_compra_usd_brl += round(float(v["total_reais"]), 2)
                        total_compra_usd += round(float(v["total"]), 2)
                    else:
                        total_compra_brl += round(float(v["total_reais"]), 2)

                    if media_compra_por_moeda.get(moeda):
                        update_value_dict = [
                            float(media_compra_por_moeda.get(moeda)[0])
                            + round(float(total_reais), 2),
                            float(media_compra_por_moeda.get(moeda)[1])
                            + round(float(quantidade_negociada), 5),
                        ]
                        up_dict_venda = {moeda: update_value_dict}
                        media_compra_por_moeda.update(up_dict_venda)
                    if media_compra_por_moeda.get(moeda) == None:
                        media_compra_por_moeda[f"{moeda}"] = [
                            round(float(total_reais), 2),
                            round(float(quantidade_negociada), 5),
                        ]

                transacoes_binance_db = database.search_notas(id_trader)
                if transacoes_binance_db:
                    print(
                        f"{count_total_operations}) {bcolors.BOLD}{bcolors.VERMELHO} Transação já incluída no sistema {bcolors.FIM}"
                    )
                else:
                    add_notas(
                        moeda,
                        moeda_operacao,
                        valor_negociado,
                        valor_reais,
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
                    print(
                        f"{count_total_operations}) {bcolors.BOLD}{bcolors.AMARELO}Transação incluída com sucesso!!!{bcolors.FIM}"
                    )
                count_total_operations += 1

        total_geral_compra = total_compra_brl + total_compra_usd_brl
        total_geral_venda = total_venda_brl + total_venda_usd_brl
        wr_file.write("\n\n")
        print("\n")
        # ----------------------DICIONÁRIO RESUMINDO AS COMPRAS DO MES CORRENTE----------------------#
        print("\n")
        moedas_com_compra_mes = list(set(lista_moedas_mes_compra))
        if len(moedas_com_compra_mes) > 0:
            print(f"{bcolors.VERDE}Compras:{bcolors.FIM}")
            for i in sorted(moedas_com_compra_mes):
                dict_por_moeda_compra = media_compra_por_moeda.get(i)[0]
                dict_por_moeda_compra_quantidade = round(
                    (media_compra_por_moeda.get(i)[1]), 5
                )
                media_por_moeda_compra = (
                    dict_por_moeda_compra / dict_por_moeda_compra_quantidade
                )
                dict_por_moeda_compra_format = locale.currency(
                    dict_por_moeda_compra, grouping=True, symbol=None
                )
                print(
                    f"{i} \t\t\tQuantidade: {dict_por_moeda_compra_quantidade} \t\tPreço Médio: R$ {locale.currency(media_por_moeda_compra, grouping=True, symbol=None)} \t\tTotal: R$ {dict_por_moeda_compra_format}"
                )
        print("\n")
        # ----------------------DICIONÁRIO RESUMINDO AS VENDAS DO MES CORRENTE----------------------#
        print("\n")
        moedas_com_venda_mes = list(set(lista_moedas_mes))
        if len(moedas_com_venda_mes) > 0:
            print(f"{bcolors.VERMELHO}Vendas:{bcolors.FIM}")
            for i in sorted(moedas_com_venda_mes):
                dict_por_moeda_venda = media_venda_por_moeda.get(i)[0]
                dict_por_moeda_venda_quantidade = round(
                    (media_venda_por_moeda.get(i)[1]), 5
                )
                media_por_moeda_venda = (
                    dict_por_moeda_venda / dict_por_moeda_venda_quantidade
                )
                dict_por_moeda_format = locale.currency(
                    dict_por_moeda_venda, grouping=True, symbol=None
                )
                print(
                    f"{i}  \t\tQuantidade: {dict_por_moeda_venda_quantidade} \t\tPreço Médio: R$ {locale.currency(media_por_moeda_venda, grouping=True, symbol=None)} \t\tTotal: R$ {dict_por_moeda_format}"
                )
        print("\n")
        print(
            f"{bcolors.ROXO}Total Compra Reais: R$ {locale.currency(total_compra_brl, grouping=True, symbol=None)}{bcolors.FIM}\t\t\t {bcolors.ROXO}Total Compra em Dolar: USD {locale.currency(total_compra_usd, grouping=True, symbol=None)} | R$ {locale.currency(total_compra_usd_brl, grouping=True, symbol=None)}{bcolors.FIM}"
        )
        print(
            f"{bcolors.OCEANO}Total Venda Reais: R$ {locale.currency(total_venda_brl, grouping=True, symbol=None)}{bcolors.FIM}\t\t\t {bcolors.OCEANO}Total Venda em Dolar: USD {locale.currency(total_venda_usd, grouping=True, symbol=None)} | R$ {locale.currency(total_venda_usd_brl, grouping=True, symbol=None)}{bcolors.FIM}"
        )

        wr_file.write(
            f"Total Compra Reais: R$ {locale.currency(total_compra_brl, grouping=True, symbol=None)}\t\t\t Total Compra em Dolar: R$ {locale.currency(total_compra_usd, grouping=True, symbol=None)}\n"
        )
        wr_file.write(
            f"Total Venda Reais: R$ {locale.currency(total_venda_brl, grouping=True, symbol=None)}\t\t\t Total Venda em Dolar: R$ {locale.currency(total_venda_usd, grouping=True, symbol=None)}"
        )
        print("\n")
        wr_file.write("\n\n")

        print(
            f"{bcolors.VERDE}Total Geral Compra: R$ {locale.currency(total_geral_compra, grouping=True, symbol=None)}{bcolors.FIM}"
        )
        print(
            f"{bcolors.VERMELHO}Total Geral Venda: R$ {locale.currency(total_geral_venda, grouping=True, symbol=None)}{bcolors.FIM}"
        )
        wr_file.write(
            f"Total Geral Compra: R$ {locale.currency(total_geral_compra, grouping=True, symbol=None)}\n"
        )
        wr_file.write(
            f"Total Geral Venda: R$ {locale.currency(total_geral_venda, grouping=True, symbol=None)}\n\n"
        )
        print("\n")

    for k, v in saldos.items():
        if v["comissoes"]:
            print("\n")
            print(
                f'Moeda: {k} - Compra: {v["compra"]} - Venda: {v["venda"]} - Saldo: {v["saldo"]}'
            )
            wr_file.write(
                f'Moeda: {k} - Compra: {v["compra"]} - Venda: {v["venda"]} - Saldo: {v["saldo"]}\n'
            )
            counter = Counter()
            for i in v["comissoes"]:
                counter.update(i)
            for k, v in counter.items():
                print(f"Comissao: {k} \t {round(float(v), 8)}")
                wr_file.write(f"Comissao: {k} \t {round(float(v), 8)}\n")
        wr_file.write("\n")

try:
    make_json_file()
    print(f'{bcolors.VERDE}Arquivo Json para VUEjs gerado com sucesso!!!{bcolors.FIM}')
except Exception as e:
    print(f"{bcolors.VERMELHO}Problema em Gerar o Arquivo Json para VueJS:   {e}{bcolors.FIM}")