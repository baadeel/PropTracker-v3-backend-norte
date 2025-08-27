from scrape.pisos.refresh_particulares import refresh_particulares_parte_1 as refresh_pisos_1
from scrape.pisos.refresh_particulares import refresh_particulares_parte_2 as refresh_pisos_2
from scrape.idealista.refresh_particulares import refresh_particulares as refresh_idealista
from scrape.yaencontre.refresh_particulares import refresh_particulares as refresh_yaencontre
from scrape.indomio.refresh_particulares import refresh_particulares as refresh_indomio

if __name__ == "__main__":
    refresh_idealista()
    refresh_pisos_1()
    refresh_pisos_2()
    refresh_yaencontre()
    refresh_indomio()