#!/usr/bin/env python2

#
# Description:  This script is run at boot in a Rackconnected
#               cloud server.  It will continue to run until
#               Rackconnect automation is complete, then it will
#               launch the scripts inside /etc/crewchief.d/.
#

#
# Filelist:     /etc/crewchief/
#               /etc/crewchief/crewchief.conf
#               /etc/crewchief/tasks.d/
#

import os
import sys
import time
import glob
import syslog
import requests
import subprocess
import ConfigParser


def parse_config():
    ''' Obtain the user settings from /etc/crewchief/crewchief.conf. '''
    # parse the config file
    config = ConfigParser.ConfigParser()
    config.read('/etc/crewchief/crewchief.conf')
    # quit if the file is malformed or missing
    if 'settings' not in config.sections():
        syslog.syslog('malformed or missing configuration file')
        sys.exit(1)
    # set the defaults
    settings = {}
    settings['max_api_attempts'] = 10
    settings['api_wait_seconds'] = 60
    # overwrite the defaults with values from config file
    for each in ['max_api_attempts', 'api_wait_seconds']:
        try:
            settings[each] = config.get('settings', each)
        except ConfigParser.NoOptionError:
            pass
    # return our settings dictionary
    return settings


def get_datacenter():
    ''' Obtain the datacenter from the xenstore. '''
    xencmd = ['xenstore-read', 'vm-data/provider_data/region']
    datacenter = subprocess.check_output(xencmd).rstrip('\n')
    return datacenter


def query_api(settings):
    '''  '''
    apiurl = 'https://{DC}.{DOMAIN}/{VERSION}/{INFO}'.format(
        DC=get_datacenter(),
        DOMAIN='api.rackconnect.rackspace.com',
        VERSION='v1',
        INFO='automation_status')
    for each in range(settings.get('max_api_attempts')):
        try:
            rcstatus = requests.get(apiurl, timeout=3).text
        except requests.exceptions.Timeout:
            syslog.syslog('rackconnect API call timeout, '
                          'sleeping 60 seconds')
            time.sleep(settings.get('api_wait_seconds'))
            continue
        else:
            if rcstatus == 'DEPLOYED':
                syslog.syslog('rackconnect automation complete')
                return True
            else:
                syslog.syslog('rackconnect automation not yet complete, '
                              ' sleeping 60 seconds')
                time.sleep(settings.get('api_wait_seconds'))
                continue
    else:
        syslog.syslog('hit max api attempts, giving up')
        return False


def get_tasks(settings):
    '''  '''
    tasks_dir = '/etc/crewchief/tasks.d'
    scripts = glob.glob('{}/*'.format(tasks_dir))
    try:
        scripts.remove('{}/README'.format(tasks_dir))
    except ValueError:
        pass
    scripts.sort()
    return scripts


def call_tasks(scripts):
    '''  '''
    for script in scripts:
        try:
            subprocess.check_call(script)
        except OSError:
            syslog.syslog('skipping non-executable script {}'.format(script))
        except subprocess.CalledProcessError as e:
            syslog.syslog('script {} exited with a status of {}'.format(
                script, e.returncode))
        else:            
            syslog.syslog('successfully ran script {}'.format(script))
    else:
        syslog.syslog('completed all tasks')


def main():
    settings = parse_config()
    if query_api(settings):
        scripts = get_tasks(settings)
        call_tasks(scripts)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

# vim: set syntax=python sw=4 ts=4 expandtab :
