import json
import csv
import matplotlib.pyplot as mp
import math
from scipy.integrate import quad

wean_day = 0
breeding_start_day_h = 0
avg_gestation_len = 0
dry_period = 0
birth_weight_avg_ho = 0
target_heifer_preg_day = 0
wood_l = []
wood_m = []
wood_n = []

avg_breeding_to_preg_time = 0
avg_calving_to_preg_time_for_parity_1 = 0
avg_calving_to_preg_time_for_parity_2 = 0
avg_calving_to_preg_time_for_parity_3 = 0
avg_cow_culling_age = 0
avg_mature_body_weight = 0
avg_CI = 0

t1 = 0
t2 = 0
t3 = 0
t4 = 0
t5 = 0
t6 = 0
t7 = 0
t8 = 0
t9 = 0
t10 = 0
t11 = 0


def set_input_vars():
    with open('input/animal/animal_management_animal.json') as f:
        data = json.load(f)

        global wean_day
        global breeding_start_day_h
        global avg_gestation_len
        global dry_period
        global birth_weight_avg_ho
        global target_heifer_preg_day
        global wood_l
        global wood_m
        global wood_n

        wean_day = data['animal_config']['farm_level']['calf']['wean_day']
        breeding_start_day_h = data['animal_config']['management_decisions']['breeding_start_day_h']
        avg_gestation_len = data['animal_config']['farm_level']['repro']['avg_gestation_len']
        dry_period = data['animal_config']['farm_level']['repro']['avg_gestation_len'] - data['animal_config']['management_decisions']['days_in_preg_when_dry']
        birth_weight_avg_ho = data['animal_config']['farm_level']['bodyweight']['birth_weight_avg_ho']
        #target_heifer_preg_day = data['animal_config']['farm_level']['bodyweight']['target_heifer_preg_day']
        wood_l = data['animal_config']['from_literature']['milking']['wood_l']
        wood_m = data['animal_config']['from_literature']['milking']['wood_m']
        wood_n = data['animal_config']['from_literature']['milking']['wood_n']

def set_herd_output():
    desired_rows = []
    desired_rows_len = 700

    with open('output/CSVs/life_cycle_report/herd_report/herd_report.csv') as c:
        reader = csv.DictReader(c)
        for row in reader:
            desired_rows.append(dict(row))
            if len(desired_rows) > desired_rows_len:
                desired_rows.pop(0)

    global avg_breeding_to_preg_time
    global avg_calving_to_preg_time_for_parity_1
    global avg_calving_to_preg_time_for_parity_2
    global avg_calving_to_preg_time_for_parity_3
    global avg_cow_culling_age
    global avg_mature_body_weight
    global avg_CI

    avg_breeding_to_preg_time = sum([float(row['avg_breeding_to_preg_time']) for row in desired_rows]) / desired_rows_len
    avg_calving_to_preg_time_for_parity_1 = sum([float(row['avg_calving_to_preg_time_for_parity_1']) for row in desired_rows]) / desired_rows_len
    avg_calving_to_preg_time_for_parity_2 = sum([float(row['avg_calving_to_preg_time_for_parity_2']) for row in desired_rows]) / desired_rows_len
    avg_calving_to_preg_time_for_parity_3 = sum([float(row['avg_calving_to_preg_time_for_parity_3']) for row in desired_rows]) / desired_rows_len
    avg_mature_body_weight = sum([float(row['avg_mature_body_weight']) for row in desired_rows]) / desired_rows_len
    avg_CI = sum([float(row['avg_caving_interval']) for row in desired_rows]) / desired_rows_len

    non_zero_culling_age = []
    for row in desired_rows:
        num = float(row['avg_cow_culling_age'])
        if num > 0:
            non_zero_culling_age.append(num)

    avg_cow_culling_age = sum(non_zero_culling_age) / len(non_zero_culling_age)


def set_timeline():
    global wean_day
    global breeding_start_day_h
    global avg_gestation_len
    global avg_breeding_to_preg_time
    global avg_calving_to_preg_time_for_parity_1
    global avg_calving_to_preg_time_for_parity_2
    global avg_calving_to_preg_time_for_parity_3
    global avg_cow_culling_age

    global t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11
    global target_heifer_preg_day

    t1 = 1
    t2 = wean_day
    t3 = int(breeding_start_day_h + avg_breeding_to_preg_time)
    t4 = int(t3 + avg_gestation_len)
    t5 = int(t4 + avg_calving_to_preg_time_for_parity_1)
    t6 = int(t5 + avg_gestation_len)
    t7 = int(t6 + avg_calving_to_preg_time_for_parity_2)
    t8 = int(t7 + avg_gestation_len)
    t9 = int(t8 + avg_calving_to_preg_time_for_parity_3)
    t10 = int(t9 + avg_gestation_len - 60)
    t11 = int(avg_cow_culling_age)

    target_heifer_preg_day = t3


