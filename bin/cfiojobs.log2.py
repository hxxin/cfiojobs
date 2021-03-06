#!/usr/bin/env python
# -*- coding:utf-8 -*-
#from multiprocessing.dummy import Pool as ThreadPool
from subprocess import Popen, PIPE
import cfiojobsutil.utils as cu 
#import stackless 
import os
import sys

try:
    logdir    = sys.argv[1]
    #remove last '/'
    if logdir[-1] == '/' :
        logdir=logdir[:-1]
    output_dir = logdir + '/_report/'
    try:
        os.mkdir(output_dir)
    except:
        pass 
except IndexError:
    print "script Usage: \n",sys.argv[0]," <cluster fiolog dir>  <nocompare|rbd> \nplease pass in directory name first, the other options can be omitted."
    exit()
try:
    output_mode = sys.argv[2]
except IndexError:
    output_mode = 'normal'

#pool = ThreadPool()

# special index  ['bw', 'iops', 'lat_max', 'lat_avg', 'lat_min', 'lat_stddev']
avg_index   = ['bw', 'iops', 'lat_avg']
avg_index_note = u'测试平均带宽MiB/s,测试平均iops,测试平均延迟(ms)\n'

# the performance threshold value
dev_perf_index  = {'hdd' :0.9,
                   'nvme':0.6,
                   'rbd' :0.6
                  }

