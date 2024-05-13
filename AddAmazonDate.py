#!/usr/bin/env python
# coding: utf-8

# In[2]:


from  selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# função que inclui data do anuncio pelo link do produto
def add_date_adv(dataframe):
    
    
    data = dataframe.copy()
    
    # iniciando as configurações do navegador
    service =Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    # desabilitando imagens para mais agilidade
    prefs = {"profile.managed_default_content_settings.images":2}
    options.add_experimental_option("prefs",prefs)

    #executando o Chrome de forma invisivel (headless)
    options.add_argument("--headless=new")

    # iniciando navegador
    driver = webdriver.Chrome(service = service, options = options)  


    data['Data publicação'] = ''

    for i in tqdm(range(len(data['link produto'])),position = 0, leave = True ): 

        
        driver.get(data['link produto'].iloc[i])

        pages_research = driver.find_elements(By.ID, 'productDetails_detailBullets_sections1')
        if len(pages_research) ==0:
            pages_research = driver.find_elements(By.XPATH, '//*[@id="detailBulletsReverseInterleaveContainer_feature_v2"]')

            if len(pages_research) == 0:
                pages_research = driver.find_elements(By.XPATH,'//*[@id="detailBulletsWrapper_feature_div"]')
        
        headers = [header.text.replace('\n', ',') for header in pages_research]

        headers = str(headers).split(',')


        for x in range(len(headers)):

            if 'Disponível para compra desde' in headers[x]:
                data['Data publicação'].iloc[i] = headers[x]
                
    return data


# In[ ]:




