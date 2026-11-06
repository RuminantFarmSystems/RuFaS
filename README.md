[![Flake8](https://img.shields.io/badge/Flake8-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Pytest](https://img.shields.io/badge/Pytest-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Mypy](https://img.shields.io/badge/Mypy-1165%20errors-red)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)


# RuFaS: Ruminant Farm Systems

**RuFaS** is an open-source, next-generation, whole-farm modeling environment that simulates dairy farm production and environmental impact. It is designed to support research, innovation, and sustainable decision-making in ruminant animal agriculture. 

---

# Dependency
For Mon Système Fourrager, the default branch is `dev-msf`.
This branch MUST NOT be deleted, since:
- it includes modifications to the RuFaS source code in order to allow its usage as a dependency
    (e.g. removing useless verifications of the python version and dependencies);
- it is used to produce the tags which are used in other repos (`rufas-api` and `msf-rufas`).

Therefore, `dev-msf` is NOT the branch that should be forked with RuFaS. Instead, the branch
`dev` is the one that should be synched with `origin`, then `dev-msf` should be `rebase` on `dev`.

````mermaid
flowchart LR
    subgraph rufas["RuFaS"]
        dev["dev"]
    end

    subgraph RuFaS-MyForageSystem
        dev --> dev_forked[dev] --> dev-msf[dev-msf] --> tags
    end

    subgraph rufas-api
        tags --> models[[Pydantic models generation]]
    end
    subgraph msf-rufas
        tags --> wrapper[[RuFaS wrapper]]
    end

````

---

### 🌍 Vision

A world where the continuous generation and sharing of knowledge about ruminant production systems [^note] empower understanding and decision making to achieve socio-economic well-being and environmental sustainability.
[^note]:  **RuFaS** is currently focused on dairy cattle production systems.


---

### 🎯 Mission

To develop, maintain, and share an open, modular simulation platform that connects scientific research with real world decision making. Equip scientists, farmers, and other stakeholders with tools to understand, evaluate, and improve the environmental, economic, and social outcomes of ruminant farming systems by integrating transparent models, diverse data, and collaborative contributions.
 

---

### 🧪 Scientific Foundation

RuFaS is grounded in peer-reviewed science and collaborative development. It is maintained by a diverse community of researchers, developers, and stakeholders committed to transparency, reproducibility, and continuous improvement.

---

### ♟️ Strategy

The strategic direction of RuFaS, including its vision, mission, strategic pillars, values, and operating principles, is described in [Strategy.md](Strategy.md).

---

### 🚀 Getting Started

1. **Install Python 3.12 or 3.13** - Make sure you have one of these versions installed on your system.
2. **Set up a virtual environment**
```bash
python -m venv venv
source venv/bin/activate on Mac/Linux or venv\Scripts\activate on Windows
```
3. **Install dependencies**
```bash
pip install .
```
4. **Enable output display** - Navigate to `output/output_filters/` and rename `_csv_all_variables.txt` → `csv_all_variables.txt` (remove the leading underscore).
5. **Run RuFaS**
```bash
python main.py
```
6. **Learn more** if you have further questions read through the documentation on our [GitHub Pages site](https://ruminantfarmsystems.github.io/RuFaS/) or watch our [onboarding video series](https://www.youtube.com/playlist?list=PLqq6i4QOoueR-a2mxVX3Gc78s1wvTRfr1).

---

### 🤝 How to Contribute

RuFaS welcomes coding and noncoding contributions from individuals demonstrating interest and commitment to our program standards. You can:
- 🧪 Test features and report bugs
- 💡 Suggest new features or improvements
- 🗣️ Engage in scientific discussions and peer reviews
- 💻 Submit code, documentation, or scientific literature
- 🧰  Help with user support and onboarding
- 🎨  Design user interfaces or visual assets
- 📣  Promote RuFaS within your networks

> Please see the [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) code of conduct and [CONTRIBUTING.md](https://github.com/RuminantFarmSystems/RuFaS/blob/dev/CONTRIBUTING.md?plain=1) for full details.

> For prerequisites and testing read the [PREREQUISITES](https://ruminantfarmsystems.github.io/RuFaS/_wiki/Github-Actions.html) and [End-to-End Testing](https://ruminantfarmsystems.github.io/RuFaS/_wiki/End%E2%80%90to%E2%80%90End-Testing.html) files.

---

### 📜 License

RuFaS is licensed under GPLv3. See the [COPYING.md](https://github.com/RuminantFarmSystems/RuFaS/pull/2369) and [COPYING.LESSER.md](https://github.com/RuminantFarmSystems/RuFaS/pull/2369) files for details.

---

## 📬 Contact

For questions, sponsorship inquiries, or collaboration proposals, please email contact@rufas.org.

---

## 🧑‍🔬 Acknowledgements

Thanks to all the [individuals](https://www.rufas.org/the-team) and [organizations](https://www.rufas.org/partners) that contributed to RuFaS development and maintenance in the past and continue to contribute today. Contributions to the RuFaS GitHub repository are recorded [here](https://github.com/RuminantFarmSystems/RuFaS/graphs/contributors).
