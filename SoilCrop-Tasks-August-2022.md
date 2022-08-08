# Tasks for Brandon Aug 8-26

1. Finish checking all files in `RUFAS/routines/field/` for Sphinx docstrings and for pseudocode references.
    * [x] Add documentation to all files that remain undocumented
    * [x] Check that all attributes and parameters have psuedocode references
    * [x] If psuedocode (and/or docstrings) are missing and cannot be easily found and added, make sure that a `#TODO` 
      with an appropriate GitHub Issue reference is included
    * [x] Please make a list of ALL attributes and parameters that don't have pseudocode/documentation and send that list to 
      Hector (with me CC'd), asking him to let us know what they mean so that we can write documentation. For example 
      `BaseCrop.fr_n1` vs `BaseCrop.fr_n2` have bad documentation (Issue #179). A list of all instances will make it easier
      for him to give us answers all at once. 
            *link to that list is on BaseCamp in 'Brandon Summer 2022' folder and I will be adding to it as I find new issues*
2. Make sure that all `TODO` blocks have GitHub Issues referenced. 
   * [x] **Hint:** in a bash terminal (e.g., Mac terminal or the "Terminal" tab in Pycharm), 
   the command `grep -ir "todo" folder/ | grep -iv "GitHub"` will print a list of all the
   lines (within all files in `folder/`) that contain the word "todo" but not the word "github" (case insensitive because of `-i`). 
   * Replace `folder/` in the above code with the path to whatever folder you're checking. You know where our code lives.
3. Once (1) and (2) are completed, i) `git commit` your changes locally, ii) `git pull` any changes 
from the remote into your local branch, iii) `git push` your changes to the remote branch, and 
iv) create a pull request (PR) in GitHub (make sure `base: sequential_v3` and 
`compare: sequential_v3_docstrings`). 
   * [ ] Be sure to request Reid as a reviewer on this PR. 
   * [ ] Be descriptive in the PR comment: give a short list of the changes made.
5. Once the pull request has been submitted, create a new branch called "sequential_v3_unittest" 
(for example, type `git checkout -b "sequential_v3_unittest"` into your terminal). 
   * [ ] **Double check** that your editor is working off of this new branch - in pycharm that's in the lower right. 
   * [ ] If you have any questions or need help, **please** ask Reid. He's made it very clear to me that he is happy to
   assist and we both encourage you to ask for help as often as needed. **There are no stupid questions!** 
6. Begin working on the unit tests that I've outlined in the next section below.
   * [ ] Work through the steps in order, tests are among the most important parts of a system, so be thoughtful 
   about how you write them. 
   * [ ] If you get stuck, ask for help. 
   * [ ] If you get really stuck, move on to something else by making a `TODO` and a GitHub Issue. 
   We'll get back to the problem later!
   * [ ] **Commit often**, with comments about what you did, and push your code to the remote branch at the end of every 
   day **at least**. 

# Soil and Crop Unit Tests 2022

In this section, I'll talk about unit tests, I'll provide resources for learning about unit tests, and I'll provide an 
example that walks through a relatively common and simple method for writing such tests. 

First, take the time to watch this video that Pooyah made:  https://www.youtube.com/watch?v=RDudLMFSUVA. 
Watch it carefully and take notes if needed.

You may also want to read more about `pytest`. I have found this to be a useful resource: https://realpython.com/pytest-python-testing/
and this page talks about unit testing generally but uses the more basic `unittest` module (I recommend using `pytest` instead): 
https://realpython.com/python-testing/. **Refer to these documents often**, they will be very useful and will help you become better 
at writing tests. They take practice, so don't get discouraged. As always, ask for help if you need it - Reid is available.

Once you're ready to write tests, I'd suggest you start by looking at the code path diagram for the Soil and Crop module:
https://3.basecamp.com/3486446/buckets/5296287/uploads/5162606254. 
Note that each box in this diagram represents a function within RUFAS. Note also that each arrow shows which additional 
functions are called by the first function. For example, the very first function in the model is `main()` (at the top in blue). 
The main function calls two other functions `input_prompt()` and `SimulationEngine.simulate()`, etc. 

The purple boxes represent functions within the Soil and Crop module. Eventually, we will need to write tests for
(nearly) all of those purple boxes. But It is important to do so systematically. The functions that will be easiest
to test are those that don't call any other function (i.e., those at the bottom of the diagram). So, 
as you decide which tests to write next, keep these things in mind:
 * Start with low-level functions (those with no arrows pointing to other functions)
 * Try to start with functions that do only simple things! 
 * Save functions that do more complex things for later, once you have more practice!

