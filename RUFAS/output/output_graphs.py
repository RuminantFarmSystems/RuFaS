import matplotlib.pyplot as plt
import csv
from RUFAS import util
from tkinter.tix import Form

def graph_milk_production(day):
    pen_avg_milk_prod = []
    milk_production_output_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs/growth_report.csv'
    with open(milk_production_output_path,'r') as csvfile:
        plots = list(csv.reader(csvfile, delimiter=','))
        
        for i in range(6, len(plots), 5):
            row = plots[i]
            pen_avg_milk_prod.append(float(row[5]))

    f1 = plt.figure(1)
    plt.plot(day, pen_avg_milk_prod)
    plt.xlabel('Day in Simulation (day)')
    plt.ylabel('Average Milk Production (kg)')
    plt.title('Average Milk Production per Animal for Milk-Producing Pen')
    
    save_dir = util.get_base_dir() / 'Outputs/diagnostics/animal'
    path = str(save_dir / 'milk_production')
    f1.savefig(path + '')

def graph_manure_excretion(day):
    manure = {}
    manure[0] = []
    manure[1] = []
    manure[2] = []
    manure[3] = []
    manure[4] = []
    
    num_animals = {}
    num_animals[0] = []
    num_animals[1] = []
    num_animals[2] = []
    num_animals[3] = []
    num_animals[4] = []
    
    manure_production_output_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs/manure_report.csv'
    with open(manure_production_output_path,'r') as csvfile:
        plots = list(csv.reader(csvfile, delimiter=','))
        
        for i in range(2, len(plots)):
            row = plots[i]
            pen = int(row[2])
            manure[pen].append(float(row[7]))
            num_animals[pen].append(int(row[3]))
    
    f2 = plt.figure(2)
    plt.plot(day, manure[0], label='Pen 0 - Calf')
    #plt.plot(day, manure[1], label='Pen 1 - HeiferI')
    plt.plot(day, manure[2], label='Pen 2 - HeiferII')
    #plt.plot(day, manure[3], label='Pen 3 - HeiferIII')
    plt.plot(day, manure[4], label='Pen 4 - Cow')
    plt.xlabel('Day in Simulation (day)')
    plt.ylabel('Total Manure Excretion (kg)')
    plt.title('Total Manure Excretion per Pen')
    plt.legend()
    
    save_dir = util.get_base_dir() / 'Outputs/diagnostics/animal'
    path = str(save_dir / 'manure_excretion')
    f2.savefig(path + '') 
    
    f3 = plt.figure(3)
    plt.plot(day, num_animals[0], label='Pen 0 - Calf')
    #plt.plot(day, num_animals[1], label='Pen 1 - HeiferI')
    plt.plot(day, num_animals[2], label='Pen 2 - HeiferII')
    #plt.plot(day, num_animals[3], label='Pen 3 - HeiferIII')
    plt.plot(day, num_animals[4], label='Pen 4 - Cow')
    plt.xlabel('Day in Simulation (day)')
    plt.ylabel('Number of Animals in Pen')
    plt.title('Number of Animals in Each Pen')
    plt.legend()
    
    save_dir = util.get_base_dir() / 'Outputs/diagnostics/animal'
    path = str(save_dir / 'num_animals_per_pen')
    f3.savefig(path + '') 
  
def display_graphs(formulation_interval, sim_length):
    day = [i for i in range(1, sim_length, formulation_interval)]
    graph_milk_production(day)
    graph_manure_excretion(day)
    #plt.tight_layout()
    #plt.show()