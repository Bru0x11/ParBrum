from flask import Flask
import sbarra, json, pyfirmata
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
Funzione che viene usata nel momento in cui il valore di entrata risulta
essere TRUE/FALSE. Andrà quindi ad eseguire l'apertura della sbarra su arduino, oppure ritornerà errore.
:param booleano: valore TRUE/FALSE
"""
def conferma_uscita(booleano):
    sbarra.apertura_sbarra(booleano, arduino, pin_led_verde, pin_led_rosso, pin_buzzer, pin_servo)

app = Flask(__name__)
@app.route('/')
def index():
    conferma_uscita(True)
    status = {
        "status":"True"}
    return json.dumps(status)

if __name__ == '__main__':
    app.run(debug=False, port=80, host='172.16.151.203')
