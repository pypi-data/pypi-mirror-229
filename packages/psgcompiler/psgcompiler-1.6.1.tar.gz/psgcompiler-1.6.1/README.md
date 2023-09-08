
<p align="center">
  <img src="https://raw.githubusercontent.com/PySimpleGUI/PySimpleGUI/master/images/for_readme/Logo%20with%20text%20for%20GitHub%20Top.png" alt="Python GUIs for Humans">
  <h2 align="center">psgcompiler</h2>
  <h2 align="center">A PySimpleGUI Application</h2>

</p>

"Compile" your Python programs into an EXE for Windows, an APP for Mac, and a binary for Linux


![](https://raw.githubusercontent.com/PySimpleGUI/psgcompiler/main/screenshot_for_readme/psgcompiler_screenshot.jpg?token=ALAGMY3Z33WHFX3RTFXEZ73BTEUPO)



## Installation

### Old-school Straight Pip

pip install psgcompiler

### pip via `python -m pip` the python recommended way

#### If `python` is your command

python -m pip install psgcompiler

#### If `python3` is your command

python3 -m pip install psgcompiler

## Usage

Open a command window and type:   

`psgcompiler`   

## `PyInstaller` Back-end with a `PySimpleGUI` Front-end

The plan for `psgcompiler` is to provide a GUI interface for a number of the tools available to convert a Python program into a binary executable.  PyInstaller was chosen as the first back-end tool that does the heavy-lifting of converting your code into a binary executable.  The next one being added is `cx_freeze`.

`psgcompiler` collects the options that are assembled into the command that can then be run for you by launching a subprocess.  You will see the command being built as you add or remove items using the GUI.  You can run PyInstaller manually using the options shown in the "Command" box.  Type `pyinstaller` on the command line and paste the text you see under "Command" in the Home tab of the psgcompiler program. 


PyInstaller transforms your Python project into an executable that you can distribute to friends, family members, colleagues, the public, other developers, ...  Anyone that does not have Python installed on their machine will be able to run your program after you've turned it into a binary executable.

PySimpleGUI users in particular will greatly benefit from `psgcompiler` as you'll be able to distribute "Windows Programs".  Most likely no one will know you're using Python.  On Windows, you can create a single EXE file. One-file is the default setting.  After converting, you'll be left with a single EXE file.

## A Multitude Of Options

`PyInstaller` has a sh*t-ton of options!  Unlike the primitive EXE Maker that the PySimpleGUI project created, the `psgcompiler` exposes all of the options in an easy to use way.

## Simple Interface, Complex Settings

While `psgcompiler` makes it easy to specify the many options available for PyInstaller, it doesn't remove the complexity that comes with using PyInstaller.

Please refer to the **[PyInstaller documentation](https://pyinstaller.readthedocs.io/en/stable/)** to better understand the available options.  It can be tricky to convert some programs, particularly if you're using other Python packages in addition to PySimpleGUI.

## All Python Programs Welcomed...

Your Python program doesn't have to use PySimpleGUI in order to use the `psgcompiler` tool.  PySimpleGUI is being used to give you a GUI front-end to PyInstaller.  There is no requirement that your program use PySimpleGUI.


## Troubleshooting PyInstaller Problems

When it comes to PyInstaller use, I'm a user of PyInstaller, just as you are.  The PySimpleGUI project isn't populated with PyInstaller experts.  You'll need to use your programming prowess to find answers to problems you may encounter using PyInstaller.

We're making it easy for you to run PyInstaller, and soon additional similar utilities, but that doesn't mean it's going to be easy overall.

The PyInstaller documentation is well-written and can be found here:  
https://pyinstaller.readthedocs.io/en/stable/





## A Simple EXE

If your program is relatively simple, then you only need to supply the name of your Python file, and an optional icon file.

Here is an example session showing only the .pyw file and the .ico file being supplied.  


![](https://raw.githubusercontent.com/PySimpleGUI/psgcompiler/main/screenshot_for_readme/psgcompiler_gif.gif?token=ALAGMYYG5EDJ3FH7GCCWLV3BTEUSE)


## Additional Back-ends

Currently in the works is support for additional back-ends.  `cx_freeze` is up next.

## Create a Shortcut To This Program

If you're a Windows user, then use the [`psgshortcut` application](https://pypi.org/project/psgshortcut/) to make a shortcut to this program so that you can then put on your desktop or pin to your taskbar (or any  other use that stops the need to type `psgcompiler` ever again).

## Release Notes

### 1.5.1 17-Dec-2021
* Fixed FileBrowse target problem loggined in Issue 1 on GitHub
* Added PyInstaller as a required package to setup.py on PyPI

### 1.5.0 14-Nov-2021

* Added PyInstaller Help link just above the "Convert" button
	* If clicked, takes the user to the PyInstaller [When Things Go Wrong](https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html) web page.
### 1.4.0 14-Nov-2021

* Debug counter added to event loop
* Updated readme for PyPI

### 1.3.0 13-Nov-2021

* Version number of psgcompiler, PyInstaller both added to right-click-menu and to version popup

### 1.2.0 13-Nov-2021

* Added version number in the .py file
* Added version number to right click menu
* Added local copy of version for debugging
* Posted to PyPI

### 1.0.0 13-Nov-2021

* Initial release, post to PyPI and  GitHub


## License

Licensed under an LGPL3 License  
Copyright 2021

## This PySimpleGUI Application Was Designed and Written By

[Tanay Findley](https://github.com/Chr0nicT) as part of [**The PySimpleGUI Project**](http://www.PySimpleGUI.com)


## Contributing

Like the PySimpleGUI project, this project is currently licensed under an open-source license, the project itself is structured like a proprietary product. Pull Requests are not accepted.

## Copyright

Copyright 2021 PySimpleGUI
