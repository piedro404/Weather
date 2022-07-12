import os
import threading
import requests
from datetime import datetime
import pytz
import pycountry_convert as cont
from decouple import config
import getpass

#painel
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QToolButton, QLineEdit
from PyQt5.QtCore import QSize, qInf
from PyQt5.QtGui import QIcon, QPixmap, qPixelFormatAlpha


application = QApplication([])

#Redimencionando a Janela Princial
mainWindow = QMainWindow()
mainWindow.setGeometry(0, 0, 550, 750)
mainWindow.setMinimumHeight(750)
mainWindow.setMaximumHeight(750)
mainWindow.setMinimumWidth(550)
mainWindow.setMaximumWidth(550)

#Custimização da Janela
mainWindow.setWindowTitle("Clima")
mainWindow.setStyleSheet("background-color: #55efef;")
mainWindow_icon = QIcon()
mainWindow_icon.addPixmap(QPixmap("./src/icones/clima.ico"))
mainWindow.setWindowIcon(mainWindow_icon)


#Background Start
background = QLabel(mainWindow)
background.setStyleSheet("background-color: rgb(255,255,255);")
background.resize(550,750)
background.move(0,0)

#Barra de Pesquisa
searchLine = QLineEdit(mainWindow)
searchLine.setGeometry(10, 30, 480, 40)
searchLine.setStyleSheet("background-color: rgb(255,255,255); font-size : 20px;")

#Botão de Pesquisa
searchButton = QToolButton(mainWindow)
searchButton.setGeometry(500, 30, 40, 40)
searchButton_icon = QIcon()
searchButton_icon.addPixmap(QPixmap("./src/icones/go.png"))
searchButton.setIcon(searchButton_icon)
searchButton.setStyleSheet("background-color: transparent;")
searchButton.setIconSize(QSize(40, 40))

#Regiao
regionInfo = QLabel(mainWindow)
regionInfo.setStyleSheet("background-color : transparent; color : black; font-size : 20px;")
regionInfo.resize(510,30)
regionInfo.move(20,80)

#Hora e Data 
dateInfo = QLabel(mainWindow)
dateInfo.setStyleSheet("background-color : transparent; color : black; font-size : 20px;")
dateInfo.resize(210,30)
dateInfo.move(320,110)

#Temperatura 
tempInfo = QLabel(mainWindow)
tempInfo.setStyleSheet("background-color : transparent; color : black; font-size : 20px;")
tempInfo.resize(200,30)
tempInfo.move(20,110)

#Humidade 
humInfo = QLabel(mainWindow)
humInfo.setStyleSheet("background-color : transparent; color : black; font-size : 20px;")
humInfo.resize(510,30)
humInfo.move(20,140)

#Ceu 
skyInfo = QLabel(mainWindow)
skyInfo.setStyleSheet("background-color : transparent; color : black; font-size : 20px;")
skyInfo.resize(300,25)
skyInfo.move(20,170)



#Funcoes da API
#Request API
def request(api):
    r = requests.get(api)
    dados = r.json()

    return dados

#Localização
def loc(dados):
    cidade = dados["name"]
    lat, lng = dados["coord"]["lat"], dados["coord"]["lon"]
    pais_codigo = dados["sys"]["country"]
    country = pytz.country_timezones[pais_codigo]
    pais = pytz.country_names[pais_codigo]
    if(pais == "Britain (UK)"):
        pais = "United Kingdom"

    return cidade, pais, country, lat, lng

#Data e Hora
def tempo(country):
    zona = pytz.timezone(country[0])
    data = datetime.now(zona)
    horario = data.strftime("%H:%M:%S | %d/%m/%Y")

    return data, horario

#Clima
def clima(dados):
    celsius = float(dados["main"]["temp"])-273.15
    humidade = dados["main"]["humidity"]
    descricao = dados["weather"][0]["description"]
    main = dados["weather"][0]["main"]

    return celsius, humidade, descricao, main

#Alterando Informacoes
def continent(country):
    pais = cont.country_name_to_country_alpha2(country)
    cont_cod = cont.country_alpha2_to_continent_code(pais)
    cont_nome = cont.convert_continent_code_to_continent_name(cont_cod)
    
    return cont_nome

#Pesquisa
def progress(api):
    dados = request(api)
    cidade, pais, country, lat, lng = loc(dados)
    data, horario = tempo(country)
    celsius, humidade, descricao, main = clima(dados)
    continente = continent(pais)
            
    return cidade, pais, continente, horario, celsius, humidade, descricao, lat, lng, main, int(data.strftime("%H"))

#Background
def backgroundTime(hora):
    if(hora >= 5 and hora < 7):
        background.setPixmap(QPixmap('./src/icones/citySunrise.png'))
    elif(hora >= 7 and hora < 18):
        background.setPixmap(QPixmap('./src/icones/cityDay.png'))
    elif(hora == 18):
        background.setPixmap(QPixmap('./src/icones/citySunset.png'))
    else:
        background.setPixmap(QPixmap('./src/icones/cityNight.png'))

#Painel Start
timePC = int(datetime.now().strftime("%H"))
backgroundTime(timePC)
user = getpass.getuser()

regionInfo.setText(f"")
dateInfo.setText(f"")
tempInfo.setText(f"Bem-Vindo, {user}!")
humInfo.setText(f"Coloque o nome de uma região")
skyInfo.setText(f"Ex: Balsas")


#Funcoes do Painel
def search():
    try:
        cidade = searchLine.text()
        key = config("KEY")
        api = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={key}"
        result = progress(api)
        key, api = None, None
        backgroundTime(result[10])
        regionInfo.setText(f"{result[0]}/{result[1]}/{result[2]}")
        dateInfo.setText(f"{result[3]}")
        tempInfo.setText(f"Temperatura: {int(result[4])}°C")
        humInfo.setText(f"Humidade: {int(result[5])}%")
        skyInfo.setText(f"Céus: {result[6].title()}")
    except:
        regionInfo.setText(f"Algo Deu Errado!!!")
        dateInfo.setText(f"Ex: Balsas")
        tempInfo.setText(f"Veja sua internet")
        humInfo.setText(f"Ou {cidade} não foi encontrado!")
        skyInfo.setText(f"E tente novamente")


def searchThread(mainWindow):
    threading.Thread(target=search).start()

#Conectado as Funções aos Botãos  
searchButton.clicked.connect(searchThread)


mainWindow.show()
application.exec_()