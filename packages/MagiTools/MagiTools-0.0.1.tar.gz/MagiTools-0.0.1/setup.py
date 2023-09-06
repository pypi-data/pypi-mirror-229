from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='MagiTools',
    version='0.0.1',
    license='MIT License',
    author='Mag-it',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='rpa@mag-it.com.br',
    keywords='MagiTools',
    description=u'MagiTools',
    packages=['MagiTools'],
    install_requires=['pywin32==306'],)