For example, if we go to the bottom right of the figure we can see that `yields.cut()` is a very low-level function. 
Let's write some tests for this function. I've outlined how to do this below, but have not committed any work. So, you'll 
need to execute the steps yourself, which will be useful practice before diving in on your own. 

As you go through this list, check off the steps as you complete them and/or understand the message they are conveying. 

1. First, we need to open the file containing the funciton: `RUFAS/routines/field/crop/yields.py`
2. Next, we check for file-level documentation to get an idea for what the file does. 
   * [ ] From this documentation, we can learn that `field.py` contains functions associated with "calculating and 
   updating the yield values of a crop_type". 
   * [ ] We also learn that the only function in this file that gets called by another file is `update_all()`. 
   All other functions are **used** by `update_all()`. We can check our code path diagram to verify that this is the case.
3. Then, within the `field.py` file, we find the `cut()` function (on line 283).
   * [ ] We read the documentation and learn that the intended functionality of `cut()` is to "cut the crop without killing
   it". 
   * [ ] We also see that `cut()` takes two arguments: `crop_type` (which is a crop instance), and `bio_frac` (which is a 
   number indicating the proportion of biomass that should be removed by the cut).
   * [ ] We should take the time to specify in the documentation that `bio_frac` should be a float by changing line 291 from
   `bio_frac: fraction of biomass removed during the cut` to 
   `bio_frac (float): fraction of biomass removed during the cut` 
4. Next, we read through the code of `cut()` to see what it actually does. 
   * [ ] The first line is `crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)`, which sets the 
   `accumulated_HU` attribute of `crop_type` equal to its previous value multiplied by the difference of `bio_frac` 
   from 1.
   * [ ] The second line is `crop_type.fr_PHU = crop_type.accumulated_HU / crop_type.PHU`, which then divides this newly 
   calculated `accumulated_HU` value by the `PHU` attribute of `crop_type` and saves it in the `fr_PHU` attribute.
   * [ ] The third line, `crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)`, sets the `LAI_actual` attribute
   of `crop_type` to its previous value times `1 - bio_frac`.
   * [ ] The fourth line, `crop_type.fr_LAI_max = 0`, simply sets the `fr_LAI_max` attribute of `crop_type` to 0. 
   * [ ] The fifth line is `crop_type.biomass_actual -= crop_type.yield_actual`, which sets the `biomass_actual` attribute
   equal to its previous value minus the `yield_actual` attribute.
   * [ ] The sixth line is `crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)`, which sets the `bio_P` attribute of 
   `crop_type` equal to its previous value times `1 - bio_frac`. 
   * [ ] The seventh line is similar: `crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)`. This sets `bio_N` to its
   previous value times `1 - bio_frac`
   * [ ] The eighth and final line of code in `cut()` is `crop_type.ET_annual = 0`, which simply sets the `ET_annual` 
   attribute to 0. 
5. So, we now know that `cut()` depends upon some specific attributes of `crop_type`. The function does not return
anything (more on that shortly), it simply updates some attributes of the `crop_type` instance. We now know that:
   * `cut()` **needs** starting values of the following `crop_type` attributes:
     - `accumulated_HU`,
     - `PHU`,
     - `LAI_actual`,
     - `yield_actual`,
     - `biomass_actual`
     - `bio_P`, and
     - `bio_N`
   * `cut()` also **sets** the following attributes
     - `accumulated_HU`,
     - `fr_PHU`,
     - `LAI_actual`,
     - `fr_LAI_max`,
     - `biomass_actual`,
     - `bio_P`,
     - `bio_N`, and
     - `ET_annual`
6. Because `cut()` updates 8 attributes, we'll need to write **at least** 8 tests. Those tests can be summarized as
follows (note the two different types):
   * Is `accumulated_HU` properly calculated by `cut()`?
   * Is `fr_PHU` properly calculated by `cut()`? 
   * Is `LAI_actual` properly calculated by `cut()`? 
   * Does `fr_LAI_max` equal 0 after running `cut()`?
   * Is `biomass_actual` properly calculated by `cut()`? 
   * Is `bio_P` properly calculated?
   * Is `bio_N` properly calculated?
   * Does `ET_annual` equal 0 after running `cut()`?
