from setuptools import setup

setup(
    name = 'devpotato-bot',
    version = '0.3.2',
    description='Telegram bot for cryptopotato chat',
    packages = ['devpotato_bot'],
    python_requires='>=3.6',
    install_requires=['python-telegram-bot>=12.3.0'],
    author='Vladislav Glinsky',
    author_email='cl0ne@mithril.org.ua',
    url="https://code.nix.org.ua/cl0ne/cryptopotato-bot",
    license='MIT',
    license_file='LICENSE'
)
