from setuptools import setup, find_packages

setup(
    name='BookWise',
    version='1.2.2',
    author='Shaurya',
    author_email='01shauryagarg@email.com',  
    description='A simple library management system',
    packages=find_packages(),
    install_requires=[
        
    ],
    entry_points={
        'console_scripts': [
            'library=library.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