7. Let's decide to put all tests of the `yields.py` file into a single new test file called `tests/test_yields.py`. 
   * [ ] We start by importing relevant modules. We need the `base_crop.py` module to create our `crop_type` object and the 
   `yields.py` module for the functions to test. We'll also import `MagicMock` and the `pytest` module:
   ```python
   from RUFAS.routines.field.crop.crop_types import base_crop
   from RUFAS.routines.field.crop.yields import cut
   from unittest.mock import MagicMock
   import pytest
   ```
   * [ ] Next we want to create our `crop_type` object by mocking the `BaseCrop` class. 
   Two things to consider here are 1) we don't need ALL `BaseCrop` attributes, which is why we mock and 2) we don't 
   want to have to code up a crop object for each test, so we'll create a reusable function instead:
   ``` 
   def mock_crop(HU=0.1, PHU=8.8, LAI=2.3, yld=3.0, P=0.5, N=0.7, bmass=3.2):
    mcrop = MagicMock(base_crop.BaseCrop)
    mcrop.accumulated_HU = HU
    mcrop.PHU = PHU
    mcrop.LAI_actual = LAI
    mcrop.yield_actual = yld
    mcrop.bio_P = P
    mcrop.bio_N = N
    mcrop.biomass_actual = bmass
    return mcrop
   ```
   This code creates and returns a mock crop object each time it is called. Note also that I set the starting values
   of the attributes arbitrarily - They just need to be the right type and should be somewhat reasonable. 
   * [ ] Now we can write our first test, using `pytest` syntax. For that, all we need is to write a function that starts with 
   `test_` and that  `assert`s something. The first test will check that `cut()` correctly updates the `accumulated_HU` 
   attribute. We want our tests to have long and very descriptive names that start with "test", so we'll call it 
   `test_cut_correctly_sets_accumulated_HU`:
   ```python
   def test_cut_correctly_sets_accumulated_HU():
    crop = mock_crop()
    cut(crop, 0.33)
    assert pytest.approx(crop.accumulated_HU) == 0.1 * (1 - 0.33)
   ```
   All this function did was 1) create our mock crop, 2) call the `cut()` function on that crop, and 3) assert that
   the new value of `accumulated_HU` must be (approximately) equal to `0.1 * (1 - 0.33)`, which is the initial 
   value of `accumulated_HU` (initialized by `mock_crop`) multiplied by 1 - the `bio_frac` parameter supplied. 

   Note that our tests would fail if we asserted that these quantities were exactly equal 
   (`crop.accumulated_HU == 0.1 * (1 - 0.33)`). This is because of rounding errors and is why we need `pytest.approx()`.
9. The `test_yields.py` file should now contain this code:
   ```python
   from RUFAS.routines.field.crop.crop_types import base_crop
   from RUFAS.routines.field.crop.yields import cut
   from unittest.mock import MagicMock
   import pytest
    
   def mock_crop(HU=0.1, PHU=8.8, LAI=2.3, yld=3.0, P=0.5, N=0.7, bmass=3.2):
       mcrop = MagicMock(base_crop.BaseCrop)
       mcrop.accumulated_HU = HU
       mcrop.PHU = PHU
       mcrop.LAI_actual = LAI
       mcrop.yield_actual = yld
       mcrop.bio_P = P
       mcrop.bio_N = N
       mcrop.biomass_actual = bmass
       return mcrop
   
   def test_cut_correctly_sets_accumulated_HU():
       crop = mock_crop()
       cut(crop, 0.33)
       assert pytest.approx(crop.accumulated_HU) == 0.1 * (1 - 0.33)
   ```
   and we can run our tests from the terminal with the command `pytest -v tests/test_yields.py`. Run this command
   to ensure that your test passed.
10. Try writing the remaining tests on your own without looking at the code below. It will be good practice. 
    Once you're done, compare to what I've written:
    ```python
    def test_cut_correctly_sets_fr_PHU():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.fr_PHU) == (0.1 * (1 - 0.33)) / 8.8

    def test_cut_correctly_sets_LAI_actual():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.LAI_actual) == 2.3 * (1 - 0.33)
   
    def test_cut_sets_fr_LAI_max_to_zero():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.fr_LAI_max) == 0
   
    def test_cut_correctly_sets_biomass_actual():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.biomass_actual) == 3.2 - 3.0
   
    def test_cut_correctly_sets_bio_P():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.bio_P) == 0.5 * (1 - 0.33)
   
    def test_cut_correctly_sets_bio_N():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.bio_N) == 0.7 * (1 - 0.33)
   
    def test_cut_sets_ET_annual_to_zero():
        crop = mock_crop()
        cut(crop, 0.33)
        assert pytest.approx(crop.ET_annual) == 0
    ```
