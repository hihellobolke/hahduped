#!/usr/bin/env python

import argparse
import re
import csv
import datetime


parser = argparse.ArgumentParser(description='Parses Hadoop log file, and generates CSV file for import in Excel')
parser.add_argument('logFile', type=argparse.FileType('r'),
                   help='Hadoop log file to read')
parser.add_argument('outFile', type=argparse.FileType('w'),
                   help='Output file as csv file to import in excel')
args = parser.parse_args()


def logFile_reader(logFile):
    print("Reading log file: {}".format(logFile.name))
    fields = "ID_TYPE", "ID_VALUE", "START_TIME", "FINISH_TIME", "DURATION"
    stats = {}
    # Let's define regex that match fields we are intrested in...
    regex_jobid = re.compile('JOBID="([^"]+)"')
    regex_taskid = re.compile('TASKID="([^"]+)"')
    regex_start_time = re.compile('(START|LAUNCH)_TIME="([0-9]+)"')
    regex_finish_time = re.compile('FINISH_TIME="([0-9]+)"')
    #
    for line in args.logFile:
        id_type = None
        id_value = None
        #
        match_jobid = regex_jobid.search(line)
        if match_jobid:
            id_type = "JOBID"
            id_value = match_jobid.group(1)
        #
        match_taskid = regex_taskid.search(line)
        if match_taskid:
            id_type = "TASKID"
            id_value = match_taskid.group(1)
        #
        if id_type and id_value:
            if id_type not in stats:
                stats[id_type] = {}
            if id_value not in stats[id_type]:
                stats[id_type][id_value] = {}
            #
            mystat = stats[id_type][id_value]
            #
            if 'START_TIME' not in mystat:
                match_start_time = regex_start_time.search(line)
                if match_start_time:
                    mystat['START_TIME'] = int(match_start_time.group(2))
                    #mystat['START_TIME_HUMAN'] = unix2human_time(match_start_time.group(1))
                    if 'FINISH_TIME' in mystat:
                        mystat['DURATION'] = mystat['FINISH_TIME'] - mystat['START_TIME']
            #
            match_finish_time = regex_finish_time.search(line)
            if match_finish_time:
                mystat['FINISH_TIME'] = int(match_finish_time.group(1))
                #mystat['FINISH_TIME_HUMAN'] = unix2human_time(match_finish_time.group(1))
                if 'START_TIME' in mystat:
                    mystat['DURATION'] = mystat['FINISH_TIME'] - mystat['START_TIME']
    #
    return fields, stats

def unix2human_time(utime):
    return datetime.datetime.fromtimestamp(int(utime)).strftime('%Y-%m-%d %H:%M:%S')


if args.outFile:
    csvwriter = csv.writer(args.outFile)
    fields, stats = logFile_reader(args.logFile)
    # write Header
    csvwriter.writerow(fields)
    # write data
    count = 0
    for id_type in stats:
        for id_value in stats[id_type]:
            csvrow = [id_type, id_value]
            for field in fields[2:]:
                try:
                    csvrow.append(stats[id_type][id_value][field])
                except:
                    csvrow.append("")
            count += 1
            csvwriter.writerow(csvrow)
    print("Finished writing {} rows: {}".format(count, args.outFile.name))