def run_sim():
    animal = AvgAnimal()
    days_born_lst = []
    body_weight_lst = []
    milk_production_lst = []

    for _ in range(t11 - 1):
        days_born_lst.append(animal.days_born)

        body_weight_lst.append(animal.body_weight)

        if animal.milk_production > 0:
            milk_production_lst.append(animal.milk_production)
        else:
            milk_production_lst.append(None)

        animal.daily_update()

    return days_born_lst, body_weight_lst, milk_production_lst


def graph(days_born_lst, body_weight_lst, milk_production_lst):
    fig, ax = mp.subplots()
    fig.suptitle('Average Animal')
    ax.plot(days_born_lst, milk_production_lst, color='red', linestyle='-.')
    ax.set_xlabel('Days Born')
    ax.set_ylabel('Milk Production (kg)', color='red')

    style = dict(size=8, color='black')
    ax.text(t1 - 23, 54, "T1", **style)
    mp.axvline(x=t1, linestyle=':', color='#8deba6')

    ax.text(t2 - 23, 54, "T2", **style)
    mp.axvline(x=t2, linestyle=':', color='#8deba6')

    ax.text(t3 - 23, 54, "T3", **style)
    mp.axvline(x=t3, linestyle=':', color='#8deba6')

    ax.text(t4 - 23, 54, "T4", **style)
    mp.axvline(x=t4, linestyle=':', color='#8deba6')

    ax.text(t5 - 23, 54, "T5", **style)
    mp.axvline(x=t5, linestyle=':', color='#8deba6')

    ax.text(t6 - 23, 54, "T6", **style)
    mp.axvline(x=t6, linestyle=':', color='#8deba6')

    ax.text(t7 - 23, 54, "T7", **style)
    mp.axvline(x=t7, linestyle=':', color='#8deba6')

    ax.text(t8 - 23, 54, "T8", **style)
    mp.axvline(x=t8, linestyle=':', color='#8deba6')

    ax.text(t9 - 23, 54, "T9", **style)
    mp.axvline(x=t9, linestyle=':', color='#8deba6')

    # ax.text(t10 - 23, 54, "T10", **style)
    # mp.axvline(x=t10, linestyle=':', color='#8deba6')

    ax.text(t11 - 30, 54, "T10", **style)
    mp.axvline(x=t11, linestyle=':', color='#8deba6')

    mp.axvspan(t6 - dry_period, t6, color='#ebc58d', alpha=0.5)
    mp.axvspan(t8 - dry_period, t8, color='#ebc58d', alpha=0.5)
    #mp.axvspan(t10, t11, color='#ebc58d', alpha=0.5)

    ax2 = ax.twinx()
    ax2.plot(days_born_lst, body_weight_lst, color='blue')
    ax2.set_ylabel('Body Weight (kg)', color='blue')

    # mp.show()
    mp.savefig('average_animal.png')
    mp.close()


