from setuptools import setup, find_packages

# read the README.md content
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='ftiPackage',
    version='0.1.0',
    url='https://github.com/asadrk988/ftiPackage.git',
    author='Asad',
    author_email='asadrk988@gmail.com',
    description="The FTI Visualization Package is designed to create customizable data visualizations tailored to FTI's needs.",
    packages=find_packages(),    
    install_requires=['pandas', 'plotly', 'pytest', 'matplotlib', 'circlify'],
    long_description=long_description,
    long_description_content_type="text/markdown",
)