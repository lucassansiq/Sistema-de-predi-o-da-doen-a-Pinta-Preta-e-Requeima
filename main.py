#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import email.message
import smtplib
import sqlite3
import pandas as pd
import PySimpleGUI as sg
from datetime import date, timedelta, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget)
from front import Ui_MainWindow
import sys
import threading
import serial

umidade = 0
temperatura = 0

db = sqlite3.connect('sistemaTCC.db', check_same_thread=False)
cursor = db.cursor()


# Enviar alertas para o email
def enviarEmailAlertadeIrrigacao():
    corpo_email = """
    <p>Faça uma irrigação do Agrotoxico Hoje</p>
    <p>Agrotóxico: </p>
    """

    msg = email.message.Message()
    msg['Subject'] = "Alerta de Irrigação"
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

# Verifica se teve alta no dia anterior, se sim ele insere na mesmo registro e inicia o tratamento se não grava um novo registro de alta
def verificaUltimaUmidade():
    dataOntem = date.today() - timedelta(1)
    dataOntem = str(dataOntem)
    ultimoRegistro = retornaUltimaDataAlerta()
    ultimoID = retornaUltimaRegistroAlerta()
    if (dataOntem == ultimoRegistro):
        cursor.execute(f"UPDATE Alerta SET segundoAlerta = '{date.today()}' WHERE id = {ultimoID};")
        db.commit()
        print("Atualizou")
        escolha = input('''
        Alerta de Clima!
        Deseja Iniciar um Tratamento? (Sim ou Não)
        ''')
        if (escolha == 'sim') or (escolha == 's') or (escolha == 'S') or (escolha == 'Sim') or (escolha == 'SIM'):
            iniciarTratamento('teste')
    else:
        cursor.execute(f"INSERT INTO Alerta (primeiroAlerta) VALUES ('{date.today()}')")
        db.commit()
        print("Inseriu")


