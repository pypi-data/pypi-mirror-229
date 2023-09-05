from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='buble',
  version='6.0',
  author='ForestBu',
  author_email='tvc55.admn@gmail.com',
  description='Buble library PyPi',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/ForestBu/Buble',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='buble if else elif elseif perimeter square area while for python file os system pause time timer login password register log reg',
  python_requires='>=3.7'
)
