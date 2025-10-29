from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from RUFAS.EEE.economics.digester_costs import (
    DigesterCostCalculator,
    DigesterSystemCostProfile,
    LinearCostEquation,
)
from RUFAS.EEE.economics.equations import EconomicEquations
from RUFAS.EEE.economics.framework import EconomicFramework
from RUFAS.EEE.economics.metrics import EconomicMetrics


def test_run_economic_analysis_uses_dcfror_when_capital_present(
    mocker: MockerFixture,
) -> None:
    im_cls = mocker.patch("RUFAS.EEE.economics.framework.InputManager")
    im_cls.return_value.get_data.return_value = pd.DataFrame({"Cost": [100]})
    mock_calc_cls = mocker.patch("RUFAS.EEE.economics.framework.DCFRORCalculator")

    run_economic_analysis()

    mock_calc_cls.assert_called_once_with()
    mock_calc_cls.return_value.calculate.assert_called_once_with()
    mock_partial_budget_cls.return_value.calculate_partial_budget.assert_not_called()


def test_run_economic_analysis_uses_pba_when_no_capital(mocker: MockerFixture) -> None:
    im_cls = mocker.patch("RUFAS.EEE.economics.framework.InputManager")
    im_cls.return_value.get_data.return_value = pd.DataFrame({"Cost": [0]})
    mock_pba = mocker.patch("RUFAS.EEE.economics.framework.calculate_partial_budget")

    run_economic_analysis()

    mock_pba.assert_called_once_with()


def test_calculate_roi() -> None:
    assert EconomicMetrics.calculate_roi(150.0, 100.0) == 50.0


def test_calculate_payback_period() -> None:
    cash_flows = [-50, 20, 20, 20]
    assert EconomicMetrics.calculate_payback_period(cash_flows) == 2.5


def test_calculate_net_annual_cash_flow() -> None:
    result = EconomicMetrics.calculate_net_annual_cash_flow([100, 120], [80, 90])
    assert result.tolist() == [20, 30]


def test_calculate_mpsp() -> None:
    assert math.isnan(EconomicMetrics.calculate_mpsp(100.0, 50.0))


def test_calculate_digester_capital_cost() -> None:
    result = DigesterCostCalculator.calculate_digester_capital_cost(
        animal_units=10.0,
        digester_volume=20.0,
        farm_type_flag=1.0,
        below_ground_flag=0.0,
        concrete_flag=1.0,
        steel_flag=0.0,
        alpha=1.0,
        r1=0.5,
        r2=0.3,
        psi1=0.1,
        psi2=0.2,
        psi3=0.05,
        psi4=0.07,
        epsilon=0.0,
    )
    assert legacy == expected


def test_capital_recovery_factor() -> None:
    result = DigesterCostCalculator.capital_recovery_factor(0.05, 10)
    expected = 0.05 * (1 + 0.05) ** 10 / ((1 + 0.05) ** 10 - 1)
    assert pytest.approx(result, rel=1e-6) == expected


def test_scale_installed_cost() -> None:
    assert DigesterCostCalculator.scale_installed_cost(1000.0, 150.0, 100.0, 0.6) == pytest.approx(
        1000.0 * (150.0 / 100.0) ** 0.6
    )


def test_calculate_digester_capex() -> None:
    crf = DigesterCostCalculator.capital_recovery_factor(0.05, 20)
    afc = 5000.0
    assert DigesterCostCalculator.calculate_digester_capex(afc, crf) == pytest.approx(afc / crf)


def test_calculate_digester_operational_cost() -> None:
    result = DigesterCostCalculator.calculate_digester_operational_cost(
        True,
        animal_units=10.0,
        farm_type_flag=1.0,
        below_ground_flag=0.0,
        concrete_flag=1.0,
        steel_flag=0.0,
        beta=1.0,
        omega1=0.3,
        phi1=0.1,
        phi2=0.2,
        phi3=0.05,
        phi4=0.07,
        epsilon=0.0,
    )
    expected = math.exp(1.0 + 0.3 * math.log(10.0) + 0.1 * 1.0 + 0.2 * 0.0 + 0.05 * 1.0 + 0.07 * 0.0)
    assert pytest.approx(result) == expected

    assert (
        DigesterCostCalculator.calculate_digester_operational_cost(
            False,
            animal_units=10.0,
            farm_type_flag=1.0,
            below_ground_flag=1.0,
            concrete_flag=1.0,
            steel_flag=0.0,
        )
        == 0.0
    )


