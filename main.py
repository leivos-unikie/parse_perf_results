# SPDX-FileCopyrightText: 2022-2024 Technology Innovation Institute (TII)
# SPDX-License-Identifier: Apache-2.0

import os
import csv
import pandas
import shutil

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

# How many columns are reserved for information extracted from the file name
build_info_size = 5

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


def parse_build_info(file, file_index):
    # Expected file name format: perf_results_YYYY-MM-DD_BuildMachine-BuildID_SDorEMMC
    info = file.split('_results_')[-1]
    commit_date = info.split('_')[0]
    build = info.split('_')[1]
    build_machine = build.split('-')[0]
    build_id = build.split('-')[-1]
    boot_source = info.split('_')[-1]
    line_index = file_index

    build_info = [line_index, build_machine, build_id, boot_source, commit_date]

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


def save_to_csv(file, config, csv_file_name, file_index):

    results = parse_build_info(file, file_index)

    with open(path_to_data + "/" + csv_file_name, 'a') as f:

        writer_object = csv.writer(f)

        for i in range(len(config)):
            results.append(
                extract_value(file, config[i][0], config[i][1], config[i][2], config[i][3])
            )
        # print(results)
        writer_object.writerow(results)
        f.close()


def normalize_columns(csv_file_name, normalize_to):
    # Set the various results to the same range.
    # This makes it easier to notice significant change in any of the result parameters with one glimpse
    # If columns are plotted later on the whole picture is well displayed

    data = pandas.read_csv(path_to_data + "/" + csv_file_name)

    # Cut away the columns which are not actual measurement data and find max values
    pure_data = data.drop(columns=data.columns[0:build_info_size])
    max_values = pure_data.max(numeric_only=True)

    data_rows = len(data.axes[0])
    # print(len(data.axes[1]))
    data_columns = len(max_values)

    # Normalize all columns between 0...normalize_to
    for i in range(build_info_size, build_info_size + data_columns):
        for j in range(data_rows):
            normalized = data.iat[j, i] / max_values[i - build_info_size]
            data.iloc[[j],[i]] = normalized * normalize_to
    data.to_csv(path_to_data + "/" + "normalized_" + csv_file_name, index=False)


def calc_statistics(csv_file_name):
    data = pandas.read_csv(path_to_data + "/" + csv_file_name)

    # Cut away the columns which are not actual measurement values
    pure_data = data.drop(columns=data.columns[0:build_info_size])

    # Calculate column averages
    column_avgs = (pure_data.mean(numeric_only=True)).tolist()
    # print("Average for each column:")
    # print(column_avgs)

    column_stds = (pure_data.std(numeric_only=True)).tolist()
    # print("Standard deviation for each column:")
    # print(column_stds)

    column_min = (pure_data.min(numeric_only=True)).tolist()
    # print("Min for each column:")
    # print(column_min)

    column_max = (pure_data.max(numeric_only=True)).tolist()
    # print("Max for each column:")
    # print(column_max)

    data_rows = len(data.axes[0])
    # print(len(data.axes[1]))
    data_columns = len(column_avgs)

    # Detect significant deviations from column mean

    # Find the result which is furthest away from the column mean.
    # Not taking into account those results which are within 1 std from column mean.
    max_deviations = ['-'] * (data_columns + build_info_size)
    for i in range(build_info_size, build_info_size + data_columns):
        for j in range(data_rows):
            if abs(data.iat[j, i] - column_avgs[i - build_info_size]) > column_stds[i - build_info_size]:
                distance = abs(data.iat[j, i] - column_avgs[i - build_info_size]) / column_stds[i - build_info_size]
                if max_deviations[i] == '-':
                    max_deviations[i] = distance
                elif distance > max_deviations[i]:
                    max_deviations[i] = distance

    # Check if values of the last data row are 1 std away from their column mean.
    last_row_deviations = ['-'] * (data_columns + build_info_size)
    last_row_deviations[build_info_size - 1] = "LRD"
    for i in range(build_info_size, build_info_size + data_columns):
        if abs(data.iat[data_rows - 1, i] - column_avgs[i - build_info_size]) > column_stds[i - build_info_size]:
            distance = (data.iat[data_rows - 1, i] - column_avgs[i - build_info_size]) / column_stds[i - build_info_size]
            last_row_deviations[i] = distance

    shutil.copyfile(path_to_data + "/" + csv_file_name, path_to_data + "/raw_" + csv_file_name)

    with open(path_to_data + "/" + csv_file_name, 'a') as f:

        writer_object = csv.writer(f)

        writer_object.writerow([])
        writer_object.writerow(last_row_deviations)

        writer_object.writerow(create_stats_row(build_info_size - 1, "average", column_avgs))
        writer_object.writerow(create_stats_row(build_info_size - 1, "std", column_stds))
        writer_object.writerow([])
        writer_object.writerow(create_stats_row(build_info_size - 1, "max", column_max))
        writer_object.writerow(create_stats_row(build_info_size - 1, "min", column_min))

        f.close()


def create_stats_row(shift, label, value_list):
    row = ['-'] * shift
    row.append(label)
    row = row + value_list
    return row


def create_csv_file(config, csv_file_name):

    header = ['index', 'build_machine', 'build_id', 'boot_src', 'build_date']
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

    file_index = 0
    for f in file_list:
        save_to_csv(f, parse_config, "perf_results.csv", file_index)
        save_to_csv(f, find_bit_parse_config, "perf_find_bit_results.csv", file_index)
        file_index += 1

    normalize_columns("perf_results.csv", 100)
    normalize_columns("perf_find_bit_results.csv", 100)

    calc_statistics("perf_results.csv")
    calc_statistics("perf_find_bit_results.csv")

if __name__ == '__main__':
    main()
