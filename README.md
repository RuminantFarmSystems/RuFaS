> **Sobre este fork**
>
> Este repositório é um fork de [RuminantFarmSystems/RuFaS](https://github.com/RuminantFarmSystems/RuFaS), criado a
> partir da versão 1.0.5 (branch `dev`, commit `9af6eca`, de 05/11/2026).
>
> - **Motivo:** acrescentar modelos de dieta de custo mínimo para vacas leiteiras, com preços de Goiás, que
>   usam a biblioteca de alimentos do RuFaS:
>   - [`helpful_scripts/nrc2001_dieta_lp/`](helpful_scripts/nrc2001_dieta_lp/): exigências do NRC (2001);
>   - [`helpful_scripts/nasem2021_dieta_lp/`](helpful_scripts/nasem2021_dieta_lp/): exigências do NASEM (2021),
>     escrito com PuLP.
> - **Camada local adicional:** interface offline em `interface/`, servidor `abrir_interface.py` e planejamento de produção em `helpful_scripts/interface_rufas/`, com motor NASEM independente e ambiente isolado. Consulte o README dessa camada para instalação, hipóteses e limitações. O núcleo e as entradas do RuFaS são preservados.
> - **Comparabilidade:** as simulações do RuFaS dão os mesmos resultados do original. Os modelos de dieta são
>   independentes e não substituem a formulação de rações do RuFaS.
> - **Objetivo da interface:** formular a dieta de custo mínimo para uma produção de leite informada, nos padrões NRC e NASEM. O leite é parâmetro; somente as quantidades dos alimentos são otimizadas. Horizonte e rebanho definem o planejamento e os totais.
> - Este fork não é uma versão oficial nem endossada pelo projeto RuFaS. Assim como o original, é distribuído
>   sob a licença GPLv3.

[![Flake8](https://img.shields.io/badge/Flake8-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Pytest](https://img.shields.io/badge/Pytest-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Mypy](https://img.shields.io/badge/Mypy-690%20errors-red)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)


# RuFaS: Ruminant Farm Systems

**RuFaS** is an open-source, next-generation, whole-farm modeling environment that simulates dairy farm production and environmental impact. It is designed to support research, innovation, and sustainable decision-making in ruminant animal agriculture. 

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
