#!/bin/sh

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/oracle/11.2/client64/lib/

if [ "$#" -ne 1 ]; then
    echo -e "\nNeed a date i.e. 20211213"
    echo -e "bash worker_archiv.sh 20211213\n"
    exit 2
fi

PATH_TO_IMGIDIR=/home/c7071039/sabo_projects/P3_imgi_wrapper_dev
PATH_TO_HATPRO=/home/c7071039/sabo_projects/P2_hatpro
SQLITE_DB_FILE=${PATH_TO_HATPRO}/hatprodata.db
PATH_TO_PYTHON2=${PATH_TO_HATPRO}/venv/bin
PATH_TO_PYTHON3=${PATH_TO_IMGIDIR}/venv/bin

MYEAR=$(date --date="$1" +'%Y')
MMONTH=$(date --date="$1" +'%m')
MDAY=$(date --date="$1" +'%d')

# i.e. $1 -> /mnt/rawdata/hatpro_profiles/Y2015/M09/D12
PATH_TO_RAWDATA="/mnt/rawdata/hatpro/Y"${MYEAR}"/M"${MMONTH}"/D"${MDAY}
echo ${PATH_TO_RAWDATA}

#maybe left because testing
if [ -e ${SQLITE_DB_FILE} ]
then
    /bin/rm ${SQLITE_DB_FILE}
fi

for i in {00..23}
    do
        PATH_TO_RAWDATA_WITH_HOUR=${PATH_TO_RAWDATA}"/H"${i}
        #echo ${PATH_TO_RAWDATA_WITH_HOUR}
        ${PATH_TO_PYTHON2}/python ${PATH_TO_HATPRO}/masterfile.py ${PATH_TO_RAWDATA} ${PATH_TO_HATPRO} ${i} && ${PATH_TO_PYTHON3}/python ${PATH_TO_IMGIDIR}/modules/insertHatpro.py ${PATH_TO_RAWDATA_WITH_HOUR}
        if [ -e ${SQLITE_DB_FILE} ]
        then
            /bin/rm ${SQLITE_DB_FILE}
        fi
    done

