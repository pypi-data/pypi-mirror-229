from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='randomstrrang',
  version='0.0.1',
  description='generate a text string randomly',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Patricia Greer',
  author_email='patricia.greer88@outlook.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='rand string',
  packages=find_packages(),
  install_requires=[''] 
)
