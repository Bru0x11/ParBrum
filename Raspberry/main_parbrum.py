import sbarra, qr_code
import requests
import time
import pyfirmata
from pyfirmata import Arduino

"""
Inizializzazione variabili per Arduino:
-arduino: stringa che identifica l'Arduino collegato alla porta usb del raspberry;
-pin_*: mi indica in quale pin di Arduino sono collegati i vari led/buzzer/servo
"""
arduino = Arduino("/dev/ttyACM0")
pin_led_verde = 4
pin_led_rosso = 2
pin_buzzer = 6
arduino.digital[pin_led_rosso].write(1)
iteratore = pyfirmata.util.Iterator(arduino)
iteratore.start()
pin_servo = arduino.get_pin('d:9:s')


"""
Attiva la webcam e passa alla funzione di richiesta dell'autenticazione la stringa rilevata
"""    
def cattura_webcam():
    codice_identificativo = qr_code.readQrCode()
    check_QrCode_string(codice_identificativo)

"""
Effettua una richiesta HTTP al servizio di autenticazione del backend 
e passa il valore ottenuto alla funzione conferma_entrata()
"""
def check_QrCode_string(codice_identificativo):
    url = 'http://172.16.150.165:8000/parcheggio/reciveRasp/'
    payload = {"qr_code": codice_identificativo}
    req = requests.post(url, json=payload)
    response = req.json()
    if(response['status'] == "true"):
        conferma_entrata(True)
    else:
        conferma_entrata(False)

"""
Funzione a cui viene passato
param: booleano di tipo boolean 
Richiama la funzione apertura_sbarra() che in base al valore ricevuto aprirà la sbarra 
o attiverà il buzzer che segnala l'errore nell'identificazione.
"""
def conferma_entrata(booleano):
    sbarra.apertura_sbarra(booleano, arduino, pin_led_verde, pin_led_rosso, pin_buzzer, pin_servo)
    
while True:
    cattura_webcam()
    time.sleep(20)
