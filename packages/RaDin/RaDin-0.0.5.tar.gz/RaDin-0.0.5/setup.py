from setuptools import setup

VERSION = "0.0.5"
DESCRIPTION = "It's a School's Database Modifier, That is written by Abuzar Alvi."
LONG_DESCRIPTION = "It's a School's Database Modifier, That is written by Abuzar Alvi. They can perform many tasks like insert, check, update, delete, add, sub or many more things."

# Setting up
setup(
    name="RaDin",
    version=VERSION,
    author="Abuzar",
    author_email="radinofficial15@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=['radin'],
    install_requires=['sqlite3>=3.43.0', 'datetime>=5.2', 'calendar>=3.11.5'],
    keywords=['school', 'database', 'school database','arithmetic', 'mathematics', 'python', 'RaDin', 'RaDin database', 'database modifier'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)