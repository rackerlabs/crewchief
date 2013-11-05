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
    config = ConfigParser.ConfigParser()
    config.read('/etc/crewchief/crewchief.conf')
    settings = {}
    settings['max_api_attempts'] = config.get('main', 'max_api_attempts')
    settings['api_wait_seconds'] = config.get('main', 'api_wait_seconds')
    return settings


def get_datacenter():
    xencmd = ['xenstore-read', 'vm-data/provider_data/region']
    datacenter = subprocess.check_output(xencmd).rstrip('\n')
    return datacenter


def query_api():
    apiurl = 'https://{DC}.{DOMAIN}/{VERSION}/{INFO}'.format(
        DC=get_datacenter(),
        DOMAIN='api.rackconnect.rackspace.com',
        VERSION='v1',
        INFO='automation_status')

    for each in range(settings.get('max_api_attempts')):
        try:
            rcstatus = requests.get(apiurl, timeout=3).text
        except requests.exceptions.Timeout:
            syslog.syslog('rackconnect API call timeout, sleeping 60 seconds')
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
        syslog.syslog('hit maximum api attempts, giving up')
        return False


def call_tasks():
    tasks_dir = '/etc/crewchief/tasks.d'
    scripts = glob.glob('{}/*'.format(tasks_dir))
    try:
        scripts.remove('{}/README'.format(tasks_dir))
    except ValueError:
        pass
    scripts.sort()

    for script in scripts:
        try:
            subprocess.call([script])
        except OSError:
            syslog.syslog('skipping non-executable script {}'.format(script))
        else:            
            syslog.syslog('running executable script {}'.format(script))
    else:
        syslog.syslog('completed all tasks')


def main():
    settings = parse_config()
    if query_api(settings):
        call_tasks(settings)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

# vim: set syntax=python sw=4 ts=4 expandtab :
