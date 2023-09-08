from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description_file = fh.read()


classifiers = [
  'Development Status :: 1 - Planning',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: MIT License',
  'Operating System :: Microsoft :: Windows :: Windows 11',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='fastsetup',
  version='0.3.0',
  description='Static code in python scripts',
  long_description = long_description_file,
  long_description_content_type="text/markdown",
  url='',  
  author='Tareq Abeda',
  author_email='TareqAbeda@outlook.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='fastsetup', 
  packages=find_packages(),
  install_requires=[] 
)
