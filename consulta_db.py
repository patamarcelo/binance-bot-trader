#!/usr/local/bin/python3
from database import create_tables, add_notas, search_notas
from database import select_all_trades, select_all_monthyear, select_moeda_trades
import database
from models import BinanceTrades
from colors import bcolors
import collections

import locale

locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")

# trades_binance = database.select_all_trades()


def format_reais(valor):
    return (
        f"{bcolors.VERDE}R$ {locale.currency(valor, grouping=True, symbol=None)}{bcolors.FIM}"
        if valor > 0
        else f"{bcolors.VERMELHO}R$ {locale.currency(valor, grouping=True, symbol=None)}{bcolors.FIM}"
    )

def format_reais_nocolor(valor):
    return (
        f"R$ {locale.currency(valor, grouping=True, symbol=None)}"   
    )

def atualizacao_saldo_moeda_bnb_comi():
    if comissao_moeda == "BNB" and preco_medio.get("BNB") != None:
        quant = preco_medio.get("BNB")[0]
        val = preco_medio.get("BNB")[1]
        new_quant = quant - comissao
        update_preco_medio_comissao = {
                "BNB": [new_quant, val]
            }
        preco_medio.update(update_preco_medio_comissao)

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


def filtro_pesquisa_db(moeda_pesquisa):
    meses_ano = database.select_all_monthyear()
    if len(moeda_pesquisa) > 2:
        trades_binance = database.select_moeda_trades(moeda_pesquisa)    

    else:
        trades_binance = database.select_all_trades()
    preco_medio = {}
    moeda_comissao = []
    lucro_prejuízo_acumulado = 0
    lucro_prejuízo_acumulado_valores = {}
    for i in meses_ano:
        date_db = i[1].strftime("%Y-%m")
        print("\n")
        mes_corrente = f"{i[3]} - {i[4]}"
        print(f'{bcolors.AMARELO}{mes_corrente}{bcolors.FIM}')
        lucros_acumulado_mes = 0
        prejuizo_acumulado_mes = 0
        lucro_prejuzio_acumulado_mes = 0
        vendas_mes = False
        compras_mes = False
        total_vendas_mes = 0
        total_compras_mes = 0
        for i in trades_binance:
            j = BinanceTrades(
                i[0],
                i[1],
                i[2],
                i[3],
                i[4],
                i[5],
                i[6],
                i[7],
                i[8],
                i[9],
                i[10],
                i[11],
                i[12],
                i[13],
                i[14],
                i[15],
            )
            # print(j)
            comissao_moeda = j.comissao_moeda
            moeda_comissao.append(comissao_moeda)
            comissao = j.comissao
            chech_date = j.data.strftime("%Y-%m")
            moeda = j.moeda
            if "USD" in moeda:
                moeda = moeda.replace("USDT", "")
            if "BRL" in moeda:
                moeda = moeda.replace("BRL", "")
            quantidade_negociada_calculo = j.quantidade_negociada
            quantidade_negociada_calculo = (
                quantidade_negociada_calculo - comissao
                if moeda[:len(comissao_moeda)] == comissao_moeda
                else quantidade_negociada_calculo
            )
            # valor_negociado_calculo = j.valor_negociado
            valor_negociado_reais = j.valor_negociado_reais
            valor_negociado_calculo = valor_negociado_reais
            valor_total_reais = j.total_reais


            if chech_date == date_db:
                valor_negociado = (
                    f"USD {locale.currency(j.valor_negociado, grouping=True, symbol=None)}"
                    if "USD" in j.moeda[-4:]
                    else f"R$ {locale.currency(j.valor_negociado, grouping=True, symbol=None)}"
                )
                valor_total = (
                    f" R$ {locale.currency(j.total_reais, grouping=True, symbol=None)}"
                )

                if j.tipo == "BUY":
                    compras_mes = True
                    total_compras_mes += valor_total_reais
                    print(
                        f"{bcolors.VERDE}{j.moeda} \t\t {BinanceTrades.format_date(j.data)} \t\t Quant: {j.quantidade_negociada:.6f} \t\tPreço Orig: {valor_negociado} \tPreço Reais: {format_reais_nocolor(valor_negociado_reais)}  \t\t USDT {j.cotacao_dolar}\tComissão: {j.comissao:.6f} | {j.comissao_moeda}\nTotal: {valor_total}{bcolors.FIM}"
                    )

                    if preco_medio.get(moeda) == None:
                        calc_preco_medio = (
                            quantidade_negociada_calculo * valor_negociado_calculo
                        ) / quantidade_negociada_calculo
                        preco_medio[f"{moeda}"] = [
                            quantidade_negociada_calculo,
                            calc_preco_medio,
                        ]
                    else:
                        quantidade_atual = preco_medio.get(moeda)[0]
                        media_compra_atual = preco_medio.get(moeda)[1]
                        quantidade_atualizada = round(
                            float((quantidade_negociada_calculo + quantidade_atual)), 6
                        )
                        novo_preco_medio = (
                            (quantidade_atual * media_compra_atual)
                            + (quantidade_negociada_calculo * valor_negociado_calculo)
                        ) / quantidade_atualizada
                        update_preco_medio = {
                            moeda: [quantidade_atualizada, novo_preco_medio]
                        }
                        preco_medio.update(update_preco_medio)
                    print(
                        f"Quantidade Atual: {preco_medio.get(moeda)[0]} | Preço Médio: R$ {locale.currency(preco_medio.get(moeda)[1], grouping=True, symbol=None)}"
                    )

                else:
                    vendas_mes = True
                    total_vendas_mes += valor_total_reais
                    print(
                        f"{bcolors.VERMELHO}{j.moeda} \t\t {BinanceTrades.format_date(j.data)} \t\t Quant: {j.quantidade_negociada:.6f} \t\tPreço Orig: {valor_negociado} \tPreço Reais: {format_reais_nocolor(valor_negociado_reais)} \t\t USDT {j.cotacao_dolar}\tComissão: {j.comissao:.6f} | {j.comissao_moeda}\nTotal: {valor_total}{bcolors.FIM}"
                    )
                    if preco_medio.get(moeda) == None:
                        print(f"{bcolors.AMARELO}Moeda {j.moeda} teve venda sem antes ter comprado...{bcolors.FIM}")
                    else:
                        quantidade_atual      = preco_medio.get(moeda)[0]
                        media_compra_atual    = preco_medio.get(moeda)[1]
                        quantidade_atualizada = round(
                            float((quantidade_atual - quantidade_negociada_calculo)), 6
                        )
                        if quantidade_atual > 0.000000: 
                            update_preco_medio = {
                                moeda: [quantidade_atualizada, media_compra_atual]
                            }
                            preco_medio.update(update_preco_medio)
                            print(
                                f"Quantidade Atual: {quantidade_atualizada:.6f}  | Preço Médio: R$ {locale.currency(preco_medio.get(moeda)[1], grouping=True, symbol=None)}"
                            )
                        else: 
                            update_preco_medio = {
                                moeda: [0.00000, media_compra_atual]
                            }
                            preco_medio.update(update_preco_medio)

                        lucro_prejuizo = (valor_total_reais) - (
                            media_compra_atual * quantidade_negociada_calculo
                        )
                        # print(f"{valor_total_reais} - ({media_compra_atual} * {quantidade_negociada_calculo})")
                        # print(f'Lucro / Prejuízo: R$ {locale.currency(lucro_prejuizo, grouping=True, symbol=None)}')
                        print(f'Lucro Prejuízo: {format_reais(lucro_prejuizo)}')
                        if lucro_prejuizo > 0:
                            lucros_acumulado_mes += lucro_prejuizo
                            print(format_reais(lucros_acumulado_mes))
                        else:
                            prejuizo_acumulado_mes += lucro_prejuizo
                            print(format_reais(prejuizo_acumulado_mes))
        if compras_mes or vendas_mes:
            print(f"\n\n{bcolors.AZUL}=========================================={bcolors.FIM}\n{mes_corrente}\n")
        if compras_mes:
            print(f"Total Compras: {format_reais(total_compras_mes)}\n")

        if vendas_mes:
            lp_acum = lucros_acumulado_mes + prejuizo_acumulado_mes
            lucro_prejuízo_acumulado_valores.update({mes_corrente : lp_acum})
            lucro_prejuízo_acumulado += lp_acum
            print(f"Total Vendas: {format_reais_nocolor(total_vendas_mes)}\n")
            print(
                f"{bcolors.VERMELHO}Prejuízo Acumulado Mês: {format_reais(prejuizo_acumulado_mes)}{bcolors.FIM}"
            )
            print(
                f"{bcolors.VERDE}Lucro Acumulado Mês: {format_reais(lucros_acumulado_mes)}{bcolors.FIM}"
            )
            print('\n')
            print(f"Lucro/Prejuízo Mês: {format_reais(lp_acum)}")
            print(f"\n{bcolors.AZUL}=========================================={bcolors.FIM}")


    print(f"\n\n{bcolors.AZUL}=========================================={bcolors.FIM}\n\n")
    for k,v in lucro_prejuízo_acumulado_valores.items():
        print(f'{k}: \t\t{format_reais(v)}')
    print(f'\nLucro/Prejuízo Geral: {format_reais(lucro_prejuízo_acumulado)}')

    print(f"\n\n{bcolors.AZUL}=========================================={bcolors.FIM}\n\n")
    preco_medio_ordem = collections.OrderedDict(sorted(preco_medio.items()))
    for k, v in preco_medio_ordem.items():
        quantidade_dict = v[0]
        preco_medio_dict = v[1]
        # if 'USD' in k:
        # print(f'{k}: Quantidade: {quantidade_dict} | Preço Médio: USDT {locale.currency(preco_medio_dict, grouping=True, symbol=None)}')
        # else:
        print(
            f"{k}\t: Quantidade: {quantidade_dict:.6f} \t| Preço Médio: R$ {locale.currency(preco_medio_dict, grouping=True, symbol=None)}"
        )
    print(f"\n\n{bcolors.AZUL}=========================================={bcolors.FIM}")


# for i in list(set(moeda_comissao)):
#     print(i)
# # id_db,
# #         moeda,
# #         moeda_operacao,
# #         valor_negociado,
# #         tipo,
# #         data,
# #         quantidade_negociada,
# #         valor_total,
# #         cotacao_dolar,
# #         total_reais,
# #         comissao,
# #         comissao_moeda,
# #         id_order,
# #         id_trade,


menu = f"""
Escolha a opcao abaixo:
{bcolors.AMARELO}1){bcolors.FIM} Filtre 1 Moeda ou deixe em branca para todas!!
{bcolors.AMARELO}2){bcolors.FIM} Sair

Sua Escolha: 
"""


def app():
    while (user_input := input(menu)) != "2":
        if user_input:
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
            filtro_pesquisa_db(user_input.upper())
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
        else:
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
            filtro_pesquisa_db('0')
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
            print(f'{bcolors.ROXO}{"========" * 30}{bcolors.FIM}')
if __name__ == "__main__":
    app()