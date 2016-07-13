#!/usr/bin/python


from setuptools import setup, find_packages
import txweb

version = txweb.__version__

install_requires = [
    'six>=1.8.0',
    'Twisted>=15.0.0',
    'pyOpenSSL >= 0.13',
    'cyclone',
    'pycrypto'
]
install_requires_empty = []

package_data={}


setup(name='txweb',
      version=version,
      author='jamiesun',
      author_email='jamiesun.net@gmail.com',
      url='https://github.com/talkincode/txweb',
      license='MIT',
      description='python web framework',
      long_description=open('README.md').read(),
      classifiers=[
       'Development Status :: 6 - Mature',
       'Intended Audience :: Developers',
       'Programming Language :: Python :: 2.6',
       'Programming Language :: Python :: 2.7',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
      packages=find_packages(),
      package_data=package_data,
      keywords=['toughstruct','cyclone','twisted','web'],
      zip_safe=True,
      include_package_data=True,
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              'txwebctl = txweb.txwebctl:main',
              'txappctl = txweb.txappctl:main',
          ]
      }
)