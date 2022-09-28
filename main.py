#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import email.message
import smtplib
import sqlite3
import pandas as pd

import PySimpleGUI as sg

from datetime import date, timedelta, datetime

from Tools.scripts.dutree import display

umidade = 35
temperatura = 25


db = sqlite3.connect('sistemaTCC.db')
cursor = db.cursor()


#Enviar alertas para o email
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
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')

def enviarEmailInicioDeTratamento(doenca,agrotoxico):
    corpo_email = printAgrotoxicoEmail(doenca,agrotoxico)

    msg = email.message.Message()
    msg['Subject'] = "Inicio de Tratamento"
    msg['From'] = 'lucas.sansiq@gmail.com'
    msg['To'] = 'lucas.san12@outlook.com.br'
    password = 'werxxmsxrubeugii'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')

# In[ ]:

#Verifica se teve alta no dia anterior, se sim ele insere na mesmo registro e inicia o tratamento se não grava um novo registro de alta
def verificaUltimaUmidade():
    dataOntem = date.today() - timedelta(1)
    dataOntem = str(dataOntem)
    ultimoRegistro = retornaUltimaDataAlerta()
    ultimoID = retornaUltimaRegistroAlerta()
    if(umidade >= 80):
        if(dataOntem == ultimoRegistro):
            cursor.execute(f"UPDATE Alerta SET segundoAlerta = '{date.today()}' WHERE id = {ultimoID};")
            db.commit()
            print("Atualizou")
        else:
            cursor.execute(f"INSERT INTO Alerta (primeiroAlerta) VALUES ('{date.today()}')")
            db.commit()
            print("Inseriu")

