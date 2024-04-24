import os
import csv
import pandas

from extract_value import *

path_to_data = "../perf_data"

# These should be extracted from the file_name.
build = "himalia-102"
build_cmd = ""

# Dictionary defining locations where to extract each result value.
parse_config = [
    ('sched/pipe', 5, ' ', 'usecs/op'),
    ('syscall/basic', 4, ' ', 'usecs/op'),
    ('mem/memcpy', 4, ' ', 'MB/sec'),
    ('mem/memset', 4, ' ', 'MB/sec'),
    ('numa-mem', 8, ' ', ' GB/sec/thread'),
    ('futex/hash', 8, 'Averaged', ' operations/sec'),
    ('futex/wake ', 13, 'threads in ', ' ms '),
    ('futex/wake-parallel', 13, '(waking 1/4 threads) in ', ' ms '),
    ('futex/requeue', 13, 'threads in ', ' ms '),
    ('futex/lock-pi', 8, 'Averaged ', ' operations/sec'),
    ('epoll/wait', 7, 'Averaged ', ' operations/sec'),
    ('ADD operations', 0, 'Averaged ', ' ADD operations'),
    ('MOD operations', 0, 'Averaged ', ' MOD operations'),
    ('DEL operations', 0, 'Averaged ', ' DEL operations'),
    ('internals/synthesize', 5, 'time per event ', ' usec'),
    ('internals/kallsyms-parse', 1, 'took: ', ' ms ')
]

# Separate config for the test 'mem/find_bit' which has multiple output values.
find_bit_parse_config = []
bits = 1
while bits < 2050:
    bits_set = 1
    while bits_set < bits + 1:
        find_bit_parse_config.append(('{} bits set of {} bits'.format(bits_set, bits), 1, 'Average for_each_set_bit took:', ' usec (+-'))
        bits_set *= 2
    bits *= 2


def list_files(path):
    file_list = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            file_list.append(os.path.join(path, name))
    file_list.sort(key=os.path.getctime)
    return file_list


def extract_values(_file_list, detect_string, offset, start_string, end_string):

    for f in _file_list:
        value = extract(f, detect_string, offset, start_string, end_string)
        # print(value)

    return value


def save_to_csv(file_list, config, csv_file_name):

    results = [1, build_cmd, build]
    for i in range(len(config)):
        results.append(
            extract_values(file_list, config[i][0], config[i][1], config[i][2], config[i][3])
        )

    # print(len(parse_config))
    # print(results)

    header = ['test_run', 'build_cmd', 'build']
    for i in range(len(config)):
        header.append(config[i][0])
    # print(header)
    panda_data = pandas.DataFrame([results], columns=header)
    # print(panda_data)
    panda_data.to_csv(path_to_data + "/" + csv_file_name, index=False)


def main():

    file_list = list_files(path_to_data)
    print("Going to extract result values from these files: ")
    print(file_list)
    print()

    save_to_csv(file_list, parse_config, "perf_results.csv")
    save_to_csv(file_list, find_bit_parse_config, "perf_find_bit_results.csv")


if __name__ == '__main__':
    main()
