from setuptools import setup

setup(name='byteboss',
version='0.0.2',
description='Test',
author='zenafey',
author_email='zenafey@eugw.ru',
packages=['byteboss', 'byteboss.resource', 'byteboss.resource.engines'],
license='MIT',
install_requires=['requests', 'colorama', 'aiohttp'])