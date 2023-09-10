from setuptools import setup, find_packages

# with open('requirements.txt') as f:
#     required = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='asocialgraph',
    version='1.0.2',
    packages=find_packages(),
    description='Social Graph API',
    # install_requires=required,
    author='Graphy',
    # description='API for working with the product Social Graph'
    long_description=long_description,
    long_description_content_type="text/markdown",
)
