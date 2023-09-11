from __future__ import annotations

import pytest
from pytest import approx

from RUFAS.routines.animal.ration.ration_config import RationConfig


def test_default_initialization():
    """
    Test the default initialization of the RationConfig class.

    This test checks that when a RationConfig object is instantiated without
    any parameters, all its attributes are correctly set to their default values.
    """
    # Act
    ration_config = RationConfig()

    # Assert
    assert ration_config.price == []
    assert ration_config.n == 0
    assert ration_config.NEmaint == 0
    assert ration_config.NEa == 0
    assert ration_config.NEpreg == 0
    assert ration_config.NEl == 0
    assert ration_config.NEg == 0
    assert ration_config.MP_req == 0
    assert ration_config.C_req == 0
    assert ration_config.P_req == 0
    assert ration_config.TDN == []
    assert ration_config.DE == []
    assert ration_config.EE == []
    assert ration_config.is_fat == []
    assert ration_config.BW == approx(0)
    assert ration_config.calcium == []
    assert ration_config.phosphorus == []
    assert ration_config.NDF == []
    assert ration_config.type == []
    assert ration_config.is_wetforage == []
    assert ration_config.Kd == []
    assert ration_config.N_A == []
    assert ration_config.N_B == []
    assert ration_config.CP == []
    assert ration_config.dRUP == []
    assert ration_config.limit == []
    assert not ration_config.cow_type
    assert ration_config.DMIest is None


@pytest.mark.parametrize(
    'price, NEmaint, NEa, NEpreg, NEl, NEg,'
    'MP_req, C_req, P_req, TDN, DE, EE,'
    'is_fat, BW, calcium, phosphorus, NDF, type_input,'
    'is_wetforage, Kd, N_A, N_B, CP, dRUP,'
    'limit, cow_type, DMIest',
    [
        # Default values
        ([], 0, 0, 0, 0, 0,
         0, 0, 0, [], [], [],
         [], 0, [], [], [], [],
         [], [], [], [], [], [],
         [], False, None),

        # Custom values
        ([1, 2], 3, 4, 5, 6, 7,
         8, 9, 10, [11, 12], [13, 14], [15, 16],
         [True, False], 17, [18, 19], [20, 21], [22, 23], [24, 25],
         [True, False], [26, 27], [28, 29], [30, 31], [32, 33], [34, 35],
         [36, 37], True, 38),
    ],
)
def test_custom_initialization(price: list[float], NEmaint: float, NEa: float, NEpreg: float, NEl: float, NEg: float,
                               MP_req: float, C_req: float, P_req: float, TDN: list[float], DE: list[float],
                               EE: list[float], is_fat: list[bool], BW: float, calcium: list[float],
                               phosphorus: list[float], NDF: list[float], type_input: list[str],
                               is_wetforage: list[bool], Kd: list[float], N_A: list[float], N_B: list[float],
                               CP: list[float], dRUP: list[float], limit: list[float], cow_type: bool, DMIest: float) \
        -> None:
    """
    Test the initialization of the RationConfig class with custom values.

    This test verifies that all attributes are correctly initialized based on the provided values.
    """

    # Act
    ration_config = RationConfig(
        price_=price,
        NEmaint_=NEmaint,
        NEa_=NEa,
        NEpreg_=NEpreg,
        NEl_=NEl,
        NEg_=NEg,
        MP_req_=MP_req,
        C_req_=C_req,
        P_req_=P_req,
        TDN_=TDN,
        DE_=DE,
        EE_=EE,
        is_fat_=is_fat,
        BW_=BW,
        calcium_=calcium,
        phosphorus_=phosphorus,
        NDF_=NDF,
        type_=type_input,
        is_wetforage_=is_wetforage,
        Kd_=Kd,
        N_A_=N_A,
        N_B_=N_B,
        CP_=CP,
        dRUP_=dRUP,
        limit_=limit,
        cow_type_=cow_type,
        DMIest_=DMIest,
    )

    # Assert
    assert ration_config.price == price
    assert ration_config.n == len(price)
    assert ration_config.NEmaint == NEmaint
    assert ration_config.NEa == NEa
    assert ration_config.NEpreg == NEpreg
    assert ration_config.NEl == NEl
    assert ration_config.NEg == NEg
    assert ration_config.MP_req == MP_req
    assert ration_config.C_req == C_req
    assert ration_config.P_req == P_req
    assert ration_config.TDN == TDN
    assert ration_config.DE == DE
    assert ration_config.EE == EE
    assert ration_config.is_fat == is_fat
    assert ration_config.BW == approx(BW)
    assert ration_config.calcium == calcium
    assert ration_config.phosphorus == phosphorus
    assert ration_config.NDF == NDF
    assert ration_config.type == type_input
    assert ration_config.is_wetforage == is_wetforage
    assert ration_config.Kd == Kd
    assert ration_config.N_A == N_A
    assert ration_config.N_B == N_B
    assert ration_config.CP == CP
    assert ration_config.dRUP == dRUP
    assert ration_config.limit == limit
    assert ration_config.cow_type == cow_type
    assert ration_config.DMIest == DMIest
