import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
#from openpyxl import *
from IPython.display import HTML
import webbrowser
import os
from datetime import datetime, timedelta

#### BASES ####

dataHoje = datetime.today().strftime('%m-%d-%Y')

url_moedas = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/Moedas?$top=100&$format=json&$select=simbolo,nomeFormatado,tipoMoeda"

base_Moedas1 = pd.read_json(url_moedas)
base_Moedas1 = pd.json_normalize(base_Moedas1['value'])
base_Moedas = pd.DataFrame(base_Moedas1)

base_Moedas_sigla = list(set(base_Moedas["simbolo"]))
base_Moedas_sigla.sort()

#### ERROR HANDLER ####

url_teste = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda='USD',dataCotacao='" + dataHoje + "')?&$top=100&$format=json&$select=paridadeCompra,paridadeVenda,cotacaoCompra,cotacaoVenda,dataHoraCotacao,tipoBoletim"

base_chk1 = pd.read_json(url_teste)
base_chk1 = pd.json_normalize(base_chk1['value'])
base_chk = pd.DataFrame(base_chk1)


if base_chk.empty:
    messagebox.showinfo(title = "Sem atualização ainda", message = "Boletim diário ainda não foi divulgado pelo BACEN")
    while base_chk.empty:
        dataHoje = datetime.today() - timedelta(days=dia_atraso)
        dataHoje = dataHoje.strftime('%m-%d-%Y')
        url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda='USD',dataCotacao='" + dataHoje + "')?&$top=100&$format=json&$select=paridadeCompra,paridadeVenda,cotacaoCompra,cotacaoVenda,dataHoraCotacao,tipoBoletim"
        base_chk1 = pd.read_json(url)
        base_chk1 = pd.json_normalize(base_chk1['value'])
        base_chk = pd.DataFrame(base_chk1)
        dia_atraso = dia_atraso + 1
        if not base_chk.empty:
            break

#### FORM ####

class conversor:

    def __init__(self):
        
        root = Tk()
        root.geometry('400x650')

        self.currency = StringVar()
        self.ValorCRY = StringVar()
        self.ValorBRL = StringVar()
        self.CotacaoVenda = StringVar()
        self.CotacaoCompra = StringVar()
        self.DataHora = StringVar()
        self.TipoBol = StringVar()
        self.CRYFinal = StringVar()
        self.BRLFinal = StringVar()        
        self.NomeMoeda = StringVar()
        
        root.title('API consulta Boletim Cambio - Banco Central')
        Label(root, text = "Moeda").pack(anchor=W, pady = 5, padx = 10)
        ttk.Combobox(root,values = base_Moedas_sigla, textvariable=self.currency, width = 300).pack(anchor=W,pady = 5, padx = 10)
        Label(root, text = "Valor para conversão - CRY").pack(anchor=W, pady = 5, padx = 10)
        Entry(root, textvariable = self.ValorCRY).pack(anchor=W, pady = 5, padx = 10)
        Label(root, text = "Valor para conversão - BRL").pack(anchor=W, pady = 5, padx = 10)
        Entry(root, textvariable = self.ValorBRL).pack(anchor=W, pady = 5, padx = 10)
        Label(root, text = "Cotação Venda").pack(anchor=W, pady = 5, padx = 10)
        Venda_Cotacao = Label(root, textvariable = self.CotacaoVenda).pack(anchor=W, pady = 5, padx = 10)
        Label(root, text = "Cotação Compra").pack(anchor=W, pady = 5, padx = 10)
        Compra_Cotacao = Label(root, textvariable = self.CotacaoCompra).pack(anchor=W, pady = 5, padx = 10)
        Label(root, text = "Data/Hora Cotação").pack(anchor=W, pady = 5, padx = 10)
        Label(root, textvariable = self.DataHora).pack(anchor=W, pady = 5, padx = 10)
        Label(root, text = "Boletim").pack(anchor=W, pady = 5, padx = 10)
        Label(root, textvariable = self.TipoBol).pack(anchor=W, pady = 5, padx = 10)
        Label(root, textvariable = self.CRYFinal).pack(anchor=W, pady = 5, padx = 10)
        Label(root, textvariable = self.BRLFinal).pack(anchor=W, pady = 5, padx = 10)
        Label(root, textvariable = self.NomeMoeda).pack(anchor=W, pady = 5, padx = 10)
        Button(root, text = "Converter",
                                          command = self.Convertbt).pack()

        root.mainloop()

    def Convertbt(self):
        
        SelectedCurrency = self.currency.get()
        CRY = self.ValorCRY.get()
        BRL = self.ValorBRL.get()

        url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda='" + SelectedCurrency + "',dataCotacao='" + dataHoje + "')?&$top=100&$format=json&$select=paridadeCompra,paridadeVenda,cotacaoCompra,cotacaoVenda,dataHoraCotacao,tipoBoletim"

        base1 = pd.read_json(url)
        base1 = pd.json_normalize(base1['value'])
        base = pd.DataFrame(base1)
        base = base.tail(1)

        CV = float(base.cotacaoVenda)
        CC = float(base.cotacaoCompra)
        DH = str(base.dataHoraCotacao)
        BOL = str(base.tipoBoletim)

        self.CotacaoVenda.set('BRL {:,.2f}'.format(CV, '10.2f'))
        self.CotacaoCompra.set('BRL {:,.2f}'.format(CC, '10.2f'))
        self.DataHora.set(DH)
        self.TipoBol.set(BOL)        

        if CRY == "":
            CRY = float(BRL) / CC
        elif BRL == "":
            BRL = float(CRY) * CV

        self.CRYFinal.set(SelectedCurrency+' {:,.2f}'.format(float(CRY), '10.2f'))
        self.BRLFinal.set('BRL {:,.2f}'.format(float(BRL), '10.2f'))

        Nome_Moeda = base_Moedas[(base_Moedas['simbolo'] == SelectedCurrency)].iloc[0,1]

        self.NomeMoeda.set(Nome_Moeda)

conversor()
