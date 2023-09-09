from setuptools import setup, find_packages


setup(
    name='miqatools',
    version='1.1.3',
    license='GPLv3',
    author="Gwenn Berry",
    author_email='gwenn@magnalabs.co',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://www.magnalabs.co',
    keywords='miqa',
    install_requires=[
          'asyncio', 'aiohttp',
      ]
)