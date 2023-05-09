To add a new grouping scenario, follow these steps:

1. (Optional) Add extra combinations in Pen.AnimalCombination: If the new scenario requires additional animal combinations that are not already defined in the `Pen.AnimalCombination` Enum, add them. This step is optional if the new scenario only uses the existing combinations.

2. Specify the details of each combination in AnimalGroupingScenario: Add a new Enum member in the `AnimalGroupingScenario` class for the new scenario. Each scenario must be a dictionary of the form `{ Pen.AnimalCombination: [List of animal type/subtype names] }`.

3. Make sure each scenario is both exhaustive and non-overlapping:
    - Exhaustive: Each scenario must account for all animal types and subtypes present in that scenario. In other words, every animal type or subtype should be assigned to a combination.
    - Non-overlapping: Each animal type or subtype must be associated with one and only one animal combination. There should be no duplicates or overlaps between the combinations.

4. Update the subtype naming functions if necessary: If the new scenario requires different naming conventions for animal subtypes, update the relevant `_get_*_name` methods in the `AnimalGroupingScenario` class. For example, if the new scenario requires a new naming convention for cows, update the `_get_cow_name` method.
