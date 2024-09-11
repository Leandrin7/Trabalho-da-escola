import os
import sys
import speech_recognition as sr
import webbrowser as browser
import urllib.request, json, requests
import threading
from gtts import gTTS
from playsound import playsound
from datetime import datetime
from bs4 import BeautifulSoup
from requests import get
from translate import Translator
from vosk import Model, KaldiRecognizer
import pyaudio

# Função de Criação de Áudio
def cria_audio(audio, mensagem, lang='pt-br'):
    tts = gTTS(mensagem, lang=lang)
    tts.save(audio)
    playsound(audio)
    os.remove(audio)

# Função de Monitoramento com Vosk
def monitora_audio_vosk():
    model = Model("vosk-model-small-pt-0.3")
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    while True:
        print('Diga algo, estou te ouvindo')
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            mensagem = recognizer.Result().lower()
            print('Você disse:', mensagem)
            executa_comandos(mensagem)
            break
    stream.stop_stream()
    stream.close()
    mic.terminate()

# Otimização com threading para execuções simultâneas
def run_task(task, *args):
    thread = threading.Thread(target=task, args=args)
    thread.start()

# Função para Notícias
def noticias():
    site = get('https://news.google.com/home?hl=pt-BR&gl=BR&ceid=BR:pt-419')
    noticias = BeautifulSoup(site.text, 'html.parser')
    for item in noticias.findAll('item')[:5]:
        cria_audio("noticia.mp3", item.title.text)

# Função para Cotação de Moedas
def cotacao(moeda):
    requisicao = get(f'https://economia.awesomeapi.com.br/all/{moeda}-BRL')
    {
    "USDBRL": {
        "code": "USD",
        "codein": "BRL",
        "name": "Dólar Americano/Real Brasileiro",
        "high": "6",
        "low": "5.2257",
        "varBid": "-0.2745",
        "pctChange": "-2.52",
        "bid": "5.2279",
        "ask": "5.2285",
        "timestamp": "1591109752",
        "create_date": "2024-09-21 11:55:53"

    },
    "EURBRL": {
        "code": "EUR",
        "codein": "BRL",
        "name": "Euro/Real Brasileiro",
        "high": "6.798",
        "low": "5.844",
        "varBid": "-0.1235",
        "pctChange": "-2.07",
        "bid": "5.8462",
        "ask": "5.8497",
        "timestamp": "1591109753",
        "create_date": "2024-09-21 11:55:56"
    }
}

    cotacao = requisicao.json()
    nome = cotacao[moeda]['name']
    data = cotacao[moeda]['create_date']
    valor = cotacao[moeda]['bid']
    cria_audio("cotacao.mp3", f"Cotação do {nome} em {data} é {valor}")

# Função para Clima
def clima(cidade):
    token = "<c194322c1d60797bb3cd42b610d322e9>"
    base_url = "https://home.openweathermap.org/?"
    complete_url = base_url + "appid=" + token + "&q=" + cidade
    response = requests.get(complete_url)
    retorno = response.json()
    if retorno["cod"] == 200:
        valor = retorno["main"]
        current_temperature = valor["temp"]
        current_humidiy = valor["humidity"]
        tempo = retorno["weather"]
        weather_description = tempo[0]["description"]
        clima = (f"Em {cidade}, temperatura é de {str(int(current_temperature - 273.15))}°C e umidade de {str(current_humidiy)}%.")
        cria_audio("clima.mp3", clima)

# Função Tradutor
def tradutor(traducao):
    if traducao == 'inglês':
        traduz = Translator(from_lang="pt-br", to_lang='english')
        cria_audio("traducao.mp3", "O que você gostaria de traduzir para o inglês?")
        mensagem = monitora_audio_vosk()
        traduzido = traduz.translate(mensagem)
        cria_audio("traducao.mp3", f"A tradução de {mensagem} é")
        cria_audio("traducao_eng.mp3", traduzido, lang='en')

# Execução de Comandos com Threading
def executa_comandos(mensagem):
    # exemplo de comando
    if 'hora' in mensagem:
        run_task(cria_audio, 'hora.mp3', f"Agora são {datetime.now().strftime('%H:%M')}")

# Função principal
def main():
    cria_audio("ola.mp3", "Olá, sou o Manta, sua assistente virtual! Como posso ajudar?")
    while True:
        monitora_audio_vosk()

main()
