#!/usr/bin/env python2

import os
import sys
import time
import glob
import requests
import subprocess
from syslog import syslog as log
try:
    import ConfigParser
except ImportError:
    import configparser


def parse_config():
    ''' obtain the user settings from crewchief.ini '''
    # parse the config file
    config = ConfigParser.ConfigParser()
    config.read('/etc/crewchief/crewchief.ini')
    # set the defaults
    settings = {'max_api_attempts': 10,
                'api_wait_seconds': 60}
    try:
        for each in config.options('main'):
            # test if the config option is a valid key
            if each in settings.keys():
                try:
                    # overwrite the default setting to the one from config
                    settings[each] = config.getint('main', each)
                except ValueError:
                    # not an interger, use the default
                    log('{}: invalid value, using default'.format(each))
            else:
                # the option is bogus
                log('{}: invalid option'.format(each))
    except ConfigParser.NoSectionError:
        # the file is malformed or missing
        log('malformed or missing configuration file, using defaults')
    # return our settings dictionary
    return settings


def get_region():
    ''' obtain the region from the xenstore '''
    xencmd = ['xenstore-read', 'vm-data/provider_data/region']
    region = subprocess.check_output(xencmd).rstrip('\n')
    return region


def query_api(settings):
    ''' query the Rackconnect API to see if automation is complete '''
    # pull our settings from the dictionary
    max_api_attempts = settings.get('max_api_attempts')
    api_wait_seconds = settings.get('api_wait_seconds')
    sleepmsg = 'sleeping {} seconds'.format(api_wait_seconds)
    # construct the endpoint url
    apiurl = 'https://{REGION}.{DOMAIN}/{VERSION}/{INFO}'.format(
        REGION=get_region(),
        DOMAIN='api.rackconnect.rackspace.com',
        VERSION='v1',
        INFO='automation_status')
    # loop the API call until done or max attempts
    for each in range(int(max_api_attempts)):
        try:
            rcstatus = requests.get(apiurl, timeout=3).content
        except requests.exceptions.Timeout:
            log('rackconnect API call timeout, {}'.format(sleepmsg))
            time.sleep(api_wait_seconds)
            continue
        else:
            if rcstatus == 'DEPLOYED':
                log('rackconnect automation complete')
                return True
            else:
                log('rackconnect automation incomplete, {}'.format(sleepmsg))
                time.sleep(api_wait_seconds)
                continue
    else:
        log('hit max api attempts, giving up')
        return False


def get_tasks(settings):
    ''' obtain the list of scripts from /etc/crewchief/tasks.d '''
    tasks_dir = '/etc/crewchief/tasks.d'
    scripts = glob.glob('{}/*'.format(tasks_dir))
    try:
        scripts.remove('{}/README'.format(tasks_dir))
    except ValueError:
        pass
    scripts.sort()
    return scripts


def call_tasks(scripts):
    ''' run the scripts from the input list '''
    for script in scripts:
        scriptname = os.path.basename(script)
        try:
            status = subprocess.call(script)
        except OSError:
            log('task {} skipped'.format(scriptname))
        else:
            if status == 0:
                log('task {} completed'.format(scriptname))
            else:
                log('task {} failed {}'.format(scriptname, status))
    else:
        log('completed all tasks')


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
