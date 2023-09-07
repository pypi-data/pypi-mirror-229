from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'TIE International Microsoft Business Central API'
LONG_DESCRIPTION = 'A package that allows you to connect to Microsoft Business Central API. Customized for TIE International.'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name='tie_bcd_api_v2',
    version=VERSION,
    author='Michael Schori',
    author_email='<michael@tie-international.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'microsoft', 'business', 'central', 'api', 'tie', 'international'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
