'''
Apre la sbarra ed attiva il led verde se valore_passato_qrcode è true, altrimenti attiva il buzzer che segnala l'errore
'''
def apertura_sbarra(valore_passato_qrcode, arduino, pin_led_verde, pin_led_rosso, pin_buzzer, pin_servo):
    
    if valore_passato_qrcode:
        arduino.digital[pin_led_rosso].write(0)
        arduino.digital[pin_led_verde].write(1)
        pin_servo.write(100)
        arduino.pass_time(7)
        pin_servo.write(0)
    else:
        tempo = 0
        while tempo < 800:
            arduino.digital[pin_buzzer].write(1)
            arduino.digital[pin_buzzer].write(0)
            tempo += 1

    arduino.digital[pin_led_verde].write(0)
    arduino.digital[pin_led_rosso].write(1)
