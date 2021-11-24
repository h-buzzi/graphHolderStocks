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
    '''Função que cria um DataFrame com todos os Holders da ação.
    
    Possui 2 modos de operação, 'link' e 'stocks'. \n Stocks apenas precisa fornecer o nome da Ação desejada.
    Para link, forneça a url com a tabela das ações, em seguida forneça qual a posição da tabela no site de cima para baixo,
    qual o nome do cabeçalho e o suffixo caso precise
    
    Input Stock: Modo de operação, nome ação \n
    Input Link: Modo de operação, url, posição da tabela, cabeçalho da coluna, sufixo da string
    
    Output: DataFrame sobre informações dos Holders da empresa'''
    #################
    def get_tickers(): #Pega os tickers da ação
        if mode == 'link': # Confere o modo
            if table_Header == None or index_ofTable == None: # Confere se foi fornecido os requisitos para obter a tabela
                print('Erro: nenhum cabeçalho//n° da tabela informado em get_holders_stock_DataFrame') # Informa erro
                sys.exit() #Cancela o código
                return
            else:
                #Se for 1 link, ele lê o HTML e retorna todas as tabelas do site, e para selecionar a tabela, o usuário indica qual sua posição com index_ofTable. Ele pega todas as siglas (tickers) do stock
                tickers = pd.read_html(name)[index_ofTable][table_Header] # Tabela de siglas dos stocks
                #Old syntax : tickers = pd.read_html(name)[index_ofTable].Ticker
                return tickers
        elif mode == 'stocks': # Se for stock
            tickers = name # a Sigla da ação é o nome fornecido
            return tickers
        else:
            print('Erro: modo inválido em get_holders_stock_DataFrame') # Se forneceu um modo inválido, printa o erro
            sys.exit() #Cancela o código
            return
    ################# 
    def create_holdersData(tickers):
        try: # Irá tentar obter o shape das ações
            tickers.shape #Se tiver
            table = 1 #É uma tabela
        except AttributeError: #Se não tiver shape ele levanta AttributeError, logo, é apenas 1 ação
            table = 0 #Não é tabela
        
        if table == 1: # Para tabela
            frames = [] #pré-alocação do DataFrame
            for ticker in tickers: #Percorre todas as ações
                if suffix != None: #Se tiver sufixo...
                    var = yf.Ticker(ticker + suffix) #...adiciona no nome da ação e pega seu Ticker no Yahoo Finance
                else: #Não tem sufixo
                    var = yf.Ticker(ticker) #Pega pelo próprio nome o Ticker no Yahoo Finance
                frame = var.institutional_holders #Pega as informações dos holders
                if type(frame) == type(None): #Se não tiver informação sobre ação
                    continue #Pula para próxima ação
                frame['Comp'] = var.ticker #Salva o nome da ação em seus respectivos holders
                frames.append(frame) #Adiciona no dataFrame
            frames['% Out'] = 100*frames['% Out'] #Ajusta o float para representar a porcentagem em %
            return pd.concat(frames) #Concatena o dataFrame para ajeitá-lo
        
        elif table == 0: # Para 1 ação
            var = yf.Ticker(tickers) #Pega o ticker da ação
            frames = var.institutional_holders #Pega as informações dos holders
            frames['Comp'] = var.ticker #Salva o nome da ação em seus respectivos holders
            frames['% Out'] = 100*frames['% Out'] #Ajusta o float para representar a porcentagem em %
            return frames #Retorna o DataFrame da Ação
    #################
            
    tickers = get_tickers() #Pega a(s) sigla(s) das ações
    all_stockHolders = create_holdersData(tickers) #Fornece as siglas e cria o DataFrame
    return all_stockHolders

