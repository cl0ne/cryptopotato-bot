from setuptools import setup

setup(
    name='devpotato-bot',
    version='0.5.0',
    description='Telegram bot for cryptopotato chat',
    packages=['devpotato_bot'],

    python_requires='>=3.6',
    install_requires=[
        'python-telegram-bot>=12.6',
        'cachetools>=4',
        'python-dateutil>=2.8',
        'SQLAlchemy>=1.3',
        'alembic>=1.4'
    ],

    author='Vladislav Glinsky',
    author_email='cl0ne@mithril.org.ua',
    url="https://code.nix.org.ua/cl0ne/cryptopotato-bot",
    license='MIT',
    license_file='LICENSE'
)
