Title: Field-manure connection design  
Authors: Clay Morrow; Loi Pham; Vempalli Sudharsan Varma  
Date Created: 6 Feb 2023  
Last update: 6 Feb 2023  

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

# Desired variables

In order to keep the model flexible, we should probably anticipate all the future cases that RuFaS will need
to handle (without necessarily implementing all possible scenarios at present). At the most complex, a farm may wish to
utilize both solid manure and liquid manure separately. Therefore, the manure should perhaps be
partitioned into two pools: **solid manure** and **manure slurry**. The default (and perhaps most common) scenario would
be to only have slurry and no solid manure, but it is important to allow for both. The following example would easily
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
  liquid_manure: Optional[ManureData] = ManureData()
  solid_manure: Optional[ManureData] = None
```

Below are the variables that we anticipate the modules will need access to from the other module.

#### Manure variables used by SC module

The manure will need the following variables. The units don't matter for now (but should be metric), 
just be clear on what units you are reporting in, and we can handle conversion later, if necessary.
* Manure amount:
  - mass
  - volume (necessary for liquid) and/or density (nice to have for solid)
  - percent solid (for slurry; >= 20% is considered solid manure)
* Nutrient concentrations (percent of manure mass):
  - Nitrogen
  - Phosphorus
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
