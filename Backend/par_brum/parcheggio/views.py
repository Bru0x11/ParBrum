from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers import serialize
from .models import  Prenotazione, InfoParcheggio
import json, datetime,pyqrcode, jwt
import  requests , hashlib
import smtplib, ssl
from datetime import date
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

postiParcheggioTotali = 10

#Restituisce le informazioni relative ad una prenotazione specifica sottoforma di JSON
def getPrenotazione(request,id_Prenotazione):
    try:
        response = checkHeader(request.headers['Authorization'])
    except:
        response= False
    if(response == True):
        prenotazione = Prenotazione.objects.get(pk=id_Prenotazione)
        o = {}
        o['id'] = prenotazione.pk
        o["data"] = str(prenotazione.data)
        o["nome"] = prenotazione.nome
        o["cognome"] = prenotazione.cognome
        o["email"] = prenotazione.email
        o["qrCode"] = prenotazione.qrCode
        response = o
    else:
        response= {'status': 'Unauthorizated'}
    return HttpResponse(json.dumps(response))

#Modifica del record della prenotazione e richiesta di apertura della sbarra
def deletePrenotazione(request, id_Prenotazione):
    try:
        response = checkHeader(request.headers['Authorization'])
    except:
        response= False
    if(response == True):
        response = {'status':'False'}
        status= exitRequestRaps()
        if(status == True):
            eventToUpdate = Prenotazione.objects.get(pk =id_Prenotazione )
            eventToUpdate.qrCode = "EXIT"
            eventToUpdate.save()
            response = {'status':'True'}
    return HttpResponse(json.dumps(response))

#Inserimento di un nuovo Prenotazione
def insertPrenotazione(request):
    data = json.loads(request.body)
    data_prenotazione = str(data['data'])
    try:
        response = checkPostiLiberi(data_prenotazione)
    except:
        response = False
    if(response == False):
        response = {'status': 'Full'}
    if(response == True):
        response = {'status':'False'}
        newPrenotazione = Prenotazione()
        newPrenotazione.nome = data['nome']
        newPrenotazione.cognome = data['cognome']
        newPrenotazione.data = data['data']
        newPrenotazione.email = data['email']
        newPrenotazione.qrCode = creazione_qrcode(newPrenotazione.pk,data['nome'],data['cognome'],data['data'])
        newPrenotazione.save()
        prenotazioneEffettuata = Prenotazione.objects.get(qrCode= newPrenotazione.qrCode)

        toEncode={
        'qrCode': prenotazioneEffettuata.qrCode,
        'id': prenotazioneEffettuata.pk
        }
        encoded_jwt = jwt.encode(toEncode, "secret", algorithm="HS256")
        year = str(prenotazioneEffettuata.data.year)
        month = str(prenotazioneEffettuata.data.month)
        day = str(prenotazioneEffettuata.data.day+1)
        response ={'status':'True',
                    'access_token':encoded_jwt,
                    'id': prenotazioneEffettuata.pk,
                    'token_type' : 'bearer',
                    'expires_in': str(year+"-"+month+"-"+day)
                    }
        #Passaggio parametri per la generazione dell'email riguardante la prenotazione
        invioEmailPrenotazione(prenotazioneEffettuata.nome, prenotazioneEffettuata.cognome, prenotazioneEffettuata.pk, prenotazioneEffettuata.qrCode, prenotazioneEffettuata.email, prenotazioneEffettuata.data)

    return HttpResponse(json.dumps(response))

#Ripristino token jwt che permette l'accesso ai dati della prenotazione richiesta
def recuperoPrenotazione(request):
    data = json.loads(request.body)
    response = {'status':'false'}
    try:
        prenotazione = Prenotazione.objects.get(pk=data['id'])
        toCheck = prenotazione.data
        if(str(toCheck) == data['data']):
            toEncode={
                'qrCode': prenotazione.qrCode,
                'id': prenotazione.pk
                }
            encoded_jwt = jwt.encode(toEncode, "secret", algorithm="HS256")
            response = {
                'status': 'True',
                'id': prenotazione.pk,
                'access_token':encoded_jwt
                }
        else:
         response= {'status': 'wrongData'}
    except:
        response ={'status': 'wrongId'}
    return HttpResponse(json.dumps(response))


#ENDPOINT SERVIZI PARCHEGGIO

#Calcola i posti disponibili in una determinata data e restituisce i valori
def getPostiDisponibili(request,selected_data):
    postiOccupati =  Prenotazione.objects.filter(data= selected_data).count()
    #print(postiOccupati)
    postiRimasti= postiParcheggioTotali-postiOccupati
    response = {
        "totali": postiParcheggioTotali,
        "liberi": postiRimasti
    }
    #print(response)
    return HttpResponse(json.dumps(response))

#Restituisce tutte le informazioni riguardanti il parcheggio nell'istante richiesto
def getParkInfo(request,selected_data):
    infoParking =  InfoParcheggio.objects.last()
    postiOccupati =  Prenotazione.objects.filter(data= selected_data).exclude(qrCode="EXIT").count()
    postiRimasti= postiParcheggioTotali-postiOccupati
    response = {
        "timestamp": str(infoParking.data.strftime("%Y-%m-%d %H:%M:%S")),
        "temperatura":infoParking.temperatura,
        "umidita": infoParking.umidita,
        "meteo": infoParking.meteo,
        "totali": postiParcheggioTotali,
        "liberi": postiRimasti
    }
    return HttpResponse(json.dumps(response))

#restituisce le informazioni riguardanti lo stato interno del parcheggio rilevate per l'ultima volta
def getParkInfoRasp(request):
    infoParking =  InfoParcheggio.objects.last()
    response = {
        "timestamp": str(infoParking.data.strftime("%Y-%m-%d %H:%M:%S")),
        "temperatura":infoParking.temperatura,
        "umidita": infoParking.umidita,
        "meteo": infoParking.meteo
    }
    return HttpResponse(json.dumps(response))

