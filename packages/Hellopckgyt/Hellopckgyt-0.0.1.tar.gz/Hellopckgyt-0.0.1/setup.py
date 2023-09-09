from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Hello Package'
LONG_DESCRIPTION = 'Basic Hello Package.'

# Setting up
setup(
    name="Hellopckgyt",
    version=VERSION,
    author="NeuralNine (Florian Dedov)",
    author_email="<nillduek@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    #install_requires=['opencv-python', 'pyautogui', 'pyaudio'],
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)