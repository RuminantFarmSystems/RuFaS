'''
Created on Oct 19, 2017

Created by the USDA-ARS at Madison, Wisconsin
Kristan, Kass, Jit
'''

if __name__ == '__main__':
    pass

"""This class is a Simulation Controller object. An instance of this object
runs a simulation. Functions in the class are divided based on time periods;
year, month, day"""
class SimulationController:
    global state  # an array of length 3; 0=year 1=month 2=day
    state = [0, 0, 0]

    'Constructor of a Simulation Controller Object'
    def __init__(self, units, duration):
        self.units = units
        self.duration = duration
    
    'This function marks the start of a new year.'
    def annualSimStart(self, state):
        print("Annual simulation starting: " + str(state[0] + 1))
        
    'This function marks the start of a new month'
    def monthlySim(self, state):
        print("Starting sim for month: " + str(state[1] + 1))
        for i in range(30):
            state[2] = i
            self.dailySim(state)  # call dailySim for each day
            print("Ending monthly sim: " + str(state[1]))

    'This function marks the start of a day.'
    def dailySim(self, state):
        print("Daily sim: " + str(state[2] + 1))
    
    'This function marks the end of a year.'
    def annualSimEnd(self, state):
        print("Annual simulation ending: " + str(state[0]))

    """This recursive function iterates through all the years, months, and days 
    for the simulation"""
    def simulationEngine(self, state):
        # IF simulation's years is greater than input, quit
        if state[0] > self.duration - 1:
            return state
        
        #ELSE, begin new year
        self.annualSimStart(state)
        
        #Iterate through months
        for i in range(12):
            state[1] = i
            self.monthlySim(state)
        
        #End the year, and increment year count
        self.annualSimEnd(state)
        state[0] += 1
        
        return self.simulationEngine(state)

    'This function runs a simulation by calling the simulation engine.'
    def runSimulation(self):
        print(self.duration)
        finalState = self.simulationEngine(state)
        print(finalState)


"""Execution of the program begins here. A new simulation controller object is 
created to run the simulation."""
simulation = SimulationController(4, 4)
simulation.runSimulation()
