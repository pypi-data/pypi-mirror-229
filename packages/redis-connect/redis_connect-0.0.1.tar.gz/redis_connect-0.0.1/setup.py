from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Dynamic connection to redis'
LONG_DESCRIPTION = 'A package that allows to connect to redis via sentinel'

# Setting up
setup(
    name="redis_connect",
    version=VERSION,
    author="Sabari T",
    author_email="<sabariit.t@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['redis'],
    keywords=['python', 'redis', 'sentinel'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
