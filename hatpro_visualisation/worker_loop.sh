#!/bin/bash

#$1 -> datefrom in format e.g. 20140922
#$2 -> dateto in format e.g. 20140922

##

PATH_TO_IBOXDIR=/home/c7071039/sabo_projects/P3_iboxcreator

if [ "$#" -ne 2 ]; then
    echo -e "\nNeed begin-date i.e. 20211213 and an end-date"
    echo -e "bash worker_loop.sh 2021201 20211213\n"
    exit 2
fi

start=$1
end=$2

start=$(date -d $start +%Y%m%d)
end=$(date -d $end +%Y%m%d)

while [[ $start -le $end ]]
do
    tempend=$(date -d"$start + 1 day" +"%Y%m%d")
    bash script_sabo.sh ${start} ${tempend}
    #bash ${PATH_TO_IBOXDIR}/workerFILLED_dat.sh ${STATNR} ${start} 
	start=$(date -d"$start + 1 day" +"%Y%m%d")
done
