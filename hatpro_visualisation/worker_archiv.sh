#!/bin/bash

yest=$(date -d"$start - 1 day" +"%Y%m%d")
today=$(date +"%Y%m%d")
bash script_sabo.sh ${yest} ${today}
