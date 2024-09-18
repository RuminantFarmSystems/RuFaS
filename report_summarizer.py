import os
import csv

fileprefix = "test-18"
directory = "E:\\Backup\\RUFAS_SA\\output\\reports\\"
report_prefix = "report_"

num_files = 128
digits = len(str(num_files))

logfiles = [filename for filename in os.listdir(directory) if filename.startswith(fileprefix) and report_prefix in filename]

all = []
for num in range(num_files):
    actual_num = num + 1
    try:
        logfilefound = [file for file in logfiles if "run " + f"{actual_num}".zfill(digits) in file][-1]
        with open(directory + logfilefound, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            temporary = []
            for row in spamreader:
                temporary.append(row)
            all.append(temporary[-1])
        print(actual_num)
    except Exception as e:
        print(e)
        print(f'failed on run {actual_num}')
        all.append([])

with open('eggs.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in all:
        spamwriter.writerow(row)