11. After writing these 8 tests, there is one additional test to write. `cut()` is a side-effect function, meaning that 
it doesn't return anything. Instead, it changes the objects that were given as input. One potential problem with these
functions is that it can be hard to keep track of all the things that have changed. Up until now, we've only tested
attributes in an isolated way: create a mock, change the mock, test one value. But, we need to make sure that all of
the values are calculated correctly **at the same time**. So, our final test will do just that: 

    ```python
    def test_cut_correctly_sets_all():
        crop = mock_crop()
        cut(crop, 0.33)
        test_list = [
            pytest.approx(crop.accumulated_HU) == 0.1 * (1 - 0.33),
            pytest.approx(crop.fr_PHU) == (0.1 * (1 - 0.33)) / 8.8,
            pytest.approx(crop.LAI_actual) == 2.3 * (1 - 0.33),
            pytest.approx(crop.fr_LAI_max) == 0,
            pytest.approx(crop.biomass_actual) == 3.2 - 3.0,
            pytest.approx(crop.bio_P) == 0.5 * (1 - 0.33),
            pytest.approx(crop.bio_N) == 0.7 * (1 - 0.33),
            pytest.approx(crop.ET_annual) == 0
        ]
        assert all(test_list)
    ```
    It may be tempting to **only** include this last function since it tests everything, but if this test fails, 
    you won't know where it fails. It is better to have individual tests separated.
12. Make sure to 
    * [ ] save these 9 tests in `test_yields.py`, and 
    * [ ] execute `pytest -v tests/test_yields.py` one last time
to make sure that the tests all passed. Then you can commit these changes and push it to the remote branch! 
13. That's it. We're done testing `cut()` for now but there are some things to keep in mind:
    * [ ] The above tests are not DRY (do not repeat yourself) and there are ways to make this suite of tests much clearner.
    That's a bit more complicated though, so for now, simple is better. 
    * [ ] We have also only verified that `cut()` works for a **very** specific set of starting conditions. We'll eventually
    need to test a variety of starting conditions to make our tests more robust. But again, for now, simple is better.
    * [ ] When writing tests you will be looking at the code in an in-depth way, which means that it is the ideal time
    to improve code when possible. For example, I mentioned in (5) that the `cut()` function returns nothing. We also know
    that `bio_frac` should be a `float`. Yet, these facts are not clear from the function definition. 
    We can (and should) take this opportunity to change the definition of cut to be more clear: 
    `def cut(crop_type, bio_frac: float) -> None:`. Always be on the lookout for ways to improve or refactor the code but 
    **only** do so if it will not take a lot of extra work (i.e., quick and simple improvements rather than full re-writes).    
15. Now that we're done testing `cut()`, you should write your own tests for `calc_nutrient_removal()`, `calc_yield_act()`,
`calc_yield_max()`,  `calc_dry_down()`, `calc_HI_act()`, and `calc_HI_max()`. (from `yields.py`) into the 
`test_yields.py` file. 
    * [ ] Notice that you'll need to mock some additional crop attributes. These can be added directly to the 
    `mock_crop` function. 
    * [ ] Ignore `calc_quality_assessment()` and `calc_harvest_quality()`, since they don't do anything right now. 
    * [ ] you may also want save `kill()` for later, since you'll first need to test the `FieldManagement.schedule_application()`
    function (in a file called `tests/test_field_management.py`). 
    * [ ] Make sure to document all the functions you've tested and all those you've decided to skip for now (perhaps create a 
    GitHub issue for all skipped/missing tests)
15. Try writing some tests for `update_all()` too. 
    * [ ] Does it actually update all the attributes it is supposed to? 
    * [ ] What should be different when `PHU` is > 1 vs when it is > 1? 
16. Move onto other low-level functions and work your way up. If you aren't confident in your ability to test a function,
skip it or ask for help. 
17. Make sure you 
     * [ ] create a list of all the tests you've written (and those that still need tests). 
     * [ ] Also check the `test_field.py` file to see which functionality has already been tested. 
     Move any such tests out of this file into their respective test files (for example the 
     `test_soil_carbon_aggregation()` test should be moved to `tests/test_carbon_cycle.py`, etc.)
18. You've got this!
