BlueWho
=======
**Descrizione:** Informa e notifica alla rilevazione di nuovi dispositivi bluetooth

**Copyright:** 2009-2021 Fabio Castelli <muflone(at)vbsimple.net>

**Licenza:** GPL-3+

**Codice sorgente:** https://github.com/muflone/bluewho

**Documentazione:** http://www.muflone.com/bluewho

Informazioni
------------

La scansione automaticamente rilever&agrave; ogni dispositivo visibile e per
ciascun dispositivo rilevato sar&agrave; mostrata una notifica.

Ogni dispositivo trovato sar&agrave; salvato in lista col suo nome, tipo,
indirizzo e data e orario dell'ultimo avvistamento.

Per ogni dispositivo pu&ograve essere richiesto un elenco dei servizi Bluetooth
disponibili.

Requisiti di sistema
--------------------

* Python 2.x (sviluppato e testato per Python 2.7.5)
* Libreria XDG per Python 2
* Libreria GTK+3.0 per Python 2
* Libreria GObject per Python 2
* Libreria BlueZ per Python 2
* Libreria Distutils per Python 2 (generalmente fornita col pacchetto Python)

Per la notifica audio &egrave; necessario che sia installato nel sistema uno
dei seguenti riproduttori audio:

 * canberra-gtk-play
 * aplay
 * paplay
 * mplayer

Il programma eseguir&agrave; la ricerca e utilizzer&agrave il primo riproduttore
trovato.

Installazione
-------------

E' disponibile uno script di installazione distutils per installare da sorgenti.

Per installare nel tuo sistema utilizzare:

    cd /percorso/alla/cartella
    python2 setup.py install

Per installare i files in un altro percorso invece del prefisso /usr standard
usare:

    cd /percorso/alla/cartella
    python2 setup.py install --root NUOVO_PERCORSO

Utilizzo
--------

Se l'applicazione non è stata installata utilizzare:

    cd /path/to/folder
    python2 bluewho.py

Se l'applicazione è stata installata utilizzare semplicemente il comando
bluewho.