def test_estimate_digester_costs_linear_equations() -> None:
    estimates = DigesterCostCalculator.estimate_digester_costs("Covered Lagoon - RNG", 1000)

    assert pytest.approx(estimates["capital_expenditure"]) == 875 * 1000 + 625_000

    operating = estimates["operating_costs"]
    assert pytest.approx(operating["labor"]) == 94.5 * 1000 + 67_500
    assert pytest.approx(operating["energy"]) == 34.80 * 1000 + 21.0
    assert pytest.approx(operating["repairs"]) == 66.69 * 1000 + 40.25

    assert estimates["useful_life_years"] == 20
    assert pytest.approx(estimates["salvage_value_fraction"]) == 0.15
    assert pytest.approx(estimates["biogas_yield_ft3_per_cow_day"]) == 72.0
    assert pytest.approx(estimates["methane_content_fraction"]) == 0.6


def test_get_digester_cost_profile_normalizes_names() -> None:
    profile = DigesterCostCalculator.get_digester_cost_profile("plug flow chp")

    assert pytest.approx(profile.capital_cost(5000)) == 2_625 * 5000 + 2_000_000
    operating = profile.annual_operating_costs(5000)
    assert pytest.approx(operating["labor"]) == 75 * 5000 + 45_000
    assert pytest.approx(operating["energy"]) == 12.5 * 5000 + 7_500
    assert pytest.approx(operating["repairs"]) == 37.5 * 5000 + 22_500


def test_estimate_digester_trucking_cost() -> None:
    assert pytest.approx(DigesterCostCalculator.estimate_digester_trucking_cost(1000)) == 137.5 * 1000
    assert pytest.approx(DigesterCostCalculator.estimate_digester_trucking_cost(5000)) == 137.5 * 5000


def test_equation_helpers() -> None:
    years = EconomicEquations.construct_timeline(2, 5)
    assert years.tolist() == [-1, 0, 1, 2, 3, 4, 5]

    df = EconomicEquations.discount_factor(0.1, 2)
    assert pytest.approx(df) == 1 / (1.1**2)
    assert pytest.approx(EconomicEquations.discount_factor(0.1, -1)) == 1 / 1.1

    construction_rates = [0.5, 0.5]
    cap = EconomicEquations.annual_capital_spent(100.0, construction_rates)
    assert cap.tolist() == [50.0, 50.0]

    equity = EconomicEquations.equity_contribution(100.0, construction_rates, 0.4)
    assert equity.tolist() == [20.0, 20.0]

    lp = EconomicEquations.loan_principal(100.0, construction_rates, 0.6)
    assert lp.tolist() == [30.0, 30.0]

    ci = EconomicEquations.construction_interest(lp, 0.05)
    assert ci.tolist() == [1.5, 3.0]

    npv_ci = EconomicEquations.npv_capital_plus_interest(cap, ci, 0.1, np.array([-1, 0]))
    expected_npv = (cap + ci) * np.array(
        [
            EconomicEquations.discount_factor(0.1, -1),
            EconomicEquations.discount_factor(0.1, 0),
        ]
    )
    assert np.allclose(npv_ci, expected_npv)

    payment = EconomicEquations.annual_loan_payment(1000.0, 0.05, 5, 0.8)
    expected_payment = 1000.0 * 0.05 * 0.8 / (1 - (1 + 0.05) ** -5)
    assert pytest.approx(payment) == expected_payment

    int_pay = EconomicEquations.interest_payment(800.0, 0.05)
    assert pytest.approx(int_pay) == 40.0

    remaining = EconomicEquations.principal_after_payment(800.0, payment, int_pay)
    assert pytest.approx(remaining) == 800.0 - payment + int_pay

    dep = EconomicEquations.depreciation_schedule(1000.0, np.array([0.1, 0.2]))
    assert dep.tolist() == [100.0, 200.0]

    nr = EconomicEquations.net_revenue(500.0, 200.0, 30.0, 20.0)
    assert nr == 250.0

    loss = EconomicEquations.loss_carry_forward(-50.0)
    assert loss == -50.0

    taxable = EconomicEquations.taxable_income(nr, loss)
    assert taxable == 200.0

    tax = EconomicEquations.income_tax(taxable, 0.3)
    assert tax == 60.0

    aci = EconomicEquations.annual_cash_income(500.0, 200.0, 50.0, tax)
    assert aci == 190.0

    pv = EconomicEquations.present_value(aci, EconomicEquations.discount_factor(0.1, 1))
    assert pytest.approx(pv) == aci / 1.1

    npv = EconomicEquations.net_present_value(np.array([pv]), np.array([10.0]))
    assert pytest.approx(npv) == pv - 10.0
