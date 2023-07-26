.. _user-defined-ration-user-manual :

User-defined ration (udr) user manual
=====================================

**Brief workflow is as follows:**

**Step 1:** Note the supplied udr.json and associated feed & animal
JSONs used for RuFaS input.

**Step 2:** Modify values in
input/userdefinedration/user_defined_ration_input_percentages.json

**Step 3:** If you add or remove feed items, *be sure to* update the
input/feed/**user_defined_ration**\ \_feed.json accordingly (with help
of some automatic steps below, if desired)

**Detailed workflow**

**Step 1:** User should first look at udr.json, and note the change in
both animal and feed inputs.

**Step 2:** User should first modify the following file as desired:

input/userdefinedration/user_defined_ration_input_percentages.json

This file contains a dictionary where the key value pairs are the feed
ID and their associated desired percent of the supplied ration. Be
careful that these total 100: since this input method isn’t user-facing
yet, I didn’t spend too much dev time implementing safeguards on user
input. So: *user beware! We can enforce an error if they don’t total
100, or leave as is for now to more easily go above a DMI estimate (e.g.
if the estimates always feel “low”, here you can feed 120% by making the
percents here go above a total of 1)*

*Note:* there are a few other values one can change.

First is the amount of tolerance of those percentages allowed in the
optimization step.

Under normal circumstances, there are no bounds on a ration formulation
on a per item basis (each possible feed designated in the feed JSON
specified in the main input JSON).

This is because the nonlinear optimization step (which uses the minimize
function from scipy) will attempt numerous “solutions”, which are
combinations of different feed items in different amounts. So they’re
only bound insofar as they must be within the bounds of 0 (including 0,
so no feeds are required in a ration, by default) and 100kg.

The procedure here instead bounds each feed according to the input
percentages as a proportion of the DMI estimate, and the tolerance value
allows that value to have a window around the target value, in cases
where a slight deviation is acceptable.

   As an example: a user may want 30% of the ration to be “feed X”, but
   it is OK if the fit is within some tolerance of those percentages.

   Because these are percentages of the percent tolerance, not raw +/-
   values, a tolerance of 0.033 would allow any value from 29-30.9

   NOTE: We need to think about how to handle cases in which the
   solution drops below the total DMI: e.g. not meeting the minimum DMI
   because the target percentages were too high, and optimization
   lowered the totals - but they don't sum to 100. This could lead to a
   warning that the user needs to widen bounds for X items…but it might
   be such an edge case that it’s not worth a complex method like this.

The second option the user can modify in the input_percentages file is
the milk reduction percent value. This method ensures that milk
production doesn’t drop too far below the “optimal” value.

The idea is as follows: if a user-defined ration cannot be “solved” at
the minimize step, the amount of lactation will be reduced for each
animal in the pen. Then each animals’ requirements are recalculated, and
the optimization problem is once again attempted.

The logic is that reducing the lactation requirements make it more
likely the ration will “work”, and RuFaS proceeds as normal. However, a
particularly poor ration will reduce milk production to 0, which is
unlikely in reality (unless a truly horrific ration is supplied, of
course). Since this is a simplified way to make some adjustment for a
poorly fit ration, we are implementing a lower bound on how far
lactation can drop, with the idea being that a user will be warned that
the ration supplied is not ideal for X reasons.

So in practice: if you set it to 0.75, lactation will only reduce until
the pen average is 75% of the estimated “target” lactation. So you
*could* set it to 1, and it simply won’t drop.

Finally, when using the user_defined_ration the user must ensure that
the main input JSON is "pointing" to the
'input/feed/user_defined_ration_feed.json'

See the next step to check if this file is correct.

**Step 3:** You can modify the
'input/feed/user_defined_ration_feed.json' manually, ensuring the keys
supplied in the ration_percents file are in the purchased and the
different animal types lists.

**Step 4:** double check settings in the
animal_user_defined_ration.json: the only change here from master is
user_input flag.

"ration": {

   "user_input": true,

   "formulation_interval": 30

}

However, always check the energy_and_nutrient_calculation_method
selection as well, since that is often changed in/during testing and
carries different assumptions.

**Step 5:** Now run RuFaS as normal! Note that the ration figures show
fixed feed proportions in each pen that scale with animal population.
