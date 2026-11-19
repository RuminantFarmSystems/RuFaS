# RuFaS Beef Feedlot Step 1 — Enums Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `FEEDLOT_STEER` and `FEEDLOT_HEIFER` members plus an `is_feedlot` property to `AnimalType`, and add `STEER` to the `Sex` enum, so the rest of the beef module can identify feedlot animals.

**Architecture:** Extends the existing `AnimalType` enum in `RUFAS/biophysical/animal/data_types/animal_types.py` with two new members and one boolean property, following the exact same pattern as the existing `is_heifer` and `is_cow` properties. Also extends the `Sex` enum in `animal_enums.py` with `STEER`, needed because feedlot nutrition equations distinguish steers from intact males and females. All changes are validated by tests written first (TDD, per RuFaS policy).

**Tech Stack:** Python 3.12+, pytest >= 9.0.3, Black, mypy (strict), Flake8

---

## File Map

| Action   | Path |
|----------|------|
| **Create** | `tests/test_biophysical/test_animal/test_feedlot/__init__.py` |
| **Create** | `tests/test_biophysical/test_animal/test_feedlot/conftest.py` |
| **Create** (write first!) | `tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py` |
| **Modify** | `RUFAS/biophysical/animal/data_types/animal_types.py` |
| **Modify** | `RUFAS/biophysical/animal/data_types/animal_enums.py` |
| **Modify** | `pyproject.toml` (add pytest markers) |
| **Modify** | `changelog.md` |

---

## Task 1: Create the feature branch

- [ ] **Step 1.1: Verify you are on rufas-cattle**

```bash
git status
git branch
```

Expected: current branch is `rufas-cattle`, working tree clean.

- [ ] **Step 1.2: Create and switch to the feature branch**

```bash
git checkout -b feature/beef-step-1-enums
git branch
```

Expected: `* feature/beef-step-1-enums` in output.

---

## Task 2: Add pytest markers to pyproject.toml

This must be done before running tests so pytest doesn't warn about unknown marks.

- [ ] **Step 2.1: Open `pyproject.toml` and replace the pytest section**

Current content in `pyproject.toml` (lines 66–67):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

Replace it with:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit test — single isolated function",
    "component: Component test — single class/module",
    "integration: Integration test — 2-3 modules together",
    "regression: Regression test — existing dairy suite",
    "validation: NRC 2016 validation against published benchmarks",
    "nrc2016: Specifically validates against NRC 2016 Chapter 20",
    "smoke: Import/instantiation smoke test",
    "slow: Takes > 5 seconds to run",
]
```

- [ ] **Step 2.2: Verify pyproject.toml is valid**

```bash
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('OK')"
```

Expected: `OK`

---

## Task 3: Create the test_feedlot directory and write the FAILING test (RED)

> **TDD mandate:** Write the test before touching `animal_types.py` or `animal_enums.py`. The test must fail first.

- [ ] **Step 3.1: Create the `test_feedlot` package directory**

Create `tests/test_biophysical/test_animal/test_feedlot/__init__.py` with empty content:

```python
```

(Empty file — just marks the directory as a Python package.)

- [ ] **Step 3.2: Create `conftest.py` with shared fixtures**

Create `tests/test_biophysical/test_animal/test_feedlot/conftest.py`:

```python
import pytest
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_enums import Sex


@pytest.fixture(scope="module")
def all_animal_types() -> list[AnimalType]:
    """All AnimalType enum members."""
    return list(AnimalType)


@pytest.fixture(scope="module")
def feedlot_types() -> list[AnimalType]:
    """Only the feedlot AnimalType members."""
    return [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER]


@pytest.fixture(scope="module")
def dairy_types() -> list[AnimalType]:
    """All non-feedlot AnimalType members."""
    return [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.DRY_COW,
        AnimalType.LAC_COW,
    ]
```

- [ ] **Step 3.3: Create `test_feedlot_enums.py` — write ALL tests now, before any implementation**

Create `tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py`:

```python
"""
Unit tests for feedlot-specific enum additions.

Tests are written before implementation (TDD). They verify:
- FEEDLOT_STEER and FEEDLOT_HEIFER exist in AnimalType
- is_feedlot property returns True for feedlot types, False for dairy types
- is_feedlot is mutually exclusive with is_heifer and is_cow
- Sex.STEER exists with value "steer"
"""

import pytest
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_enums import Sex


