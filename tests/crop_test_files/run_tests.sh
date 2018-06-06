#!/bin/sh


python3 compare.py heat_unit_expected.csv heat_units_results.csv
python3 compare.py root_depth_expected.csv root_depth_results.csv
python3 compare.py gammareg_expected.csv gammareg_results.csv
python3 compare.py LAI_expected.csv LAI_results.csv

python3 compare.py biomass_expected.csv biomass_results.csv
python3 compare.py yield_expected.csv yield_results.csv
python3 compare.py phosphorus_uptake_expected.csv phosphorus_uptake_results.csv
