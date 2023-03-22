"""UDRtesting.py
"""


import RUFAS.routines.animal.ration.user_defined_ration as udr
udrv = udr.user_defined_ration_values()
udrv.lactating_cow_ration
udrv.ration_all


from RUFAS.routines.animal.ration import ration_driver as ration_driver
available_feeds = ration_driver.AvailableFeeds()


ration_percentages = udrv.lactating_cow_ration
ration_all = udrv.ration_all



ration_formatting(ration_all, ration_percentages, 10)