# ---------------------------------------------------------------------------
# AnimalType — new members
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_feedlot_steer_member_exists() -> None:
    """AnimalType.FEEDLOT_STEER must exist."""
    assert hasattr(AnimalType, "FEEDLOT_STEER")


@pytest.mark.unit
def test_feedlot_heifer_member_exists() -> None:
    """AnimalType.FEEDLOT_HEIFER must exist."""
    assert hasattr(AnimalType, "FEEDLOT_HEIFER")


@pytest.mark.unit
def test_feedlot_steer_value() -> None:
    """FEEDLOT_STEER value must be 'FeedlotSteer' (CamelCase, matching dairy convention)."""
    assert AnimalType.FEEDLOT_STEER.value == "FeedlotSteer"


@pytest.mark.unit
def test_feedlot_heifer_value() -> None:
    """FEEDLOT_HEIFER value must be 'FeedlotHeifer'."""
    assert AnimalType.FEEDLOT_HEIFER.value == "FeedlotHeifer"


# ---------------------------------------------------------------------------
# AnimalType.is_feedlot property — True for feedlot types
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER])
def test_is_feedlot_true_for_feedlot_types(animal_type: AnimalType) -> None:
    """is_feedlot must be True for FEEDLOT_STEER and FEEDLOT_HEIFER."""
    assert animal_type.is_feedlot is True


# ---------------------------------------------------------------------------
# AnimalType.is_feedlot property — False for all dairy types
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "dairy_type",
    [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.DRY_COW,
        AnimalType.LAC_COW,
    ],
)
def test_is_feedlot_false_for_dairy_types(dairy_type: AnimalType) -> None:
    """is_feedlot must be False for all existing dairy AnimalType members."""
    assert dairy_type.is_feedlot is False


# ---------------------------------------------------------------------------
# Mutual exclusivity — a feedlot animal is neither a heifer nor a cow
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER])
def test_feedlot_is_not_heifer(animal_type: AnimalType) -> None:
    """Feedlot types must NOT satisfy is_heifer — they are not dairy heifers."""
    assert animal_type.is_heifer is False


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER])
def test_feedlot_is_not_cow(animal_type: AnimalType) -> None:
    """Feedlot types must NOT satisfy is_cow — they are not dairy cows."""
    assert animal_type.is_cow is False


@pytest.mark.unit
def test_every_animal_type_has_is_feedlot() -> None:
    """is_feedlot property must exist on every AnimalType member (not just feedlot ones)."""
    for member in AnimalType:
        assert hasattr(member, "is_feedlot"), f"Missing is_feedlot on {member}"
        assert isinstance(member.is_feedlot, bool), f"is_feedlot not bool on {member}"


@pytest.mark.unit
def test_at_most_one_of_feedlot_heifer_cow_is_true() -> None:
    """For every AnimalType, at most one of is_feedlot/is_heifer/is_cow is True."""
    for member in AnimalType:
        flags = [member.is_feedlot, member.is_heifer, member.is_cow]
        assert sum(flags) <= 1, (
            f"{member}: more than one of is_feedlot/is_heifer/is_cow is True"
        )


# ---------------------------------------------------------------------------
# Sex enum — new STEER member
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sex_steer_member_exists() -> None:
    """Sex.STEER must exist for feedlot nutrition equations."""
    assert hasattr(Sex, "STEER")


@pytest.mark.unit
def test_sex_steer_value() -> None:
    """Sex.STEER value must be 'steer' (lowercase, matching existing male/female convention)."""
    assert Sex.STEER.value == "steer"


@pytest.mark.unit
def test_sex_steer_is_distinct_from_male() -> None:
    """STEER (castrated) must be a distinct Sex member from MALE (intact)."""
    assert Sex.STEER != Sex.MALE
```

- [ ] **Step 3.4: Run the tests — they MUST FAIL (red phase)**

```bash
pytest tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py -v
```

Expected output (all 14 tests fail with `AttributeError` or `ImportError`):
```
FAILED test_feedlot_enums.py::test_feedlot_steer_member_exists
FAILED test_feedlot_enums.py::test_feedlot_heifer_member_exists
...
14 failed, 0 passed
```

> **If any test passes at this point, stop.** It means the enum already exists or the test is wrong. Investigate before proceeding.

---

## Task 4: Implement the enum changes (GREEN)

- [ ] **Step 4.1: Modify `RUFAS/biophysical/animal/data_types/animal_types.py`**

Replace the entire file content with:

```python
from enum import Enum


