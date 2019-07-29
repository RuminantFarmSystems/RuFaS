import matplotlib.pyplot as plt
import csv
from RUFAS import util

def graph_milk_production():
    day = []
    pen_avg_milk_prod = []
    milk_production_output_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs/growth_report.csv'
    with open(milk_production_output_path,'r') as csvfile:
        plots = list(csv.reader(csvfile, delimiter=','))
        
        for i in range(6, len(plots), 5):
            row = plots[i]
            day.append(i)
            pen_avg_milk_prod.append(float(row[5]))
    
    plt.plot(day, pen_avg_milk_prod)
    plt.xlabel('Day in Simulation When Ration is Calculated (day)')
    plt.ylabel('Average Milk Production (kg)')
    plt.title('Average Milk Production per Animal for Milk-Producing Pens')
    plt.show()

def graph_manure_excretion():
    day = []
    manure = {}
    manure[0] = []
    manure[1] = []
    manure[2] = []
    manure[3] = []
    manure[4] = []
    
    manure_production_output_path = util.get_base_dir() / 'Outputs/Sample_Farm_Outputs/manure_report.csv'
    with open(manure_production_output_path,'r') as csvfile:
        plots = list(csv.reader(csvfile, delimiter=','))
        
        day = [i for i in range(2, len(plots), 5)]
        
        for i in range(2, len(plots)):
            row = plots[i]
            pen = int(row[2])
            manure[pen].append(float(row[7]))
    
    plt.plot(day, manure[0], label='Pen 0 - Calf')
    #plt.plot(day, manure[1], label='Pen 1 - HeiferI')
    plt.plot(day, manure[2], label='Pen 2 - HeiferII')
    #plt.plot(day, manure[3], label='Pen 3 - HeiferIII')
    plt.plot(day, manure[4], label='Pen 4 - Cow')
    plt.xlabel('Day in Simulation When Ration is Calculated (day)')
    plt.ylabel('Total Manure Excretion (kg)')
    plt.title('Total Manure Excretion per Pen')
    plt.legend()
    plt.show()


def display_graphs():
    graph_milk_production()
    graph_manure_excretion()