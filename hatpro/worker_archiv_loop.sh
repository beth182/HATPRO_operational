#!/bin/bash

#$1 -> datefrom in format e.g. 20140922
#$2 -> dateto in format e.g. 20140922

if [ "$#" -ne 2 ]; then
    echo -e "\nNeed a begin-date i.e. 20211201 and an end-date"
    echo -e "bash worker_archiv_loop.sh 20211201 20211213\n"
    exit 2
fi

PATH_TO_HATPRO=/home/c7071039/sabo_projects/P2_hatpro

start=$1
end=$2

start=$(date -d $start +%Y%m%d)
end=$(date -d $end +%Y%m%d)

while [[ $start -le $end ]]
do
    /bin/bash ${PATH_TO_HATPRO}/worker_archiv.sh ${start}

    ##create archiv image
    tempend=$(date -d"$start + 1 day" +"%Y%m%d")
    bash /home/c7071039/sabo_projects/P3_hatpro_visualisation/script_sabo.sh ${start} ${tempend}

    start=$(date -d"$start + 1 day" +"%Y%m%d")
done

