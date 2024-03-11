parametri_rilevati = []
"""
Funzione che restituisce la temperatura e l'umidità rilevata dal sensore dht22
param dht: parametro che rappresenta il dht22.
return: ritorna un vettore [temperatura, umidità]
"""
def calcolo_temperatura(dht):
    parametri_rilevati.clear()
    temperatura_gradi = dht.temperature
    umidita = dht.humidity
    parametri_rilevati.append("Temp: {:.1f} C ".format(temperatura_gradi))
    parametri_rilevati.append("Umidita': {}%".format(umidita))
    return parametri_rilevati

"""
Funzione che rileva la temperatura e l'umidità che venogno memorizzati in un JSON
param dht: parametro che rappresenta il dht22
return: json contenente temperatura ed umidità
"""
def value_sensore(dht):
    parametri_rilevati.clear()
    temperatura_gradi = dht.temperature
    umidita = dht.humidity
    response = {"temp": temperatura_gradi, "umidita": umidita}
    return response