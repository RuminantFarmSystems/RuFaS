# Tasks for Brandon Aug 8-26

1. Finish checking all files in `RUFAS/routines/field/` for Sphinx docstrings and for pseudocode references
    * Add documentation to all files that remain undocumented
    * Check that all attributes and parameters have psuedocode references
    * If psuedocode (and/or docstrings) are missing and cannot be easily found and added, make sure that a `#TODO` 
      with an appropriate GitHub Issue reference is included.
2. Make sure that all `TODO` blocks have GitHub Issues referenced. 
   * **Hint:** in a bash terminal (e.g., Mac terminal or the "Terminal" tab in Pycharm), 
   the command `grep -ir "todo" folder/ | grep -iv "GitHub"` will print a list of all the
   lines (of files) in `folder/` that contains the word "todo" but not the word "github". 
   * Replace `folder/` in the above code with the path to whatever folder you're checking. 
3. Once (1) and (2) are completed, i) `git commit` your changes locally, ii) `git pull` any changes 
from the remote into your local branch, iii) `git push` your changes to the remote branch, and 
iv) create a pull request (PR) in GitHub (make sure `base: sequential_v3` and 
`compare: sequential_v3_docstrings`). 
   * Be sure to request Reid as a reviewer. 
   * Be descriptive in the PR comment: give him a short list of the changes made.
5. Once the pull request has been submitted, create a new branch called "sequential_v3_unittest" 
(for example, type `git checkout -b "sequential_v3_unittest"`). 
   * **Double check** that your editor is working off of this new branch. 
   * If you have any questions or need help, **please** ask Reid. He's made it very clear to me that he is happy to
   help and we both encourage you to ask for help often as needed. **There are no stupid questions!** 
6. Begin working on the unit tests that I've outlined below.
   * Work through the steps in order, tests are among the most important parts of a system, so be thoughtful 
   about how you write them. 
   * If you get stuck, ask for help. 
   * If you get really stuck, move on to something else by making a `TODO` and a GitHub Issue. 
   We'll get back to the problem later!
   * **Commit often**, with comments about what you did, and push your code to the remote branch at the end of every 
   day at least. 

# Soil and Crop Unit Tests 2022

These resources will be helpful for understanding unit tests in python: https://realpython.com/python-testing/ and this
one introduces `pytest`: https://realpython.com/pytest-python-testing/
**refer to these documents often**. Take some time to read through them before you start writing tests. I'm going
to use `pytest` below and recommend you do the same.

Start by looking at the code path diagram; https://3.basecamp.com/3486446/buckets/5296287/uploads/5162606254  
Note that each box represents a function RUFAS. Note also that each arrow shows which additional functions are called
by the first function. For example, the very first function in the model is `main()` (at the top in blue). The main 
function calls two functions `input_prompt()` and `SimulationEngine.simulate()`, etc. 

The purple boxes represent functions within the Soil and Crop module. Eventually, we will need to write tests for
(nearly) all of those purple boxes. But It is important to do so systematically. The functions that will be easiest
to test are those that don't call any other function (i.e., those at the bottom of the diagram). So, 
as you decide which tests to write next, keep these things in mind:
 * Start with low-level functions (those with no arrows pointing to other functions)
 * Try to start with functions that do only simple things! 
 * Save functions that do more complex things for later, once you have more practice!

For example, if we go to the bottom right of the figure we can see that `yields.cut()` is a very low-level function. 
Let's write some tests for this function. I've outlined how to do this, but have not committed the work. So, please 
execute these steps as practice. 

1. First, we need to open the file `RUFAS/routines/field/crop/yields.py`
2. Next, we check for file-level documentation to get an idea for what the file does. 
   * From this documentation, we can learn that `field.py` contains functions associated with "calculating and 
   updating the yield values of a crop_type". 
   * We also learn that the only function that gets called by another file is `update_all()`. All other functions in
   this file are **used** by `update_all()`. We check our code path diagram to verify that this is the case.
3. Then, within the `field.py` file, we find the `cut()` function (on line 283).
   * We read the documentation and learn that the intended functionality of `cut()` is to "cut the crop without killing
   it". 
   * We also see that `cut()` takes two arguments: `crop_type` (which is a crop instance), and `bio_frac` (which is a 
   number indicating the fraction of biomass that should be removed).
   * We should take the time to specify in the documentation that `bio_frac` should be a float by changing line 291 from
   `bio_frac: fraction of biomass removed during the cut` to 
   `bio_frac (float): fraction of biomass removed during the cut` 
