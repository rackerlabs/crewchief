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
import syslog

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def parse_config():
    ''' obtain the user settings from crewchief.cnf '''
    # parse the config file
    config = configparser.ConfigParser()
    config.read('/etc/crewchief/crewchief.cnf')
    # set the defaults
    settings = {'max_api_attempts': 10,
                'api_wait_seconds': 60}
    # overwrite defaults with values from config file
    try:
        # check if this section exists
        config.options('main')
    except configparser.NoSectionError:
        # the file is missing or there is no main section
        syslog.syslog('missing or malformed configuration file, '
                      'using default settings')
    else:
        # loop through each config option
        for each in config.options('main'):
            # test if the config option is a valid key
            if each in settings.keys():
                try:
                    # get the value
                    value = config.getint('main', each)
                except ValueError:
                    # not an interger, leave as default
                    syslog.syslog('{0}: invalid value, using default'.format(
                        each))
                else:
                    # do the overwrite
                    settings[each] = value
            else:
                # the option is bogus
                syslog.syslog('{0}: invalid option'.format(each))
    # return our settings dictionary
    return settings


def get_region():
    ''' obtain the region from the xenstore '''
    # system command to pull region from xenstore
    xencmd = ['xenstore-read', 'vm-data/provider_data/region']
    # set region to none initially
    region = None
    try:
        process = subprocess.Popen(xencmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except EnvironmentError:
        syslog.syslog('could not execute xenstore-read command')
    else:
        output = process.communicate()
        # 0 stdout
        # 1 stderr
        if output[0]:
            # overwrite region with the correct value
            region = output[0].rstrip('\n')
            syslog.syslog('obtained region {0} from xenstore'.format(region))
        elif 'No such file or directory' in output[1]:
            # xenfs isn't mounted yet
            syslog.syslog('unable to read xenstore')
        elif 'Permission denied' in output[1]:
            # wasn't run as root
            syslog.syslog('permission denied accessing xenstore')
        else:
            syslog.syslog('unknown error accessing xenstore')
    return region


def query_api(settings):
    ''' query the Rackconnect API to see if automation is complete '''
    # pull our settings from the dictionary
    max_api_attempts = settings.get('max_api_attempts')
    api_wait_seconds = settings.get('api_wait_seconds')
    # loop the API call until done or max attempts
    for each in range(max_api_attempts):
        region = get_region()
        if region:
            # construct the endpoint url
            apiurl = 'https://{REGION}.{DOMAIN}/{VERSION}/{INFO}'.format(
                REGION=region,
                DOMAIN='api.rackconnect.rackspace.com',
                VERSION='v1',
                INFO='automation_status')
            req = Request(apiurl)
            try:
                # make the http GET request
                res = urlopen(req, timeout=3)
            except Exception:
                syslog.syslog('could not connect to rackconnect API')
            else:
                rcstatus = res.read()
                if rcstatus == 'DEPLOYED':
                    syslog.syslog('rackconnect automation complete')
                    return True
                else:
                    syslog.syslog('rackconnect automation incomplete')
        # if get_region fails we have a log message from that function
        time.sleep(api_wait_seconds)
    else:
        syslog.syslog('hit max api attempts, giving up')
        return False


def get_tasks():
    ''' obtain the list of tasks from /etc/crewchief/tasks.d '''
    # set the tasks directory
    tasks_dir = '/etc/crewchief/tasks.d'
    # create a list of all the files in that directory
    tasks = glob.glob('{0}/*'.format(tasks_dir))
    # sort the tasks to honor numbered order (00-foo, 01-bar, etc.)
    tasks.sort()
    # return the list
    return tasks


def call_tasks(tasks):
    ''' run the scripts from the input list '''
    for task in tasks:
        # strip off the path to the script name
        taskname = os.path.basename(task)
        try:
            # run the script and save the exit status
            status = subprocess.call(task)
        except OSError:
            # not executable
            scriptmsg = 'task {TASK} skipped'.format(TASK=taskname)
        else:
            if status == 0:
                scriptmsg = 'task {TASK} completed'.format(TASK=taskname)
            else:
                scriptmsg = 'task {TASK} failed ({EXIT})'.format(
                    TASK=taskname,
                    EXIT=status)
        syslog.syslog(scriptmsg)
    else:
        syslog.syslog('finished processing tasks')


def main():
    # set the ident for syslog
    syslog.openlog('crewchief')
    settings = parse_config()
    if query_api(settings):
        tasks = get_tasks()
        call_tasks(tasks)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

# vim: set syntax=python sw=4 ts=4 expandtab :
