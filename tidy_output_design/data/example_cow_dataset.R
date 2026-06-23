# ---- Libraries ----
library(tidyverse)

# ---- Parameters ----

n_pens = 10 # number of pens
cows_per_pen = 100 # average cows per pen
annual_turnover = 0.2 # proportion of cows replaced each year
n_rations = 5 # number of different ration types
n_years = 3 # number of years
sparsity = 0.3 # proportion of NAs on average
n_vars = 10 # number of variables measured for each cow

# ---- Generate fake ration data ----

ration_tab = tibble(
  domain = "RationInfo",
  ration_id = seq_len(n_rations),
  ration_name = paste0("ration_", ration_id),
  carbon = runif(n = n_rations, min = 0.7, 0.8),
  nitrogen = 1 - carbon
)

# ---- Generate fake pen data ----

pen_tab = tibble(
  domain = "PenInfo",
  pen_id = seq_len(n_pens),
  pen_name = paste0("pen_", pen_id),
  bedding = sample(c("straw", "bare ground", "pillows"), size = n_pens, replace = TRUE),
  latitude = 43.073051 + rnorm(n_pens, sd = 0.1),
  longitude = -89.401230 + rnorm(n_pens, sd = 0.1)
)

# ---- Generate variable metadata table ----

variable_lookup <- tibble(
  domain = "CowVariableLookup",
  var_id = seq_len(n_vars),
  var_name = paste0("var_", var_id),
  units = sample(
    x = c("cm", "lbs", "L", "unitless", "sq. mm", "ounces"),
    size = n_vars, replace = TRUE
  ),
  description = NA
)

## ---- Generate fake cow data ----
data_list = list()

# for (year in seq_len(n_years)) for (pen in seq_len(n_pens)) {
for (pen in seq_len(n_pens)){
  # get the initial cow ids (nested within pen)
  cow_ids = seq_len(runif(1, 90, 110))

  pen_data = tibble()

  for (year in seq_len(n_years)){

    # select ration for this pen this year
    pen_ration = sample(n_rations, 1)

    # replace some cows members
    if (year > 1){
      n_replaced = round(abs(rnorm(n = 1, mean = annual_turnover, sd = 0.025)) * length(cow_ids))
      which_replaced = sample(length(cow_ids), n_replaced)
      cow_ids[which_replaced] = max(cow_ids) + seq_len(n_replaced)
    }

    # set the base ID columns
    base = expand_grid(
      domain = "CowMeasurements",
      pen_id = pen, ration_id = pen_ration, year = year, day = seq_len(365), cow_num = cow_ids
    )

    # generate the variable values (regressions with pen, ration, day, and year effects)
    data = map(
      seq_len(n_vars),
      function(x){
        (0.02*pen) + (0.05*pen_ration)+ (0.01*base$day) + base$year*0.2*(x-2) + rnorm(n = nrow(base))
      }
    ) %>% bind_cols %>% setNames(., paste0("var_", seq_len(ncol(.)))) %>% suppressMessages()

    # sparsify the data (randomly replace values with NA with a given probability)
    data = apply(
      X = data, MARGIN = 2,
      FUN = function(col){
        ifelse(as.logical(rbinom(n = length(col), size = 1, prob = sparsity)), NA, col)
      }
    )

    # Add the label columns to these data and stack them with our pen table
    pen_data = bind_rows(pen_data, cbind(base, data))
  }
    # add the pen data to the list
    data_list[[pen]] = pen_data
}

# stack all the pen data tables into a single table, and ensure cows have unique IDs
data = data_list %>% bind_rows() %>%
  mutate(cow_id = as.numeric(factor(paste(pen_id, cow_num, sep = "_")))) %>%
  select(-c(cow_num)) %>% relocate(cow_id, .before = "var_1")

# and collect all the tables into the "output manager"
big_nested_tab <- tibble(
  domain = c("RationInfo", "PenInfo", "CowVariableLookup", "CowMeasurements"),
  description = c(
    "info about rations", "info about animal pens",
    "cow measurement metadata", "measurements of cows"
  ),
  data = list(ration_tab, pen_tab, variable_lookup, data)
)

saveRDS(big_nested_tab, "example_cow_dataset.rds")
