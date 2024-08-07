<!--
    Copyright 2022-2024 TII (SSRC) and the Ghaf contributors
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

# parse_perf_results
A tool for extracting data from perf test output files to csv files.

Calculates if the last result of each test column is beyond threshold
from the test column mean value.

Normalized columns make it easier to monitor all tests with one glance
after plotting.

- Name format of the perf test output files should be as following:
perf_results_YYYY_MM_DD_BUILDER-BuildID

- Define path to the perf files in the beginning of main.py

- Running the parser:
python main.py

- Produces these csv files to the location defined by path_to_data variable:

  - raw_perf_results.csv
  - perf_results.csv
  - normalized_perf_results.csv
  - raw_perf_find_bit_results.csv
  - perf_find_bit_results.csv
  - normalized_perf_find_bit_results.csv
