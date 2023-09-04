from setuptools import setup, find_packages

setup(
    name='QuantEdgeBacktesting',
    version='0.1.0',
    description='Allows the backtesting of trading strategies using historic market data.',
    author='Robert Flowerday',
    author_email='rob.flowerday@hotmail.co.uk',
    url='https://github.com/robflowerday/QuantEdgeBacktesting',
    packages=find_packages(),
    install_requires=[
        'QuantEdgeMarketData',
    ],
)
