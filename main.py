#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import sqlite3
import smtplib
import email.message
from datetime import datetime

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

def iniciarTratamento():
    data = (datetime.today())
    cursor.execute(f"INSERT INTO Data (dataInicial) VALUES ('{data}')")
    db.commit()

iniciarTratamento()