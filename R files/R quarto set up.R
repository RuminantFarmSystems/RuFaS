library(reticulate)

reticulate::use_virtualenv("C:/Users/Kristan Reed/RuFaS-Docs/RuFaS-Docs/.venv")

reticulate::py_install("jupyter", pip = TRUE)