#Método para retornar a ultima data registrada na tabela Alerta
def retornaUltimaDataAlerta():
    cursor.execute("select primeiroAlerta from Alerta order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return(final)

#Método para retornar o ultimo ID registrado na Tabela Alerta
def retornaUltimaRegistroAlerta():
    cursor.execute("select MAX(id) from Alerta")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return(final)

def retornaUltimoRegistroTratamento():
    cursor.execute("select MAX(id) from Tratamento")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return(final)

def retornaDataProximaAplicacao():
    id = retornaUltimoRegistroTratamento()
    cursor.execute(f"select dataProximaAplicacao from Tratamento where id = {id}")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return(final)

def enviaAlerta(duracao):
    data = str(date.today())
    dataProximaAplicacao = retornaDataProximaAplicacao()
    idTratamento = retornaUltimoRegistroTratamento()
    if(data == dataProximaAplicacao):
        enviarEmailAlertadeIrrigacao()
        atualizacaoDataAplicacao = datetime.strptime(dataProximaAplicacao, '%Y-%m-%d').date()
        atualizacaoDataAplicacao = atualizacaoDataAplicacao + timedelta(duracao)
        cursor.execute(f"UPDATE Tratamento SET dataProximaAplicacao = '{atualizacaoDataAplicacao}' WHERE id = {idTratamento};")
        db.commit()

#Função para apresentar ultima temperatura maxima apresentada no bloco "Ultima atualização de Tempo e Umidade"
def ultimaTemperaturaMaxima():
    cursor.execute("select temperatura from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)

#Função para a apresentar ultima umidade maxima apresentada no bloco "Ultima atualização de Tempo e Umidade"
def ultimaUmidadeMaxima():
    cursor.execute("select umidade from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[2:-3]
    return (final)

#Função para apresentar data no bloco "Ultima atualização de Tempo e Umidade"
def dataDeMaxima():
    cursor.execute("select data from AltaDoDia order by id desc limit 1")
    result = cursor.fetchall()
    final = str(result)[3:-4]
    return (final)

#Função para apresentar ultima aplicacao de agrotoxico de um tratamento ativo
def mostraUltimaAplicacaoNaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if(ativo == "1"):
        cursor.execute("select dataFinal from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    return(final)

#Função para apresentar proxima aplicacao de agrotoxico de um tratamento ativo
def mostraProximaAplicacaoNaAcao():
    cursor.execute("select ativo from Tratamento order by id desc limit 1")
    result = cursor.fetchall()
    ativo = str(result)[2:-3]
    final = ""
    if(ativo == "1"):
        cursor.execute("select dataProximaAplicacao from Tratamento order by id desc limit 1")
        result = cursor.fetchall()
        final = str(result)[3:-4]
    return(final)

#Função para apresentar inicio do tratamento ativo
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

#Função para apresentar agrotoxico do tratamento ativo
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

#Funcao para retornar a temperatura
def apresentaTemperatura():
    porcentagem = f"{str(temperatura)}%"
    return porcentagem

#Funcao para retornar a umidade
def apresentaUmidade():
    porcentagem = f"{str(umidade)}%"
    return porcentagem

#Inicia o tratamento, grava no banco o registro do inicio de um tratamento
def iniciarTratamento(doenca,agrotoxico,tempo):

    #Retornar o id do agrotoxico escolhido para o tratamento
    cursor.execute(f"select id from Agrotoxicos where agrotoxico = '{agrotoxico}' and doenca = '{doenca}' order by id desc limit 1")
    result = cursor.fetchall()
    id = str(result)[2:-3]

    #validacao do do tempo de intervalo entre as aplicacoes
    duracao = 0
    if tempo == 0:
        duracao = 8
    elif tempo == 1:
        duracao = 7
    elif tempo == 2:
        duracao = 10
    else:
        sg.popup_ok('Selecione o Clima')

    #Retornar a quantidade total de aplicacoes
    cursor.execute(f"select qtAplicacoes from Agrotoxicos where id = {id}")
    result = cursor.fetchall()
    qtAplicacoes = str(result)[3:-4]

    #Data que iniciou o tratamento
    dataInicio = (date.today())

    #Soma a data os dias de intervalo para proxima aplicacao e armazena na variavel
    proximaAplicacao = dataInicio + timedelta(duracao)

    #Multiplica a quantidade de aplicacaoes com o intervalo entre eles, depois soma com a data que iniciou para mostrar a data final
    qtDiasTotal = int(duracao)* int(qtAplicacoes)
    dataFinal = dataInicio + timedelta(qtDiasTotal)

    cursor.execute(f"INSERT INTO Tratamento (agrotoxico,dataInicial,dataProximaAplicacao,dataFinal,ativo,intervaloDeAplicacoes) VALUES ({id},'{dataInicio}','{proximaAplicacao}','{dataFinal}',1,{duracao})")
    db.commit()
    print("Inserido!")

    enviarEmailInicioDeTratamento(doenca,agrotoxico)


#Monta o corpo do email enviado no inicio do tratamento
def printAgrotoxicoEmail(doenca,agrotoxico):
    cursor.execute(f"select composicao from Agrotoxicos where agrotoxico = '{agrotoxico}' and doenca = '{doenca}'")
    result = cursor.fetchall()
    composicao = str(result)[3:-4]

    cursor.execute(f"select manuseio from Agrotoxicos where agrotoxico = '{agrotoxico}' and doenca = '{doenca}'")
    result = cursor.fetchall()
    manuseio = str(result)[3:-4]

    cursor.execute(f"select qtAplicacoes from Agrotoxicos where agrotoxico = '{agrotoxico}' and doenca = '{doenca}'")
    result = cursor.fetchall()
    qtAplicacoes = str(result)[3:-4]

    cursor.execute(f"select dosagem from Agrotoxicos where agrotoxico = '{agrotoxico}' and doenca = '{doenca}'")
    result = cursor.fetchall()
    dosagem = str(result)[3:-4]

    texto = f'''
    <h1>Agrotóxico: {agrotoxico}</h1>
    <p>Usado no combate da: {doenca}</p>
    
    <p>Composição: {composicao}</p>
    <p>Manuseio: {manuseio}</p>
    <p>Quantidade de aplicações: {qtAplicacoes}</p>
    <p>Dosagem: {dosagem}</p>
    '''

    return texto

#Retirar as tags do texto para email, para mostrar na tela
def printAgrotoxico(doenca,agrotoxico):
    text = printAgrotoxicoEmail(doenca,agrotoxico).replace("<p>","")
    text = text.replace("</p>","")
    text = text.replace("<h1>","")
    text = text.replace("</h1>","")
    print(text)

def exportarTratamentos():
    cursor.execute("SELECT agrotoxico, dataInicial, dataFinal,intervaloDeAplicacoes FROM Tratamento")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(columns={0:'Agrotoxico',1:'Inicio do Tratamento',2:'Termino do Tratamento',3:'Intervalo entre as Aplicacoes'},inplace=True)
    dados.to_excel("C:/Users/lucas/Desktop/Tratamentos.xlsx", index=False)
    print("Arquivo exportado!")

def exportarAgrotoxicos():
    cursor.execute("SELECT agrotoxico, doenca, composicao,manuseio,qtAplicacoes,dosagem FROM Agrotoxicos")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(columns={0: 'Agrotoxico', 1: 'Doenca Preventiva', 2: 'Composicao',3: 'Manuseio',4:'Quantidade de Aplicacoes',5:'Dosagem'}, inplace=True)
    dados.to_excel("C:/Users/lucas/Desktop/Agrotoxicos.xlsx", index=False)
    print("Arquivo exportado!")

def exportarAltas():
    cursor.execute("SELECT temperatura, umidade, data FROM AltaDoDia")
    result = cursor.fetchall()
    dados = pd.DataFrame(data=result)
    dados.rename(columns={0: 'Temperatura Maxima', 1: 'Umidade Maxima', 2: 'Data da Alta'}, inplace=True)
    dados.to_excel("C:/Users/lucas/Desktop/Registros de Alta.xlsx", index=False)
    print("Arquivo exportado!")

def exportarDados(escolha):
    if (escolha == 0):
        exportarTratamentos()
    elif (escolha == 1):
        exportarAgrotoxicos()
    elif (escolha == 2):
        exportarAltas()
    else:
        sg.popup_ok('Selecione uma opção Valida')

#exportarDados(2)
#iniciarTratamento("testando","teste",2)
#printAgrotoxico("testando","teste")


