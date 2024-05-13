#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import pandas as pd
import re
from datetime import datetime

def extrair_data(data_str):
    
    # Expressão regular para encontrar a data no formato "dia mês ano"
    pattern = r'(\d+)\s+(\w+)\s+(\d{4})'
    
    match = re.search(pattern, data_str)
    
    if match:
        day_str, month_str, year_str = match.groups()
        # Mapeia o nome do mês para o número do mês
        months = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
            'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        month = months[month_str.lower()]
        # Formata a data no formato 'ano-mês-dia'
        
        data = datetime(int(year_str), int(month), int(day_str))
        return data
    else:
        return None



# Função para extrair o número de parcelas
def extrair_n_parcelas(texto):
    
    pattern = r'(\d+)\s*x'
    match = re.search(pattern, texto)
    
    if match:
        return int(match.group(1))
    else:
        return 0
    
    
    
    # função para extrair o valor junto a "sem juros"    
def extrair_valor_parcelas(texto):   
    pattern = r'R\$\s*([\d.,]+)\s*(com juros|sem juros)'

    
    valor = re.search(pattern, texto)
    if valor:
        return valor.group(1)
    else:
        return 0

def n_avaliacao_seller(texto):
    pattern = r'(\d+)\s+avaliações'

    qtde = re.search(pattern, texto)
    if qtde:
        return qtde.group(1)
    else:
        return None
    
    
def trata_dados(dataframe: pd.DataFrame, item):
    
    data = dataframe.copy()
    
    # adiciona coluna de item pesquisado
    data['item'] = item
    
    # processo trasnformar a lista de categorias em colunas
    data['Categoria0'] = 0    
    data['Categoria1'] = 0
    data['Categoria2'] = 0
    data['Categoria3'] = 0
    data['Categoria4'] = 0
    data['Categoria5'] = 0
    data['Categoria6'] = 0
    
     
    
    # adiciona as categorias da lista nas colunas a cada linha
    for i in range(len(data['categoria'])):

        for x in range(len(data['categoria'].iloc[i])):
            data[f'Categoria{x}'].iloc[i] = data['categoria'].iloc[i][x]


    # repete a ultima categoria nas colunas de categoria restante
    for i in range(len(data['categoria'])):

            for x in range(1,7):
                if data[f'Categoria{x}'].iloc[i] == 0:
                    data[f'Categoria{x}'].iloc[i] = data[f'Categoria{x-1}'].iloc[i]
                    
                    
    # coverte a coluna de data publicação de texto para formato data
    data['Data publicação'] = data['Data publicação'].apply(extrair_data)
    
    # extraindo qtde parcelas
    data['n parcelas'] = data['parcelas'].apply(lambda x: int(extrair_n_parcelas(x)))
    
    # extraindo valor parcelas
    data['valor parcelas'] = data['parcelas'].apply(lambda x: extrair_valor_parcelas(str(x)))
    
    data.drop(['parcelas'],axis = 1, inplace = True)
    
    # extraindo numero de avaliações vendedor
    data['N avaliação vendedor'] = data['Avaliação vendedor'].apply(lambda x: n_avaliacao_seller(str(x)))
    
    # extraindo numero de avaliações do produto
    data['qtde avaliacao produto'] = data['qtde avaliacao produto'].apply(lambda x: n_avaliacao_seller(str(x)))
    
    # corrigindo coluna preço
    data['preço'] = data['preço'].apply(lambda x: x.replace(f'\n', ','))
    
    data['escolha amazon'] = data['escolha amazon'].apply(lambda x: x.replace('Escolha\nda Amazon', 'sim'))
    
    data['loja'] = data['loja'].apply(lambda x: x.replace('Visite a loja ', '').replace('Marca: ', ''))
    
    data.rename(columns={'loja': 'marca'}, inplace = True)
    
    data.drop(['categoria'],axis = 1, inplace = True)
    data.drop(['Avaliação vendedor'],axis = 1, inplace = True)
    
    return data

