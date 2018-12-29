#!/bin/bash

#job_group=quicknormal
job_group=quicknormal
timestamp=$(date +%Y%m%d)
output_excel_name="test_fio_"$timestamp'.xlsx'
group_list=$(grep -vE "^$|^#" ./grouplist)

if [[ -z $group_list ]];then
    echo "no valid group name in grouplist!"
    exit 1
elif [[ -z $1 ]] || [[ -z $group_list ]];then
    echo "function: test the group in grouplist single and/or parallel"
    echo "default fio test job group: $job_group "
    echo "default excel report name : $output_excel_name"
    echo "currently valid group list: \"$group_list\""
    echo -e "Usage: \vnohup $0  <-s|-p|-all>  <output excel file name>  &>grouplist.log &"
    exit 1
fi
[[ -n $2 ]] && output_excel_name="$2"

function group_test(){
    mode=$1
    [[ $mode == "single" ]] && mode_arg="-s"
    for i in $group_list;do
        nohup $(dirname $0)/cfiojobs -g $i -b $i -j $job_group -f $mode_arg --fio -o $i"_"$mode"_"$timestamp &> $i"_"$mode"_"$timestamp.log &
    done
}

function wait_test(){
    while ps aux |grep $(whoami) |grep cfiojobs |grep '\-\-'fio'\ ' |grep -vq grep ;do
        sleep 60
    done
}


if [[ $1 == "-s" ]] ;then
    group_test "single"
elif [[ $1 == "-p" ]] ;then
    group_test "parallel"
elif [[ $1 == "-all" ]] ;then
    group_test "parallel"
    wait_test
    group_test "single"
    wait_test
    for i in $group_list;do
        #[[ $(grep -vE "^$|^#" conf/$i'.blk' |sort -u |wc -l) -eq 1 ]] && continue
        $(dirname $0)/bin/cfiojobs.contrast2.sh $i"_parallel_"$timestamp $i"_single_"$timestamp $output_excel_name 
    done 
    tar czf test_"$timestamp"_report.tar.gz $(find ./ -type f -name *_all_host.csv) $(find ./ -type f -name *_all_host-contrast.csv)
    tar czf test_"$timestamp".tar.gz *"$timestamp" *"$timestamp".log 
fi
