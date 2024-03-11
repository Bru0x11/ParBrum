
from django.contrib import admin
from django.urls import path, include


from parcheggio import views as par_brum_views

urlpatterns = [
    #PATH PER LA GESTIONE DELLE API
    path("getPrenotazione/<int:id_Prenotazione>/", par_brum_views.getPrenotazione),
    path("insertPrenotazione/", par_brum_views.insertPrenotazione),
    path("deletePrenotazione/<int:id_Prenotazione>/", par_brum_views.deletePrenotazione),
    path("postiRimasti/<str:selected_data>/", par_brum_views.getPostiDisponibili),
    path("getParkInfo/<str:selected_data>/", par_brum_views.getParkInfo),
    path("reciveRasp/", par_brum_views.qrCodeChecker),
    path("getMeteo/", par_brum_views.meteoParcheggio),
    path("insertInfoParking/", par_brum_views.insertInfoParcheggio),
    path("recuperoPrenotazione",par_brum_views.recuperoPrenotazione),
    path("getInfoMeteoRasp/",par_brum_views.getParkInfoRasp),
]