4. Next, we read through the code of `cut()` to see what it actually does. 
   * The first line is `crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)`, which sets the 
   `accumulated_HU` attribute of `crop_type` equal to its previous value multiplied by the difference of `bio_frac` 
   from 1.
   * The second line is `crop_type.fr_PHU = crop_type.accumulated_HU / crop_type.PHU`, which then divides this newly 
   calculated `accumulated_HU` value by the `PHU` attribute of `crop_type` and saves it in the `fr_PHU` attribute.
   * The third line, `crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)`, sets the `LAI_actual` attribute
   of `crop_type` to its previous value times `1 - bio_frac`.
   * The fourth line, `crop_type.fr_LAI_max = 0`, simply sets the `fr_LAI_max` attribute of `crop_type` to 0. 
   * The fifth line is `crop_type.biomass_actual -= crop_type.yield_actual`, which sets the `biomass_actual` attribute
   equal to its previous value minus the `yield_actual` attribute.
   * The sixth line is `crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)`, which sets the `bio_P` attribute of 
   `crop_type` equal to its previous value times `1 - bio_frac`. 
   * The sevent line is similar: `crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)`. This sets `bio_N` to its
   previous value times `1 - bio_frac`
   * The eigth and final line of code in `cut()` is `crop_type.ET_annual = 0`, which simply sets the `ET_annual` 
   attribute to 0. 
5. So, we now know that `cut()` depends upon some specific attributes of `crop_type`. The function does not return
anything, it simply updates some attributes of the `crop_type` instance. We now know that:
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
   * is `accumulated_HU` properly calculated by `cut()`?
   * is `fr_PHU` properly calculated by `cut()`? 
   * is `LAI_actual` properly calculated by `cut()`? 
   * does `fr_LAI_max` equal 0 after running `cut()`?
   * is `biomass_actual` properly calculated by `cut()`? 
   * is `bio_P` properly calculated?
   * is `bio_N` properly calculated?
   * does `ET_annual` equal 0 after running `cut()`?
7. Let's write these tests in a new file. Let's decide to put all tests of the `yields.py` file in one single test file
called `tests/test_yields.py`. 
   * We start by importing relevant modules. We need the `crop.py` module to create our `crop_type` object and the 
   `yields.py` module for our function. We'll also import `MagicMock` and the `pytest` module:
   ```python
   from RUFAS.routines.field.crop.crop_types import base_crop
   from RUFAS.routines.field.crop.yields import cut
   from unittest.mock import MagicMock
   import pytest
   ```
   * Next we want to create our `crop_type` object by mocking the `BaseCrop` class. 
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
   This code creates and returns a mock crop object each time it is called.
   * Now we can write our first test, using pytest syntax. For that, all we need is to write a function that `assert`s
   that something is True. The first test will check that `cut()` correctly updates the `accumulated_HU` attribute. We
   want our tests to have long and very descriptive names that start with "test", so we'll call it 
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
8. The `test_yields.py` file should now contain this code:
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
9. Try writing the remaining tests on your own without looking at the code below. It will be good practice. 
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
10. After writing these 8 tests, there is one additional test to write. `cut()` is a side-effect function, meaning that 
it doesn't return anything. Instead, it changes the objects that were given as input. One potential problem with these
functions is that it can be hard to keep track of all the bits that have changed. Up until now, we've only tested
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
    It may be tempting to **only** include this last function, but if this test fails, you won't know where it fails.
    It is better to have individual tests separated.
11. Make sure to save these 9 tests in `test_yields.py`, and execute `pytest -v tests/test_yields.py` one last time
to make sure that the tests all passed. Then you can commit these changes and push it to the remote branch! 
12. Next add some tests for `calc_nutrient_removal()`, `calc_yield_act()`, `calc_yield_max()`,  `calc_dry_down()`,
`calc_HI_act()`, and `calc_HI_max()`. 
(from `yields.py`) into the `test_yields.py` file. 
    * Notice that you'll need to mock some additional crop attributes. These can be added directly to the 
    `mock_crop` function. 
    * Ignore `calc_quality_assessment()` and `calc_harvest_quality()`, since they don't do anything. 
    * you can also ignore `kill()` for now, unless you're comfortable also testing the 
    `FieldManagement.schedule_application()` function, which `kill()` calls (there's a mistake in the path diagram). 
    Or you can write some tests and a #TODO where further tests are needed.
13. Try writing some tests for `update_all()` too. Does it actually update all the attributes it is supposed to? What
should be different when `PHU` is > 1 vs when it is > 1? 
14. Move onto other low-level functions and work your way up. If you aren't confident in your ability to test a function,
skip it or ask for help. 
15. Make sure you create a list of all the tests you've written (and those that still need tests written). Also check
the `test_field.py` file to see which functionality has already been tested. 
16. You've got this!
