# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 08:33:04 2021

@author: hbuzzi
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import sys

def get_holders_stock_DataFrame(mode, name, index_ofTable = None, table_Header = None, suffix = None):
    
    def get_tickers(): #Pega os tickers da ação
        if mode == 'link':
            if table_Header == None or index_ofTable == None:
                print('Erro: nenhum cabeçalho//n° da tabela informado em get_holders_stock_DataFrame')
                sys.exit()
                return
            else:
                #Se for 1 link, ele lê o HTML e retorna todas as tabelas do site, e para selecionar a tabela, o usuário indica qual sua posição com index_ofTable. Ele pega todas as siglas (tickers) do stock
                tickers = pd.read_html(name)[index_ofTable][table_Header]
                #Old syntax : tickers = pd.read_html(name)[index_ofTable].Ticker
                return tickers
        elif mode == 'stocks': 
            tickers = name
            return tickers
        else:
            print('Erro: modo inválido em get_holders_stock_DataFrame')
            sys.exit()
            return
        
    def create_holdersData(tickers):
        try:
            tickers.shape
            table = 1
        except AttributeError:
            table = 0
        
        if table == 1:     
            frames = []
            for ticker in tickers:
                if suffix != None:    
                    var = yf.Ticker(ticker + suffix)
                else:
                    var = yf.Ticker(ticker)
                frame = var.institutional_holders
                if type(frame) == type(None):
                    continue
                frame['Comp'] = var.ticker
                frames.append(frame)
            return pd.concat(frames)
        elif table == 0:
            var = yf.Ticker(tickers)
            frames = var.institutional_holders
            frames['Comp'] = var.ticker
            frames['% Out'] = 100*frames['% Out']
            return frames
            
    tickers = get_tickers()
    all_stockHolders = create_holdersData(tickers)
    return all_stockHolders

def create_Graph(mode, dataFrame, color_company, color_holder, metric_size, metric_edge, fig_Size):
    
    def create_node_size(metric):
        return [metric*v for v in dict(G.degree()).values()]
    
    def create_node_edge(metric):
        edgelist = nx.to_edgelist(G)
        return [metric*v[2]['% Out'] for v in edgelist]
    
    def create_node_colors(color_company, color_holder):
        colors = []
        for node in G:
            if node in dataFrame['Comp'].values:
                colors.append(color_company)
            else:
                colors.append(color_holder)
        return colors
    
    def node_margins():
        ax = plt.gca()
        ax.collections[0].set_edgecolor('#696969') ##Black
        return
        
    def draw_Graph(G, nd_size, edge_value, colors, fgS):
        fig = plt.figure(figsize=fgS)
        if mode == 'stocks':
            layout = nx.spring_layout(G)
        elif mode == 'link':
            layout = nx.spring_layout(G,k = 5*1/np.sqrt(len(G.nodes())), iterations = 2)
        nx.draw(G, with_labels = True, node_color=colors, node_size = nd_size, width = edge_value, pos = layout)
        nx.draw_networkx_edge_labels(G, layout, edge_labels = nx.get_edge_attributes(G,'% Out'))
        node_margins()
        fig.text(0,0,'Porcentagem total segurada: ' + str(sum(dataFrame['% Out'])) + '%', fontsize = 15)
        return
        
    G = nx.from_pandas_edgelist(dataFrame, 'Holder', 'Comp', edge_attr=True)
    draw_Graph(G = G, fgS = fig_Size, nd_size = create_node_size(metric_size), edge_value = create_node_edge(metric_edge), colors = create_node_colors(color_company, color_holder))
    return G
    
## Exemplo tabela B3 nos EUA (obrigatório EUA por causa do yfinances)
# site = 'https://en.wikipedia.org/wiki/List_of_companies_listed_on_B3' #Site com a lista de todas ações na B3 para usar no yahoo finance
# all_holders = get_holders_stock_DataFrame(mode = 'link', name = site, index_ofTable = 0, table_Header = 'Ticker', suffix = '.SA') #DataFrame com todos holders da(s) compania(s)
#Graph = create_Graph(all_holders,'red','yellow',50,50, (50,50)) #Retorna o Grafo

## Exemplo Ação AMBEV
stock = 'ABEV3.SA'
modo = 'stocks'
all_holders = get_holders_stock_DataFrame(mode = modo, name = stock)

## Montagem e visualização Grafo
Graph = create_Graph(modo,all_holders,'red','yellow',500,3, (12,12)) #Retorna o Grafo
print(sum(all_holders['% Out']))