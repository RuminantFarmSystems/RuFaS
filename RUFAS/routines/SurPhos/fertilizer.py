

def update_all(surphos):
    time = surphos.time
    day = time.day
    year = time.year
    fert_app = surphos.fertilizer_app

    for x in range(len(fert_app)):
        if fert_app.day[x] == day and fert_app.year[x] == year:
            surphos.fert_sum += fert_app.mass  # fertpkg(x)
            surphos.no_rains = 0
            surphos.fert_CNT = 1.0

            if fert_app.depth[x] == 0.0:
                surphos.fert_p_avg += fert_app.mass[x] * 0.75
                fert_PST = surphos.fert_p_avg  # TODO fert_PST is frtpst and unused
                surphos.rs_fert_p += fert_app.mass[x] * 0.25

            else:
                surphos.fert_p_avg += fert_app.mass[x] * 0.75 * fert_app.surface_percent[x]
                fert_PST = surphos.fert_p_avg  # above
                surphos.rs_frt_p += fert_app.mass[x] * 0.25 * fert_app.surface_percent[x]

                no = 0
                for y in range(0, 3):
                    if surphos.depths_layer[y] >= fert_app.depth[x]:
                        no = y
                        break

                sum_fac = 0.0

                for w in range(0, 3):
                    surphos.labile_P_layer[w] *= surphos.area

                for k in range(0, no - 1):  # TODO weird, can be -1 but that might be intentional
                    surphos.fact = surphos.depths_layer[k] / fert_app.depth[x]
                    surphos.labile_P_layer[k] += (fert_app.mass[x] * surphos.fact
                                                  * (1.0 - fert_app.surface_percent[x]))
                    sum_fac = sum_fac + surphos.fact

                surphos.fact = 1.0 - sum_fac
                surphos.labile_P_layer[no] += (fert_app.mass[x] * surphos.fact
                                               * (1.0 - fert_app.surface_percent[x]))

                for w in range(0, 3):
                    surphos.labile_P_layer[w] /= surphos.area
