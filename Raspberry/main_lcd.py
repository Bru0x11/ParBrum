import calcolo_temperatura
import time, requests
from RPi import GPIO
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

"""
Inizializzazione variabili per sensore DHT22 e LCD1602:
-lcd_*: indica quale GPIO viene assegnato ad ogni elemento del lcd,il quale viene usato
        in modalità 4 bit.
"""
lcd_columns = 16
lcd_rows = 2
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d4 = digitalio.DigitalInOut(board.D13)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d7 = digitalio.DigitalInOut(board.D11)

#Inizializzazione della classe lcd
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

"""
Funzione che mostra sul lcd un messaggio di benvenuto al parcheggio alternato alla temperatura e umidità.
I due valori vengono presi dalla funzione calcolo_temperatura() passando il dht inizializzato precedentemente.
:return:
"""
def display_temperatura():

    try:
        lcd.clear()
        frase_benvenuto = "Benvenuto al\n" + "ParBrum!"
        lcd.message = frase_benvenuto
        time.sleep(4)
        risultato_finale = calcolo_temperatura.calcolo_temperatura(dht)
        lcd.message = risultato_finale[0] + "\n" + risultato_finale[1]
        time.sleep(4)
    except Exception as e:
        print(e)

"""
Funzione che apre il tetto del parcheggio utilizzando due servi tramite la libreria GPIO.
"""
def apri_tetto():
    servoPIN = 10 #pin utilizzato dal primo servo
    servoPIN2 = 9 #pin utilizzato dal secondo servo

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    GPIO.setup(servoPIN2, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)  # GPIO 10 PWM con 50Hz
    p2 = GPIO.PWM(servoPIN2, 50)# GPIO9 PWM con 50Hz

    #Inizializzazione
    p.start(2.5)
    p2.start(2.5)

    #Movimento servi per aprire
    p.ChangeDutyCycle(7.5)
    p2.ChangeDutyCycle(7.5)
    time.sleep(2)
    
    #Interruzione movimento servi
    p.stop()
    p2.stop()

"""
Funzione che apre il tetto del parcheggio utilizzando due servi tramite la libreria GPIO.
"""
def chiudi_tetto():
    servoPIN = 10 #pin utilizzato dal primo servo
    servoPIN2 = 9 #pin utilizzato dal secondo servo
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    GPIO.setup(servoPIN2, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)  # GPIO 10 PWM con 50Hz
    p2 = GPIO.PWM(servoPIN2, 50)# GPIO 9 PWM con 50Hz
    
    #Inizializzazione
    p.start(2.5)  
    p2.start(2.5)
    
    #Movimento servi per chiudere
    p.ChangeDutyCycle(12.5)
    p2.ChangeDutyCycle(12.5)
    time.sleep(2)
    
    #Interruzione movimento servomotori
    p.stop()
    p2.stop()

"""
Funzione che richiede al sito informazioni inerenti al meteo. Qualora esse siano -temporale-, -pioggia- oppure
la temperatura è maggiore di 25 gradi, allora il tetto viene chiuso, altrimenti il tetto viene aperto.
"""
def getMeteo():
    url = 'http://172.16.150.165:8000/parcheggio/getInfoMeteoRasp'
    req = requests.get(url)
    response = req.json()
    if (response['meteo'] == "Thunderstorm" or response['meteo'] == "Rain" or int(response['temperatura']) > 25):
        chiudi_tetto()
    else:
        apri_tetto()

"""
Funzione che inserisce all'interno del database informazioni inerenti alla temperatura e all'umidità.
"""
def setTempAndHum():
    sensore = calcolo_temperatura.value_sensore(dht)
    temperatura = sensore["temp"]
    umidita = sensore["umidita"]
    payload = {"temperatura": temperatura, "umidita": umidita}
    url = 'http://172.16.150.165:8000/parcheggio/insertInfoParking/'
    req = requests.post(url, json=payload)
    

while True:
    display_temperatura()
    getMeteo()
    setTempAndHum()
    time.sleep(60)