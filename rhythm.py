import os

"""
To make this a .exe file:

pyinstaller -F -i [ICON FILE] rhythm.py

If you don't have an icon file, you can remove -i [ICON FILE].
"""

if __name__ == '__main__':
	os.system('start cmd /c python main.py')
