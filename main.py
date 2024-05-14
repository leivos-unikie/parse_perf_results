# SPDX-FileCopyrightText: 2022-2024 Technology Innovation Institute (TII)
# SPDX-License-Identifier: Apache-2.0

import os
import csv
import pandas

path_to_data = "../perf_data/SD"

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
        find_bit_parse_config.append(
            ('{} bits set of {} bits'.format(bits_set, bits), 1, 'Average for_each_set_bit took:', ' usec (+-')
        )
        bits_set *= 2
    bits *= 2

# print(find_bit_parse_config)
print("Extracting " + str(len(find_bit_parse_config)) + " separate results from find bit tests.")
print("Extracting " + str(len(parse_config)) + " separate results from other tests.")


def list_files(path):
    file_list = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if name.find("perf_results") != -1 and name.find("csv") == -1:
                file_list.append(os.path.join(path, name))

    # file_list.sort(key=os.path.getctime)
    # The file creation time may differ from actual build date.
    # Let's sort according to file name (perf_results_YYYY-MM-DD_BuildMachine-BuildID) simply in ascending order.
    ordered_file_list = sorted(file_list)

    return ordered_file_list


def parse_build_info(file):
    # Expected file name format: perf_results_YYYY-MM-DD_BuildMachine-BuildID_SDorEMMC
    info = file.split('_results_')[-1]
    commit_date = info.split('_')[0]
    build = info.split('_')[1]
    build_machine = build.split('-')[0]
    build_id = build.split('-')[-1]
    boot_source = info.split('_')[-1]

    build_info = [commit_date, build_machine, build_id, boot_source]

    return build_info


def extract_value(file, detect_str, offset, str1, str2):

    with open(file, 'r') as f:

        # read all lines using readline()
        lines = f.readlines()

        row_index = 0
        match_index = -1

        for row in lines:
            # find() method returns -1 if the value is not found,
            # if found it returns index of the first occurrence of the substring
            if row.find(detect_str) != -1:
                match_index = row_index
                # print(match_index)
            row_index += 1

        if match_index < 0:
            print("Error in extracting '{}': Result value not found.".format(detect_str))
            return ''

        line = lines[match_index + offset]
        # print(line)
        res = ''

        try:
            # getting index of substrings
            idx1 = line.index(str1)
            idx2 = line.index(str2)
            # print(idx1)
            # print(idx2)

            # getting elements in between
            for idx in range(idx1 + len(str1), idx2):
                res = res + line[idx]

            res = float(res)
            # print("Extracting '{}': {}".format(detect_str, res))
            return res

        except:
            print("Error in extracting '{}': Result value not found.".format(detect_str))
            return res


def save_to_csv(file, config, csv_file_name):

    results = parse_build_info(file)

    with open(path_to_data + "/" + csv_file_name, 'a') as f:

        writer_object = csv.writer(f)

        for i in range(len(config)):
            results.append(
                extract_value(file, config[i][0], config[i][1], config[i][2], config[i][3])
            )
        # print(results)
        writer_object.writerow(results)
        f.close()


def calc_statistics(csv_file_name):
    data = pandas.read_csv(path_to_data + "/" + csv_file_name)

    # Calculate column averages
    column_avgs = data.mean(numeric_only=True)
    print("Average for each column:")
    print(column_avgs)

    column_stds = data.std(numeric_only=True)
    print("Standard deviation for each column:")
    print(column_stds)

    avgs = column_avgs.tolist()
    stds = column_stds.tolist()
    # print(len(data.axes[0]))
    # print(len(data.axes[1]))
    # print(len(avgs))

    print()
    print("Parameters which are further than 1 std away from column mean.")
    for i in range(4, 3 + len(avgs)):
        for j in range(len(data.axes[0])):
            if abs(data.iat[j, i] - avgs[i - 4]) > stds[i - 4]:
                print()
                print(data.columns.values.tolist()[i])
                print(j)
                print(data.iat[j, i])
                print("Distance from column mean (standard deviations):")
                print(abs(data.iat[j, i] - avgs[i - 4]) / stds[i - 4])
                # print(avgs[i - 4])
                # print(stds[i - 4])


def create_csv_file(config, csv_file_name):

    header = ['build_date', 'build_machine', 'build_id', 'boot_src']
    for i in range(len(config)):
        header.append(config[i][0])

    with open(path_to_data + "/" + csv_file_name, 'w') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(header)
        f.close()


def main():

    file_list = list_files(path_to_data)
    print("Going to extract result values from these files: ")
    print(file_list)
    print()

    create_csv_file(parse_config, "perf_results.csv")
    create_csv_file(find_bit_parse_config, "perf_find_bit_results.csv")

    for f in file_list:
        save_to_csv(f, parse_config, "perf_results.csv")
        save_to_csv(f, find_bit_parse_config, "perf_find_bit_results.csv")

    calc_statistics("perf_results.csv")
    print()
    calc_statistics("perf_find_bit_results.csv")

if __name__ == '__main__':
    main()
