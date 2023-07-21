.. _animal-module-background :

=========================================
**Animal Module Background - Read First**
=========================================

**Overview**

  We keep track of the animals in the herd based on the stage of life they
  are in: calf, heifer (which is further divided into stages heiferI,
  heiferII, and heiferIII), and cow. There is also a separate group of
  replacement market animals (of type heiferIII) which are purchased and
  added to the herd if necessary. All animals in the herd are updated on a
  daily basis and every ration_interval (a time interval specified in the
  input JSON file, e.g. 14 days), the animals are grouped into pens and
  are assigned a ration.

  .. image:: media/image4.jpg
     :width: 6.5in
     :height: 4.33333in
     :name: Figure 1

 `Figure 1`_ Provides a heuristic overview of the Animal Module processes and flow of information

**Important classes:**
  -  AnimalManagement
  
  -  LifeCyleManager
  
  -  Pen
  
  -  AnimalBase
  
      -  Calf, HeiferI, HeiferII, HeiferIII, Cow

**Class Relationships:**

  * Cow extends HeiferIII extends HeiferII extends HeiferI extends Calf
    extends AnimalBase (note: we will use the uppercase version of the
    animal groups to refer to the class but the lowercase version to
    refer to the group: e.g. “HeiferII instance” vs “the list of
    heiferIIs”)

  * There is one instance of AnimalManagement. It has a list for each
    animal class, as well as a list of HeiferIIIs for the replacement
    market. It also has a list of Pen instances (each of which have
    characteristics specified in the input JSON file), which store the
    list of animals that are housed in that pen. The animals in the
    Pen lists contain the same elements as the elements in the
    AnimalManagement animal lists (but the Pen list is more of a
    pointer to the list in AnimalManagement: appending to one list
    appends to the other as well). The AnimalManagement instance also
    has an instance of LifeCycleManager, which is where the daily
    update methods are stored.

  .. image:: media/image1.png
     :width: 6.18229in
     :height: 4.46829in
     :name: Figure 2
  `Figure 2`_  provides an overview Entity Relationship Diagram of the Animal Module

**Initialization**

  The animal management input JSON files specifies how many of each animal
  group will be in the initial herd and replacement market. (“herd_num”
  refers to the amount of cows that should be in the simulation at any one
  time, i.e. the target size.)

  .. image:: media/image3.png
     :width: 2.95313in
     :height: 2.23377in

  We have a database file (animals.sqlite) from which we draw basic animal
  information to create the initial herd. The class AnimalInitialization
  contains the code to query the database to create the lists of instances
  of each animal group that will be stored in the AnimalManagement class.
  For initialization, we have two options: the user can elect to either
  draw initial animals from the existing database or to re-populate the
  database with new animals and draw from that.

  (1) The purpose for this database is to have a pool of steady-state
      animals to draw from. It has a table for each class of animal, and
      each table has a column for each characteristic of that animal
      stage. There is also a table for the replacement market. For
      example, the calves table looks like:
    ..

    .. image:: media/image5.png
       :width: 2.73958in
       :height: 2.21875in
      
    ..

      As the animals get older, there are more characteristics that are
      necessary to describe the animal, so there are more columns for the
      tables representing heifers and cows. (As an example, there are
      currently ~1 000 entries in the calves table, ~6 000 entries in each
      of the heiferI and heiferII tables,~600 entries in the heiferIII
      table, ~16 000 entries in the cows table, and ~30 000 entries in the
      replacement market table.) Each record in these tables represents an
      animal that could possibly be chosen to be part of the initial herd.
      Continuing the example in Figure 1, if “calf_num” is 80, we choose 80
      random entries from the calves table, and the values in these rows
      are used in the constructors of 80 Calf objects (similarly for the
      other animal groups).

  (2) If the user chooses to repopulate the database file with new animal
      entries, before the simulation starts 20 000 calves are created
      and they are simulated for 5 000 days. At the end of each day, a
      row is appended to the appropriate table for each animal (for
      example, if the animal is in the heiferII stage then there will be
      a new row in the heiferII table for each day that it stays in the
      heiferII stage). Once this “pre-simulation” is done, the initial
      herd is created as described above.

  See the :ref:`animal-life-cycle-pseudocode` Section A.1A.D for more information 
  about Animal Initialization.

**Daily Updates**

  There are several operations that happen on a daily basis:

    (1) The animals are updated (more on that below).

    (2) The animal ID to the pen dictionary is updated.
      * The AnimalManagement class stores a dictionary with the animal IDs as 
        keys and the pen they are in as values in pen.id_pen.
      * Animal ID - Pen ID pairs are updated daily. New born calves or purchased
        animals are added to pens based on their animal group and the pen with 
        the lowest stocking density

    (3) We iterate through each animal to calculate specific nutrient requirements, 
    nutrient updates, and nutrient compositions. We do this on a pen-by-pen basis, 
    using logic found within the  ration_driver.py file. There is logic within this 
    file to calculate average requirements for specific pens, as well as 
    supporting logic to gather the feed information needed to fulfill/output those 
    requirements. The pseudocode document for the ration_driver file can be found 
    here: :ref:`ration_driver_logic` 

    (4) If it is the end of a ration_interval, we:
      #. Iterate through each animal to calculate the animals’ general nutrient 
         requirements. (See :ref:`calf-requirements`, :ref:`heifer-requirements`,
         :ref:`dairy-cattle-requirements`, and :ref:`cow-heifer-calf-combined-requirements`)
      #. Allocate the animals to pens based on their animal groups, their age or
         their days in milk.
      #. Calculate the average or X percentile of nutrient requirements for the 
         animals in each pen.
      #. Calculate the ration based on the average animal in each pen. We use 
         nonlinear programming optimization for all rations except for the calf 
         rations
      #. Iterate through each animal to calculate the manure excreted.
      #. Calculate animal averages for particular values for each pen (e.g. growth).

  The AnimalManagement class calls the daily updates by passing the animal lists to the LifeCycleManager’s daily_update() function, which returns the updated lists.

  Animal daily update routines update:

    *  Attributes related to the animal’s age, body weight and composition, 
       reproductive status, and health on a daily basis (See the :ref:`animal-life-cycle-pseudocode` for more information). The daily updates are performed 
       by iterating through each animal list and calling the update functions 
       for that animal instance based on its Class.

    *  The culling status of the animal based on production, reproduction, and 
       health status. If culled, the animal is removed from that animal list 
       (See the :ref:`animal-life-cycle-pseudocode`, Section A.1A.C).

    *  Animals are added from the replacement herd if the current herd is too small.

    *  Class changes. If the animal ages up on a certain day (for example, from 
       Calf to HeiferI), then the necessary attributes of the Calf instance are 
       passed to the HeiferI constructor, the Calf object is removed, and the 
       new HeiferI object is added to the heiferI list.

    *  The LifeCycleManager also keeps track of statistics (e.g. number of 
       animals culled for each reason for which an animal can be culled) that 
       are written to the output.

  .. image:: media/image2.jpg
   :width: 6.52604in
   :height: 4.93826in
   :name: Figure 3
  
  `Figure 3`_ Provides the call structure of of the Animal Module

  Each animal object stores, along with its characteristics, four dictionaries that use the simulation days as keys:

    (1) *Animal Events* - appended to only when a significant life cycle event happens to the animal

    (2) *Pen History* - appended to every time the animal switches pens

    (3) *Body Weight History* - appended to every day

    (4) *Milk History* - appended to every day (only cows produce milk, so only Cow instances have a Milk History)