# Método para retornar a ultima data registrada na tabela Alerta
def retornaUltimaDataAlerta():
    cursor.execute("select primeiroAlerta from Alerta order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


# Método para retornar data Final do ultimo tratamento registrada
def retornaDataFinalTratamento():
    id = retornaUltimoRegistroTratamento()
    cursor.execute(f"select dataFinal from Tratamento where id = {id}")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


# Método para retornar o ultimo ID registrado na Tabela Alerta
def retornaUltimaRegistroAlerta():
    cursor.execute("select MAX(id) from Alerta")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


def retornaUltimoRegistroTratamento():
    cursor.execute("select MAX(id) from Tratamento")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Retorna Intervalo de Aplicacoes do ultimo registro de tratamento
def retornaUltimoIntervaloDeAplicacoes():
    cursor.execute(f"select intervaloDeAplicacoes from Tratamento where id = {retornaUltimoRegistroTratamento()}")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


def retornaDataProximaAplicacao():
    id = retornaUltimoRegistroTratamento()
    cursor.execute(f"select dataProximaAplicacao from Tratamento where id = {id}")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


def enviaAlerta(duracao):
    data = str(date.today())
    dataProximaAplicacao = retornaDataProximaAplicacao()
    idTratamento = retornaUltimoRegistroTratamento()
    if (data == dataProximaAplicacao):
        enviarEmailAlertadeIrrigacao()
        atualizacaoDataAplicacao = datetime.strptime(dataProximaAplicacao, '%Y-%m-%d').date()
        atualizacaoDataAplicacao = atualizacaoDataAplicacao + timedelta(duracao)
        cursor.execute(
            f"UPDATE Tratamento SET dataProximaAplicacao = '{atualizacaoDataAplicacao}' WHERE id = {idTratamento};")
        db.commit()


# Função para apresentar ultima temperatura maxima apresentada no bloco "Ultima atualização de Tempo e Umidade"
def ultimaTemperaturaMaxima():
    cursor.execute("select temperatura from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Função para a apresentar ultima umidade maxima apresentada no bloco "Ultima atualização de Tempo e Umidade"
def ultimaUmidadeMaxima():
    cursor.execute("select umidade from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


# Função para apresentar data no bloco "Ultima atualização de Tempo e Umidade"
def dataDeMaxima():
    cursor.execute("select data from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)


# Função para apresentar ultima aplicacao de agrotoxico de um tratamento ativo
def mostraUltimaAplicacaoNaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select dataFinal from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    return (final)


# Função para apresentar proxima aplicacao de agrotoxico de um tratamento ativo
def mostraProximaAplicacaoNaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select dataProximaAplicacao from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    return (final)


# Função para apresentar inicio do tratamento ativo
def mostraInicioDaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select dataInicial from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    return (final)


# Função para apresentar agrotoxico do tratamento ativo
def mostraAgrotoximoDaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if (ativo == "1"):
        cursor.execute("select agrotoxico from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    return (final)


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
    '''
    Classificação de Agrotóxicos
    Pinta Preta = 1
    Requeima = 2
    Ambos = 3
    '''

    # Retornar o id do agrotoxico escolhido para o tratamento
    cursor.execute(f"select id from Agrotoxicos where agrotoxico = '{agrotoxico}' order by id desc limit 1")
    result = cursor.fetchall()
    id = str(result)[2:-3]

    # validacao do do tempo de intervalo entre as aplicacoes
    duracao = 0
    if tempo == 0:
        duracao = 8
    elif tempo == 1:
        duracao = 7
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


def exportarAltas():
    cursor.execute("SELECT temperatura, umidade, data FROM AltaDoDia")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(columns={0: 'Temperatura Maxima', 1: 'Umidade Maxima', 2: 'Data da Alta'}, inplace=True)
    pathDir = "C:/Users/lucas/Desktop/Registros de Alta.xlsx"
    dados.to_excel(pathDir, index=False)
    print("Arquivo exportado!")
    sg.popup_ok('Arquivo exportado!')


def exportarDados(escolha):
    if (escolha == 0):
        exportarTratamentos()
    elif (escolha == 1):
        exportarAgrotoxicos()
    elif (escolha == 2):
        exportarAltas()
    else:
        sg.popup_ok('Selecione uma opção Valida')


def verificaTratamentoAtivo():
    id = retornaUltimoRegistroTratamento()
    cursor.execute(f"select ativo from Tratamento where id = {id} ")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


def alteracaoDoenca(doenca):
    if doenca == 1:
        final = "Pinta Preta"
    elif doenca == 2:
        final = "Requeima"
    elif doenca == 3:
        final = "Ambas"
    return final


def atualizaTratamento():
    ativo = verificaTratamentoAtivo()
    if (ativo == "0"):
        if (umidade >= 70) and (temperatura >= 15):
            verificaUltimaUmidade()
        else:
            print("Temp e Umidade normal")
    else:
        print("Tratamento em Andamento")


def verificaAplicacao():
    if (verificaTratamentoAtivo() == "1"):
        if (str(date.today()) == retornaDataFinalTratamento()):
            print("Aplicar Agrotóxico")
            cursor.execute(f"UPDATE Tratamento SET ativo = {0} WHERE id = {retornaUltimoRegistroTratamento()};")
            db.commit()
            print("Tratamento Finalizado")

        else:
            if (retornaDataProximaAplicacao() == str(date.today())):
                print("Aplicar Agrotoxico")
                atualizaAplicacao = date.today() + timedelta(int(retornaUltimoIntervaloDeAplicacoes()))
                cursor.execute(
                    f"UPDATE Tratamento SET dataProximaAplicacao = '{atualizaAplicacao}' WHERE id = {retornaUltimoRegistroTratamento()};")
                db.commit()
                print("Data Atualizada")



def retornaIdDoenca(doenca):
    cursor.execute(f"select id from Doencas where doenca = '{doenca}' ")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)


def retornaArrayDeAgrotoxicos(doenca='Ambos'):
    cursor.execute(f"select agrotoxico from Agrotoxicos where doenca = {retornaIdDoenca(doenca)} ")
    result = cursor.fetchall()
    return (result)


def retornaArrayDeDoencas():
    cursor.execute(f"select doenca from Doencas")
    result = cursor.fetchall()
    return (result)

def principalSistema():
    while (1):
        verificaAplicacao()

def atualizaTemperaturaUmidade():
    while True: #Loop para a conexão com o Arduino
        try:  #Tenta se conectar, se conseguir, o loop se encerra
            arduino = serial.Serial('COM6', 9600)
            print('Arduino conectado')
            break
        except:
            pass
    while True: #Loop principal
        msg = str(arduino.readline()) #Lê os dados em formato de string
        umidade = int(msg[40:-11]) #Fatia a string, converte para int e atualiza a umidade global
        print(f"Umidade {umidade}") #Imprime a mensagem
        temperatura = int(msg[16:-35])  #Fatia a string, converte para int e atualiza a temperatura global
        print(f"Temperatura {temperatura}")  # Imprime a mensagem
        arduino.flush() #Limpa a comunicação


# INICIO INTERFACE
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Sistema de gerenciamento")

        # PAGINAS DO SISTEMA
        self.btn_dashbord.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_dashbord))
        self.btn_acao.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_acao))
        self.btn_exportar.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pgexportar))




'''if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()'''


# FIM INTERFACE

class myThread(threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        if (self.name == "1"):
            while True:  # Loop para a conexão com o Arduino
                try:  # Tenta se conectar, se conseguir, o loop se encerra
                    arduino = serial.Serial('COM6', 9600)
                    print('Arduino conectado')
                    break
                except:
                    pass
            while True:  # Loop principal
                msg = str(arduino.readline())  # Lê os dados em formato de string
                umidade = int(msg[40:-11])  # Fatia a string, converte para int e atualiza a umidade global
                print(f"Umidade {umidade}")  # Imprime a mensagem
                temperatura = int(msg[16:-35])  # Fatia a string, converte para int e atualiza a temperatura global
                print(f"Temperatura {temperatura}")  # Imprime a mensagem
                arduino.flush()  # Limpa a comunicação
        else:
            if(self.name == "2"):
                    app = QApplication(sys.argv)
                    window = MainWindow()
                    window.show()
                    app.exec()
            else:
                if(self.name == "3"):
                    tempNum = 0
                    while(True):
                        verificaAplicacao()
            print("Exiting " + self.name)



# Create new threads
thread1 = myThread(1, "1", 1)
thread2 = myThread(2, "2", 2)
thread3 = myThread(3, "3", 3)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

