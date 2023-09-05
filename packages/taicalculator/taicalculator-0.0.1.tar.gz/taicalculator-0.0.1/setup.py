from setuptools import setup, find_packages

classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: MacOS',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.11'
]

setup(
    name='taicalculator',
    version='0.0.1',
    description='First Python Library',
    long_description=open('readme.txt').read()+'\n\n'+open('changelog.txt').read(),
    url='',
    author='Tai Do',
    author_email='ductai.do@digipen.edu',
    License='MIT',
    classifiers=classifiers,
    keyword='calculator',
    packages=find_packages(),
    install_requires=['']
)