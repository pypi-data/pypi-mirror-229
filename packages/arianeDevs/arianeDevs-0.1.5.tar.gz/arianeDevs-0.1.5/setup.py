from setuptools import setup, find_packages

setup(
    name='arianeDevs',
    version='0.1.5',
    description='arianeDevs',
    author='alandevcol',
    author_email='alandevcol@gmail.com',
    url='https://github.com/alandevcol/arianeDevs',
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
    ],
    include_package_data=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
