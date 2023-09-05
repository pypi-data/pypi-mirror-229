
from distutils.core import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'sim_sensors',
  packages = ['sim_sensors'],
  version = '0.3',
  license='MIT',
  description = 'A collection of classes that simulate IoT sensors',
  long_description=long_description,
  author = 'Ivan Šarić / Path Variable',
  author_email = 'ivan@path-variable.com',
  url = 'https://www.path-variable.com',
  keywords = ['simulated', 'sensors', 'iot'],
  install_requires=[],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)