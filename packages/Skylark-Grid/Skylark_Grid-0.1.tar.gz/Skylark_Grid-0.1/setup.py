from setuptools import setup, find_packages

with open('readme.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='Skylark_Grid',
    version='0.1',
    description='An image grid maker tool',
    author='Prem Varma',
    author_email='prem.varma@skylarklabs.ai',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'numpy'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
