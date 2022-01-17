import json
import main
import shutil
import os

h1 = {"name": "H1", "heifer_repro_method": "ED",
      "heifer_synchED_protocol": None, "heifer_TAI_protocol": None}
h2 = {"name": "H2", "heifer_repro_method": "synch-ED",
      "heifer_synchED_protocol": "2P", "heifer_TAI_protocol": "5dCG2P"}
h3 = {"name": "H3", "heifer_repro_method": "TAI",
      "heifer_synchED_protocol": None, "heifer_TAI_protocol": "5dCG2P"}

c1 = {"name": "C1", "cow_repro_method": "ED-TAI", "cow_presynch_protocol": None, "cow_TAI_protocol": "OvSynch 56",
      "tai_program_start_day": 70, "voluntary_waiting_period": 50, "cow_resynch_protocol": "TAIafterPD"}
c2 = {"name": "C2", "cow_repro_method": "TAI", "cow_presynch_protocol": "PreSynch",
      "cow_TAI_protocol": "OvSynch 56", "tai_program_start_day": 41, "voluntary_waiting_period": 50, "cow_resynch_protocol": "TAIbeforePD"}
      # to be consistent, I put "voluntary_waiting_period" here, but what value should be put here?
c3 = {"name": "C3", "cow_repro_method": "TAI", "cow_presynch_protocol": "Double OvSynch",
      "cow_TAI_protocol": "OvSynch 56", "tai_program_start_day": 45, "voluntary_waiting_period": 50, "cow_resynch_protocol": "TAIbeforePD"}
      # to be consistent, I put "voluntary_waiting_period" here, but what value should be put here?

heifer_strategies = [h1, h2, h3]
cow_strategies = [c1, c2, c3]

def trial(heifer_strategy, cow_strategy, rep):
    output_file = heifer_strategy['name'] + '_' + cow_strategy['name'] + '_' + str(rep)
    print("output_file", output_file)

    file = open("./input/animal/animal_management_animal.json")
    json_object = json.load(file)
    file.close()

    # inputs for heifers
    json_object['animal_config']['management_decisions']['heifer_repro_method'] = heifer_strategy['heifer_repro_method']
    json_object['animal_config']['farm_level']['repro']["ED_related"]["heifer_synchED_protocol"] = heifer_strategy["heifer_synchED_protocol"]
    json_object['animal_config']['farm_level']['repro']['TAI_related']['heifer_TAI_protocol'] = heifer_strategy['heifer_TAI_protocol']

    # inputs for cows
    json_object['animal_config']['management_decisions']['cow_repro_method'] = cow_strategy['cow_repro_method']
    json_object['animal_config']['farm_level']['repro']['TAI_related']['cow_TAI_protocol'] = cow_strategy['cow_TAI_protocol']
    json_object['animal_config']['farm_level']['repro']['TAI_related']['tai_program_start_day'] = cow_strategy['tai_program_start_day']
    json_object['animal_config']['farm_level']['repro']['TAI_related']['cow_resynch_protocol'] = cow_strategy['cow_resynch_protocol']
    json_object['animal_config']['farm_level']['voluntary_waiting_period'] = cow_strategy['voluntary_waiting_period']
    json_object['animal_config']['farm_level']['repro']['TAI_related']['cow_presynch_protocol'] = cow_strategy['cow_presynch_protocol']

    file = open("./input/animal/animal_management_animal.json", 'w')
    json.dump(json_object, file)
    file.close()

    # file = open("./input/animal/animal_management_animal.json")
    # json_object = json.load(file)
    # print("heifer repro menthod", json_object['animal_config']['management_decisions']['heifer_repro_method']) # it has been successfully changed
    # file.close()
    
    # print("here start run main()")
    main.main()

    shutil.move(
        'output/CSVs/life_cycle_report/herd_report/herd_report.csv', 'save_directory')
    os.rename('save_directory/herd_report.csv',
              'save_directory/' + output_file + '.csv')


R = 3
for i in range(len(heifer_strategies)):
    for rep in range(R):
        print("\n >>>enter point", "\n heifer: ", heifer_strategies[i], "\n cow: ", cow_strategies[i], "\n rep: ", rep)
        trial(heifer_strategies[i], cow_strategies[i], rep)
