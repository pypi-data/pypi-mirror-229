from setuptools import setup, find_packages

setup(
    name='steam_grabber',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'rsa',
        'yarl',
    ],
    author='Y0natari',
    author_email='nickxon015@gmail.com',
    description='Async lib to grab a lot of useful info about an account. 2FA must be turned off. Supports proxy.',
    license='MIT',
)
