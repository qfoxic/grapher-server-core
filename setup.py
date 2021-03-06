from setuptools import setup


setup(
    name='grapher-core',
    version='2.0.2',
    license='Apache Software License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['data', 'visualization', 'monitoring', 'graphs'],
    python_requires='~=3.7',
    description='Grapher core server and libraries',
    author='Volodymyr Paslavskyy',
    author_email='qfoxic@gmail.com',
    packages=['grapher.core'],
    install_requires=['websockets==6.0'],
    url='https://github.com/qfoxic/grapher-server-core',
    download_url='https://github.com/qfoxic/grapher-server-core/archive/2.0.2.tar.gz'
)
