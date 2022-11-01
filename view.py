#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import email.message
import smtplib
import sqlite3

from threading import Lock
import pandas as pd
import PySimpleGUI as sg
from datetime import date, timedelta, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow)
from front import Ui_MainWindow
import sys
import numpy as np


# Variaveis globais
umidade = 0
temperatura = 0
agrotoxicoAtivo = ""
inicioTratamento = ""
proximaAplicacao = ""
ultimaAplicacao = ""
temperaturaMaxima = ""
umidadeMaxima = ""
dataDeMaxima = ""

# Conexao com o Banco de Dados e declaracao da variavel cursos para manipulação do BD
db = sqlite3.connect('sistemaTCC.db', check_same_thread=False)
cursor = db.cursor()


def retornaAgrotoxicoAtivo():
    return (agrotoxicoAtivo)


def retornaInicioTratamento():
    return (inicioTratamento)


def retornaProximaAplicacao():
    return (proximaAplicacao)


def retornaUltimaAplicacao():
    return (ultimaAplicacao)


def retornaUltimaTemperaturaMaxima():
    return (f"{temperaturaMaxima}ºC")


def retornaUltimaUmidadeMaxima():
    return (f"{umidadeMaxima}%")


def retornaDataDeMaxima():
    return (dataDeMaxima)



# Funcao para enviar o email ao iniciar um tratamento
def enviarEmailInicioDeTratamento(agrotoxico):
    corpo_email = printAgrotoxicoEmail(agrotoxico)

    msg = email.message.Message()
    msg['Subject'] = "Inicio de Tratamento"
    msg['From'] = 'lucas.sansiq@gmail.com'
    msg['To'] = 'lucas.san12@outlook.com.br'
    password = 'werxxmsxrubeugii'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


# In[ ]:

# Verifica se teve alta no dia anterior, se sim ele insere na mesmo registro e indica o tratamento se não grava um novo registro de alta
def verificaUltimaUmidade():
    dataOntem = date.today() - timedelta(1)
    dataOntem = str(dataOntem)
    ultimoRegistro = retornaUltimaDataAlerta()
    ultimoID = retornaUltimaRegistroAlerta()
    if (dataOntem == ultimoRegistro):
        cursor.execute(f"UPDATE Alerta SET segundoAlerta = '{date.today()}' WHERE id = {ultimoID};")
        db.commit()
        print("Atualizou")
        sg.popup_ok('Possivel Proliferação de Doenças\n\n'
                    '  Inicie agora um Tratamento')
    else:
        cursor.execute(f"INSERT INTO Alerta (primeiroAlerta) VALUES ('{date.today()}')")
        db.commit()
        print("Inseriu")


