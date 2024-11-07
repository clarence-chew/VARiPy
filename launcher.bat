@echo off
python -c "import sys; exit(sys.version_info < (3, 10))" || (
    echo Your Python version is not supported. Please install Python 3.10 or later.
    pause
    exit /b 1
)
python -c "import tkinter" || (
    echo Tkinter is not installed.
    echo Please make sure you have Python with Tkinter installed.
    pause
    exit /b 1
)
python -c "import selenium" || (
    echo Selenium is not installed.
    echo Please make sure you have Selenium installed using:
    echo pip install selenium
    pause
    exit /b 1
)

python src\main.py