class AnimalType(Enum):
    """The different types/subtypes of animals on a farm.

    Attributes
    ----------
    CALF : str
        A pre-weaned calf.
    HEIFER_I : str
        A heifer that is weaned but not yet bred.
    HEIFER_II : str
        A heifer that is either eligible for breeding (based on user-inputted Breeding Start Day for heifers),
        or in early pregnancy.
    HEIFER_III : str
        A close-up heifer (a heifer within the user-defined close-up period, i.e. Prefresh Day).
    DRY_COW : str
        A cow in the stage of their lactation cycle where milk production ceases prior to calving.
    LAC_COW : str
        A lactating cow.
    FEEDLOT_STEER : str
        A castrated male beef animal on a feedlot finishing programme.
    FEEDLOT_HEIFER : str
        A female beef animal on a feedlot finishing programme that has not calved.

    """

    CALF = "Calf"
    HEIFER_I = "HeiferI"
    HEIFER_II = "HeiferII"
    HEIFER_III = "HeiferIII"
    DRY_COW = "DryCow"
    LAC_COW = "LacCow"
    FEEDLOT_STEER = "FeedlotSteer"
    FEEDLOT_HEIFER = "FeedlotHeifer"

    @property
    def is_heifer(self) -> bool:
        """True if the animal is a dairy heifer, False otherwise."""
        return self in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III)

    @property
    def is_cow(self) -> bool:
        """True if the animal is a dairy cow, False otherwise."""
        return self in (AnimalType.DRY_COW, AnimalType.LAC_COW)

    @property
    def is_feedlot(self) -> bool:
        """True if the animal is a feedlot beef animal, False otherwise."""
        return self in (AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER)
```

- [ ] **Step 4.2: Modify `RUFAS/biophysical/animal/data_types/animal_enums.py`**

Replace the entire file content with:

```python
from enum import Enum


class Breed(Enum):
    """Enum indicating the breed of the animal."""

    HO = "Holstein"
    JE = "Jersey"


class Sex(Enum):
    """Enum indicating the sex of the animal."""

    MALE = "male"
    FEMALE = "female"
    STEER = "steer"


class AnimalStatus(Enum):
    """Enum indicating the status of the animal after performing daily routines update."""

    REMAIN = "remain"
    LIFE_STAGE_CHANGED = "life stage changed"
    DEAD = "dead"
    SOLD = "sold"
```

- [ ] **Step 4.3: Run the feedlot enum tests — they MUST PASS (green phase)**

```bash
pytest tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py -v
```

Expected:
```
PASSED test_feedlot_enums.py::test_feedlot_steer_member_exists
PASSED test_feedlot_enums.py::test_feedlot_heifer_member_exists
...
14 passed, 0 failed
```

> **If any test still fails, fix the implementation before proceeding. Do NOT move on with a failing test.**

---

## Task 5: Run regression tests (dairy suite)

- [ ] **Step 5.1: Run the data_types regression suite**

```bash
pytest tests/test_biophysical/test_animal/test_data_types/ -v --tb=short
```

Expected: **0 failures, 0 errors.** This suite exercises the existing `is_heifer` and `is_cow` logic. The new `is_feedlot` property must not break it.

- [ ] **Step 5.2: Run the full test suite excluding feedlot (full dairy regression)**

```bash
pytest tests/ -k "not test_feedlot" --tb=short -q
```

Expected: same number of passes as before this branch was created, 0 failures, 0 errors.

> If any non-feedlot test fails, investigate. The most likely cause is a circular import or a test that iterates over all AnimalType members and doesn't expect the new feedlot ones. Fix before proceeding.

---

## Task 6: Code quality checks

- [ ] **Step 6.1: Black formatting**

```bash
black RUFAS/biophysical/animal/data_types/animal_types.py RUFAS/biophysical/animal/data_types/animal_enums.py tests/test_biophysical/test_animal/test_feedlot/
```

Expected: `reformatted` or `1 file left unchanged` for each file. Re-run `pytest` if Black changed anything (it shouldn't, but confirm).

- [ ] **Step 6.2: mypy type check**

```bash
python -m mypy RUFAS/biophysical/animal/data_types/animal_types.py RUFAS/biophysical/animal/data_types/animal_enums.py tests/test_biophysical/test_animal/test_feedlot/
```

Expected: `Success: no issues found` (or the same error count as on `dev-msf` before this branch — do NOT increase the error count).

- [ ] **Step 6.3: Flake8 lint**

```bash
flake8 RUFAS/biophysical/animal/data_types/animal_types.py RUFAS/biophysical/animal/data_types/animal_enums.py tests/test_biophysical/test_animal/test_feedlot/
```

Expected: no output (zero violations).

---

## Task 7: Update changelog and commit

- [ ] **Step 7.1: Add a changelog entry to `changelog.md`**

Open `changelog.md` and add the following entry under `## Changelog Entries` (PR number will be filled in after the PR is opened — use `TBD` for now):

