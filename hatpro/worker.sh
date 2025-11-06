#!/bin/sh

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/oracle/11.2/client64/lib/

PATH_TO_IMGIDIR=/home/c7071039/sabo_projects/P3_imgi_wrapper_dev
PATH_TO_HATPRO=/home/c7071039/sabo_projects/P2_hatpro
SQLITE_DB_FILE=${PATH_TO_HATPRO}/hatprodata.db
PATH_TO_PYTHON2=${PATH_TO_HATPRO}/venv/bin
PATH_TO_PYTHON3=${PATH_TO_IMGIDIR}/venv/bin

#get actual HOUR
YEAR=$(TZ=UTC /bin/date -d "2 hour ago" +"%Y")
MONTH=$(TZ=UTC /bin/date -d "2 hour ago" +"%m")
DAY=$(TZ=UTC /bin/date -d "2 hour ago" +"%d")
HOUR=$(TZ=UTC /bin/date -d "2 hour ago" +"%H")

# i.e. $1 -> /mnt/rawdata/hatpro/Y2023/M12/D15
PATH_TO_RAWDATA_RAW="/mnt/rawdata/hatpro/"
#PATH_TO_RAWDATA_WITH_HOUR=${PATH_TO_RAWDATA}"Y"${YEAR}"/M"${MONTH}"/D"${DAY}"/H"${HOUR}
PATH_TO_RAWDATA=${PATH_TO_RAWDATA_RAW}"Y${YEAR}/M${MONTH}/D${DAY}"
echo ${PATH_TO_RAWDATA}
PATH_TO_RAWDATA_WITH_HOUR=${PATH_TO_RAWDATA}"/H${HOUR}"
echo ${PATH_TO_RAWDATA_WITH_HOUR}

if [ -e ${SQLITE_DB_FILE} ]
then
    /bin/rm ${SQLITE_DB_FILE}
fi

${PATH_TO_PYTHON2}/python ${PATH_TO_HATPRO}/masterfile.py ${PATH_TO_RAWDATA} ${PATH_TO_HATPRO} ${HOUR} && ${PATH_TO_PYTHON3}/python ${PATH_TO_IMGIDIR}/modules/insertHatpro.py ${PATH_TO_RAWDATA_WITH_HOUR}

if [ -e ${SQLITE_DB_FILE} ]
then
    /bin/rm ${SQLITE_DB_FILE}
fi

## hier müsste noch die bilderzeugung für die letzten 48h hatprobild eingefügt werden
