from setuptools import setup
from pathlib import Path


# this_directory = Path(__file__).parent
# long_description = (this_directory / "README.rst").read_text()


setup(
    name='sqlite_fsm_storage',
    version='2.0.6',
    author='EgorBlaze',
    author_email='blazeegor@gmail.com',
    description='AioSQLiteStorage is a very good FSM Storage for Telegram bots on Python.',
    license='Apache License, Version 2.0, see LICENSE file',
    packages=['sqlite_fsm_storage'],
    install_requires=['aiogram', 'aiosqlite'],
    classifiers=['Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python']
)