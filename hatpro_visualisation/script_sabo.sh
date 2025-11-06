#!/bin/bash

# bash script here to define period that gets plotted
# author: Lukas Lehner, lehner.lukas(at)hotmail.com
# date: March 2017

# SABO rework 2023.11.14

startdate_small=$1
enddate_small_plusone=$2

startdate="${startdate_small} 00:00"
enddate="${enddate_small_plusone} 00:00"

echo "startdate_small:"$startdate_small
echo "enddate_small_plusone:"$enddate_small_plusone

cd /home/c7071039/sabo_projects/P3_imgi_wrapper_dev
WRAPPER_PATH="/home/c7071039/sabo_projects/P3_imgi_wrapper_dev/"
${WRAPPER_PATH}venv/bin/python ${WRAPPER_PATH}modules/wrapper.py --station 200 --begin $startdate_small --end $enddate_small_plusone > /tmp/200_hatpro.csv
${WRAPPER_PATH}venv/bin/python ${WRAPPER_PATH}modules/wrapper.py --station 201 --begin $startdate_small --end $enddate_small_plusone > /tmp/201_hatpro.csv
${WRAPPER_PATH}venv/bin/python ${WRAPPER_PATH}modules/wrapper.py --station 202 --begin $startdate_small --end $enddate_small_plusone > /tmp/202_hatpro.csv
cd /home/c7071039/sabo_projects/P3_hatpro_visualisation

############################
# start main program
############################
archive='1' # 0: this task should not produce a archived graph (different plot)
echo "start main.py with date: "$startdate
echo "end main.py with date: "$enddate
echo "archive main.py with date: "$archive
${WRAPPER_PATH}venv/bin/python /home/c7071039/sabo_projects/P3_hatpro_visualisation/main.py $startdate $enddate $archive # absolute paths!!

#mv /mnt/imgi4-a/piano_oper/images/hatpro/hatpro_new.png /mnt/imgi4-a/piano_oper/images/hatpro/hatpro_current.png
#TZ='UTC'
#date "+%Y-%m-%d_%H:%M:%S" > /mnt/data/lidar/images/hook.txt
