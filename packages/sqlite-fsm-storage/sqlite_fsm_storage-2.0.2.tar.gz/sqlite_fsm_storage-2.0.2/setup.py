from setuptools import setup


with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()


setup(
    name='sqlite_fsm_storage',
    version='2.0.2',
    author='EgorBlaze',
    author_email='blazeegor@gmail.com',
    description='SQLiteStorage is a very good FSM Storage for Telegram bots.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License, Version 2.0, see LICENSE file',
    packages=['sqlite_fsm_storage'],
    install_requires=['aiogram', 'aiosqlite']
)