from setuptools import setup, find_packages

CLASSIFIERS = [
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
]

setup(
    name='cowsay',
    version='6.0',
    url='https://github.com/VaasuDevanS/cowsay-python',
    license='GNU-GPL',
    author='Vaasudevan Srinivasan',
    author_email='vaasuceg.96@gmail.com',
    entry_points={'console_scripts': ['cowsay=cowsay.__main__:cli']},
    description='The famous cowsay for GNU/Linux is now available for python',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    classifiers=CLASSIFIERS,
)
