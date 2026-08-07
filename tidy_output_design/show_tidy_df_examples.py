# only works after sourcing tidy-rufas-output_design-doc.qmd

## ---- Setup ----
from pprint import pprint
import pandas as pd
import sys
from pympler.asizeof import asizeof

# function to display pools in readable way
def show_pool(pool):
  for k, v in pool.items():
    print(f"{k}:")
    pprint(pool[k])
    print("\n")

new_pool = fill_pool(cases, ntime = 4)

## ---- New pool format ----

# look at the pool structure
show_pool(new_pool)

# get the first key and value
first_key = list(new_pool.keys())[0]
first_val = list(new_pool.values())[0]

# look at the first value (list of records)
pprint(first_val)

## ---- Data frames ----

# convert the first element into a data frame
pd.DataFrame(first_val)

# and the last element
pd.DataFrame(list(new_pool.values())[-1])

# add the information from the tuple key:
df = pd.DataFrame(first_val)
df[["module", "caller", "variable"]] = first_key
print(df.to_string())

# A list of dataframe can easily be stacked together:
new_list = frame_pool(new_pool)
new_frame = stack_frames(new_list)

## ---- Multiple values in a record ----

multi_pool = {
  ("Shapes", "get_shape_size", "size"): [
    {"color": "blue", "width": 3, "height": 3, "weight": 1},
    {"color": "red", "width": 3, "height": 1.5, "weight": 2},
    {"color": "green", "weight": 5} # omit width and height
  ]
}
stack_frames(frame_pool(multi_pool))

## ---- RuFaS pool analogue (how output pool currently looks) ----

# concatenate the elements of each tuple key: "module.function.variable"
new_keys = ['.'.join(str(val) for val in k) for k in new_pool.keys()]

# convert current pool to rufas version
old_pool = {
  new_keys[0]: [v["value"] for v in list(new_pool.values())[0]], # first set
  f"{new_keys[1]}.'field=A'": [v["value"] for v in list(new_pool.values())[1] if v["field"] == 'A'], # second set
  # third set
  f"{new_keys[2]}.field='A',crop='corn'": [
    v["value"] for v in list(new_pool.values())[2] if v["field"] == 'A' and v["crop"] == 'corn'
  ],
  f"{new_keys[2]}.field='A',crop='alfalfa'": [
    v["value"] for v in list(new_pool.values())[2] if v["field"] == 'A' and v["crop"] == 'alfalfa'
  ],
  f"{new_keys[2]}.field='B',crop='alfalfa'": [
    v["value"] for v in list(new_pool.values())[2] if v["field"] == 'B' and v["crop"] == 'alfalfa'
  ],
  # last set
  f"{new_keys[3]}.field='A',crop='corn'": [
    v["value"] for v in list(new_pool.values())[3] if v["field"] == 'A' and v["crop"] == 'corn'
  ],
  f"{new_keys[3]}.field='A',crop='alfalfa'": [
    v["value"] for v in list(new_pool.values())[3] if v["field"] == 'A' and v["crop"] == 'alfalfa'
  ],
  f"{new_keys[3]}.field='B',crop='alfalfa'": [
    v["value"] for v in list(new_pool.values())[3] if v["field"] == 'B' and v["crop"] == 'alfalfa'
  ]
}

# Print the entire dictionary in a readable way
show_pool(old_pool)
## This version of the pool may be smaller, but it is very lossy (much information is lost)


## ---- Compare sizes ----

# build size data frame (bytes) using two methods
size_df = pd.DataFrame(
  [
    {"native": new_pool.__sizeof__(), "sys": sys.getsizeof(new_pool), "pympler": asizeof(new_pool)},
    {"native": old_pool.__sizeof__(), "sys": sys.getsizeof(old_pool), "pympler": asizeof(old_pool)},
  ],
  index=["new_pool", "old_pool"]
)

# display the table
print(size_df.transpose().to_string())
## Practically, the new pool is larger, as it contains more information (pympler).

## ---- Filtering ----

# crop table
stacked[(stacked.module == "FieldManager") & (stacked.caller == "measure_crops")]

# heard 
stacked[(stacked.module == "HerdManager") & (stacked.caller == "measure_consumption")]

## ---- Pivoting`
