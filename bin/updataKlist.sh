#/bin/bash

today=$(date +"%Y%m%d")

for tsDir in $(ls -d ../output/${today}*/)
do
    ts=`basename $tsDir`
    for content in `ls -d ${tsDir}_content_*`
    do 
       basename $content >> ../data/klist.$ts
    done
done
