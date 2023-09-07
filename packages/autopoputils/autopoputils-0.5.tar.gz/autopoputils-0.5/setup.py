from setuptools import setup, find_packages

setup(
    name='autopoputils',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'requests',
        'selenium'
    ],
    author='David Schwartz',
    author_email='david.schwartz@devfactory.com',
    description='Auto Populate GDoc tables using LLMs Utilities.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/yourrepository',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
