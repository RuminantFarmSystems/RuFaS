import os
import json

filelist = os.listdir('output')
file = [file for file in filelist if file.startswith('all_variables')][-1]

keyselect = 'ration_for_pen_3'

with open(str('output/' + file)) as f:
    data = json.load(f)
actual_key = [key for key in list(data.keys()) if key.endswith(keyselect)][0]
ration_raw = data[actual_key]
ration_list = list(ration_raw.values())[0]

for line in ration_list:
    del line['status']
    del line['objective']

percent_dicts = []
DMI_list = []
for line in ration_list:
    percent_dict = {}
    DMI = 0
    for key in line.keys():
        DMI += line[key]
        line[key] = round(line[key],4)
    DMI_list.append(DMI)
    for key in line.keys():
        percent_dict[key] = round(line[key]/DMI, 4)
    percent_dicts.append(percent_dict)

for pos in range(len(percent_dict) - 3, len(percent_dict)):
    DMItotal = round(DMI_list[pos],2)
    print('\n')
    print(f'ration for interval {pos}')
    print(f'raw kgs, total = {DMItotal}kg')
    print(ration_list[pos])
    print('percent of DMI')
    print(percent_dicts[pos])