'''
Created on Oct 19, 2017

Created by the USDA-ARS at Madison, Wisconsin
Kristan, Kass, Jit
'''

"""This class represents a Simulation Controller object. An instance of this 
object represents one simulation."""

class SimController:

    'Global variables'
    global currYear, currMonth, currDay
    currYear = 1
    currMonth = 1
    currDay = 0

    'Constructor of a Simulation Controller Object'

    def __init__(self, duration):
        self.duration = duration

    'This function marks the start of a new year.'

    def annualSimStart(self):
        print("Annual simulation starting: " + str(currYear))

    'This function marks the start of a new month'

    def monthlySim(self):
        global currYear, currMonth, currDay
        print("Starting sim for month: " + str(currMonth + 1))
        for i in range(30):
            currDay = i
            self.dailySim()  # call dailySim for each day

    'This function marks the start of a day.'

    def dailySim(self):
        print("Daily sim: " + str(currDay + 1))

    'This function marks the end of a year.'

    def annualSimEnd(self):
        print("Annual simulation ending: " + str(currYear))

    """This recursive function iterates through all the years, months, and days 
    for the simulation"""

    def simulationEngine(self):
        global currYear, currMonth, currDay

        # IF simulation's years is greater than input, quit
        if currYear > self.duration:
            return

        # ELSE, begin new year
        self.annualSimStart()

        # Iterate through months
        for i in range(12):
            currMonth = i
            self.monthlySim()

        # End the year, and increment year count
        self.annualSimEnd()
        currYear += 1

        return self.simulationEngine()

    'This function runs a simulation by calling the simulation engine.'

    def runSimulation(self):
        print(self.duration)
        finalState = self.simulationEngine()
