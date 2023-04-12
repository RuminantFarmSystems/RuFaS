Title: Field-manure connection design  
Authors: Clay Morrow; Loi Pham; Vempalli Sudharsan Varma; Ed Hansen  
Date Created: 6 Feb 2023  
Last update: 12 Apr 2023  

# Introduction

This document should serve as a guide for connecting the manure module to the soil and crop (SC)
module. The creation of this document follows a meeting with Varma and Loi on 6-Feb-2023 where 
we discussed the manure variables that the SC module needed from the manure module. Therefore, part 
of the purpose of this document will be to outline the (types of) variables that each model uses from
the other.

# Manure application to fields

The primary reason that the SC and manure modules need to be connected is that a common type of soil nutrient amendment
in agricultural fields is manure application. Broadly speaking, there are 2 types of applications methods,
broadcasting and injection:

* **Broadcasting** utilizes either solid or liquid (slurry) manure
  - *Simple broadcasting* spreads the manure onto the surface of a field
  - *Broadcasting with incorporation* mixes the manure into the soil (via tillage) after it has been spread onto the 
  surface
  - Simple broadcasting requires less effort but results in substantial nutrient (e.g., ammonia) loss.
  - the incorporation version also promotes N mineralization but can degrade the soil due to the required tillage.
* **Injection** directly places liquid manure beneath the surface of the soil. This method reduces nutrient loss
and soil disturbance but requires more energy. There are 3 types, but the distinctions are not important for the
purposes of this document:
  * *knife*
  * *sweep*
  * *disk*/*coulter*

Ideally, the transaction between the Manure module and the Field module would be stateless. This means that when an 
application of manure is added to the field, the Manure module will put all the necessary variables into some type of 
object and then the Field module will read all of those variables from that object. Field will have no knowledge of how
much manure the Manure module is tracking in total or how it calculated the variables for that application of manure, 
and vice versa.

# Desired variables
In order to keep the model flexible, we should probably anticipate all the future cases that RuFaS will need
to handle (without necessarily implementing all possible scenarios at present). At the most complex, a farm may wish to
utilize both manure applied by machine and by animals, and manure produced by both cow and non-cow sources (resulting in
4 different types of manure pools - machine-applied cow, machine-applied non-cow, animal-applied cow, animal-applied 
non-cow). Because RuFaS is more oriented towards modeling dairy farms, it may make sense to only track cow manure by 
default, while still allowing for non-cow manure to be tracked. The following example would easily
allow for this extension in the future:

```python
# manure_output_classes.py
from typing import Optional
from dataclasses import dataclass

class ManureData:
  """class for tracking manure data"""

@dataclass
class ManurePools:
  """class containing the available manure, partitioned into solid and slurry. Defaults to liquid-only"""
  stored_cow_manure: Optional[ManureData] = ManureData()
  stored_non_cow_manure: Optional[ManureData] = None
  grazing_cow_manure: Optional[ManureData] = ManureData()
  grazing_non_cow_manure: Optional[ManureData] = None
```

Below are the variables that we anticipate the modules will need access to from the other module.

#### Manure variables used by SC module

The manure will need the following variables. The units don't matter for now (but should be metric), 
just be clear on what units you are reporting in, and we can handle conversion later, if necessary.
* Manure amount:
  - dry weight equivalent of the manure
  - percent dry matter content
  - source animal ([Optional] cow, swine, or poultry)
  - field coverage (fraction of the field that is covered by manure)
* Nutrient concentrations (percent of manure mass):
  - Nitrogen
  - Phosphorus
    - fraction of phosphorus that is water-extractable and inorganic
    - (possibly) fraction of phosphorus that is water-extractable and organic
  - Potassium
  - Water (if convenient)
  - Carbon (if convenient)
  - Calcium (if possible)
  - Magnesium (if possible)
  - Sulfur (if possible)

#### SC variables used by manure module

In general, the SC variables that need to be tracked involve the desired amount of nutrients, which translate to
manure requests. Then the amount of manure taken for the SC module should be removed from the manure module:
* manure application day (scheduled)
* required nutrient amounts (nitrogen, phosphorus, etc.) on application date
* requested manure mass (from each pool) as determined by required nutrients
