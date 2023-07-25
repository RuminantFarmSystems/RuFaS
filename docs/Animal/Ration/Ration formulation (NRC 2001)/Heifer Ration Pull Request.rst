==============================
**Heifer Ration Pull Request**
==============================

*Heifer Ration Implementation:*

-Most functionality from the cow ration formulation is used when
calculating the Heifer ration with slight modifications

-*Modification:* The file **cow_requirements.py** is changed to
**animal_requirements.py** and now contains optional inputs in the main
function that are used in heifer requirements calculations

-*Modification:* The heifer ration has less constraints on the non-LP
model, and so in **ration_NLP.py** there is shorter list of constraints
to be input into the scipy minimize function

-*Modification:* animal_type is added global variable in
**ration_NLP.py** to indicate if the optimization called is for a dry
cow, lactating cow, or heifer. There are conditional statements on this
animal_type variable sprinkled throughout the file

*Requirements Calculations Overhaul:*

*-Functions Removed:*

**Name:** Pen.call_animal_nutrient_rqmts()

**Location:** pen.py

**Description:** This is a *Pen* class function that calls the animal
requirements (formally just hardcoded) function for all animals in the
pen. We no longer calculate nutrient requirements through pen functions;
furthermore, the pen class variable “DBW” was removed as it is no longer
used in the ration formulation.

**Replacement:** In this branch, nutrient requirements are now
calculated by an *AnimalManagement* class function that iterates through
ALL animals in the simulation and calls new function
animal.set_nutrient_rqmts()

**Name:** Pen.calc_anvg_nutrient_rqmts()

**Location:** pen.py

**Description:** This file is no longer necessary or relevant to the
ration formulation (pen averages are calculated within the ration module
(under the class Requirments.set_requirements()

Accordingly, the class variables **self.avg_BW**, **self.avgDMIest,**
are dropped

**Name:** Animal_Management.calc_avg_nutrient_rqmts()

**Description:** For the same reasons as for removing the function
above. These files also were nested in each other through calls.

**Replacement:** Functionality for setting requirements to each pen can
be implemented through (Requirments.set_requirements()) (not necessary
but for sake of replacement functionality)

**Name:** Pen.calc_avg_stats()

**Description:** This function was used to update average pen stats for
when animals were added to pens mid-formulation. This is no longer
necessary because the animals nutrients requirements are called directly
before every ration cycle.

**Replacement:** Not necessary

*-New Functions:*

**Name:** animal.set_nutrient_rqmts()

**Location:** heiferI.py, heiferIII.py, cow.py

**Description:** This is a class function (each slightly different
across different animal classes) that runs said animal’s attributes
through the calc_rqmts() function from animal_requirements.py in the
ration module. This function then sets the return values to nutrient
requirement class variables

**V_Patches Changes:**

*Pen Allocation Method Overhaul:*

•The new and improved pen allocation groups animals more efficiently (by
not necessarily using all pens) takes into account a stocking density,
and the type of animal a pen is meant for. New input parameters for the
animal_managment json include a max stocking density for each pen (key:
‘max_stocking_density’), and a list for the animal types allowed in the
pen (key: ‘animal_groups’). These two parameters will then be stored as
class variables for each pen object.

-pen.\ *max_stocking_density:* variable that is upper bound on stocking
density for a certain pen

-pen.\ *animal_groups*: variable added to Pen class which is a list of
strings for valid animal types in given pen (if list is empty, model
assumes pen can be used for any animal group). The valid animal types
are as follows: “calf,” “growing,” “close-up,” and “l_cow.” The spelling
of each of the variables are exactly as shown above, without the quotes
and other punctuation.

•Furthermore, the algorithm first runs through all pens input in the
simulation and checks if there is a sufficient amount of stalls (of
according animal_group type pens). If not, default pens will be created
prior to grouping.

•(See flow chart for visual description of the new algorithm)

*Changes to:* *daily_update_pen_id()*:

-we now add an animal to a pen of their according group (‘calf’,
‘growing’, ‘close-up’, ‘l_cow’)

-We check if there are pens that need animals, and either way, pick a
pen with the lowest current stocking density

-no longer require queue for pens needing animals, we will just keep
stocking densities as balanced as possible

*Changes to clustering_pen_grouping.py*

-just a slight change to the indexing, no longer hardcoded first
lactating cow pen at 5, more generalized input so the pen id value is
not contingent upon the grouping
