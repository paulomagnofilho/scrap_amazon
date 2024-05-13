#!/usr/bin/env python
# coding: utf-8

# In[10]:


import requests
from bs4 import BeautifulSoup
import re
from  selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
from tqdm import tqdm
from progressbar import ProgressBar

class Amazon():
    
    def __init__(self, item, pages):
        self.item = item
        self.pages = pages
        
        if ' ' in self.item:
            self.item = self.item.replace(' ', '+')

        # url caso seja uma palavra
        else:
            self.item = self.item
        
    # método que retorna as urls das paginas
    def amazon_urls(self):
        print('Extraindo urls...')


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

        # lista para adicionar as urls
        url_list = []
        
        # url da primeira página
        url = f'https://www.amazon.com.br/s?k={self.item}'

        # adicionando a url na lista
        url_list.append(url)

        time.sleep(0.1)
        # barra de progresso
        progress_bar = ProgressBar().start()
        progress_bar.update((1/self.pages)*100)

        if self.pages == 1:
            return url_list


        # abrindo a pagina 
        driver.get(url)

        # extraindo a url das páginas no rodapé
        pages_research = driver.find_elements(By.CLASS_NAME, 's-pagination-item.s-pagination-button')

        # extraindo a url da página 2
        url2 = pages_research[0].get_attribute('href')

        # adicionado a url a lista
        url_list.append(url2)

        # variavel para incremento e usar no slice da url da pagina seguinte
        n = 2


        progress_bar.update((2/self.pages)*100)


        if self.pages == 2:
            return url_list

        elif self.pages >2:
            for i in range(self.pages-2):

                time.sleep(0.1)

                progress_bar.update(((i+2)/self.pages)*100)

                # inicia o navegador
                service = Service()
                #options = webdriver.ChromeOptions()
                #driver2 = webdriver.Chrome(service = service, options = options)   
                driver.get(url2)

                # extrai a classe com as urls da pagina no rodapé
                pages_research2 = driver.find_elements(By.CLASS_NAME, 's-pagination-item.s-pagination-button')

                # extrai a url da página seguinte
                url2 = pages_research2[n].get_attribute('href')

                # adiciona a url a lista de urls
                url_list.append(url2)

                # fecha a página
                #driver2.close()

                # incremento ao slice
                n = n+1
        else:
            pass


        # fecha a primeira página
        driver.close()
        return url_list
    
    # método que faz raspagem na amazon conforme url
    def amazon_scrap(self,url):

        # lista para receber dicionario com os dados dos produto
        products_data = []

        # procedimento para iniciar o navegador
        service = Service()
        options = webdriver.ChromeOptions()

        # desabilitando imagens para mais agilidade
        prefs = {"profile.managed_default_content_settings.images":2}
        options.add_experimental_option("prefs",prefs)

        #executando o Chrome de forma invisivel (headless)
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(service = service, options = options)
        #url = f'https://www.amazon.com.br/s?k={item}'

        # abrindo o Chrome
        driver.get(url)

        # lista para armazenar os dados dos produtos
        products_list = []

        # na amazon os patrocinados aparecem nesta ordem em todas as páginas
        patrocinados = [0,1,2,3,20,21,22,23,56,57,58,59]
        patrocinados = list(map(lambda x: x*2, patrocinados))

        # extraindo as url dos produtos
        url_products = driver.find_elements(By.CLASS_NAME, 'a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')



        #executando o Chrome de forma invisivel (headless)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver2 = webdriver.Chrome(service = service, options = options)
        # iteração nas urls dos produtos
        # as urls aparecem duplicadas, então, itera a cada 2
        for i in tqdm(range(0,len(url_products),2), position = 0, leave = True):

            url_prod = url_products[i].get_attribute('href')
            # abrindo o navegador Chrome da url do produto

            driver2.get(url_prod)
            
            try:
                # extraindo o nome do produto
                product = driver2.find_element(By.XPATH,'//*[@id="productTitle"]').text
            except NoSuchElementException:
                product = 'indisponível'
            # se produto patrocinado
            ptr = 'sim' if i in patrocinados else 'não'

            # extraindo o preço
            # dependendo da página o preço esta em um local diferente do código
            try:
                price = driver2.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]').text
            except NoSuchElementException:

                try:
                    price = driver2.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]').text
                except NoSuchElementException:
                    price = 'Não disponível'

            # avaliação do produto, nem todos produtos possuem
            try:

                eval_product = driver2.find_element(By.XPATH, '//*[@id="acrPopover"]/span[1]/a/span')
                eval_product = eval_product.text
            except:
                eval_product = ''

            # quantidade de avaliações, nem todos possuem
            try:
                quant_eval = driver2.find_element(By.XPATH, '//*[@id="acrCustomerReviewText"]').text
            except:
                quant_eval = ''

            ###################################################################################
            # o vendedor do produto pode aparecer de duas formas diferentes
            # em vendido por como um link, ou sendo a amazon sem link

            # extraindo o vendedor em vendido por como link
            try:
                seller = driver2.find_element(By.XPATH, '//*[@id="sellerProfileTriggerId"]').text
                url_seller = driver2.find_element(By.XPATH, '//*[@id="sellerProfileTriggerId"]').get_attribute('href')

                # abrindo o navegador Chrome da url do vendedor
                #driver3 = webdriver.Chrome(service = service, options = options)
                driver2.get(url_seller)

                # avaliação (%) com a quantidade e nota do vendedor
                eval_seller = driver2.find_element(By.CLASS_NAME, 'a-link-normal.feedback-detail-description.no-text-decoration').text
                
                rating_seller = driver2.find_element(By.ID, 'effective-timeperiod-rating-year-description').text
                if rating_seller:
                    pass
                else:
                    rating_seller = driver2.find_element(By.ID,'effective-timeperiod-rating-lifetime-description').text
                
                
                #driver3.close()

            except NoSuchElementException:

                # vendido por amazon sem link
                try:
                    # path com o nome da amazon, retorna sem avaliações
                    driver2.get(url_prod)
                    seller = driver2.find_element(By.XPATH, '//*[@id="merchantInfoFeature_feature_div"]/div[2]/div/span').text
                    eval_seller = ''
                    rating_seller = ''
                except:
                    seller = ''
                    eval_seller = ''
                    rating_seller = ''


            # caso o vendido por não tenha, aparece link da loja 
            try:    
                driver2.get(url_prod)
                shop = driver2.find_element(By.XPATH, '//*[@id="bylineInfo"]').text
            except:
                shop = ''

            ################################################################################################
            driver2.get(url_prod)

            # quantidade de imagens
            images = driver2.find_elements(By.CLASS_NAME, 'a-spacing-small.item.imageThumbnail.a-declarative')
            images = len(images)

            # quantidade de vídeos
            try:
                videos = driver2.find_elements(By.CLASS_NAME, 'a-spacing-small.item.videoThumbnail.a-declarative')
                videos = len(videos)
            except:
                videos = ''

            # parcelas, se possui
            try:
                installments = driver2.find_element(By.XPATH, '//*[@id="installmentCalculator_feature_div"]/span[1]')
                installments = installments.text

            except:
                installments = ''

            # quantidade de compras produto
            try:
                purchases = driver2.find_element(By.XPATH, '//*[@id="social-proofing-faceout-title-tk_bought"]').text

            except:
                purchases = ''

            #categoria do produto
            try:
                categories = []
                category = driver2.find_elements(By.CLASS_NAME, 'a-link-normal.a-color-tertiary')
                for x in category:
                    categories.append(x.text)

            except:
                category = ''

            # se é escolha amazon
            try:
                amazon_pick = driver2.find_element(By.CLASS_NAME, 'a-size-small.aok-float-left.ac-badge-rectangle').text

            except:
                amazon_pick = 'não'




            products_list.append({'produto':product, 'preço':price,'patrocinado':ptr,'avaliacao produto':eval_product, 
                                  'qtde avaliacao produto':quant_eval,'vendedor': seller,'loja':shop, 'Avaliação vendedor': eval_seller,
                                  'Nota do vendedor': rating_seller,'qtde imagens':images,'qtde videos':videos ,'parcelas':installments, 'qtde compras':purchases,
                                  'categoria':categories, 'escolha amazon':amazon_pick, 'link produto': url_prod})




            #driver2.close()
            

        driver2.close()
        driver.quit()
        return pd.DataFrame(products_list)

        ################################################


        
        
    def executa_scrap(self):
    
        # dataframe principal para mesclar
        df_amazon = pd.DataFrame()

        # extraindo as urls das páginas pela função amazon_urls
        self.list_url = self.amazon_urls()
        print(f'Raspando páginas...')
        
        # iterando na lista de urls e utilizando a barra de progresso
        for pagina in tqdm(range(len(self.list_url)),position = 1, leave = True):
            

            print(f'Pagina {pagina+1}...')
            df_pagina = self.amazon_scrap(self.list_url[pagina])
            df_amazon = pd.concat([df_amazon, df_pagina], ignore_index = True)

        return df_amazon

