# tests/ — pytest conventions

`pytest` (config in `pyproject.toml`: `testpaths = ["tests"]`). Coverage via
`.github/.coveragerc` (omits `__init__.py`).

## Layout — mirror `RUFAS/`

- Root modules → `tests/test_<module>.py`
  (e.g. `RUFAS/simulation_engine.py` → `tests/test_simulation_engine.py`).
- Packages → `tests/test_<package>/` mirroring the source tree:
  - `tests/test_biophysical/` → `test_animal/`, `test_crop_soil_field/`,
    `test_feed_storage/`, `test_manure/`
  - `tests/test_EEE/`, `tests/test_data_structures/`
- Note `RUFAS/rufas_time.py` → `tests/test_time.py` (name differs).

## Patterns

- **Mocking**: `mocker.patch.object(Cls, "attr", ...)` ONLY — never string-path
  `mocker.patch("pkg.mod.Name")` / `with patch("...")`, never direct assignment
  `Class.method = MagicMock()`. Prefer patching estimator/manager methods over
  rewiring whole objects.
- **Mock only reachable states** — when stubbing an internal helper's return
  value, feed it only states the production code can actually produce (check
  what the real callee can return before writing the stub). A green test on an
  unreachable state validates dead code and hides it from review.
- **Floats**: compare with `pytest.approx(...)`, never `==` — even for
  pass-through or literal-zero values. Justify the tolerance by the reference
  value's origin (`rel=1e-6` algebraic identity; `rel=0.03`–`0.05` published /
  validation-workbook value).
- **Fixtures**: per-package fixture modules (e.g. `tests/test_EEE/fixtures.py`),
  imported explicitly into test files. If two test files in the same package
  build the same object (`__new__` + attribute-list builders), move the builder
  into that package's `fixtures.py` instead of copying it. `pytest-lazy-fixtures` is available — use
  `from pytest_lazy_fixtures import lf` to reference a fixture inside
  `@pytest.mark.parametrize` (the maintained successor of `pytest-lazy-fixture`,
  which broke on pytest ≥ 8).
- **Time**: freeze with `freezegun` when exercising `RUFAS/rufas_time.py` or
  date-dependent logic.
- Tests commonly build real `InputManager()` / `OutputManager()` and patch the
  unit under test.
- Full type annotations on test functions and fixtures (mypy strict applies to
  `tests/` too — see `pyproject.toml` mypy `exclude`).

## What to cover (RuFaS code-review rule)

- **Every modified/added function needs a unit test** + a NumPy-style docstring.
- The suite must cover **normal operation, edge cases, AND invalid inputs** — not
  just the happy path. See the
  [Code review](https://github.com/RuminantFarmSystems/RuFaS/wiki/Code-review) wiki.
- **Patch via `mocker.patch.object` only** (see Patterns above) — direct
  class-attribute assignment leaks across tests (no teardown) and breaks under
  pytest's collection order; string-path patches silently break on refactors.
- **One benchmark scenario = one home** — never pin the same reference value
  (e.g. an NRC scenario) in two test files: duplicated pins drift and their
  derivation comments contradict each other. Before adding a `*_benchmarks.py`
  file, fold the scenarios into the existing calculator test file. Pin expected
  values as named module attributes with unit + conditions, and cite the source
  workbook by filename in the module header. Before committing a derivation
  comment, verify it actually reproduces the pinned value — a wrong derivation
  next to a right pin poisons future reviews.

## End-to-end (E2E) tests

Beyond unit tests, RuFaS freezes expected model outputs per domain and compares
on each run (guards against unintended output changes). Run:

```
python main.py -p input/metadata/end_to_end_testing_tm_metadata.json
```

Setting up a new domain or updating expected results has a human-in-the-loop
guard — use the **`rufas-e2e-testing`** skill (it mirrors the wiki procedure).
A deliberate output change → mark the PR `[OutputChange]`.

## Running

```
pytest                                   # all unit/integration
pytest tests/test_EEE/test_energy.py     # one file
pytest tests/test_units.py::test_x       # one test
coverage run --rcfile=.github/.coveragerc && coverage report
```

Don't lower coverage or add new mypy errors — CI ratchets both against `dev`.
