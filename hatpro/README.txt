##aus cronjob meteo-data

#IMGI DB INSERT Stuff
#-------------------------------------------------------------------
###läuft auf der acinn-meteo über 4h ein run, warum?
### P2 Version läuft auf acinn-meteo, weil P3 version viel zu langsam
###15 * * * * /bin/bash /mnt/imgi2-a/c7071039/imgi_wrapper_dev/insert_hatpro_data_ALL.sh > /dev/null 2>&1