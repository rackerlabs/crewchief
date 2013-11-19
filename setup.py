import setuptools

setuptools.setup(
    name='crewchief',
    version='0.2',
    description=('Launch scripts after Rackconnect automation is complete.'),
    author='Carl George',
    author_email='carl.george@rackspace.com',
    url='https://github.com/rackerlabs/crewchief',
    license='Apache License, Version 2.0',
    py_modules=['crewchief'],
    entry_points={
        'console_scripts': [
            'crewchief=crewchief:main'
        ]
    },
    data_files=[
        ('/etc/crewchief', ['data_files/package/crewchief.cnf']),
        ('/etc/crewchief/tasks.d', ['data_files/package/10-example'])
    ],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux'
    ]
)

# vim: set syntax=python sw=4 ts=4 expandtab :
