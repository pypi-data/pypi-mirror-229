from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Telegram logging handler for python'

setup(
    name="telegram_logging_handler",
    version=VERSION,
    author="Alexandr Agakin",
    author_email="<agakinalexnadr@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'telegram', 'logging', 'logger'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)