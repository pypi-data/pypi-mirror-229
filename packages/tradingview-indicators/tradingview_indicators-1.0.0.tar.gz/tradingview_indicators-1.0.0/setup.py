from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'An accurate calculation of technical analysis indicators'

setup(
    name="tradingview_indicators",
    version=VERSION,
    author="m-marqx (Mateus Marques)",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas', 'numpy'],
    keywords=['python', 'TradingView', 'technical analysis', 'indicators'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)