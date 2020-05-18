import csv
import re
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np
import pandas as pd
from loguru import logger
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'], 'size': 9})

logger.add("info.log", mode="w")

class DadosPrint(object):

    def __init__(self):
        self.plots = pd.DataFrame()
        self.limites = pd.DataFrame()
        self.dados = dict()
        self.line_color = [(0, 0, 0), (0.4, 0.4, 0.4), (0.5, 0.5, 0.5), (0.6, 0.6, 0.6), (0.7, 0.7, 0.7)]
        self.line_style = ["-", "--", "-.", ":", "-"]
        self.marker_type = ["None", "s", "o", "p", "*"]
        self.n_markers = [(0.0, 0.0), (0.1, 0.33), (0.05, 0.28), (0, 0.25), (0.15, 0.07)]
        self.style_limites = {"Range Min": "-", "Range Max": "-", 
                              "Alarme Min Min": "--", "Alarme Max Max": "--",
                              "Alarme Min": "-.", "Alarme Max": "-.", 
                              "Normal": ":"}
        self.color_limites = {"Range Min": (1, 0, 0), "Range Max": (1, 0, 0), 
                              "Alarme Min Min": (0.8, 0, 0.4), "Alarme Max Max": (0.8, 0, 0.4),
                              "Alarme Min": (0.6, 0, 0.4), "Alarme Max": (0.6, 0, 0.4), 
                              "Normal": (0, 0, 1)}
        self.linewidth = 0.8
        self.grid_color = (0.8, 0.8, 0.8)
        self.minor_grid_color = (0.85, 0.85, 0.85)

    def ler_dados(self, dados_print):
        for dado_print in dados_print:
            self.dados[dado_print] = []
            with open(dado_print, 'r') as csvfile:
                if re.match(".*\.rec", dado_print):
                    row_reader = csv.reader(csvfile, delimiter="\t")
                else:
                    row_reader = csv.reader(csvfile, delimiter=";")
                for row in row_reader:
                    self.dados[dado_print].append(row)

    def ler_limites(self, dados_limites):
        self.limites = pd.read_excel(dados_limites, header=0, sheet_name=0, na_values=np.NaN)

    def ler_plots(self, dados_plots):
        self.plots = pd.read_excel(dados_plots, header=0, shteet_name=0, na_values=np.NaN)

    def limpa_rec(self):
        for arquivo in self.dados.keys():
            if re.match(".*\.rec", arquivo):
                tempo_snap = []
                del_snap = []
                for i, linha in enumerate(self.dados[arquivo][:]):
                    if linha:
                        if re.match(".*LABDEV.*", linha[0]) and i == 0:
                            del_snap.append(i)
                        if re.match(".*LABDEV.*", linha[0]) and i != 0:
                            del_snap.append(i)
                            del_snap.append(i+1)
                            tempo_snap.append(self.dados[arquivo][i+2][0])
                    else:
                        del_snap.append(i)

                for index_del in del_snap[::-1]:
                    del self.dados[arquivo][index_del]

                t_overlap = []
                for t_snap in tempo_snap:
                    for i, linha in enumerate(self.dados[arquivo]):
                        if t_snap == linha[0]:
                            t_overlap.append(i)

                for i in range(1, len(t_overlap)+1, 2)[::-1]:
                    del self.dados[arquivo][t_overlap[i-1]:t_overlap[i]]

    def limpa_csv(self):
        for arquivo in self.dados.keys():
            if re.match(".*\.csv", arquivo) and not re.match('limites_plots.csv', arquivo) and not \
                    re.match('cfg_graficos.csv', arquivo):
                del self.dados[arquivo][0]

    def print_graficos(self):
        now = datetime.datetime.now()
        drt = "Graficos " + str(now.day) + "-" + str(now.month) + "-" + str(now.year) + " " + str(now.hour) + "h" + \
                str(now.minute) + "m" + str(now.second) + "s"
        os.mkdir(drt)
        
        for grafico in self.plots.iterrows():
            plot_x = []
            plot_y = []
            out_break = False
            nome_grafico = ""
            legend = []
            n_vars = 0
            for variavel_plt in grafico[1][1:].replace(np.nan, ''):
                if variavel_plt == '':
                    continue
                n_vars += 1 
                legend.append(re.sub(":.*", "", variavel_plt))
                nome_grafico = nome_grafico + re.sub(":.*", "", variavel_plt) + '--'

                for arquivo in self.dados.keys():
                    if out_break:
                        out_break = False
                        break
                    for j, header_var in enumerate(self.dados[arquivo][0]):
                        if header_var == variavel_plt:
                            plot_x.append([float(sublist[0]) for sublist in self.dados[arquivo][1:-1]])
                            plot_y.append([float(sublist[j]) for sublist in self.dados[arquivo][1:-1]])
                            out_break = True
                            break
            
            if plot_x == [] or plot_y == [] or len(plot_x) != n_vars or len(plot_y) != n_vars:
                logger.info(f"Não foi encontrado o gráfico {grafico[1][1:].replace(np.nan, '')}")
                continue
            
            limites = []
            for limite in self.limites.iterrows():
                if limite[1][0] == grafico[1][1]:
                    limites = self.limites.iloc[limite[0],:]

            self.plot_data(np.array(plot_x), np.array(plot_y), grafico[1]["y_label"], legend, limites)

            nome_grafico = re.sub(":.*", "", nome_grafico)
            save_dir = os.path.join(os.getcwd(), drt)
            plt.savefig(save_dir + '\\' + str(grafico[0]+1) + ". " + nome_grafico[0:-1] + ".pdf", bbox_inches="tight", pad=0.1)
            plt.close()

    def plot_data(self, plt_x, plt_y, nome_y, legend, limites):
        fig = plt.figure(figsize=(17/2.54, 5/2.54))
        max_x = -1e300
        min_x = 1e300
        for x in plt_x:
            max_x = max(x.max(), max_x)
            min_x = min(x.min(), min_x)

        i = 0
        for x, y in zip(plt_x, plt_y):
            plt.plot(x, y, linewidth=self.linewidth, linestyle=self.line_style[i], color=self.line_color[i],
                     marker=self.marker_type[i], mec=self.line_color[i], mfc=(1, 1, 1),
                     markevery=self.n_markers[i], ms=6)
            i = i + 1

        plot_min_y, plot_max_y = plt.ylim()
        limites = pd.DataFrame(limites).transpose().copy()
        limites.replace(np.nan, '')
        for column in limites.columns:
            if column == "Variável" or limites[column].iloc[0] == '':
                continue
            try:
                plt.plot([min_x, max_x], [limites[column], limites[column]], linewidth=self.linewidth*2/3, color=self.color_limites[column], linestyle=self.style_limites[column])
            except:
                continue

        plt.xlabel("Tempo (s)")
        plt.ylabel(nome_y)
        plt.minorticks_on()
        plt.grid(b=True, which="major", linestyle="-", color=self.grid_color, linewidth=self.linewidth/2)
        plt.grid(b=True, which="minor", linestyle=":", color=self.minor_grid_color, linewidth=self.linewidth/2)
        plt.xlim(min_x, max_x)
        plt.ylim(plot_min_y, plot_max_y)
        plt.legend(legend, loc="best")
        plt.tight_layout(pad=0.1)
