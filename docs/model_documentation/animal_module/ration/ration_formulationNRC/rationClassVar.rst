Ration Class Variables
======================

  | Last Updated: January 28, 2021 

Nutrient Amounts in the Ration

From the optimized ration, we will calculate nutrients amounts and
concentrations. These values will serve as inputs to other functions in
the animal module.

Calculate the amount (kg) of a nutrient in the ration. Default options
should include:

1. Dry matter (dm)

2. Crude protein (cp)

3. Acid detergent fiber (adf)

4. Neutral detergent fiber (ndf)

5. Lignin (lignin)

6. Ash (ash)

7. Phosphorus (phosphorus)

8. Potassium (potassium

Nitrogen (N)

The amount of each nutrient in the total rations is calculated as the
sum of the nutrient concentration multiplied by the amount of the feed
for all feeds in the ration.

.. math:: nutrient\text{_}amount = \ \sum_{i = 1}^{}{(\frac{nutrient\text{_}conc\text{_}feed_{i}}{100} \times {feed}_{i}\text{_}amount)}

nutrient amount = amount of nutrient (kg)

nutrient conc feed\ :sub:`i` = concentration of nutrient in feed i (%)

feed\ :sub:`i` amount = amount of feed i in the ration (kg)

Calculate the concentration of a nutrient in the ration (in a separate
dictionary). Default options should include:

1. Dry matter (dm)

2. Crude protein (cp)

3. Acid detergent fiber (adf)

4. Neutral detergent fiber (ndf)

5. Lignin (lignin)

6. Ash (ash)

7. Phosphorus (phosphorus)

8. Potassium (potassium

9. Nitrogen (N)

The concentration of each nutrient in the ration is calculated as the
amount of the nutrient divided by the total amount of the ration.
Nutrient concentrations are calculated as a percentage.

.. math:: nutrient\text{_}conc = \ \frac{nutrient\text{_}amt}{dm\text{_}amt} \times 100

nutrient conc = nutrient concentration (%)

nutrient amount = amount of nutrient (kg)

dm amount = dry matter amount (kg)

Example from lactating_cow_manure_excretion.py

Li's example to highlight difference between DM and DMI, as well
as respective calculations:
Suppose we have a diet with only feeds A and B and the result from the
linear programming is
  - A = 10 kg
  - B = 15 kg
Then, since all the variables in the solution are in DM basis, the 
DMI= 10 + 15 + = 25 kg.
Let the DM content of A be 80%, of B be 40%.
Farmers need to feed 10 / 0.8 = 12.5 kg ofA and 15 / 0.4 = 37.5 kg of B (as fed basis).
Then, the DM content of the diet is (10 + 15) / (12.5 + 37.5) = 50%.

For the nutrient compositions
Let the CP content of A be 80%, of B be 40%.
Then the CP content of the diet is (10 * 0.8 + 15 * 0.4) / (10 + 15) = 56% in DM basis.

Similarly for ADF, LIG, Ash, and NDF.

Calculating nitrogen in feeds:

For most feeds, nitrogen concentration can be estimated as CP
concentration divided by 6.25.

:math:`N\text{_}amount\text{_}{feed}_{i} = \ \frac{\frac{CP\text{_}conc\text{_}feed_{i}}{6.25}}{100} \times {feed}_{i}\text{_}amount`
[A.2.A.1]

N amount feed\ :sub:`i` = amount of nitrogen (kg)

CP conc feed\ :sub:`i` = crude protein concentration of nutrient in feed
i (%)

feed\ :sub:`i` amount = amount of feed i in the ration (kg)

For milk-based feeds (feed library entries 121, 122, 155, and 157), N is
estimated as CP concentration divided by 6.38.

:math:`N\text{_}amount\text{_}{feed}_{i} = \ \frac{\frac{CP\text{_}conc\text{_}feed_{i}}{6.38}}{100} \times {feed}_{i}\text{_}amount`
[A.2.A.2]

N amount feed\ :sub:`i` = amount of nitrogen (kg)

CP conc feed\ :sub:`i` = crude protein concentration of nutrient in feed
i (%)

feed\ :sub:`i` amount = amount of feed i in the ration (kg)

These values are used to calculate N amount and N concentration of the
ration.
