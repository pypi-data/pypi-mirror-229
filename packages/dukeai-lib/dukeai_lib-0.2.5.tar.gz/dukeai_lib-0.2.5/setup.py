from setuptools import setup, find_packages

setup(
    name='dukeai_lib',
    version="0.2.5",
    description="Common functions used across the DUKE.ai project environments.",
    url='https://duke.ai',
    author='Blake Donahoo',
    author_email='blake@duke.ai',
    license='GNU General Public License v3 (GPLv3)',
    packages=find_packages(),
    keywords=['dukeai', 'duke.ai'],
    install_requires=[
        'chalice~=1.27.1',
        'requests~=2.27.1',
        'base58==2.1.1',
        'urllib3~=1.26.9'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Utilities"
    ],
)

# python3 -m build
# python3 -m twine upload --repository duke-pypi dist/dukeai_lib-0.2.0*

