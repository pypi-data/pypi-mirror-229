from setuptools import setup

setup(
    name="CGIRMSlib",
    version="0.1",
    description="Derivada para uso em conversões de python para o RMS",
    author="CGI",
    author_email="andre.ershov@cgi.com",
    packages=["CGIRMSLib"],
    install_requires=[
        'pandas',
        'datetime',
    ],
)