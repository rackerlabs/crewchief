import os
import platform
import setuptools
import sys


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def get_distro():
    return platform.linux_distribution()[0].lower()

files = [('/etc/crewchief.d', ['data_files/crewchief.d/10-example'])]
if is_exe('/sbin/initctl'):
    # upstart
    distro = get_distro()
    if 'ubuntu' in distro:
        print('Detected distro as Ubuntu.')
        f = ('/etc/init', ['data_files/upstart-ubuntu/crewchief.conf'])
        files.append(f)
    elif 'centos' in distro:
        print('Detected distro as CentOS.')
        f = ('/etc/init', ['data_files/upstart-redhat/crewchief.conf'])
        files.append(f)
    elif 'red hat' in distro:
        print('Detected distro as Red Hat.')
        f = ('/etc/init', ['data_files/upstart-redhat/crewchief.conf'])
        files.append(f)
    else:
        sys.exit('Unrecognized upstart system.')
elif is_exe('/usr/lib/systemd/systemd'):
    # systemd
    print('Detected systemd init system.')
    f = ('/usr/lib/systemd/system', ['data_files/systemd/crewchief.service'])
    files.append(f)
else:
    sys.exit('Unsupported distro.')

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
