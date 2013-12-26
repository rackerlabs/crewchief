import os
import setuptools


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

files = [('/etc/crewchief.d', ['data_files/crewchief.d/10-example'])]
if is_exe('/sbin/initctl'):
    # upstart
    f = ('/etc/init', ['data_files/upstart/crewchief.conf'])
    files.append(f)
elif is_exe('/usr/lib/systemd/systemd'):
    # systemd
    f = ('/usr/lib/systemd/system', ['data_files/systemd/crewchief.service'])
    files.append(f)

setuptools.setup(
    name='crewchief',
    version='0.4',
    description=('Launch scripts after Rackconnect automation is complete.'),
    author='Carl George',
    author_email='carl.george@rackspace.com',
    url='https://github.com/rackerlabs/crewchief',
    license='Apache License, Version 2.0',
    py_modules=['crewchief'],
    install_requires=['argparse'],
    entry_points={
        'console_scripts': [
            'crewchief=crewchief:main'
        ]
    },
    data_files=files,
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux'
    ]
)

# vim: set syntax=python sw=4 ts=4 expandtab :
