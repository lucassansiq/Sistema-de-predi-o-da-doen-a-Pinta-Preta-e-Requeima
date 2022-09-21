#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import sqlite3
import smtplib
import email.message
from datetime import date, timedelta

db = sqlite3.connect('sistemaTCC.db')
cursor = db.cursor()

#Enviar alertas para o email
def enviar_email():
    corpo_email = """
    <p>Parágrafo1</p>
    <p>Parágrafo2</p>
    """

    msg = email.message.Message()
    msg['Subject'] = "Assunto"
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

#Inicia o tratamento, grava no banco a data de inicio, as proximas aplicacoes, e a ultima aplcacao
def iniciarTratamento(agrotoxico,intervaloAplicacao,duracao):
    data = (date.today())
    proximaAplicacao = data + timedelta(intervaloAplicacao)
    dataFinal = data + timedelta(duracao)
    cursor.execute(f"INSERT INTO Tratamento (agrotoxico,dataInicial,dataProximaAplicacao,dataFinal) VALUES ('{agrotoxico}','{data}','{proximaAplicacao}','{dataFinal}')")
    db.commit()



#Verifica se teve alta no dia anterior, se sim ele insere na mesmo registro e inicia o tratamento se não grava um novo registro de alta
def verificaUltimaUmidade(umidade):
    dataOntem = date.today() - timedelta(1)
    ultimoRegistro = retornaUltimaDataAlerta()
    ultimoID = retornaUltimaRegistroAlerta()
    if(umidade >= 80):
        if(dataOntem == ultimoRegistro):
            cursor.execute(f"UPDATE Alerta SET segundoAlerta = '{dataOntem}' WHERE id = {ultimoID};")
            db.commit()
        else:
            cursor.execute(f"INSERT INTO Alerta (primeiroAlerta) VALUES ('{date.today()}')")
            db.commit()

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
