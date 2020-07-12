'''
RUFAS: Ruminant Farm Systems Model
File name: animal_base.py
Author(s): Katrina Wang, kw433@cornell.edu
Description: This file stores and draws values of simulated 
                animals in and from the database
'''
###############################################################################

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.cow import Cow
import sqlite3
from enum import IntEnum

class AnimalValues(IntEnum):
    id = 0
    breed = 1
    birth_date = 2
    days_born = 3
    birth_weight = 4
    body_weight = 5
    wean_weight = 6
    mature_body_weight = 7
    events = 8
    repro_program = 9
    tai_method_h = 10
    synch_ed_method_h = 11
    estrus_count = 12
    estrus_day = 13
    tai_program_start_day_h = 14
    synch_ed_program_start_day_h = 15
    synch_ed_estrus_day = 16
    stop_day = 17
    conception_rate = 18
    ai_day = 19
    abortion_day = 20
    days_in_preg = 21
    gestation_length = 22
    p_gest_for_calf = 23
    presynch_method = 24
    tai_method_c = 25
    resynch_method = 26
    days_in_milk = 27
    parity = 28

class AnimalInitalization:
    animal_id = 0

    '''
        Generates an id
    '''
    def next_id(self):
        self.animal_id += 1
        return self.animal_id

    '''
        Description:
            Initialize the database to store animal values. Simulate animals to store in database in init is True. 
        Input:
            init: whether or not update the database with new animals
    '''
    def __init__(self, init = True):
        if init:
            conn = sqlite3.connect('input/animal/animals.sqlite')
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS calves')
            cur.execute('DROP TABLE IF EXISTS heiferIs')
            cur.execute('DROP TABLE IF EXISTS heiferIIs')
            cur.execute('DROP TABLE IF EXISTS heiferIIIs')
            cur.execute('DROP TABLE IF EXISTS cows')
            cur.execute('DROP TABLE IF EXISTS replacement')
            cur.execute('DROP TABLE IF EXISTS animal_id')
            cur.execute('CREATE TABLE IF NOT EXISTS calves \
                (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, \
                    birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, \
                        mature_body_weight VARCHAR, events VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS heiferIs \
                (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, \
                    birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, \
                        mature_body_weight VARCHAR, events VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS heiferIIs \
                (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, \
                    birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, \
                        mature_body_weight VARCHAR, events VARCHAR, repro_program VARCHAR, \
                            tai_method_h VARCHAR, synch_ed_method_h VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS heiferIIIs \
                (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, \
                    birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, \
                        mature_body_weight VARCHAR, events VARCHAR, repro_program VARCHAR, \
                            tai_method_h VARCHAR, synch_ed_method_h VARCHAR, estrus_count VARCHAR, \
                                estrus_day VARCHAR, tai_program_start_day_h VARCHAR, \
                                    synch_ed_program_start_day_h VARCHAR, synch_ed_estrus_day VARCHAR, \
                                        stop_day VARCHAR, conception_rate VARCHAR, ai_day VARCHAR, \
                                            abortion_day VARCHAR, days_in_preg VARCHAR, gestation_length VARCHAR, \
                                                p_gest_for_calf VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS cows \
                (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, \
                    birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, \
                        mature_body_weight VARCHAR, events VARCHAR, repro_program VARCHAR, \
                            tai_method_h VARCHAR, synch_ed_method_h VARCHAR, estrus_count VARCHAR, \
                                estrus_day VARCHAR, tai_program_start_day_h VARCHAR, \
                                    synch_ed_program_start_day_h VARCHAR, synch_ed_estrus_day VARCHAR, \
                                        stop_day VARCHAR, conception_rate VARCHAR, ai_day VARCHAR, \
                                            abortion_day VARCHAR, days_in_preg VARCHAR, gestation_length VARCHAR, \
                                                p_gest_for_calf VARCHAR, presynch_method VARCHAR, tai_method_c VARCHAR, \
                                                    resynch_method VARCHAR, days_in_milk VARCHAR, parity VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS replacement \
                (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, \
                    birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, \
                        mature_body_weight VARCHAR, events VARCHAR, repro_program VARCHAR, \
                            tai_method_h VARCHAR, synch_ed_method_h VARCHAR, estrus_count VARCHAR, \
                                estrus_day VARCHAR, tai_program_start_day_h VARCHAR, \
                                    synch_ed_program_start_day_h VARCHAR, synch_ed_estrus_day VARCHAR, \
                                        stop_day VARCHAR, conception_rate VARCHAR, ai_day VARCHAR, \
                                            abortion_day VARCHAR, days_in_preg VARCHAR, gestation_length VARCHAR, \
                                                p_gest_for_calf VARCHAR, presynch_method VARCHAR, tai_method_c VARCHAR, \
                                                    resynch_method VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS animal_id (id VARCHAR)')
            cur.execute('INSERT INTO animal_id VALUES (' + str(self.animal_id) + ')')
            conn.commit()
            conn.close()
            self.init_animals()
        else:
            conn = sqlite3.connect('input/animal/animals.sqlite')
            cur = conn.cursor()
            cur.execute('SELECT * FROM animal_id')
            row = cur.fetchone()
            self.animal_id = int(row[AnimalValues.id])
            conn.close()

    '''
        Description:
            Simulate animals to be stored in the database
        Inputs:
            animal_num: number of animals to simulate
            sim_days: number of days to simulate
    '''
    def init_animals(self, animal_num = 20000, sim_days=5000):
        calves = []
        heiferIs = []
        heiferIIs = []
        heiferIIIs = []
        cows = []
        replacement = []

        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()

        for _ in range(animal_num):
            args = {
                'id' : self.next_id(),
                'breed': 'HO',
                'birth_date': 0,
                'days_born': 0,
                'p_init': 0
            }
            calf = Calf(args)
            if not (calf.culled or calf.sold):
                calves.append(calf)

        for _ in range(sim_days):
            for calf in calves:
                wean_day = calf.update()
                if wean_day:
                    args = calf.get_calf_values()
                    args.update(id = self.next_id())

                    heiferI = HeiferI(args)
                    heiferIs.append(heiferI)
                    calves.remove(calf)

            for heiferI in heiferIs:
                second_stage = heiferI.update()
                if second_stage:
                    args = heiferI.get_heiferI_values()
                    args.update(id = self.next_id())
                    args.update(repro_program = 'TAI')
                    args.update(tai_method_h = '5dCG2P')
                    args.update(synch_ed_method_h = '2P')

                    heiferII = HeiferII(args)
                    heiferIIs.append(heiferII)
                    heiferIs.remove(heiferI)

            for heiferII in heiferIIs:
                cull_stage, third_stage = heiferII.update()
                if cull_stage:
                    heiferIIs.remove(heiferII)
                if third_stage:
                    args = heiferII.get_heiferII_values()
                    args.update(id = self.next_id())

                    heiferIII = HeiferIII(args)
                    heiferIIIs.append(heiferIII)
                    heiferIIs.remove(heiferII)

            for heiferIII in heiferIIIs:
                cow_stage = heiferIII.update()
                if cow_stage:
                    args = heiferIII.get_heiferIII_values()
                    args.update(id = self.next_id())
                    args.update(repro_program = 'TAI')
                    args.update(presynch_method = 'PreSynch')
                    args.update(tai_method_c = 'OvSynch 56')
                    args.update(resynch_method = 'TAIafterPD')
                    
                    cow = Cow(args)
                    cows.append(cow)

                    args.update(id = self.next_id())
                    replacement_cow = Cow(args)
                    replacement.append(replacement_cow)

                    heiferIIIs.remove(heiferIII)
                    
            for cow in cows:
                _, _, _, culled, new_born = cow.update(False)
                if culled or cow.calves > 4:
                    cows.remove(cow)
                if new_born:
                    args = {
                        'id': self.next_id(),
                        'breed': 'HO',
                        'birth_date': 0,
                        'days_born': 0,
                        'p_init': cow.p_gest_for_calf
                    }
                    cow.p_animal = cow.p_animal - cow.p_gest_for_calf + \
                        cow.p_growth + cow.dP_reserves
                    cow.p_gest_for_calf = 0

                    calf = Calf(args)
                    if not (calf.culled or calf.sold):
                        calves.append(calf)

        for calf in calves:
            cur.execute('INSERT INTO calves (id, breed, birth_date, days_born, birth_weight, \
                body_weight, wean_weight, mature_body_weight, events) VALUES (?,?,?,?,?,?,?,?,?)', 
                (calf.id, calf.breed, calf.birth_date, calf.days_born, calf.birth_weight, 
                calf.body_weight, calf.wean_weight, calf.mature_body_weight, str(calf.events)))
        for heiferI in heiferIs:
            cur.execute('INSERT INTO heiferIs (id, breed, birth_date, days_born, birth_weight, \
                body_weight, wean_weight, mature_body_weight, events) VALUES (?,?,?,?,?,?,?,?,?)', 
                (heiferI.id, heiferI.breed, heiferI.birth_date, heiferI.days_born, 
                heiferI.birth_weight, heiferI.body_weight, heiferI.wean_weight, 
                heiferI.mature_body_weight, str(heiferI.events)))
        for heiferII in heiferIIs:
            cur.execute('INSERT INTO heiferIIs (id, breed, birth_date, days_born, birth_weight, \
                body_weight, wean_weight, mature_body_weight, events, repro_program, tai_method_h, \
                    synch_ed_method_h) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', 
                    (heiferII.id, heiferII.breed, heiferII.birth_date, heiferII.days_born, 
                    heiferII.birth_weight, heiferII.body_weight, heiferII.wean_weight, 
                    heiferII.mature_body_weight, str(heiferII.events), heiferII.repro_program, 
                    heiferII.tai_method_h, heiferII.synch_ed_method_h))
        for heiferIII in heiferIIIs:
            cur.execute('INSERT INTO heiferIIIs (id, breed, birth_date, days_born, birth_weight, \
                body_weight, wean_weight, mature_body_weight, events, repro_program, tai_method_h, \
                    synch_ed_method_h, estrus_count, estrus_day, tai_program_start_day_h, \
                        synch_ed_program_start_day_h, synch_ed_estrus_day, stop_day, conception_rate, \
                            ai_day, abortion_day, days_in_preg, gestation_length, p_gest_for_calf) \
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', 
                                (heiferIII.id, heiferIII.breed, heiferIII.birth_date, heiferIII.days_born, 
                                heiferIII.birth_weight, heiferIII.body_weight, heiferIII.wean_weight, 
                                heiferIII.mature_body_weight, str(heiferIII.events), heiferIII.repro_program, 
                                heiferIII.tai_method_h, heiferIII.synch_ed_method_h, heiferIII.estrus_count, 
                                heiferIII.estrus_day, heiferIII.tai_program_start_day_h, 
                                heiferIII.synch_ed_program_start_day_h, heiferIII.synch_ed_estrus_day, 
                                heiferIII.stop_day, heiferIII.conception_rate, heiferIII.ai_day, 
                                heiferIII.abortion_day, heiferIII.days_in_preg, heiferIII.gestation_length, 
                                heiferIII.p_gest_for_calf))
        for cow in cows:
            cur.execute('INSERT INTO cows (id, breed, birth_date, days_born, birth_weight, \
                body_weight, wean_weight, mature_body_weight, events, repro_program, tai_method_h, \
                    synch_ed_method_h, estrus_count, estrus_day, tai_program_start_day_h, \
                        synch_ed_program_start_day_h, synch_ed_estrus_day, stop_day, conception_rate, \
                            ai_day, abortion_day, days_in_preg, gestation_length, p_gest_for_calf, \
                                presynch_method, tai_method_c, resynch_method, days_in_milk, parity) \
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', 
                                    (cow.id, cow.breed, cow.birth_date, cow.days_born, cow.birth_weight, 
                                    cow.body_weight, cow.wean_weight, cow.mature_body_weight, 
                                    str(cow.events), cow.repro_program, cow.tai_method_h, 
                                    cow.synch_ed_method_h, cow.estrus_count, cow.estrus_day, 
                                    cow.tai_program_start_day_h, cow.synch_ed_program_start_day_h, 
                                    cow.synch_ed_estrus_day, cow.stop_day, cow.conception_rate, 
                                    cow.ai_day, cow.abortion_day, cow.days_in_preg, cow.gestation_length, 
                                    cow.p_gest_for_calf, cow.presynch_method, cow.tai_method_c, 
                                    cow.resynch_method, cow.days_in_milk, cow.calves))
        for cow in replacement:
            cur.execute('INSERT INTO replacement (id, breed, birth_date, days_born, birth_weight, \
                body_weight, wean_weight, mature_body_weight, events, repro_program, tai_method_h, \
                    synch_ed_method_h, estrus_count, estrus_day, tai_program_start_day_h, \
                        synch_ed_program_start_day_h, synch_ed_estrus_day, stop_day, conception_rate, \
                            ai_day, abortion_day, days_in_preg, gestation_length, p_gest_for_calf, \
                                presynch_method, tai_method_c, resynch_method) \
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', 
                                    (cow.id, cow.breed, cow.birth_date, cow.days_born, cow.birth_weight, 
                                    cow.body_weight, cow.wean_weight, cow.mature_body_weight, 
                                    str(cow.events), cow.repro_program, cow.tai_method_h, 
                                    cow.synch_ed_method_h, cow.estrus_count, cow.estrus_day, 
                                    cow.tai_program_start_day_h, cow.synch_ed_program_start_day_h, 
                                    cow.synch_ed_estrus_day, cow.stop_day, cow.conception_rate, 
                                    cow.ai_day, cow.abortion_day, cow.days_in_preg, cow.gestation_length, 
                                    cow.p_gest_for_calf, cow.presynch_method, cow.tai_method_c, 
                                    cow.resynch_method))
        cur.execute('UPDATE animal_id SET id = ' + str(self.animal_id))
        conn.commit()
        conn.close()


    '''
        Description:
            Get calf values from the database for initialization
        Input:
            num: number of calves to initialize
    '''
    def get_calves(self, num):
        calves = []
        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM calves').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM calves ORDER BY RANDOM() LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'p_init': 0, 
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
                'events': row[AnimalValues.events]
            }
            calf = Calf(args)
            calves.append(calf)
        conn.close()
        return calves

    '''
        Description:
            Get heiferI values from the database for initialization
        Input:
            num: number of heiferIs to initialize
    '''
    def get_heiferIs(self, num):
        heiferIs = []
        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM heiferIs').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM heiferIs ORDER BY RANDOM() LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
                'events': row[AnimalValues.events]
            }
            heiferI = HeiferI(args)
            heiferIs.append(heiferI)
        conn.close()
        return heiferIs

    '''
        Description:
            Get heiferII values from the database for initialization
        Input:
            num: number of heiferIIs to initialize
    '''
    def get_heiferIIs(self, num):
        heiferIIs = []
        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM heiferIIs').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM heiferIIs ORDER BY RANDOM() LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
                'events': row[AnimalValues.events],
                'repro_program': row[AnimalValues.repro_program],
                'tai_method_h': row[AnimalValues.tai_method_h],
                'synch_ed_method_h': row[AnimalValues.synch_ed_method_h]
            }
            heiferII = HeiferII(args)
            heiferIIs.append(heiferII)
        conn.close()
        return heiferIIs

    '''
        Description:
            Get heiferIII values from the database for initialization
        Input:
            num: number of heiferIIIs to initialize
    '''
    def get_heiferIIIs(self, num):
        heiferIIIs = []
        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM heiferIIIs').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM heiferIIIs ORDER BY RANDOM() LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
                'events': row[AnimalValues.events],
                'repro_program': row[AnimalValues.repro_program],
                'tai_method_h': row[AnimalValues.tai_method_h],
                'synch_ed_method_h': row[AnimalValues.synch_ed_method_h],
                'estrus_count': int(row[AnimalValues.estrus_count]),
                'estrus_day': int(row[AnimalValues.estrus_day]),
                'tai_program_start_day_h': int(row[AnimalValues.tai_program_start_day_h]),
                'synch_ed_program_start_day_h': int(row[AnimalValues.synch_ed_program_start_day_h]),
                'synch_ed_estrus_day': int(row[AnimalValues.synch_ed_estrus_day]),
                'stop_day': int(row[AnimalValues.stop_day]),
                'conception_rate': float(row[AnimalValues.conception_rate]),
                'ai_day': int(row[AnimalValues.ai_day]),
                'abortion_day': int(row[AnimalValues.abortion_day]),
                'days_in_preg': int(row[AnimalValues.days_in_preg]),
                'gestation_length': int(row[AnimalValues.gestation_length]),
                'p_gest_for_calf': int(row[AnimalValues.p_gest_for_calf])
            }
            heiferIII = HeiferIII(args)
            heiferIIIs.append(heiferIII)
        conn.close()
        return heiferIIIs

    '''
        Description:
            Get cow values from the database for initialization
        Input:
            num: number of cows to initialize
    '''
    def get_cows(self, num):
        cows = []
        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM cows').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM cows ORDER BY RANDOM() LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
                'events': row[AnimalValues.events],
                'repro_program': row[AnimalValues.repro_program],
                'tai_method_h': row[AnimalValues.tai_method_h],
                'synch_ed_method_h': row[AnimalValues.synch_ed_method_h],
                'estrus_count': int(row[AnimalValues.estrus_count]),
                'estrus_day': int(row[AnimalValues.estrus_day]),
                'tai_program_start_day_h': int(row[AnimalValues.tai_program_start_day_h]),
                'synch_ed_program_start_day_h': int(row[AnimalValues.synch_ed_program_start_day_h]),
                'synch_ed_estrus_day': int(row[AnimalValues.synch_ed_estrus_day]),
                'stop_day': int(row[AnimalValues.stop_day]),
                'conception_rate': float(row[AnimalValues.conception_rate]),
                'ai_day': int(row[AnimalValues.ai_day]),
                'abortion_day': int(row[AnimalValues.abortion_day]),
                'days_in_preg': int(row[AnimalValues.days_in_preg]),
                'gestation_length': int(row[AnimalValues.gestation_length]),
                'p_gest_for_calf': int(row[AnimalValues.p_gest_for_calf]),
                'presynch_method': row[AnimalValues.presynch_method],
                'tai_method_c': row[AnimalValues.tai_method_c],
                'resynch_method': row[AnimalValues.resynch_method],
                'days_in_milk': int(row[AnimalValues.days_in_milk]),
                'parity': int(row[AnimalValues.parity])
            }
            cow = Cow(args)
            cows.append(cow)
        conn.close()
        return cows

    def get_replacement_cows(self, num):
        cows = []
        conn = sqlite3.connect('input/animal/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM replacement').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM replacement ORDER BY RANDOM() LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
                'events': row[AnimalValues.events],
                'repro_program': row[AnimalValues.repro_program],
                'tai_method_h': row[AnimalValues.tai_method_h],
                'synch_ed_method_h': row[AnimalValues.synch_ed_method_h],
                'estrus_count': int(row[AnimalValues.estrus_count]),
                'estrus_day': int(row[AnimalValues.estrus_day]),
                'tai_program_start_day_h': int(row[AnimalValues.tai_program_start_day_h]),
                'synch_ed_program_start_day_h': int(row[AnimalValues.synch_ed_program_start_day_h]),
                'synch_ed_estrus_day': int(row[AnimalValues.synch_ed_estrus_day]),
                'stop_day': int(row[AnimalValues.stop_day]),
                'conception_rate': float(row[AnimalValues.conception_rate]),
                'ai_day': int(row[AnimalValues.ai_day]),
                'abortion_day': int(row[AnimalValues.abortion_day]),
                'days_in_preg': int(row[AnimalValues.days_in_preg]),
                'gestation_length': int(row[AnimalValues.gestation_length]),
                'p_gest_for_calf': int(row[AnimalValues.p_gest_for_calf]),
                'presynch_method': row[AnimalValues.presynch_method],
                'tai_method_c': row[AnimalValues.tai_method_c],
                'resynch_method': row[AnimalValues.resynch_method]
            }
            cow = Cow(args)
            cows.append(cow)
        conn.close()
        return cows


