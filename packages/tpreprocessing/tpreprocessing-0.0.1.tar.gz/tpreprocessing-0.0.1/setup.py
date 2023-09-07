from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='tpreprocessing',
  version='0.0.1',
  description='simple text preprocessing package that preprocess text by simple functions',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Mohamed Hany',
  author_email='momorwe@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='text-preprocessing', 
  packages=find_packages(),
  install_requires=[''] 
)