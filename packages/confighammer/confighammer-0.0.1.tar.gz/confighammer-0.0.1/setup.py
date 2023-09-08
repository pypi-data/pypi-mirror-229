from setuptools import setup

setup(
    name='confighammer',
    version='0.0.1',
    author='Blackwell',
    author_email='friendlyblackwell@example.com',
    url='https://github.com/friendlyblackwell/confighammer',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Common Config Reader',
    packages=['confighammer'],
    install_requires=[
        "PyYAML",
    ]
)
