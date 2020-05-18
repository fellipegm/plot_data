import os
import re
from funcs_corys_plot import DadosPrint


# Abre a pasta atual
current_dir = os.getcwd()

for dir_content in os.walk(current_dir):
    dados_print = list(filter(lambda path: (re.match('.*\.csv', path) or re.match('.*\.rec', path)),
            dir_content[2]))
    break

for dir_content in os.walk(current_dir):
    dados_limites = list(filter(lambda path: re.match('limites_plots.xlsx', path), dir_content[2]))[0]
    break

for dir_content in os.walk(current_dir):
    dados_plots = list(filter(lambda path: re.match('cfg_graficos.xlsx', path), dir_content[2]))[0]
    break

dados_arquivos = DadosPrint()
dados_arquivos.ler_dados(dados_print)
dados_arquivos.limpa_rec()
dados_arquivos.limpa_csv()
dados_arquivos.ler_limites(dados_limites)
dados_arquivos.ler_plots(dados_plots)
dados_arquivos.print_graficos()