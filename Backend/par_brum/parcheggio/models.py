from django.db import models

class Prenotazione(models.Model):
    """ il modello generico di una prenotazione """
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    email = models.CharField(max_length=256)
    data = models.DateField(auto_now_add=False)
    qrCode = models.CharField(max_length=256)

    def __str__(self):
        return self.nome

class InfoParcheggio(models.Model):
    """modello generico di un oggetto contenente le informazioni del parcheggio """
    data = models.DateTimeField()
    temperatura = models.IntegerField()
    umidita = models.IntegerField()
    meteo = models.CharField(max_length=30)

    def __str__(self):
        return self.data


