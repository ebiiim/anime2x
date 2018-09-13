python -m venv venv
call "venv/Scripts/activate.bat"

pip install requests

python setup.py

SET TMP_PIP=tmp_pip.txt
dir /b *.whl > %TMP_PIP%
SET /P OPENCV_WHL= < %TMP_PIP%
pip install %OPENCV_WHL%
del %TMP_PIP%

pip install -r requirements.txt

echo "Completed!"
pause
