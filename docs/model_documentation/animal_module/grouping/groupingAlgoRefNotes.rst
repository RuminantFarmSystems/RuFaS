.. _cow_pen_grouping_algorithm_method_module :

Cow Pen Grouping Algorithm Method Module
========================================

    | Last Updated: December 16, 2019

**Overview:** The pen allocation grouping algorithm (take from R) utilizes
K-means clustering to effectively group cows based on many factors such
as body weight, Days in Milk, weight of milk production, nutritional
requirements, etc. The algorithm was implemented and used in the animal
management system of the RuFaS simulation model.

**Location:** The python file *“clustering_pen_grouping.py”* is located in
the path **RUFAS.routines.animal** within this directory. The algorithm
is called in a file “\ *animal_managment.py”* (in the same path) called
within the function in the **pen_allocation(self)**\ *.*

**The Grouping Algorithm:** The main function in the file
“\ *clustering_pen_grouping.py”* is the function “\ **grouping(list)”**
This function takes the input of a list (which will be a list of objects
of class Cow) and outputs a 2-D list, with the first array being a List
of the cows ID numbers, and the second array being a list of the
matching pen groupings. The actual algorithm specifically sorts by DIM
(Days in Milk) and LACT (Lactation) categorization values assigned and
different cutoffs of percentiles of 'ScDNED', 'ScDMPD', 'ScMilk'.

**Running Process and Runtime:** As stated before, the module containing
the algorithm is called ONLY by the function **pen_allocation(self)**.
This function is called every new ration interval. In terms of runtime,
the algorithm with a data set of around 1000 cows, the algorithm takes
*less than a second* to run, however when we add more pens and use the
*update_animals()* function from the pen.py file, it increases the
runtime by at least a factor of 5.

**Data Input:** All the data inputs necessary will be stored in fields
within the object of class Cow. When an object of the cow is initialized
it will initiate many of these values to hard coded values, however,
they should be updated as the simulation runs (some of the values
necessary for the algorithm are just hard coded and still need to be
written in so they can be updated periodically. As for each pen, within
the Json input file, there is an option for each pen input where its
properties will be stored (number of stalls, housing type, bedding type,
pen type etc.)

**Final Notes/Next Steps:** As of now, the algorithm runs the test file
with no errors and updates the pen grouping. Further action that may
need to be taken is to label the pens for what they mean (right now they
just have integer values), and also (as stated before) make sure to
periodically update every hard coded value in each cow object.
