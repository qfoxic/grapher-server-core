from setuptools import setup


setup(
    name='grapher-core',
    version='2.0.0',
    license='Apache Software License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['data', 'visualization', 'monitoring', 'graphs'],
    python_requires='~=3.6',
    description='Grapher core server and libraries',
    author='Volodymyr Paslavskyy',
    author_email='qfoxic@gmail.com',
    packages=['grapher.core'],
    install_requires=['websockets==4.0.1'],
    url='https://github.com/qfoxic/grapher-server-core',
    download_url='https://github.com/qfoxic/grapher-server-core/archive/2.0.0.tar.gz'
)
