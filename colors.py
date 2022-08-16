#!/usr/local/bin/python3

# as
class bcolors:
    CEND      = "\33[0m"
    CBOLD     = "\33[1m"
    CITALIC   = "\33[3m"
    CURL      = "\33[4m"
    CBLINK    = "\33[5m"
    CBLINK2   = "\33[6m"
    CSELECTED = "\33[7m"

    CBLACK  = "\33[30m"
    CRED    = "\33[31m"
    CGREEN  = "\33[32m"
    CYELLOW = "\33[33m"
    CBLUE   = "\33[34m"
    CVIOLET = "\33[35m"
    CBEIGE  = "\33[36m"
    CWHITE  = "\33[37m"

#backgournd Color
    CBLACKBG  = "\33[40m"
    CREDBG    = "\33[41m"
    CGREENBG  = "\33[42m"
    CYELLOWBG = "\33[43m"
    CBLUEBG   = "\33[44m"
    CVIOLETBG = "\33[45m"
    CBEIGEBG  = "\33[46m"
    CWHITEBG  = "\33[47m"

    CGREY    = "\33[90m"
    RED    = "\33[91m"
    CGREEN2  = "\33[92m"
    CYELLOW2 = "\33[93m"
    CBLUE2   = "\33[94m"
    CVIOLET2 = "\33[95m"
    CBEIGE2  = "\33[96m"
    CWHITE2  = "\33[97m"

#backgournd Color
    CGREYBG   = "\33[100m"
    CREDBG2   = "\33[101m"
    CGREENBG2 = "\33[102m"
    CYELLOWBG2 = "\33[103m"
    CBLUEBG2   = "\33[104m"
    CVIOLETBG2 = "\33[105m"
    CBEIGEBG2  = "\33[106m"
    CWHITEBG2  = "\33[107m"

    ROSA      = "\033[95m"
    ROXO      = "\033[94m"
    OCEANO    = "\033[96m"
    VERDE     = "\033[92m"
    AMARELO   = "\033[93m"
    AZUL      = "\033[104m"
    PISCINA   = "\033[46m"
    VERMELHO  = "\033[91m"
    FIM       = "\033[0m"
    BOLD      = "\033[1m"
    ITALIC    = "\033[3m"
    UNDERLINE = "\033[4m"



if __name__ == '__main__':
    print(f'{bcolors.CBLUEBG2}{bcolors.AMARELO} Teste de cores{bcolors.FIM}')
    print(f'{bcolors.CVIOLETBG}{bcolors.AMARELO} Teste de cores{bcolors.FIM}')
    print(f'{bcolors.CBEIGEBG}{bcolors.AMARELO} Teste de cores{bcolors.FIM}')
    print(f'{bcolors.CREDBG2}{bcolors.AMARELO} Teste de cores{bcolors.FIM}')