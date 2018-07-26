from __future__ import print_function
from RUFAS.routines.animal.Holstein import Holstein
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

cow_num = 100
days = 3000 

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
def start_simulation(cow_num, days):
	cows = []
	cull_lst = []				# num of cows culled per day
	new_born_lst = []			# num of new borns per day
	new_born_sold_lst = []		# num of new borns sold per day
	total_milk_prod_lst = []	# total milk production per day
	total_manure_lst = []		# total manure per day
	total_feed_lst = []			# total feed per day
	total_ai_lst = []			# num of AI per day
	total_preg_lst = []			# num of cows pregnant per day
	total_milk_lst = []			# num of cows milking per day

	# choose breed and repro method
	for i in range(cow_num):
		new_cow = Holstein('ed-tai', 0, 'pgf-gnrh', 'ovsynch56', 'pgf', '2pgf', '2pgf')
		if new_cow.sex == 'F':
			cows.append(new_cow)

	# for i in range(cow_num):
	# 	new_cow = Jersey(sexed_semen)
	# 	if new_cow.sex == 'F':
	# 		cows.append(new_cow)
	for i in range(days):
		# print("Day " + str(days+1))
		cull_num = 0
		new_born_num = 0
		new_born_sold_num = 0
		total_milk_prod = 0
		total_manure = 0
		total_feed = 0
		calf_sold = 0
		ai_num = 0
		preg_num = 0
		milk_num = 0

		cow_num = len(cows)
		for j in range(cow_num-1, -1, -1):
			if (not cows[j].is_culled()):
				cull, calving, milk_produced, ai_given, manure, feed = cows[j].update(i)

				# new born
				if (cull):
					cull_num = cull_num + 1
				else:
					if (calving):
						new_born_num = new_born_num + 1
						if cows[j].type == 'H':
							new_cow = Holstein('ed-tai', i, 'pgf-gnrh', 'ovsynch56', 'pgf', '2pgf', '2pgf')
						# else:
							# new_cow = Jersey(sexed_semen)

						#sell male calve
						calf_sold = new_cow.sold()
						if calf_sold:
							new_born_sold_num = new_born_sold_num + 1
						else:
							cows.append(new_cow)

					# ready to breed
					if (ai_given):
						ai_num = ai_num + 1
					if (cows[j].is_preg()):
						preg_num = preg_num + 1
					if (cows[j].is_milk()):
						milk_num = milk_num + 1
					
					total_milk_prod = total_milk_prod + milk_produced
					total_manure = total_manure + manure
					total_feed = total_feed + feed

		# showing results
		cull_lst.append(cull_num)
		new_born_lst.append(new_born_num)
		new_born_sold_lst.append(new_born_sold_num)
		total_milk_prod_lst.append(total_milk_prod)
		total_manure_lst.append(total_manure)
		total_feed_lst.append(total_feed)
		total_ai_lst.append(ai_num)
		total_preg_lst.append(preg_num)
		total_milk_lst.append(milk_num)

	print("Cow count: " + str(len(cows)) + "\n")
	print("Cow #50: ")
	cows[50].print_stat()
	# draw_stat(cull_lst, new_born_lst, new_born_sold_lst, total_milk_prod_lst, total_manure_lst, total_feed_lst, total_ai_lst, total_preg_lst, total_milk_lst)

def draw_stat(cull_lst, new_born_lst, new_born_sold_lst, total_milk_prod_lst, total_manure_lst, total_feed_lst, total_ai_lst, total_preg_lst, total_milk_lst):
	fig = plt.figure()

	ax1 = fig.add_subplot(521)
	ax1.plot(cull_lst)
	ax1.set_title("Total culls per day")

	ax2 = fig.add_subplot(522)
	ax2.plot(new_born_lst)
	ax2.set_title("Total new borns per day")

	ax3 = fig.add_subplot(523)
	ax3.plot(new_born_sold_lst)
	ax3.set_title("Total new borns sold per day")

	ax4 = fig.add_subplot(524)
	ax4.plot(total_milk_prod_lst)
	ax4.set_title("Total milk production per day")

	ax5 = fig.add_subplot(525)
	ax5.plot(total_manure_lst)
	ax5.set_title("Total manure production per day")

	ax6 = fig.add_subplot(526)
	ax6.plot(total_feed_lst)
	ax6.set_title("Total feed per day")

	ax7 = fig.add_subplot(527)
	ax7.plot(total_ai_lst)
	ax7.set_title("Total AI per day")

	ax8 = fig.add_subplot(528)
	ax8.plot(total_preg_lst)
	ax8.set_title("Total preg per day")

	ax9 = fig.add_subplot(529)
	ax9.plot(total_milk_lst)
	ax9.set_title("Total cows milking per day")

	plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.5)
	plt.show()

if __name__ == '__main__':
	start_simulation(cow_num, days)