import ctypes

#Sistema
import requests
from datetime import datetime
import pytz
import pycountry_convert as cont
from decouple import config
from functools import lru_cache

#Console Interface
import getpass
from time import sleep
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress


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
@lru_cache
def progress(api):
    with Progress() as progress:
        task = progress.add_task("[green]Processing...", total=100)
        try:
            while not progress.finished: 
                dados = request(api)
                progress.update(task, advance=20)
                cidade, pais, country, lat, lng = loc(dados)
                progress.update(task, advance=15)
                data, horario = tempo(country)
                progress.update(task, advance=15)
                celsius, humidade, descricao, main = clima(dados)
                progress.update(task, advance=10)
                continente = continent(pais)
                progress.update(task, advance=40)
        
            return cidade, pais, continente, horario, celsius, humidade, descricao, lat, lng, main, int(data.strftime("%H"))

        except KeyError: 
            return 1

        except:
            return 0

@lru_cache
def emoji_hora(hora):
    if(hora >= 5 and hora < 7):
        city_e = ":city_sunrise:"
    elif(hora >= 7 and hora < 18):
        city_e = ":cityscape:"
    elif(hora == 18):
        city_e = ":city_sunset:"
    else:
        city_e = ":night_with_stars:"

    return city_e 

def emoji_clima(main):
    if(main == "Clear"):
        sky_e = ":sunny:"
    elif(main == "Clouds"):
        sky_e = ":cloud:"
    elif(main == "Rain"):
        sky_e = ":cloud_with_rain:"
    else:
        sky_e = ":cloud_with_lightning_and_rain:"

    return sky_e 

def emoji_temp(celsius):
    if(celsius <= 20):
        temp_e = ":snowflake:"
    elif(celsius > 20 and celsius <= 30):
        temp_e = ":thermometer:"
    else:
        temp_e = ":fire:"

    return temp_e 

#Interface 1
passed = "S"
while(passed != "N"):
    user = getpass.getuser()
    console = Console()
    hora_pc = int(datetime.now().strftime("%H"))
    city_emoji = emoji_hora(hora_pc)
    console.print(f"\nOlá [red]{user}[/]:busts_in_silhouette: ", style="bold") 
    sleep(0.5)
    console.print("[yellow]Bem-Vindo[/] ao :earth_americas: [cyan]Sistema de Clima[/] :cloud:", style="bold")
    sleep(0.5)

    #Loop da obrigatoriedade
    cidade = False
    try:
        while not cidade:
            console.print(f"Nome da [green]Cidade ou Estado[/] [on white]{city_emoji}[/] (coloque espaço em cada palavra[Ex: São Paulo]): :arrow_down:", style="bold")
            cidade = input()
            key = config("KEY")
        api = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={key}"

        result = progress(api)
        key, api = None, None
        
    except KeyboardInterrupt:
        console.print(f"Bye Bye :unamused:", style="bold")


    #Credenciais(Usei uma .env para quardar a minha key[from decouple import config])


    #print(result)
    #return cidade, pais, continente, horario, celsius, humidade, descricao, lat, lng, main, int(data.strftime("%H"))

    #Interface 2
    if(result != 1 and result !=0):
        cityr_emoji = emoji_hora(result[10])
        skyr_emoji = emoji_clima(result[9])
        tempr_emoji = emoji_temp(result[4])

        sleep(0.3)
        console.print(f"\n\nO [yellow]Resultado[/] da [red]Pesquisa[/] do [cyan]Clima[/] de [green]{result[0]}[/]: \n", style="bold") 
        sleep(0.2)
        console.print(f"[green]Região: {result[0]}/{result[1]}/{result[2]} [/]| [red]Latitude[/] e [cyan]Longitude[/]: [red]{result[7]}[/],[cyan]{result[8]}[/]\n", style="bold") 
        sleep(0.2)
        console.print(f"[red]Horario: {result[3]} {cityr_emoji}[/]\n", style="bold")
        sleep(0.2)
        console.print(f"[cyan]Temperatura: {int(result[4])}°C {tempr_emoji}[/]\n", style="bold")  
        sleep(0.2)
        console.print(f"[blue]Humidade: {int(result[5])}% :droplet:[/]\n", style="bold")  
        sleep(0.2)
        console.print(f"[yellow]Céus: {result[6]} {skyr_emoji}[/]\n", style="bold")  
        sleep(0.2)
    elif (result == 1):
        console.print(f"\n\nA [green]Cidade[/] {cidade} [red]NÂO[/] foi Encontrada :worried:, Porfavor [yellow]Verificar[/] se todos os [cyan]Caracteres[/] foram [red]Digitados Corretamentes[/] :expressionless: \n", style="bold") 

    else:
        console.print(f"\n\n[cyan]Pesquisa[/] não [red]concluida[/] :fearful:, [yellow]Porfavor[/] verificar sua [red]Conexão com a Internet[/] e [yellow]Tente Novamente[/] :woman_mechanic:\n", style="bold") 

    console.print(f"\n[red]{user}[/], deseja [yellow]Repitir[/]", style="bold")
    passed = Prompt.ask(choices=["S", "N"], default="N")

