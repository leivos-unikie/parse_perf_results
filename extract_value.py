def extract(file, detect_str, offset, str1, str2):

    file_name = file

    with open(file_name, 'r') as f:

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
            return ''

        line = lines[match_index + offset]
        # print(line)

        res = ''

        # getting index of substrings
        try:
            idx1 = line.index(str1)
            idx2 = line.index(str2)

            # print(idx1)
            # print(idx2)

            # getting elements in between
            for idx in range(idx1 + len(str1), idx2):
                res = res + line[idx]

            # print("The extracted string : " + res)

            res = float(res)

            return res

        except:
            return res