class AvgAnimal:
    def __init__(self):
        self.days_born = 1
        self.body_weight = birth_weight_avg_ho
        self.milk_production = 0
        self.days_in_preg = 0
        self.days_in_milk = 0
        self.conceptus_weight = 0
        self.acmilk_1 = 0
        self.acmilk_2 = 0
        self.acmilk_3 = 0

    def get_calf_bw_change(self):
        return birth_weight_avg_ho / t2

    def get_heiferI_bw_change(self):
        divisor = abs(420 - self.days_born)
        if divisor == 0:
            divisor = 1
        return (0.55 * 0.96 * avg_mature_body_weight -
										2 * birth_weight_avg_ho) / 420

    def get_heiferIII_bw_change(self):
        divisor = (avg_gestation_len - self.days_in_preg)
        if divisor == 0:
            divisor = 1
        target_ADG_heifer_preg = (0.82 * 0.96 * avg_mature_body_weight -
                                  0.96 * self.body_weight) / divisor

        CBW = birth_weight_avg_ho

        if self.days_in_preg == avg_gestation_len:
                conceptus_growth = - self.conceptus_weight
                self.conceptus_weight = 0
                self.days_in_preg = 0
        elif self.days_in_preg > 50:
                conceptus_total_weight = (0.0148 * avg_gestation_len - 2.408) * CBW
                conceptus_param = conceptus_total_weight ** (1 / 3) / (avg_gestation_len - 50)
                conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
                self.conceptus_weight += conceptus_growth
        else:
                conceptus_growth = 0

        return target_ADG_heifer_preg + conceptus_growth

    def get_cow1_bw_change(self):
        CBW = birth_weight_avg_ho
        
        # conceptus weight change during pregnancy
        if self.days_in_preg == avg_gestation_len:
                conceptus_growth = - self.conceptus_weight
                self.conceptus_weight = 0
                self.days_in_preg = 0
        elif self.days_in_preg > 50:
            conceptus_total_weight = (0.0148 * avg_gestation_len - 2.408) * CBW
            conceptus_param = conceptus_total_weight ** (1 / 3) / (avg_gestation_len - 50)
            conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
            self.conceptus_weight += conceptus_growth
        elif self.days_in_preg == avg_gestation_len:
            conceptus_growth = - self.conceptus_weight
            self.days_in_preg = 0
            self.conceptus_weight = 0
            self.tissue_changed = 0
        else:
            conceptus_growth = 0

        target_adg_cow = \
            (0.92 - 0.82) * 0.96 * avg_mature_body_weight / avg_CI
        if self.days_in_preg < 1: # before pregnancy
                 target_adg_cow = \
                     (0.92 - 0.82) * 0.96 * avg_mature_body_weight / avg_CI
        else: # after pregnancy
                target_adg_cow = \
                     (0.92 * avg_mature_body_weight - self.body_weight)/(avg_gestation_len - self.days_in_preg+1)
        
        if self.days_in_milk == 0:
            bodyweight_tissue = self.tissue_changed / dry_period
        else:
            bodyweight_tissue = \
                -20 / 65 * math.exp(1 - self.days_in_milk / 65) + \
                20 / (65 ** 2) * self.days_in_milk * \
                math.exp(1 - self.days_in_milk / 65)
            if self.days_in_preg == avg_gestation_len - dry_period - 1:
                     self.tissue_changed = 20 * self.days_in_milk/65 * math.exp(1 - self.days_in_milk/65)
        
        return target_adg_cow + conceptus_growth + bodyweight_tissue

    def get_cow2_bw_change(self):
        CBW = birth_weight_avg_ho

        # conceptus weight change during pregnancy
        if self.days_in_milk == 1:
            conceptus_growth = - self.conceptus_weight
            self.conceptus_weight = 0
            self.days_in_preg = 0
        if self.days_in_preg == avg_gestation_len:
                conceptus_growth = - self.conceptus_weight
                self.conceptus_weight = 0
                self.days_in_preg = 0
        elif self.days_in_preg > 50:
            conceptus_total_weight = (0.0148 * avg_gestation_len - 2.408) * CBW
            conceptus_param = conceptus_total_weight ** (1 / 3) / (avg_gestation_len - 50)
            conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
            self.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        target_adg_cow = \
            (1 - 0.92) * 0.96 * avg_mature_body_weight / avg_CI
        if self.days_in_preg < 1: # before pregnancy
                 target_adg_cow = \
                     (1 - 0.92) * 0.96 * avg_mature_body_weight / avg_CI
        else: # after pregnancy
                target_adg_cow = \
                     (1 * avg_mature_body_weight - self.body_weight)/(avg_gestation_len - self.days_in_preg+2)
        
        if self.days_in_milk == 0:
            bodyweight_tissue = self.tissue_changed / dry_period
        else:
            bodyweight_tissue = \
                -40 / 70 * math.exp(1 - self.days_in_milk / 70) + \
                40 / (70 ** 2) * self.days_in_milk * \
                math.exp(1 - self.days_in_milk / 70)
            if self.days_in_preg == avg_gestation_len - dry_period - 1:
                     self.tissue_changed = 40 * self.days_in_milk/70 * math.exp(1 - self.days_in_milk/70)
        
        return target_adg_cow + conceptus_growth + bodyweight_tissue


    def get_cow3plus_bw_change(self):
        CBW = birth_weight_avg_ho
        if self.days_in_milk == 1:
            conceptus_growth = - self.conceptus_weight
            self.conceptus_weight = 0
            self.days_in_preg = 0
        # conceptus weight change during pregnancy
        if self.days_in_preg == avg_gestation_len:
                conceptus_growth = - self.conceptus_weight
                self.conceptus_weight = 0
                self.days_in_preg = 0
        elif self.days_in_preg > 50:
            conceptus_total_weight = (0.0148 * avg_gestation_len - 2.408) * CBW
            conceptus_param = conceptus_total_weight ** (1 / 3) / (avg_gestation_len - 50)
            conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
            self.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        if self.days_in_preg == avg_gestation_len:
            conceptus_growth = - self.conceptus_weight
            self.conceptus_weight = 0
            self.days_in_preg = 0

        if self.days_in_milk == 0:
            bodyweight_tissue = self.tissue_changed / dry_period
        else:
            bodyweight_tissue = \
                -40 / 70 * math.exp(1 - self.days_in_milk / 70) + \
                40 / (70 ** 2) * self.days_in_milk * \
                math.exp(1 - self.days_in_milk / 70)
            if self.days_in_preg == avg_gestation_len - dry_period - 1:
                self.tissue_changed = 40 * self.days_in_milk/70 * math.exp(1 - self.days_in_milk/70)

        return conceptus_growth + bodyweight_tissue

    def get_milk(self, parity_index):
        breed_index = 0

        l = wood_l[breed_index][parity_index]
        m = wood_m[breed_index][parity_index]
        n = wood_n[breed_index][parity_index]

        return l * math.pow(self.days_in_milk, m) * \
            math.exp((0 - n) * self.days_in_milk)

    def daily_update(self):
        if self.days_born in [t3, t5, t7, t9]:
            self.days_in_preg = 1

        if self.days_born in [t4, t6, t8]:
            self.days_in_milk = 1

        if self.days_born < t2:  # stage a
            self.body_weight += self.get_calf_bw_change()

        elif t2 <= self.days_born < t3:  # stage b
            self.body_weight += self.get_heiferI_bw_change()

        elif t3 <= self.days_born < t4:  # stage c
            self.body_weight += self.get_heiferIII_bw_change()

            self.days_in_preg += 1

        elif t4 <= self.days_born < t6:  # stage d
            self.body_weight += self.get_cow1_bw_change()

            if t5 <= self.days_born:
                self.days_in_preg += 1

            if t4 <= self.days_born <= t6 - dry_period:
                self.days_in_milk += 1
                self.milk_production = self.get_milk(0)
                self.acmilk_1 += self.milk_production
            else:
                self.milk_production = 0

        elif t6 <= self.days_born < t8:  # stage e
            self.body_weight += self.get_cow2_bw_change()

            if t7 <= self.days_born:
                self.days_in_preg += 1

            if t6 <= self.days_born <= t8 - dry_period:
                self.days_in_milk += 1
                self.milk_production = self.get_milk(1)
                self.acmilk_2 += self.milk_production
            else:
                self.milk_production = 0

        elif t8 <= self.days_born <= t11:  # stage f
            self.body_weight += self.get_cow3plus_bw_change()

            if t9 <= self.days_born:
                self.days_in_preg += 1

            if t8 <= self.days_born and self.days_in_preg < 219:
                self.days_in_milk += 1
                self.milk_production = self.get_milk(2)
                self.acmilk_3 += self.milk_production
            else:
                self.milk_production = 0

        self.days_born += 1
        print(f'1st lactation production = {self.acmilk_1}')
        print(f'2nd lactation production = {self.acmilk_2}')
        print(f'3rd lactation production = {self.acmilk_3}')


if __name__ == '__main__':
    set_input_vars()
    set_herd_output()
    set_timeline()
    days_born, body_weight, milk_production = run_sim()
    graph(days_born, body_weight, milk_production)
    print(f'T1 = {t1} T2 = {t2} T3 = {t3} T4 = {t4} T5 = {t5} T6 = {t6} T7 = {t7} T8 = {t8} T9 = {t9} T10 = {t10} T11 = {t11}')
    print(f'breeding0 = {avg_breeding_to_preg_time} breeding1 = {avg_calving_to_preg_time_for_parity_1} breeding2 = {avg_calving_to_preg_time_for_parity_2} breeding3 = {avg_calving_to_preg_time_for_parity_3}')
    print(f'Lactation 1 is {t6 - t4 - 60} days, Lactation 2 is {t8 - t6 - 60} days, Lactation 3 is {t10 - t8} days, days in preg is {t11 - t9}')
    print(f'MBW = {avg_mature_body_weight}')
    #milk, err = quad(self.get_milk(0), 1, t6 - t4 - 60)
    

