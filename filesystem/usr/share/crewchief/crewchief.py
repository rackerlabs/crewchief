#!/usr/bin/env python2

# Copyright 2013 Carl George
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time
import glob
import subprocess
from syslog import syslog as log

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def parse_config():
    ''' obtain the user settings from crewchief.ini '''
    # parse the config file
    config = configparser.ConfigParser()
    config.read('/etc/crewchief/crewchief.ini')
    # set the defaults
    settings = {'max_api_attempts': 10,
                'api_wait_seconds': 60}
    # overwrite defaults with values from config file
    try:
        for each in config.options('main'):
            # test if the config option is a valid key
            if each in settings.keys():
                try:
                    # do the overwrite
                    settings[each] = config.getint('main', each)
                except ValueError:
                    # not an interger, use the default
                    log('{0}: invalid value, using default'.format(each))
            else:
                # the option is bogus
                log('{0}: invalid option'.format(each))
    except configparser.NoSectionError:
        # the file is malformed or missing
        log('malformed or missing configuration file, using defaults')
    # return our settings dictionary
    return settings


def get_region():
    ''' obtain the region from the xenstore '''
    # system command to pull region from xenstore
    xencmd = ['xenstore-read', 'vm-data/provider_data/region']
    try:
        output = subprocess.Popen(xencmd,
                                  stdout=subprocess.PIPE
                                  stderr=subprocess.PIPE
                                  ).communicate()
    except FileNotFoundError:
        msg = 'could not find xenstore-read command'
    else:
        if output[0]:
            # output on stdout is our region
            region = output[0].rstrip('\n')
            msg = 'obtained region from xenstore'
        elif 'Permission denied' in output[1]:
            # stderr probably means script wasn't run as root
            msg = 'permission denied reading xenstore'
        else:
            msg = 'unknown error while reading xenstore'
    if region:
        return region
    else:
        log(msg)
        sys.exit(msg)


def query_api(settings):
    ''' query the Rackconnect API to see if automation is complete '''
    # pull our settings from the dictionary
    max_api_attempts = settings.get('max_api_attempts')
    api_wait_seconds = settings.get('api_wait_seconds')
    sleepmsg = 'sleeping {0} seconds'.format(api_wait_seconds)
    # construct the endpoint url
    apiurl = 'https://{REGION}.{DOMAIN}/{VERSION}/{INFO}'.format(
        REGION=get_region(),
        DOMAIN='api.rackconnect.rackspace.com',
        VERSION='v1',
        INFO='automation_status')
    # loop the API call until done or max attempts
    for each in range(int(max_api_attempts)):
        try:
            req = Request(apiurl)
            res = urlopen(req, timeout=3)
            rcstatus = res.read()
        except Exception:
            log('rackconnect API error, {0}'.format(sleepmsg))
            time.sleep(api_wait_seconds)
            continue
        else:
            if rcstatus == 'DEPLOYED':
                log('rackconnect automation complete')
                return True
            else:
                log('rackconnect automation incomplete, {0}'.format(sleepmsg))
                time.sleep(api_wait_seconds)
                continue
    else:
        log('hit max api attempts, giving up')
        return False


def get_tasks(settings):
    ''' obtain the list of scripts from /etc/crewchief/tasks.d '''
    # set the tasks directory
    tasks_dir = '/etc/crewchief/tasks.d'
    # create a list of all the files in that directory
    scripts = glob.glob('{0}/*'.format(tasks_dir))
    # remove the README file from the list
    try:
        scripts.remove('{0}/README'.format(tasks_dir))
    except ValueError:
        pass
    # sort the scripts to honor numbered order (00-foo, 01-bar, etc.)
    scripts.sort()
    # return the list
    return scripts


def call_tasks(scripts):
    ''' run the scripts from the input list '''
    for script in scripts:
        # strip off the path to the script name
        scriptname = os.path.basename(script)
        try:
            # run the script and save the exit status
            status = subprocess.call(script)
        except OSError:
            # not executable
            log('task {0} skipped'.format(scriptname))
        else:
            if status == 0:
                log('task {0} completed'.format(scriptname))
            else:
                log('task {0} failed ({1})'.format(scriptname, status))
    else:
        log('finished processing tasks')


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