# controlla il numero di posti liberi in una determinata data
def checkPostiLiberi(selected_data):
    postiOccupati =  Prenotazione.objects.filter(data= selected_data).exclude(qrCode="EXIT").count()
    result = False
    if(postiOccupati < postiParcheggioTotali):
         result = True
    else:
         result = False
    return result

#Controllo del token JWT riguardanti la prenotazione
def checkHeader(header):
    try:
        toCheck = jwt.decode(header, "secret", algorithms="HS256")
        token_prenotazione = Prenotazione.objects.get(pk= toCheck['id'])
        if(token_prenotazione):
            status = True
    except:
        print("Errore di autenticazione, operazione negata.")
        status = False
    return status

#genera il codice qr, lo salva sul server e ne restituisce il percorso
def creazione_qrcode(id,nome, cognome, data):
    toHash=f"{id}_{nome}_{cognome}_{data}"
    file_name = hashlib.md5(str.encode(toHash)).hexdigest()
    qrcode = pyqrcode.create(f"{file_name}")
    qrcode.svg("media/"+f"{file_name}.svg", scale=8)
    path = "media/"+f"{file_name}.svg"
    return path

#controlla l'esistenza di un determinato qrCode valido per il giorno stesso della verifica.
def qrCodeChecker(request):
    today = date.today()
    now = today.strftime("%Y-%m-%d")
    data = json.loads(request.body)
    toCheck= "media/"+data['qr_code']+".svg"
    trovato = False
    try:
        trovato = Prenotazione.objects.get(qrCode=toCheck)
    except:
        response = {'status': 'false'}
    if(str(trovato.data) == str(now)):
        response = {'status': 'true'}
    else:
        response = {'status': 'false'}
    return HttpResponse(json.dumps(response))

#Effettua richiesta al servizio REST del Raspberry che gestisce l'apertura della sbarra
def exitRequestRaps():
    response = False
    url = 'http://172.16.151.203:80/'
    x = requests.get(url)
    responseRasp = x.json()
    if(responseRasp['status']=="True"):
       response = True
    return response

#Inserisce i dati rilevati da RaspBerry riguardanti l'ambiente del parcheggio nel DB
def insertInfoParcheggio(request):
    rasp_info = json.loads(request.body)
    response = {'status':'False'}
    newInfoParcheggio = InfoParcheggio()
    newInfoParcheggio.data = datetime.now()
    newInfoParcheggio.temperatura = rasp_info['temperatura']
    newInfoParcheggio.umidita = rasp_info['umidita']
    newInfoParcheggio.meteo = meteoParcheggio()
    newInfoParcheggio.save()
    try:
        toCheck = InfoParcheggio.objects.last()
    except:
        response = {'status':'False'}
    if(toCheck.data == newInfoParcheggio.data ):
        response = {'status':'True'}
    else:
        response = {'status':'False'}
    return HttpResponse(json.dumps(response))

#Chiamata al servizio REST che descrive il meteo
def meteoParcheggio():
    payload={'q': "Udine",
    'appid':"74a15da20deb9a594025d50243e9485a"}
    url = 'http://api.openweathermap.org/data/2.5/weather?'
    x = requests.get(url, params = payload)
    data = x.json()
    meteo=data['weather'][0]['main']
    return meteo


# SENDING EMAIL
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "parbrum@gmail.com"  # Enter your address

#Creazione dell'email riguardante la prenotazione
def invioEmailPrenotazione(nome,cognome,id,qrCode,email, data):
    receiver_email = "lorisparata@gmail.com"  # Enter receiver address
    password = "ginopino90"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Prenotazione Parbrum"
    message["From"] = sender_email
    message["To"] = email

    html =  """\
        <html>
        <body>
            <div>
                <div style="heigth=60px;   background: #ffc107; width: 100%; text-align: center;">
                    <h2 style="color: #333333; font-family: Inter; font-size: 22px; font-weight: 400; line-height: 27px; text-align: center;">Conferma Prenotazione n&deg;"""+ str(id)+"""</h2>
                </div>
                <div style="font-family: Inter; font-size: 18px; font-weight: 400; line-height: 30px;">
                <img style="display: block; margin-left: auto; margin-right: auto; width: 25%; max-width: 200px;" src='http://172.16.150.165:8000/media/icona.png'> </img> <br />
                    <h3 style="text-align: center;">Benvenuto da ParBrum</h3>
                    <p style="font-size: 14px">Ecco un riepilogo di tutte le informazioni relative alla sua prenotazione. <br />
                    Nome: """+ nome +""" <br />
                    Cognome: """+ cognome +""" <br />
                    Data della prenotazione: """+ str(data) +"""
                    <br/>Codice Qr da scannerizzare all'ingresso del parcheggio: <br />
                    <img style="display: block; margin-left: auto; margin-right: auto; width: 30%; max-width: 400px;" src='http://172.16.150.165:8000/"""+ qrCode +"""'> </img> <br />
                    Per eventuali informazioni aggiuntive o per ricevere assistenza non esitate a contattarci tramite e-mail : parbrum@gmail.com</p>
                    <div style="heigth=60px;   background: #ffc107; width: 100%; color: #333333;">
                        <h2 style="color: #333333; font-family: Inter; font-size: 22px; font-weight: 400; line-height: 27px; text-align: center;">
                    &copy; 2020 Copyright: Questo progetto &egrave; stato realizzato da Parata Loris e Brugnera Matteo</h2>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    partHtml = MIMEText(html,"html")
    message.attach(partHtml)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

