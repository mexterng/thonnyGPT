@echo off
@echo ----- clean build -----
rd /s /q .\build
call .\venv\Scripts\activate
python setup.py clean --all
pip install .





