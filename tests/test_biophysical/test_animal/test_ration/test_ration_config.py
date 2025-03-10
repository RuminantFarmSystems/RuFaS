from __future__ import annotations

import pytest
from pytest import approx

from RUFAS.biophysical.animal.ration.ration_config import RationConfig


def test_default_initialization() -> None:
    """
    Test the default initialization of the RationConfig class.

    This test checks that when a RationConfig object is instantiated without
    any parameters, all its attributes are correctly set to their default values.
    """
    # Act
    ration_config = RationConfig()

    # Assert
    assert ration_config.price_list == []
    assert ration_config.NEmaint_requirement == 0
    assert ration_config.NEa_requirement == 0
    assert ration_config.NEpreg_requirement == 0
    assert ration_config.NEl_requirement == 0
    assert ration_config.NEg_requirement == 0
    assert ration_config.MP_requirement == 0
    assert ration_config.C_requirement == 0
    assert ration_config.P_requirement == 0
    assert ration_config.TDN_list == []
    assert ration_config.DE_list == []
    assert ration_config.EE_list == []
    assert ration_config.is_fat_list == []
    assert ration_config.BW == approx(0)
    assert ration_config.calcium_list == []
    assert ration_config.phosphorus_list == []
    assert ration_config.NDF_list == []
    assert ration_config.feed_type_list == []
    assert ration_config.is_wetforage_list == []
    assert ration_config.Kd_list == []
    assert ration_config.N_A_list == []
    assert ration_config.N_B_list == []
    assert ration_config.CP_list == []
    assert ration_config.dRUP_list == []
    assert ration_config.feed_limit_list == []
    assert not ration_config.lactating
    assert ration_config.DMIest_requirement == 0.0


@pytest.mark.parametrize(
    "price, NEmaint, NEa, NEpreg, NEl, NEg,"
    "MP_req, C_req, P_req, TDN, DE, EE,"
    "is_fat, BW, calcium, phosphorus, NDF, type_input,"
    "is_wetforage, Kd, N_A, N_B, CP, dRUP,"
    "limit, lactating, DMIest",
    [
        # Default values
        (
            [],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            [],
            [],
            [],
            [],
            0,
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            False,
            None,
        ),
        # Custom values
        (
            [1, 2],
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            [11, 12],
            [13, 14],
            [15, 16],
            [True, False],
            17,
            [18, 19],
            [20, 21],
            [22, 23],
            [24, 25],
            [True, False],
            [26, 27],
            [28, 29],
            [30, 31],
            [32, 33],
            [34, 35],
            [36, 37],
            True,
            38,
        ),
    ],
)
def test_custom_initialization(
    price: list[float],
    NEmaint: float,
    NEa: float,
    NEpreg: float,
    NEl: float,
    NEg: float,
    MP_req: float,
    C_req: float,
    P_req: float,
    TDN: list[float],
    DE: list[float],
    EE: list[float],
    is_fat: list[bool],
    BW: float,
    calcium: list[float],
    phosphorus: list[float],
    NDF: list[float],
    type_input: list[str],
    is_wetforage: list[bool],
    Kd: list[float],
    N_A: list[float],
    N_B: list[float],
    CP: list[float],
    dRUP: list[float],
    limit: list[float],
    lactating: bool,
    DMIest: float,
) -> None:
    """
    Test the initialization of the RationConfig class with custom values.

    This test verifies that all attributes are correctly initialized based on the provided values.
    """

    # Act
    ration_config = RationConfig(
        price__list=price,
        NEmaint__requirement=NEmaint,
        NEa__requirement=NEa,
        NEpreg__requirement=NEpreg,
        NEl__requirement=NEl,
        NEg__requirement=NEg,
        MP__requirement=MP_req,
        C__requirement=C_req,
        P__requirement=P_req,
        TDN__list=TDN,
        DE__list=DE,
        EE__list=EE,
        is_fat__list=is_fat,
        BW_=BW,
        calcium__list=calcium,
        phosphorus__list=phosphorus,
        NDF__list=NDF,
        feed_type__list=type_input,
        is_wetforage__list=is_wetforage,
        Kd__list=Kd,
        N_A__list=N_A,
        N_B__list=N_B,
        CP__list=CP,
        dRUP__list=dRUP,
        feed_limit__list=limit,
        lactating_=lactating,
        DMIest__requirement=DMIest,
    )

    # Assert
    assert ration_config.price_list == price
    assert ration_config.NEmaint_requirement == NEmaint
    assert ration_config.NEa_requirement == NEa
    assert ration_config.NEpreg_requirement == NEpreg
    assert ration_config.NEl_requirement == NEl
    assert ration_config.NEg_requirement == NEg
    assert ration_config.MP_requirement == MP_req
    assert ration_config.C_requirement == C_req
    assert ration_config.P_requirement == P_req
    assert ration_config.TDN_list == TDN
    assert ration_config.DE_list == DE
    assert ration_config.EE_list == EE
    assert ration_config.is_fat_list == is_fat
    assert ration_config.BW == approx(BW)
    assert ration_config.calcium_list == calcium
    assert ration_config.phosphorus_list == phosphorus
    assert ration_config.NDF_list == NDF
    assert ration_config.feed_type_list == type_input
    assert ration_config.is_wetforage_list == is_wetforage
    assert ration_config.Kd_list == Kd
    assert ration_config.N_A_list == N_A
    assert ration_config.N_B_list == N_B
    assert ration_config.CP_list == CP
    assert ration_config.dRUP_list == dRUP
    assert ration_config.feed_limit_list == limit
    assert ration_config.lactating == lactating
    assert ration_config.DMIest_requirement == DMIest
