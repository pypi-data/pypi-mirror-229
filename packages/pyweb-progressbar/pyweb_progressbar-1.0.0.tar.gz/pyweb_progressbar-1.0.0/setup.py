from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r', encoding='utf-8') as f:
    return f.read()

setup(
  name='pyweb_progressbar',
  version='1.0.0',
  author='PyWebSol',
  author_email='pywebsol@gmail.com',
  description='This is a simple progressbar library',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=[],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='progressbar python pywebsol',
  python_requires='>=3.7'
)