def get_json_list(dir_name):
    cmd = 'find ' + dir_name + ' -type f -name *.log.json' 
    p = Popen([cmd],shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    return p.stdout.read().split('\n')[:-1]

def max_filter(perf_log, bp, key_index):
    pass 

def min_filter(perf_log, bp, key_index):
    pass 

def peak_filter(perf_log, bp, key_index):
    pass 

# compare with avg and add a tag of data stat 
def update_compare_tag(perf_log, perf_filter='bw'):
    global perf_list 
    global peak_dict 
    no = perf_list.index(perf_log)
    # confirm bp and blk type 
    bp = perf_log['pattern_name']
    blk_type = perf_log['blk_type']
    # update compare tag : ['deviation','stat']
    try:
        perf_list[no]['deviation'] = str(round(float(perf_log[perf_filter]) / peak_dict[blk_type][bp][perf_filter] *100, 2)) +'%'
    except:
        print(perf_log)
    if float(perf_log[perf_filter]) < float(peak_dict[blk_type][bp][perf_filter]) * dev_perf_index[blk_type]:
        perf_list[no]['stat']  = u'●'.encode('GB2312')
    else:
        perf_list[no]['stat']  = u'○'.encode('GB2312')
    # add avg_value : ['bw_global','iops_global','lat_avg_global',]
    for index in avg_index : 
        perf_list[no][index + '_global'] = float(peak_dict[blk_type][bp][index])

##################################################################################
# get an array of all result
# perf_list a list of dict 
perf_list   = list()
#for logfile in get_json_list(logdir):
    # host ip, dev(file name) , pattern 
#    log_dict = cu.load_json_log(logfile)
#    if len(log_dict) == 0 :
#        continue
#    for perf_log in cu.parse_log_dict(log_dict):
#        perf_list.append(perf_log)
#print(perf_list)

def add_valid_log(logfile):
    global perf_list 
    log_dict = cu.load_json_log(logfile)
    if len(log_dict) > 0 :
        for perf_log in cu.parse_log_dict(log_dict):
            perf_list.append(perf_log)

map(add_valid_log, get_json_list(logdir))
#map(lambda logfile: stackless.tasklet(add_valid_log)(logfile) ,get_json_list(logdir))
#stackless.run()

#def add_log(logfile):
#    global perf_list 
#    log_dict = cu.load_json_log(logfile)
#    map(lambda perf_log: perf_list.append(perf_log),  cu.parse_log_dict(log_dict))

#pool.map(add_log, get_json_list(logdir))
#pool.close()
#pool.join()

# get bs_pattern list set 
bs_pattern_list = list(set(map(lambda x : x['pattern_name'], perf_list)))
#print(bs_pattern_list)

# vag and peak values 
peak_dict = dict()
# perf list of certain type of block, like: hdd or nvme 
type_perf_list = dict()

# calculate avg value for specified index of all pattern and all blk type 
for test_blk_type in ['hdd', 'nvme', 'rbd']:
    # log screening
    blk_list = filter(lambda x : x['blk_type'] == test_blk_type, perf_list)
    blk_log_amount = len(blk_list)
    if blk_log_amount > 0:
        print test_blk_type, 'logs:', blk_log_amount 
        peak_dict[test_blk_type]=dict()
        # add to type dict 
        type_perf_list[test_blk_type] = blk_list 
        for bp in bs_pattern_list:
            blk_bp_list = filter(lambda x : x['pattern_name'] == bp, blk_list)
            log_amount = len(blk_bp_list)
            if log_amount > 0:
                peak_dict[test_blk_type][bp]  = dict()
                # cont and give sum value
                for index in avg_index:
                    index_values   = map(lambda x : float(x[index]), blk_bp_list)
                    peak_dict[test_blk_type][bp][index] = reduce(lambda x, y: x + y , index_values) /log_amount
#print(peak_dict)

# calculate vag values for each pattern 
if output_mode in ['normal', 'rbd']:
    # compare bw and iops value with global avg 
    map(update_compare_tag, perf_list)
#cu.print_dic(perf_list[1])

# save performance dict list to csv sheet 
def save_perf_list(perf_list, keys_of_column, csv_title, csv_name):
    #global perf_list 
    with open(csv_name, 'w') as output_file:
        output_file.write(csv_title)
    # get order list by key,  get list form dict 
    result_array = map(lambda dic_log: map(lambda k: dic_log[k], keys_of_column), perf_list)
    cu.save_csv(result_array, csv_name, mode='a')

# set output value keys and title then give a report
if output_mode == 'normal':
    sheet_keys  = ['hostname','filename','pattern_name','bw','bw_global','deviation','stat','iops','iops_global','lat_avg','lat_avg_global','lat_max','lat_min','iodepth','numjobs','util','size','runtime','direct','ioengine']
    #sheet_title = ','.join(sheet_keys) + '\n'
    sheet_title = u'主机名,测试设备,块大小/模式,该盘测试带宽(MiB/s),测试带宽平均值(MiB/s),相对平均带宽的比值(公式:(D2/E2)*100%),"筛选状态(该盘测试带宽值/同批次测试主机的所有同类型磁盘的带宽平均值;低于90%标为●否则记为○)",该测试每秒读写(iops),测试每秒读写(iops)平均值,该测试平均延迟(ms),测试延迟平均值(ms),该测试最大延迟(ms),该测试最低延迟(ms),读写队列深度,该测试作业并发进程数,该测试设备使用率,测试数据量,测试时长,buffer禁用状态(1=禁用),读写数据引擎\n'.encode('GB2312')
elif output_mode == 'nocompare':
    sheet_keys  = ['hostname','filename','pattern_name','bw','iops','lat_avg','lat_max','lat_min','iodepth','numjobs','util','size','runtime','direct','ioengine']
    sheet_title = '主机名,测试设备,块大小/模式,测试带宽(MiB/s),每秒读写(iops),平均延迟(ms),最大延迟(ms),最低延迟(ms),iodepth,numjobs,util,size,runtime,direct,ioengine\n'
elif output_mode == 'rbd':
    sheet_keys  = ['hostname','filename','pattern_name','bw','bw_global','iops','iops_global','lat_avg','lat_avg_global','lat_max','lat_min','lat_stddev','iodepth','numjobs','util','size','runtime','direct','ioengine','clat_ms_seq_str']
    #clat_ms_seq_key = [0.0, 1.0, 10.0, 20.0, 30.0, 40.0, 5.0, 50.0, 60.0, 70.0, 80.0, 90.0, 95.0, 99.0, 99.5, 99.9, 99.95, 99.99]
    #clat_ms_seq_key = ''join(map(lambda x: str(x) + '%,', clat_ms_seq_key))[:-1]
    clat_ms_seq_key = '99.0%,90.0%,80.0%,70.0%,60.0%,95.0%,50.0%,40.0%,30.0%,20.0%,10.0%,5.0%,1.0%,0.5%,0.1%,0.05%,0.01%'
    sheet_title_str = u'主机名,测试设备,块大小/模式,该盘测试带宽(MiB/s),测试带宽平均值(MiB/s),该测试每秒读写(iops),测试每秒读写(iops)平均值,该测试平均延迟(ms),测试延迟平均值(ms),该测试最大延迟(ms),该测试最低延迟(ms),延迟值离散度(stdev),读写队列深度,该测试作业并发进程数,该测试设备使用率,测试数据量,测试时长,buffer禁用状态(1=禁用),读写数据引擎'
    sheet_title = sheet_title_str.encode('GB2312') + ',' + clat_ms_seq_key + '\n'

# save all type of log to csv file
for test_blk_type in type_perf_list:
    perf_list_type = type_perf_list[test_blk_type]
    csv_name = output_dir + logdir.split('/')[-1] + '_' + test_blk_type + '_all_host.csv'
    if len(perf_list_type) > 0 :
        save_perf_list(sorted(perf_list_type, key=lambda x : x['filename']), sheet_keys, sheet_title, csv_name )
        print csv_name, 'report generating success!'
        # save avg sheet 
        avg_sheet = list()
        for bp in sorted(bs_pattern_list, key=lambda x: cu.bp2num(x)):
            bp_avg = dict()
            bp_avg['bp'] = bp 
            for index in avg_index:
                bp_avg[index] = peak_dict[test_blk_type][bp][index]
            avg_sheet.append(bp_avg)
        k = ['bp'] + avg_index 
        ts = u'块大小/模式,' + avg_index_note 
        t = ts.encode('GB2312')
        n = output_dir + logdir.split('/')[-1] + '_' + test_blk_type + '_avg.csv'
        save_perf_list(avg_sheet, k, t, n)
