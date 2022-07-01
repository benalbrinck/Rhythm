import os

"""
To make this a .exe file:

pyinstaller -F -i [ICON FILE] [PYTHON FILE]

Recommend making a separate file that runs it like this one so you can still edit the
code without having to make a new .exe every time.
"""

if __name__ == '__main__':
	os.system('start cmd /c python main.py')
