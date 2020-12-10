from setuptools import setup

setup(
    name='devpotato-bot',
    version='0.6.1',
    description='Telegram bot for cryptopotato chat',
    packages=['devpotato_bot'],

    python_requires='>=3.8',
    install_requires=[
        'python-telegram-bot>=13.0',
        'ujson>=3.0.0',
        'cachetools>=4',
        'pytz>=2020.4',
        'SQLAlchemy>=1.3',
        'alembic>=1.4'
    ],

    author='Vladislav Glinsky',
    author_email='cl0ne@mithril.org.ua',
    url="https://code.nix.org.ua/cl0ne/cryptopotato-bot",
    license='MIT',
    license_file='LICENSE'
)