# Funcao para retornar a ultima data registrada na tabela Alerta
def retornaUltimaDataAlerta():
    cursor.execute("select primeiroAlerta from Alerta order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


# Funcao para retornar a segunda data de alerta do ultimo registro da tabela Alerta
def retornaUltimaSegundaDataAlerta():
    cursor.execute("select segundoAlerta from Alerta order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


# Funcao para retornar data Final do ultimo tratamento registrada na tabela Tratamento
def retornaDataFinalTratamento():
    cursor.execute(f"select dataFinal from Tratamento where id = {retornaUltimoRegistroTratamento()}")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


# Funcao para retornar o ultimo ID registrado na Tabela Alerta
def retornaUltimaRegistroAlerta():
    cursor.execute("select MAX(id) from Alerta")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Funcao para retornar ID do ultimo registro da Tabela Tratamento
def retornaUltimoRegistroTratamento():
    cursor.execute("select MAX(id) from Tratamento")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Retorna Intervalo de Aplicacoes do ultimo registro de tratamento
def retornaUltimoIntervaloDeAplicacoes():
    cursor.execute(f"select intervaloDeAplicacoes from Tratamento where id = {retornaUltimoRegistroTratamento()}")
    result = cursor.fetchall()
    final = str(result)[1:-1]
    return (final)


# Funcao para retornar a data da proxima aplicacao de um tratamento ativo
def retornaDataProximaAplicacao():
    id = retornaUltimoRegistroTratamento()
    cursor.execute(f"select dataProximaAplicacao from Tratamento where id = {id}")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


def insereAltadoDia():
    cursor.execute(
        f"INSERT INTO AltaDoDia (temperatura,umidade,data) VALUES ({temperatura},{umidade},'{date.today()}');")
    db.commit()


# Função para apresentar ultima temperatura maxima apresentada no bloco "Ultima atualização de Tempo e Umidade"


def alteraUltimaTemperaturaMaxima():
    cursor.execute("select temperatura from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    global temperaturaMaxima
    temperaturaMaxima = str(result)[2:-3]


# Função para a apresentar ultima umidade maxima apresentada no bloco "Ultima atualização de Tempo e Umidade"
def alteraUltimaUmidadeMaxima():
    cursor.execute("select umidade from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    global umidadeMaxima
    umidadeMaxima = str(result)[2:-3]


# Função para apresentar data no bloco "Ultima atualização de Tempo e Umidade"
def alteraDataDeMaxima():
    cursor.execute("select data from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    global dataDeMaxima
    dataDeMaxima = str(result)[3:-4]


# Função para apresentar ultima aplicacao de agrotoxico de um tratamento ativo
def alteraUltimaAplicacaoNaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select dataFinal from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    global ultimaAplicacao
    ultimaAplicacao = final


# Função para apresentar proxima aplicacao de agrotoxico de um tratamento ativo
def alteraProximaAplicacaoNaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select dataProximaAplicacao from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    global proximaAplicacao
    proximaAplicacao = final


# Função para apresentar inicio do tratamento ativo
def alteraInicioDaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select dataInicial from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    global inicioTratamento
    inicioTratamento = final


# Função para apresentar agrotoxico do tratamento ativo
def alteraAgrotoxicoDaAcao():
    final = ""
    if (verificaTratamentoAtivo() == "1"):
        cursor.execute(
            f"SELECT a.agrotoxico FROM Tratamento as t INNER JOIN Agrotoxicos as a on t.agrotoxico = a.id WHERE t.id = {retornaUltimoRegistroTratamento()}")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    global agrotoxicoAtivo
    agrotoxicoAtivo = final


# Funcao para retornar a temperatura
def apresentaTemperatura():
    porcentagem = f"{str(temperatura)}%"
    return porcentagem


# Funcao para retornar a umidade
def apresentaUmidade():
    porcentagem = f"{str(umidade)}%"
    return porcentagem


# Inicia o tratamento, grava no banco o registro do inicio de um tratamento
def iniciarTratamento(agrotoxico, tempo=0):
    # Retornar o id do agrotoxico escolhido para o tratamento
    cursor.execute(f"select id from Agrotoxicos where agrotoxico = '{agrotoxico}' order by id desc limit 1")
    result = cursor.fetchall()
    id = str(result)[2:-3]

    # validacao do do tempo de intervalo entre as aplicacoes
    duracao = 0
    # Tempo Normal
    if tempo == 0:
        duracao = 8
    # Tempo Chuvoso
    elif tempo == 1:
        duracao = 7
    # Tempo Seco
    elif tempo == 2:
        duracao = 10
    else:
        sg.popup_ok('Selecione o Clima')

    # Retornar a quantidade total de aplicacoes
    cursor.execute(f"select qtAplicacoes from Agrotoxicos where id = {id}")
    result = cursor.fetchall()
    qtAplicacoes = str(result)[3:-4]

    # Data que iniciou o tratamento
    dataInicio = (date.today())

    # Soma a data os dias de intervalo para proxima aplicacao e armazena na variavel
    proximaAplicacao = dataInicio + timedelta(duracao)

    # Multiplica a quantidade de aplicacaoes com o intervalo entre eles, depois soma com a data que iniciou para mostrar a data final
    qtDiasTotal = int(duracao) * int(qtAplicacoes)
    dataFinal = dataInicio + timedelta(qtDiasTotal)

    cursor.execute(
        f"INSERT INTO Tratamento (agrotoxico,dataInicial,dataProximaAplicacao,dataFinal,ativo,intervaloDeAplicacoes) VALUES ({id},'{dataInicio}','{proximaAplicacao}','{dataFinal}',1,{duracao})")
    db.commit()
    print("Inserido!")

    enviarEmailInicioDeTratamento(agrotoxico)


# Monta o corpo do email enviado no inicio do tratamento
def printAgrotoxicoEmail(agrotoxico):
    cursor.execute(f"select composicao from Agrotoxicos where agrotoxico = '{agrotoxico}'")
    result = cursor.fetchall()
    composicao = str(result)[3:-4]

    cursor.execute(f"select manuseio from Agrotoxicos where agrotoxico = '{agrotoxico}'")
    result = cursor.fetchall()
    manuseio = str(result)[3:-4]

    cursor.execute(f"select qtAplicacoes from Agrotoxicos where agrotoxico = '{agrotoxico}'")
    result = cursor.fetchall()
    qtAplicacoes = str(result)[3:-4]

    cursor.execute(f"select dosagem from Agrotoxicos where agrotoxico = '{agrotoxico}'")
    result = cursor.fetchall()
    dosagem = str(result)[3:-4]

    cursor.execute(f"select doenca from Agrotoxicos where agrotoxico = 'teste'")
    result = cursor.fetchall()
    id = str(result)[2:-3]
    cursor.execute(f"select doenca from Doencas where id = {id}")
    result = cursor.fetchall()
    doenca = str(result)[3:-4]

    texto = f'''
    <h1>Agrotóxico: {agrotoxico}</h1>
    <p>Usado no combate da: {doenca}</p>

    <p>Composição: {composicao}</p>
    <p>Manuseio: {manuseio}</p>
    <p>Quantidade de aplicações: {qtAplicacoes}</p>
    <p>Dosagem: {dosagem}</p>

    <p>Inicio do Tratamento: {date.today()}</p>
    '''

    return texto


# Retirar as tags do texto para email, para mostrar na tela
def printAgrotoxico(agrotoxico):
    text = printAgrotoxicoEmail(agrotoxico).replace("<p>", "")
    text = text.replace("</p>", "")
    text = text.replace("<h1>", "")
    text = text.replace("</h1>", "")
    return (text)


# Funcao para exportar a tabela tratamentos para excel
def exportarTratamentos():
    cursor.execute(
        "SELECT a.agrotoxico, t.dataInicial, t.dataFinal,t.intervaloDeAplicacoes FROM Tratamento as t INNER JOIN Agrotoxicos as a on t.agrotoxico = a.id")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(columns={0: 'Agrotoxico', 1: 'Inicio do Tratamento', 2: 'Termino do Tratamento',
                          3: 'Intervalo entre as Aplicacoes'}, inplace=True)
    dados.to_excel("C:/Users/lucas/Desktop/Tratamentos.xlsx", index=False)
    print("Arquivo exportado!")
    sg.popup_ok('Arquivo exportado!')


# Funcao para exportar agrotoxicos para excel
def exportarAgrotoxicos():
    cursor.execute(
        "SELECT a.agrotoxico, d.doenca, a.composicao,a.manuseio,a.qtAplicacoes,a.dosagem FROM Agrotoxicos as a inner join Doencas as d on a.doenca = d.id")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(
        columns={0: 'Agrotoxico', 1: 'Doenca Preventiva', 2: 'Composicao', 3: 'Manuseio', 4: 'Quantidade de Aplicacoes',
                 5: 'Dosagem'}, inplace=True)
    dados.to_excel("C:/Users/lucas/Desktop/Agrotoxicos.xlsx", index=False)
    print("Arquivo exportado!")
    sg.popup_ok('Arquivo exportado!')


# Funcao para exportar tabela alertas para excel
def exportarAltas():
    cursor.execute("SELECT temperatura, umidade, data FROM AltaDoDia")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(columns={0: 'Temperatura Maxima', 1: 'Umidade Maxima', 2: 'Data da Alta'}, inplace=True)
    pathDir = "C:/Users/lucas/Desktop/Registros de Alta.xlsx"
    dados.to_excel(pathDir, index=False)
    print("Arquivo exportado!")
    sg.popup_ok('Arquivo exportado!')


# Funcao de escolha de qual tabela exportar
def exportarDados(escolha):
    if (escolha == 0):
        exportarTratamentos()
    elif (escolha == 1):
        exportarAgrotoxicos()
    elif (escolha == 2):
        exportarAltas()
    else:
        sg.popup_ok('Selecione uma opção Valida')


# Funcao para verificar se o ultimo tratamento está ativo
def verificaTratamentoAtivo():
    id = retornaUltimoRegistroTratamento()
    cursor.execute(f"select ativo from Tratamento where id = {id} ")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Funcao para alterar os ids de doenca para sua descricao
def alteracaoDoenca(doenca):
    if doenca == 1:
        final = "Pinta Preta"
    elif doenca == 2:
        final = "Requeima"
    elif doenca == 3:
        final = "Ambas"
    return final


# Funcao para retornar o id da doenca passada no parametro
def retornaIdDoenca(doenca):
    cursor.execute(f"select id from Doencas where doenca = '{doenca}' ")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Funcao para retornar os Agrotoxicos cadastrados no banco
def retornaArrayDeAgrotoxicos(doenca='Ambos'):
    if (doenca == 'Ambos'):
        cursor.execute(f"select agrotoxico from Agrotoxicos")
        result = cursor.fetchall()
    else:
        cursor.execute(f"select agrotoxico from Agrotoxicos where doenca = {retornaIdDoenca(doenca)} ")
        result = cursor.fetchall()
    return (result)


# Funcao para retornar as doencas cadastradas no banco
def retornaArrayDeDoencas():
    cursor.execute(f"select doenca from Doencas")
    result = cursor.fetchall()
    return (result)


def atualizacaoDeCamposUltimaAtualizacao():
    alteraUltimaTemperaturaMaxima()
    alteraUltimaUmidadeMaxima()
    alteraDataDeMaxima()
    alteraAgrotoxicoDaAcao()

# INICIO INTERFACE
class MainWindow(QMainWindow, Ui_MainWindow):

    def button_clicked(self):
        tempo = 3
        agrotoxicoAcao = self.cb_agrotoxico.currentText()
        if (self.rb_normal.isChecked()):
            tempo = 0
        else:
            if (self.rb_chuvoso.isChecked()):
                tempo = 1
            else:
                if (self.rb_seco.isChecked()):
                    tempo = 2
        if (tempo == 3):
            sg.popup_ok("Selecione um clima")
        else:
            iniciarTratamento(agrotoxicoAcao,tempo)
            alteraAgrotoxicoDaAcao()
            alteraInicioDaAcao()
            alteraProximaAplicacaoNaAcao()
            alteraUltimaAplicacaoNaAcao()
            self.txt_acao.setText(
                f"Agrotoxico: {retornaAgrotoxicoAtivo()} \n\nInicio do Tratamento: {retornaInicioTratamento()} \n\nPróxima Aplicação: {retornaProximaAplicacao()}\n\nUltima Aplicação: {retornaUltimaAplicacao()}")
            sg.popup_ok("Tratamento Iniciado")

    def onChanged1(self):
        opcao = self.cb_doencas.currentText()
        if (opcao == "Requeima"):
            agrotoxicos = retornaArrayDeAgrotoxicos("Requeima")
            agrotoxicos = np.array(agrotoxicos)
            for i in range(len(agrotoxicos)):
                self.cb_agrotoxico.addItem(str(agrotoxicos[i])[2:-2])
        else:
            if (opcao == "Pinta Preta"):
                agrotoxicos = retornaArrayDeAgrotoxicos("Pinta Preta")
                agrotoxicos = np.array(agrotoxicos)
                for i in range(len(agrotoxicos)):
                    self.cb_agrotoxico.addItem(str(agrotoxicos[i])[2:-2])
            else:
                if (opcao == "Ambos"):
                    agrotoxicos = retornaArrayDeAgrotoxicos("Ambos")
                    agrotoxicos = np.array(agrotoxicos)
                    for i in range(len(agrotoxicos)):
                        self.cb_agrotoxico.addItem(str(agrotoxicos[i])[2:-2])

    def onChanged2(self):
        texto = printAgrotoxico(self.cb_agrotoxico.currentText())
        self.txt_acaoPreventiva.setText(texto)

    def exportarDados(self):
        escolha = 3
        if (self.radioButton_4.isChecked()):
            escolha = 1
        else:
            if (self.radioButton_5.isChecked()):
                escolha = 0
            else:
                if (self.radioButton_6.isChecked()):
                    escolha = 2
        if (escolha == 3):
            sg.popup_ok("Selecione uma opção")
        else:
            exportarDados(escolha)

    def atualizaInformacoes(self):
        alteraUltimaTemperaturaMaxima()
        alteraUltimaUmidadeMaxima()
        alteraDataDeMaxima()
        alteraAgrotoxicoDaAcao()
        alteraInicioDaAcao()
        alteraProximaAplicacaoNaAcao()
        alteraUltimaAplicacaoNaAcao()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Sistema de gerenciamento")

        # PAGINAS DO SISTEMA
        self.btn_dashbord.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_dashbord))
        self.btn_acao.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_acao))
        self.btn_exportar.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_exportar))

        # DASHBOARD
        self.txt_umidade.setText(apresentaUmidade())
        self.txt_temperatura.setText(apresentaTemperatura())
        self.txt_acao.setText(
            f"Agrotoxico: {retornaAgrotoxicoAtivo()} \n\nInicio do Tratamento: {retornaInicioTratamento()} \n\nPróxima Aplicação: {retornaProximaAplicacao()}\n\nUltima Aplicação: {retornaUltimaAplicacao()}")
        self.txt_atualizacao.setText(
            f"Temperatura Maxima: {retornaUltimaTemperaturaMaxima()} \n\nUmidade Máxima: {retornaUltimaUmidadeMaxima()} \n\nData: {retornaDataDeMaxima()}")

        # TRATAMENTO
        #Ação do Botão Iniciar Tratamento
        self.btn_iniciarAcao.clicked.connect(self.button_clicked)

        #Preenchimento do combo box de doença
        self.cb_doencas.addItem("Pinta Preta")
        self.cb_doencas.addItem("Requeima")
        self.cb_doencas.addItem("Ambos")

        #Ação de alteração do comboBox de agrotoxixos
        self.cb_doencas.currentTextChanged.connect(self.onChanged1)

        #Apresentação no campo texto
        self.cb_agrotoxico.currentTextChanged.connect(self.onChanged2)

        #EXPORTAR DADOS
        self.btn_relatorio_2.clicked.connect(self.exportarDados)



alteraUltimaTemperaturaMaxima()
alteraUltimaUmidadeMaxima()
alteraDataDeMaxima()
alteraAgrotoxicoDaAcao()
alteraInicioDaAcao()
alteraProximaAplicacaoNaAcao()
alteraUltimaAplicacaoNaAcao()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
