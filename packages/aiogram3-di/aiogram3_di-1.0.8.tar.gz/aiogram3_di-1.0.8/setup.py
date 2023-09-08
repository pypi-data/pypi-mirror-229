from re import search, MULTILINE
from distutils.core import setup


with open('aiogram3_di/_version.py') as file:
    version = search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', file.read(), MULTILINE).group(1)


with open('README.md') as file:
    long_description = file.read()


setup(
  name='aiogram3_di',
  packages=['aiogram3_di'],
  version=version,
  license='MIT',
  description='Dependency Injection implementation for aiogram 3.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Vladyslav49',
  python_requires='>=3.10',
  author_email='',
  url='https://github.com/Vladyslav49/aiogram3_di',
  keywords=['Aiogram', 'Telegram', 'Bots', 'DI', 'Dependency Injection'],
  install_requires=[
    'aiogram>=3.0.0',
  ],
  classifiers=[
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
)
