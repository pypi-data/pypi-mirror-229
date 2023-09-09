from setuptools import setup

setup(
    name='qcinfo',
    version='1.0.8',
    description='A Python package for getting insights from quantum chemical calculation data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dr. Ravindra Shinde',
    author_email='r.l.shinde@utwente.nl',
    url='https://github.com/neelravi/qcinfo',
    packages=['qcinfo'],
    install_requires=["resultsFile"],
    entry_points={
        'console_scripts': [
            'qcinfo = qcinfo.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
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
