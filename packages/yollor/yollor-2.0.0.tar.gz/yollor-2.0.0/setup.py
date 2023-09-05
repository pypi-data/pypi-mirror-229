from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='yollor',
    version='2.0.0',
    license='MIT License',
    author='Lucas de Moraes "Yyax13" Claro',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='Yyax13@proton.me',
    keywords='yollor colors tags',
    description=u'A python library to insert colors into your code output',
    packages=['yollor'],)