```markdown
- [TBD](TBD) - [minor change] [Animal Module] Add FEEDLOT_STEER and FEEDLOT_HEIFER to AnimalType enum and is_feedlot property; add Sex.STEER. Foundational enums for the beef feedlot module (Step 1 of 8).
```

- [ ] **Step 7.2: Stage and commit all changes**

```bash
git add \
  RUFAS/biophysical/animal/data_types/animal_types.py \
  RUFAS/biophysical/animal/data_types/animal_enums.py \
  tests/test_biophysical/test_animal/test_feedlot/__init__.py \
  tests/test_biophysical/test_animal/test_feedlot/conftest.py \
  tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py \
  pyproject.toml \
  changelog.md

git commit -m "feat(enums): add FEEDLOT_STEER/FEEDLOT_HEIFER to AnimalType and Sex.STEER

- AnimalType.FEEDLOT_STEER = 'FeedlotSteer'
- AnimalType.FEEDLOT_HEIFER = 'FeedlotHeifer'
- AnimalType.is_feedlot property (mutually exclusive with is_heifer, is_cow)
- Sex.STEER = 'steer'
- 14 unit tests, all passing (TDD)
- Dairy regression suite: 0 failures

Step 1 of 8 — beef feedlot module."
```

---

## Task 8: Push and open the Pull Request

- [ ] **Step 8.1: Push the feature branch**

```bash
git push -u origin feature/beef-step-1-enums
```

- [ ] **Step 8.2: Open the PR targeting `rufas-cattle`**

```bash
gh pr create \
  --base rufas-cattle \
  --title "feat(enums): Step 1 — feedlot AnimalType members and is_feedlot property" \
  --body "## Summary
- Adds \`AnimalType.FEEDLOT_STEER\` and \`AnimalType.FEEDLOT_HEIFER\` to the \`AnimalType\` enum.
- Adds \`AnimalType.is_feedlot\` boolean property (same pattern as \`is_heifer\`/\`is_cow\`; mutually exclusive with both).
- Adds \`Sex.STEER\` to the \`Sex\` enum (castrated males distinct from intact \`MALE\`).
- 14 unit tests in \`tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py\`.
- pytest markers added to \`pyproject.toml\`.
- Zero regressions in the existing dairy test suite.

## Checklist
- [ ] Tests pass: \`pytest tests/test_biophysical/test_animal/test_feedlot/test_feedlot_enums.py\`
- [ ] Dairy regression: \`pytest tests/ -k 'not test_feedlot' -q\`
- [ ] Black formatted
- [ ] mypy clean
- [ ] flake8 clean
- [ ] changelog.md updated

## NRC 2016 context
These enums are Step 1 of 8 in the beef feedlot module. \`AnimalType.is_feedlot\` is the gate check used by every downstream beef calculator; nothing else can be built until it exists."
```

- [ ] **Step 8.3: Copy the PR URL and update the changelog entry**

Replace `TBD` in `changelog.md` with the actual PR number and URL from the output of the previous step, then amend the commit:

```bash
git add changelog.md
git commit --amend --no-edit
git push --force-with-lease origin feature/beef-step-1-enums
```

---

## Self-Review Checklist

- [x] **Spec coverage:** TDD golden rule (write test first → fail → implement → pass) — covered in Tasks 3–4.
  `AnimalType.FEEDLOT_STEER` ✅ Task 3/4 | `AnimalType.FEEDLOT_HEIFER` ✅ | `is_feedlot` ✅ | `Sex.STEER` ✅
- [x] **Regression gate:** dairy data_types suite + full `-k "not test_feedlot"` suite — Task 5.
- [x] **Quality gate:** Black + mypy + flake8 — Task 6.
- [x] **Changelog required by CI** — Task 7.
- [x] **Placeholder scan:** All steps contain actual code; no TBDs in the implementation steps.
- [x] **Type consistency:** `is_feedlot` returns `bool` (matching `is_heifer`/`is_cow`). Property names consistent across conftest, test file, and implementation.
