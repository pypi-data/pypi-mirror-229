from setuptools import setup

setup(
    name='serunaiAutomation',
    version='2.1',
    description='Serunai Automation',
    author='Maimul',
    author_email='maimulskates@gmail.com',
    packages=['serunaiAutomation'],
    install_requires=['selenium', 'seleniumbase', 'openpyxl', 'hashlib', 'json', 'csv', 'datetime', 'time', 'random'],
    py_modules=['serunaiAutomation.serunaiAutomate'],
    entry_points={
        'console_scripts': [
            'serunaiAutomation = serunaiAutomation.serunaiAutomate:main',
        ],
    },
)