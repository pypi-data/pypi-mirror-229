from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.29'
DESCRIPTION = 'E-Commerce platform API'
LONG_DESCRIPTION = 'Whalegistic is a E-Commerce platform and this package is the connection between Whalegistic platform API and users websites'

setup(
    name="whalegistic",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="<Whalegistic>",
    author_email="<info@whalegistic.com>",
    license='ISC',
    packages=find_packages(),
    install_requires=["pyjwt", "asyncio", "httpx"],
    keywords="e-commerce, products, webstores, orders, pim, warehouse",
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ]
)