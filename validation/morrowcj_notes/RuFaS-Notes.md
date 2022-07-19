title: Clay's RuFaS Notes  
author: Clay Morrow  
email: morrowcj@outlook.com; clay.morrow@usda.gov  
date: 11-July-2022  

# 11-July-2022 Notes

These are my notes from July 11, as I try to wrap my head around the structure of RuFaS. This
includes the code structure, pseudocode, project organization, and underlying model/theory.

## Psuedocode

In the "RuFaS Psuedocode Conventions" document, the first paragraph states that "pseudocode is a detailed
description of the underlying biological processes that need to be simulated and the document should be 
in **outline** and or short bullet point from **rather than length text**". 

The file 'pseudocode_crop' needs an introduction that orients the reader to 
what this document (and the crop module itself) does. 

## Code

It appears, at first glance, that much of the code is not conducive to isolated testing. For example, the 
`daily_crop_routine()` function takes `soil`, `crop`, `weather`, `time`, and `field_management` as obligatory 
arguments, each of which are classes specific to the RuFaS model that contain data that the routine uses. 
However, it is not clear without diving deep into the code what this function actually does. It is a void function
that updates the `crop` object, as far as I can tell. But which fields? What if I want to know that 
`daily_crop_routine()` works properly without running the full program? Also, it would help if the
function had a name that better alerted the user as to what the function does (e.g., `update_crop_daily()`).

It would be really nice if, each of the components of the model were as independent as possible. For example, 
If a user wanted to simulate ONLY crops, they should be able to `import RUFAS` and call `daily_crop_routine()`
to get simulated crop data, without needing to run the full model. Perhaps this is based on my poor understanding
of what the functions actually do. I hope this becomes more clear and that these comments become moot. 