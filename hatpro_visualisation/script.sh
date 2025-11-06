#!/bin/bash
# bash script here to define period that gets plotted
# author: Lukas Lehner, lehner.lukas(at)hotmail.com
# date: March 2017
set -e
export PYTHONPATH=$SYBASE/$SYBASE_OCS/python/python26_64r/lib
export LD_LIBRARY_PATH=/usr/lib/oracle/11.2/client64/lib:$LD_LIBRARY_PATH
export MPLBACKEND=Agg
export TZ=UTC
unset LANG
# operationally, 27 hours back from now
offset=$(TZ=UTC date +%M)
#offset=$(($offset % 10))
startdate_raw=$(TZ=UTC date +%s -d "1 day ago 2 hours ago $offset minutes ago") # 24 hours ago, subtract offset and subtract 10 minutes (that are not plotted, see xlim settings in plot module)
startdate=$(TZ=UTC date -d @$startdate_raw "+%Y-%m-%d %H:%M")
startdate_small=$(TZ=UTC date -d @$startdate_raw "+%Y%m%d")

enddate_raw=$(($startdate_raw + 93600)) # startdate + 25 hours
enddate=$(TZ=UTC date -d @$enddate_raw "+%Y-%m-%d %H:%M")
enddate_small=$(TZ=UTC date -d @$enddate_raw "+%Y%m%d") #enddate for hatpro wrapper
enddate_small_plusone=$(TZ=UTC date '+%Y%m%d' -d "$enddate + 1 day") #enddate for sybase query (last day excluded)

echo $startdate_small
echo $enddate_small_plusone

if [[ $(hostname) == "lukas-ThinkPad-T420" ]]; then 
# just do nothing
user="lukas"
else
	# hatpro wrapper: temperature, humidity, weather station data in separate files. Change path to the data files  in 'settings_url.py'.
	pushd /mnt/imgi2-a/c7071039/imgi_wrapper_dev >/dev/null
	/home/c707/c7071039/virtualenv/bin/python /mnt/imgi2-a/c7071039/imgi_wrapper_dev/wrapper.py --station 200 --begin $startdate_small --end $enddate_small_plusone  > /mnt/imgi4-a/piano_oper/tmp/200_operationell.csv
	/home/c707/c7071039/virtualenv/bin/python /mnt/imgi2-a/c7071039/imgi_wrapper_dev/wrapper.py --station 201 --begin $startdate_small --end $enddate_small_plusone  > /mnt/imgi4-a/piano_oper/tmp/201_operationell.csv
	/home/c707/c7071039/virtualenv/bin/python /mnt/imgi2-a/c7071039/imgi_wrapper_dev/wrapper.py --station 202 --begin $startdate_small --end $enddate_small_plusone  > /mnt/imgi4-a/piano_oper/tmp/202_operationell.csv #without header: --noheader
	popd >/dev/null
	# sybase query
	pushd ~acinn_sybase/Sybase2 >/dev/null
	../virtualenv/bin/python getobs.py -t tawes -s 11320 --YYYYmmdd -b $startdate_small -e $enddate_small_plusone > /mnt/imgi4-a/piano_oper/tmp/11320_sybaseforhatpro_operationell.txt
	popd >/dev/null
fi

############################
# start main program
############################
archive='0' # 0: this task should not produce a archived graph (different plot)
cd /mnt/imgi4-a/piano_oper/hatpro
/mnt/imgi4-a/piano_oper/venv/bin/python main.py $startdate $enddate $archive # absolute paths!!
mv /mnt/imgi4-a/piano_oper/images/hatpro/hatpro_new.png /mnt/imgi4-a/piano_oper/images/hatpro/hatpro_current.png
#TZ='UTC'
#date "+%Y-%m-%d_%H:%M:%S" > /mnt/data/lidar/images/hook.txt
