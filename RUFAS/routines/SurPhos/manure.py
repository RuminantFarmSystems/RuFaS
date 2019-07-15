def update_all(surphos):
    for app in
        if app.year == surphos.time.year
    manure_day = False
    if manure_day:
        surphos.cover_SLP = 0.0154 * surphos.manure_mass ** -0.55
        percent_cover = min(1.0, 0.012 * surphos.manure_mass ** 0.48)
        manure_cover_application = surphos.area * percent_cover
        manure_P_application = surphos.manure_mass * P_frac