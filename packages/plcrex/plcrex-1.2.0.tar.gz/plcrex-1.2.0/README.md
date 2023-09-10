PLCreX - Approaches towards the analysis and reuse capabilities of IEC 61131-3 Programmable Logic Controllers
=============================================================================================================

<!-- -->
<!-- [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) -->
<!-- [![made-with-sphinx-doc](https://img.shields.io/badge/Made%20with-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/) -->
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Windows](https://badgen.net/badge/icon/windows?icon=windows&label)](https://microsoft.com/windows/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Tests](https://img.shields.io/badge/Tests-passed-<COLOR>.svg)](https://shields.io/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-<COLOR>.svg)](https://shields.io/)
[![Documentation Status](https://readthedocs.org/projects/plcrex/badge/?version=latest)](https://plcrex.readthedocs.io/en/latest/?badge=latest)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

<br />
<div align="center">
  <img src="https://github.com/marwern/PLCreX/assets/92115516/8532dd0e-577a-487a-985d-8e07cc042bbc" width=650> <!-- width=400 -->

  <!-- <h3 align="center">PLCreX</h3> -->

  <p align="center">
    <strong>Quick links</strong>
    <br />
    <br />
    <a href="https://pypi.org/project/plcrex/">Releases</a>
    ·
    <a href="https://plcrex.readthedocs.io/en">Documentation</a>
    ·
    <a href="#quick-start">Quick Start</a>
    ·
    <a href="#key-features">Key Features</a>
    ·
    <a href="#licenses">Licenses</a>
    ·
    <a href="#acknowledgments">Acknowledgments</a>
  </p>
</div>

---


Quick Start
===========
<strong><a href="https://plcrex.readthedocs.io/en">Explore the docs »</a></strong>

* Download IEC-Checker ``v0.4`` via IEC-Checker's GitHub releases [[.url](https://github.com/jubnzv/iec-checker/releases/tag/v0.4)]
* Download NuSMV symbolic model checker ``v2.6.0`` via NuSMV's homepage [[.url](https://nusmv.fbk.eu/)]
* Install PLCreX via PyPI: ``pip install plcrex`` or
* Install PLCreX via PLCreX's GitHub repository: ``install-windows.bat``
     * [optional] Run local tests: ``coverage run -m pytest ./tests/ --verbose``
     * Activate virtual environment (venv): ``run.bat``

Key Features
============

<strong><a href="https://plcrex.readthedocs.io/en">Explore the docs »</a></strong>

Usage: ``python -m plcrex --help``

<img src="https://github.com/marwern/PLCreX/assets/92115516/d8780836-7345-49e2-a62e-2f9584392e5e" width=650> <!-- width=250 -->

| Tool                | Usage                                                         | Script      | Version  | Design flow                           |
|---------------------|---------------------------------------------------------------|-------------|----------|---------------------------------------|
| FBD-Optimizer       | ``plcrex fbd-optimizer [OPTIONS] SOURCE EXE EXPORT FILENAME`` | st2x        | 2.2.0    | *.xml → fbd2st → *.st → st2x → *.st   |
| FBD-to-ST Compiler  | ``plcrex fbd-to-st [OPTIONS] SOURCE EXPORT FILENAME``         | fbd2st      | 1.4.0    | *.xml → fbd2st → *.st                 |
| IEC-Checker         | ``plcrex iec-checker [OPTIONS] SOURCE EXE EXPORT FILENAME``   | iec_checker | 1.2.0    | *.st → iec_checker → *.log            |
| I/O-Impact Analysis | ``plcrex impact-analysis [OPTIONS] SOURCE EXPORT FILENAME``   | st2ia       | 1.4.1    | *.xml → fbd2st → *.st → st2ia → *.dot |
| ST-Parser           | ``plcrex st-parser [OPTIONS] SOURCE EXPORT FILENAME``         | st2ast      | 1.2.0    | *.st → st2ast → *.dot/*.txt           |
| Test-Case-Generator | ``plcrex test-case-gen [OPTIONS] FORMULA EXPORT FILENAME``    | ds2ts       | 2.1.2    | FORMULA:str → ds2ts → *.log           |
| XML-Validator       | ``plcrex xml-validator [OPTIONS] SOURCE``                     | xml_val     | 1.2.0    | *.xml → xml_val → stdout              |

> **_NOTE:_**  Use the "--help" option to see feature details

Licenses
========
PLCreX and its dependencies are licensed as follows:

| Tool        | Version | License   |
|-------------|---------|-----------|
| PLCreX      | 1.2.0   | GPLv3     |
| IEC-Checker | 0.4     | LGPL v3.0 |
| NuSMV       | 2.6.0   | LGPL v2.1 |


Acknowledgments
===============
Inspiration, code snippets, etc.

* blark [[v0.5.0](https://github.com/klauer/blark/releases/tag/v0.5.0)]
* IEC-Checker [[v0.4](https://github.com/jubnzv/iec-checker/releases/tag/v0.4)]