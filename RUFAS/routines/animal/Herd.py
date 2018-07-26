from __future__ import print_function
from RUFAS.routines.animal.Holstein import Holstein
import matplotlib as mpl

mpl.use('TkAgg')
import matplotlib.pyplot as plt

# Method: start_simulation
''' 
    Description:
        Initializes summary variables
    Input: 
        cow_num: number of cows at the beginning of the simulation
        days: how long the simulation lasts
    Output:
        cull_num: numbers of cows culled in this simulation
        new_born_num: numbers of cows born in this simulation
        new_born_sold_num: numbers of newborns (male calves) sold in this simulation
        total_milk_prod: total milk production in the simulation 
        total_manure: total manure production in the simulation
        total_feed: total feed used in the simulation
        ai_num: times of services in this simulation 
        preg_num: number of pregnancy in the whole simulation  
        milk_num: number of lactation in the whole simulation 
'''

class Herd():
    def __init__(self, input_herd_data):
        self.cow_num = input_herd_data["cow_num"]
        self.cows = []
        self.cull_lst = []  # num of cows culled per day
        self.new_born_lst = []  # num of new borns per day
        self.new_born_sold_lst = []  # num of new borns sold per day
        self.total_milk_prod_lst = []  # total milk production per day
        self.total_manure_lst = []  # total manure per day
        self.total_feed_lst = []  # total feed per day
        self.total_ai_lst = []  # num of AI per day
        self.total_preg_lst = []  # num of cows pregnant per day
        self.total_milk_lst = []  # num of cows milking per day

        # choose breed and repro method
        for i in range(self.cow_num):
            new_cow = Holstein('ed-tai', 0, 'pgf-gnrh', 'ovsynch56', 'pgf', '2pgf', '2pgf')
            if new_cow.sex == 'F':
                self.cows.append(new_cow)

        # for i in range(self.cow_num):
        # 	new_cow = Jersey(sexed_semen)
        # 	if new_cow.sex == 'F':
        # 		self.cows.append(new_cow)
            # print("Day " + str(days+1))
        self.cull_num = 0
        self.new_born_num = 0
        self.new_born_sold_num = 0
        self.total_milk_prod = 0
        self.total_manure = 0
        self.total_feed = 0
        self.calf_sold = 0
        self.ai_num = 0
        self.preg_num = 0
        self.milk_num = 0
   
    def daily_update(self, time):
        self.cull_num = 0
        self.new_born_num = 0
        self.new_born_sold_num = 0
        self.total_milk_prod = 0
        self.total_manure = 0
        self.total_feed = 0
        self.calf_sold = 0
        self.ai_num = 0
        self.preg_num = 0
        self.milk_num = 0

        day_num = (time.year-1)*365 + time.day
        cow_num = len(self.cows)

        for j in range(cow_num - 1, -1, -1):
            if (not self.cows[j].is_culled()):
                cull, calving, milk_produced, ai_given, manure, feed = self.cows[j].update(day_num)
    
                # new born
                if (cull):
                    self.cull_num = self.cull_num + 1
                else:
                    if (calving):
                        self.new_born_num = self.new_born_num + 1
                        if self.cows[j].type == 'H':
                            new_cow = Holstein('ed-tai', day_num, 'pgf-gnrh', 'ovsynch56', 'pgf', '2pgf', '2pgf')
                        # else:
                        # new_cow = Jersey(sexed_semen)
    
                        # sell male calve
                        self.calf_sold = new_cow.sold()
                        if self.calf_sold:
                            self.new_born_sold_num = self.new_born_sold_num + 1
                        else:
                            self.cows.append(new_cow)
    
                    # ready to breed
                    if (ai_given):
                        self.ai_num = self.ai_num + 1
                    if (self.cows[j].is_preg()):
                        self.preg_num = self.preg_num + 1
                    if (self.cows[j].is_milk()):
                        self.milk_num = self.milk_num + 1
    
                    self.total_milk_prod = self.total_milk_prod + milk_produced
                    self.total_manure = self.total_manure + manure
                    self.total_feed = self.total_feed + feed
    
        # showing results
        self.cull_lst.append(self.cull_num)
        self.new_born_lst.append(self.new_born_num)
        self.new_born_sold_lst.append(self.new_born_sold_num)
        self.total_milk_prod_lst.append(self.total_milk_prod)
        self.total_manure_lst.append(self.total_manure)
        self.total_feed_lst.append(self.total_feed)
        self.total_ai_lst.append(self.ai_num)
        self.total_preg_lst.append(self.preg_num)
        self.total_milk_lst.append(self.milk_num)
    
        #print("Cow count: " + str(len(self.cows)) + "\n")
        #print("Cow #50: ")
        #self.cows[50].print_stat()
        
    
    # draw_stat(cull_lst, new_born_lst, new_born_sold_lst, total_milk_prod_lst, total_manure_lst, total_feed_lst, total_ai_lst, total_preg_lst, total_milk_lst)
    
    def draw_stat(self):
        fig = plt.figure()
    
        ax1 = fig.add_subplot(521)
        ax1.plot(self.cull_lst)
        ax1.set_title("Total culls per day")
    
        ax2 = fig.add_subplot(522)
        ax2.plot(self.new_born_lst)
        ax2.set_title("Total new borns per day")
    
        ax3 = fig.add_subplot(523)
        ax3.plot(self.new_born_sold_lst)
        ax3.set_title("Total new borns sold per day")
    
        ax4 = fig.add_subplot(524)
        ax4.plot(self.total_milk_prod_lst)
        ax4.set_title("Total milk production per day")
    
        ax5 = fig.add_subplot(525)
        ax5.plot(self.total_manure_lst)
        ax5.set_title("Total manure production per day")
    
        ax6 = fig.add_subplot(526)
        ax6.plot(self.total_feed_lst)
        ax6.set_title("Total feed per day")
    
        ax7 = fig.add_subplot(527)
        ax7.plot(self.total_ai_lst)
        ax7.set_title("Total AI per day")
    
        ax8 = fig.add_subplot(528)
        ax8.plot(self.total_preg_lst)
        ax8.set_title("Total preg per day")
    
        ax9 = fig.add_subplot(529)
        ax9.plot(self.total_milk_lst)
        ax9.set_title("Total cows milking per day")
    
        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.5)
        plt.show()
    