def create_Graph(mode, dataFrame, color_company, color_holder, metric_size, metric_edge, fig_Size):
    '''Função para criação e exibição de Grafo dos holders da empresa
    
    Cria um grafo com layouts diferente dependendo da quantidade de nodos.
    
    Input: modo de operação, dataFrame dos holders, a cor do nodo da ação, a cor do nodo dos holders, métrica do tamanho dos nodos,
     métrica da grossura das arestas, métrica do tamanho da imagem
     
    Output: Objeto Grafo (e exibição do grafo pelo plot)'''
    #################
    def create_node_size(metric): #Cria o tamanho do nodo
        #Ele pega o valor da quantidade de arestas que o nodo possui e multiplica pela métrica para criar o tamanho.
        #Logo, quanto mais arestas conectadas ele possuir, maior será.
        return [metric*v for v in dict(G.degree()).values()] #Retorna o vetor de tamanho para cada nodo
    #################
    def create_node_edge(metric): #Cria tamanho da aresta
        edgelist = nx.to_edgelist(G) #Pega todas as arestas
        #Pega cada aresta, pega o valor da % Out que ela possui e multiplica pela métrica para criar o tamanho.
        #Logo, quanto maior sua % de retenção sobre a ação, mais grossa sua aresta
        return [metric*v[2]['% Out'] for v in edgelist]  #Retorna o vetor de tamanho para cada aresta
    #################
    def create_node_colors(color_company, color_holder): #Cria as cores do grafo
        colors = []#Pré-alocação
        for node in G: #Para cada nodo
            if node in dataFrame['Comp'].values: #Se for nodo da companhia/ação
                colors.append(color_company) #Coloca cor da companhia
            else:
                colors.append(color_holder) #Se for o nodo do holder, cor do holder
        return colors #Retorna vetor de cores para cada nodo
    #################
    def node_margins(): #Margem dos nodos
        ax = plt.gca()
        ax.collections[0].set_edgecolor('#696969') #Define as margens de cada nodo para Preto
        return
    #################    
    def draw_Graph(G, nd_size, edge_value, colors, fgS): #Plota o grafo
        """Plota o Grafo.
    
        Recebe o objeto grafo, seu tamanho do nodo, seu tamanho da aresta, as cores, e tamanho da figura."""
        fig = plt.figure(figsize=fgS) #Cria a figura
        if mode == 'stocks': #Se for stocks
            layout = nx.spring_layout(G) #Cria o spring layout padrão
        elif mode == 'link': #Se for tabela
            layout = nx.spring_layout(G,k = 5*1/np.sqrt(len(G.nodes())), iterations = 2) #Cria um layout que facilita visualização
        nx.draw(G, with_labels = True, node_color=colors, node_size = nd_size, width = edge_value, pos = layout) #Chama a função do networkx que plota o grafo com as especificações
        nx.draw_networkx_edge_labels(G, layout, edge_labels = nx.get_edge_attributes(G,'% Out')) #Coloca as labels em cada edge
        node_margins() #Coloca as margens pretas
        if mode == 'stocks': #Se for só 1 stock
            fig.text(0,0,'Porcentagem total segurada: ' + str(sum(dataFrame['% Out'])) + '%', fontsize = 15) #Printa também a porcentagem total retida no exterior
        return
        
    G = nx.from_pandas_edgelist(dataFrame, 'Holder', 'Comp', edge_attr=True) #Cria o grafo a partir do DataFrame
    draw_Graph(G = G, fgS = fig_Size, nd_size = create_node_size(metric_size), edge_value = create_node_edge(metric_edge), colors = create_node_colors(color_company, color_holder))
    return G
    
## Exemplo tabela B3 nos EUA (obrigatório EUA por causa do yfinances)
# site = 'https://en.wikipedia.org/wiki/List_of_companies_listed_on_B3' #Site com a lista de todas ações na B3 para usar no yahoo finance
# modo = 'link'
# all_holders = get_holders_stock_DataFrame(mode = modo, name = site, index_ofTable = 0, table_Header = 'Ticker', suffix = '.SA') #DataFrame com todos holders da(s) compania(s)
#Graph = create_Graph(all_holders,'red','yellow',50,3, (50,50)) #Retorna o Grafo

## Exemplo Ação AMBEV
stock = 'ABEV3.SA' ## Stock
modo = 'stocks' ## Modo de operação para stock
all_holders = get_holders_stock_DataFrame(mode = modo, name = stock) ##Cria DataFrame com todos os holders

## Montagem e visualização Grafo
Graph = create_Graph(modo,all_holders,'red','yellow',500,3, (12,12)) #Retorna o Grafo