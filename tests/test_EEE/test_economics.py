from pytest_mock import MockerFixture
import pandas as pd
import math
import numpy as np
import pytest

from RUFAS.EEE.economics.framework import EconomicFramework
from RUFAS.EEE.economics.metrics import (
    calculate_roi,
    calculate_payback_period,
    calculate_net_annual_cash_flow,
    calculate_mpsp,
)
from RUFAS.EEE.economics.digester_costs import (
    calculate_digester_capital_cost,
    capital_recovery_factor,
    scale_installed_cost,
    calculate_digester_capex,
    calculate_digester_operational_cost,
)
from RUFAS.EEE.economics.equations import (
    construct_timeline,
    discount_factor,
    annual_capital_spent,
    loan_principal,
    construction_interest,
    npv_capital_plus_interest,
    annual_loan_payment,
    interest_payment,
    principal_after_payment,
    depreciation_schedule,
    net_revenue,
    loss_carry_forward,
    taxable_income,
    income_tax,
    annual_cash_income,
    present_value,
    net_present_value,
)


def test_run_economic_analysis_uses_dcfror_when_capital_present(
    mocker: MockerFixture,
) -> None:
    im_cls = mocker.patch("RUFAS.EEE.economics.framework.InputManager")
    im_cls.return_value.get_data.return_value = pd.DataFrame({"Cost": [100]})
    mock_calc_cls = mocker.patch("RUFAS.EEE.economics.framework.DCFRORCalculator")
    mock_partial_budget_cls = mocker.patch("RUFAS.EEE.economics.framework.PartialBudget")
    mock_partial_budget_cls.return_value.has_partial_budget_activity.return_value = False

    EconomicFramework.run()

    mock_calc_cls.assert_called_once_with()
    mock_calc_cls.return_value.calculate.assert_called_once_with()


def test_run_economic_analysis_uses_pba_when_no_capital(mocker: MockerFixture) -> None:
    im_cls = mocker.patch("RUFAS.EEE.economics.framework.InputManager")
    im_cls.return_value.get_data.return_value = pd.DataFrame({"Cost": [0]})
    mock_partial_budget_cls = mocker.patch("RUFAS.EEE.economics.framework.PartialBudget")
    mock_partial_budget = mock_partial_budget_cls.return_value
    mock_partial_budget.has_partial_budget_activity.return_value = True

    EconomicFramework.run()

    mock_partial_budget.calculate_partial_budget.assert_called_once_with()


def test_calculate_roi() -> None:
    assert calculate_roi(150.0, 100.0) == 50.0


def test_calculate_payback_period() -> None:
    cash_flows = [-50, 20, 20, 20]
    assert calculate_payback_period(cash_flows) == 2.5


def test_calculate_net_annual_cash_flow() -> None:
    result = calculate_net_annual_cash_flow([100, 120], [80, 90])
    assert result.tolist() == [20, 30]


def test_calculate_mpsp() -> None:
    assert calculate_mpsp(100.0, 50.0) == 2.0


def test_calculate_digester_capital_cost() -> None:
    result = calculate_digester_capital_cost(
        alpha=1.0,
        r1=0.5,
        r2=0.3,
        area=10.0,
        volume=20.0,
        psi1=0.1,
        psi2=0.2,
        psi3=0.05,
        psi4=0.07,
        f_j=1.0,
        g_j=0.0,
        c_j=1.0,
        s_j=0.0,
    )
    expected = math.exp(
        1.0 + 0.5 * math.log(10.0) + 0.3 * math.log(20.0) + 0.1 * 1.0 + 0.2 * 0.0 + 0.05 * 1.0 + 0.07 * 0.0
    )
    assert result == expected


def test_capital_recovery_factor() -> None:
    result = capital_recovery_factor(0.05, 10)
    expected = 0.05 * (1 + 0.05) ** 10 / ((1 + 0.05) ** 10 - 1)
    assert pytest.approx(result, rel=1e-6) == expected


def test_scale_installed_cost() -> None:
    assert scale_installed_cost(1000.0, 150.0, 100.0, 0.6) == pytest.approx(1000.0 * (150.0 / 100.0) ** 0.6)


def test_calculate_digester_capex() -> None:
    crf = capital_recovery_factor(0.05, 20)
    afc = 5000.0
    assert calculate_digester_capex(afc, crf) == pytest.approx(afc / crf)


def test_calculate_digester_operational_cost() -> None:
    result = calculate_digester_operational_cost(
        tau=2.0,
        beta=1.0,
        omega1=0.3,
        area=10.0,
        phi1=0.1,
        phi2=0.2,
        phi3=0.05,
        phi4=0.07,
        f_j=1.0,
        g_j=0.0,
        c_j=1.0,
        s_j=0.0,
    )
    expected = 2.0 * math.exp(1.0 + 0.3 * math.log(10.0) + 0.1 * 1.0 + 0.2 * 0.0 + 0.05 * 1.0 + 0.07 * 0.0)
    assert pytest.approx(result) == expected


def test_equation_helpers() -> None:
    years = construct_timeline(2, 5)
    assert years.tolist() == [-1, 0, 1, 2, 3, 4, 5]

    df = discount_factor(0.1, 2)
    assert pytest.approx(df) == 1 / (1.1**2)

    cap = annual_capital_spent(100.0, [0.5, 0.5])
    assert cap.tolist() == [50.0, 50.0]

    lp = loan_principal(cap, 0.6)
    assert lp.tolist() == [30.0, 30.0]

    ci = construction_interest(lp, 0.05)
    assert ci.tolist() == [1.5, 1.5]

    npv_ci = npv_capital_plus_interest(cap, ci, 0.1, np.array([-1, 0]))
    expected_npv = (cap + ci) * np.array([discount_factor(0.1, -1), discount_factor(0.1, 0)])
    assert np.allclose(npv_ci, expected_npv)

    payment = annual_loan_payment(1000.0, 0.05, 5, 0.8)
    expected_payment = 1000.0 * 0.05 * 0.8 / (1 - (1 + 0.05) ** -5)
    assert pytest.approx(payment) == expected_payment

    int_pay = interest_payment(800.0, 0.05)
    assert pytest.approx(int_pay) == 40.0

    remaining = principal_after_payment(800.0, payment, int_pay)
    assert pytest.approx(remaining) == 800.0 - payment + int_pay

    dep = depreciation_schedule(1000.0, np.array([0.1, 0.2]))
    assert dep.tolist() == [100.0, 200.0]

    nr = net_revenue(500.0, 200.0, 30.0, 20.0)
    assert nr == 250.0

    loss = loss_carry_forward(-50.0)
    assert loss == -50.0

    taxable = taxable_income(nr, loss)
    assert taxable == 200.0

    tax = income_tax(taxable, 0.3)
    assert tax == 60.0

    aci = annual_cash_income(500.0, 200.0, 50.0, tax)
    assert aci == 190.0

    pv = present_value(aci, discount_factor(0.1, 1))
    assert pytest.approx(pv) == aci / 1.1

    npv = net_present_value(np.array([pv]), np.array([10.0]))
    assert pytest.approx(npv) == pv - 10.0
