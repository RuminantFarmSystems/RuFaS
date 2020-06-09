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
    events = 7
    repro_program = 8
    tai_method_h = 9
    synch_ed_method_h = 10
    mature_body_weight = 11
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
    presynch_method = 23
    tai_method_c = 24
    resynch_method = 25

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
            conn = sqlite3.connect('Inputs/animals.sqlite')
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS calves')
            cur.execute('DROP TABLE IF EXISTS heiferIs')
            cur.execute('DROP TABLE IF EXISTS heiferIIs')
            cur.execute('DROP TABLE IF EXISTS heiferIIIs')
            cur.execute('DROP TABLE IF EXISTS cows')
            cur.execute('CREATE TABLE IF NOT EXISTS calves (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, events VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS heiferIs (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, events VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS heiferIIs (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, events VARCHAR, repro_program VARCHAR, tai_method_h VARCHAR, synch_ed_method_h VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS heiferIIIs (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, events VARCHAR, repro_program VARCHAR, tai_method_h VARCHAR, synch_ed_method_h VARCHAR, mature_body_weight VARCHAR, estrus_count VARCHAR, estrus_day VARCHAR, tai_program_start_day_h VARCHAR, synch_ed_program_start_day_h VARCHAR, synch_ed_estrus_day VARCHAR, stop_day VARCHAR, conception_rate VARCHAR, ai_day VARCHAR, abortion_day VARCHAR, days_in_preg VARCHAR, gestation_length VARCHAR)')
            cur.execute('CREATE TABLE IF NOT EXISTS cows (id VARCHAR, breed VARCHAR, birth_date VARCHAR, days_born VARCHAR, birth_weight VARCHAR, body_weight VARCHAR, wean_weight VARCHAR, events VARCHAR, repro_program VARCHAR, tai_method_h VARCHAR, synch_ed_method_h VARCHAR, mature_body_weight VARCHAR, estrus_count VARCHAR, estrus_day VARCHAR, tai_program_start_day_h VARCHAR, synch_ed_program_start_day_h VARCHAR, synch_ed_estrus_day VARCHAR, stop_day VARCHAR, conception_rate VARCHAR, ai_day VARCHAR, abortion_day VARCHAR, days_in_preg VARCHAR, gestation_length VARCHAR, presynch_method VARCHAR, tai_method_c VARCHAR, resynch_method VARCHAR)')
            conn.commit()
            conn.close()
            self.init_animals()
        
        

    '''
        Description:
            Simulate animals to be stored in the database
        Inputs:
            animal_num: number of animals to simulate
            sim_days: number of days to simulate
    '''
    def init_animals(self, animal_num = 20000, sim_days=3000):
        calves = []
        heiferIs = []
        heiferIIs = []
        heiferIIIs = []
        cows = []

        conn = sqlite3.connect('Inputs/animals.sqlite')
        cur = conn.cursor()

        for _ in range(animal_num):
            args = {
                'id' : self.next_id(),
                'breed': 'HO',
                'birth_date': 0,
                'days_born': 0
            }
            calf = Calf(args)
            if not (calf._culled or calf._sold):
                calves.append(calf)

                cur.execute('INSERT INTO calves (id, breed, birth_date, days_born, birth_weight, body_weight, wean_weight, events) VALUES (?,?,?,?,?,?,?,?)', (calf._id, calf._breed, calf._birth_date, calf._days_born, calf._birth_weight, calf._body_weight, calf._wean_weight, str(calf._events)))
                conn.commit()

        for _ in range(sim_days):
            for calf in calves:
                wean_day = calf.update()
                if wean_day:
                    args = calf.get_calf_values()
                    args.update(id = self.next_id())

                    heiferI = HeiferI(args)
                    heiferIs.append(heiferI)
                    calves.remove(calf)

                    cur.execute('INSERT INTO heiferIs (id, breed, birth_date, days_born, birth_weight, body_weight, wean_weight, events) VALUES (?,?,?,?,?,?,?,?)', (heiferI._id, heiferI._breed, heiferI._birth_date, heiferI._days_born, heiferI._birth_weight, heiferI._body_weight, heiferI._wean_weight, str(heiferI._events)))
                    conn.commit()

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

                    cur.execute('INSERT INTO heiferIIs (id, breed, birth_date, days_born, birth_weight, body_weight, wean_weight, events, repro_program, tai_method_h, synch_ed_method_h) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (heiferII._id, heiferII._breed, heiferII._birth_date, heiferII._days_born, heiferII._birth_weight, heiferII._body_weight, heiferII._wean_weight, str(heiferII._events), heiferII._repro_program, heiferII._tai_method_h, heiferII._synch_ed_method_h))
                    conn.commit()

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

                    cur.execute('INSERT INTO heiferIIIs (id, breed, birth_date, days_born, birth_weight, body_weight, wean_weight, events, repro_program, tai_method_h, synch_ed_method_h, mature_body_weight, estrus_count, estrus_day, tai_program_start_day_h, synch_ed_program_start_day_h, synch_ed_estrus_day, stop_day, conception_rate, ai_day, abortion_day, days_in_preg, gestation_length) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (heiferIII._id, heiferIII._breed, heiferIII._birth_date, heiferIII._days_born, heiferIII._birth_weight, heiferIII._body_weight, heiferIII._wean_weight, str(heiferIII._events), heiferIII._repro_program, heiferIII._tai_method_h, heiferIII._synch_ed_method_h, heiferIII._mature_body_weight, heiferIII._estrus_count, heiferIII._estrus_day, heiferIII._tai_program_start_day_h, heiferIII._synch_ed_program_start_day_h, heiferIII._synch_ed_estrus_day, heiferIII._stop_day, heiferIII._conception_rate, heiferIII._ai_day, heiferIII._abortion_day, heiferIII._days_in_preg, heiferIII._gestation_length))
                    conn.commit()

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
                    heiferIIIs.remove(heiferIII)
                    
                    cur.execute('INSERT INTO cows (id, breed, birth_date, days_born, birth_weight, body_weight, wean_weight, events, repro_program, tai_method_h, synch_ed_method_h, mature_body_weight, estrus_count, estrus_day, tai_program_start_day_h, synch_ed_program_start_day_h, synch_ed_estrus_day, stop_day, conception_rate, ai_day, abortion_day, days_in_preg, gestation_length, presynch_method, tai_method_c, resynch_method) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (cow._id, cow._breed, cow._birth_date, cow._days_born, cow._birth_weight, cow._body_weight, cow._wean_weight, str(cow._events), cow._repro_program, cow._tai_method_h, cow._synch_ed_method_h, cow._mature_body_weight, cow._estrus_count, cow._estrus_day, cow._tai_program_start_day_h, cow._synch_ed_program_start_day_h, cow._synch_ed_estrus_day, cow._stop_day, cow._conception_rate, cow._ai_day, cow._abortion_day, cow._days_in_preg, cow._gestation_length, cow._presynch_method, cow._tai_method_c, cow._resynch_method))
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
        conn = sqlite3.connect('Inputs/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM calves').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM calves LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
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
        conn = sqlite3.connect('Inputs/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM heiferIs').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM heiferIs LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
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
        conn = sqlite3.connect('Inputs/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM heiferIIs').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM heiferIIs LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
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
        conn = sqlite3.connect('Inputs/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM heiferIIIs').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM heiferIIIs LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'events': row[AnimalValues.events],
                'repro_program': row[AnimalValues.repro_program],
                'tai_method_h': row[AnimalValues.tai_method_h],
                'synch_ed_method_h': row[AnimalValues.synch_ed_method_h],
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
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
                'gestation_length': int(row[AnimalValues.gestation_length])
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
        conn = sqlite3.connect('Inputs/animals.sqlite')
        cur = conn.cursor()
        while cur.execute('SELECT COUNT() FROM cows').fetchone()[0] < num:
            self.init_animals()
        rows = cur.execute('SELECT * FROM cows LIMIT ' + str(num)).fetchall()
        for row in rows:
            args = {
                'id': int(row[AnimalValues.id]),
                'breed': row[AnimalValues.breed],
                'birth_date': int(row[AnimalValues.birth_date]),
                'days_born': int(row[AnimalValues.days_born]),
                'birth_weight': float(row[AnimalValues.birth_weight]),
                'body_weight': float(row[AnimalValues.body_weight]),
                'wean_weight': float(row[AnimalValues.wean_weight]),
                'events': row[AnimalValues.events],
                'repro_program': row[AnimalValues.repro_program],
                'tai_method_h': row[AnimalValues.tai_method_h],
                'synch_ed_method_h': row[AnimalValues.synch_ed_method_h],
                'mature_body_weight': float(row[AnimalValues.mature_body_weight]),
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
                'presynch_method': row[AnimalValues.presynch_method],
                'tai_method_c': row[AnimalValues.tai_method_c],
                'resynch_method': row[AnimalValues.resynch_method]
            }
            cow = Cow(args)
            cows.append(cow)
        conn.close()
        return cows

