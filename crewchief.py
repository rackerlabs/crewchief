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

import argparse
import glob
import os
import subprocess
import sys
import syslog
import time


def log(msg, args):
    ''' Log to syslog and optionally console. '''
    if args.debug:
        sys.stdout.write('{0}\n'.format(msg))
        sys.stdout.flush()
    syslog.syslog(msg)


def call_tasks(tasks, args):
    ''' Run each task in the given task list. '''
    for task in tasks:
        # strip off the path to the script name
        taskname = os.path.basename(task)
        # run the script and save the exit status
        process = subprocess.Popen(task,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)
        status = process.wait()
        if status == 0:
            # run successfully
            result = 'completed'
        elif status == 126:
            # task not executable
            result = 'skipped'
        else:
            # unknown exit status
            result = 'exited with a status of {0}'.format(status)
        log('task {0} {1}'.format(taskname, result), args)
    else:
        log('finished processing tasks', args)


def get_tasks():
    ''' Obtain the list of tasks from /etc/crewchief.d '''
    # set the tasks directory
    tasks_dir = '/etc/crewchief.d'
    # create a list of all the files in that directory
    tasks = glob.glob('{0}/*'.format(tasks_dir))
    # sort the tasks to honor numbered order (00-foo, 01-bar, etc.)
    tasks.sort()
    # return the list
    return tasks


def status_check(args):
    ''' Obtain the RackConnect status from xenstore. '''
    # false if xenstore isn't mounted
    if not os.path.ismount('/proc/xen'):
        log('xenstore is not yet mounted', args)
        return False
    # system command to pull metadata from xenstore
    xencmd = ['xenstore-read',
              'vm-data/user-metadata/rackconnect_automation_status']
    try:
        process = subprocess.Popen(xencmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except EnvironmentError:
        # false if the command is not found
        log('failed to execute xenstore-read', args)
        return False
    else:
        output = process.communicate()
        # 0 stdout, 1 stderr
        if output[1]:
            log('recieved error from xenstore-read', args)
            log(output[1].rstrip('\n'), args)
            return False
        elif output[0] == '"DEPLOYED"\n':
            # RackConnect is done
            log('RackConnect automation complete', args)
            return True
        else:
            # status is probably DEPLOYING, FAILED, or UNPROCESSABLE
            log('RackConnect automation not yet complete', args)
            return False


def control(args):
    ''' Logic control. '''
    # loop for the count
    for attempt in range(args.count):
        if status_check(args):
            # RackConnect is done, so return out of the loop
            return True
        else:
            # wait for the interval and loop again
            time.sleep(args.interval)
    else:
        # ran out of attempts
        log('hit max api attempts, giving up', args)
        return False


def handle_args():
    ''' Process command line flags. '''
    # set main program variables
    the_name = 'crewchief'
    the_description = 'Launch scripts after RackConnect automation is complete.'
    the_version = '%(prog)s 0.4'
    # create our parser object
    parser = argparse.ArgumentParser(prog=the_name,
                                     description=the_description)
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=the_version)
    parser.add_argument('-c',
                        '--count',
                        type=int,
                        default=10,
                        help='Number of attempts to check the RackConnect '
                             'status.  Defaults to 10.')
    parser.add_argument('-i',
                        '--interval',
                        type=int,
                        default=60,
                        help='Number of seconds to wait between attempts.  '
                             'Defaults to 60.')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='')
    # parse the arguments to create args object
    args = parser.parse_args()
    return args


def main():
    # set the ident for syslog
    syslog.openlog('crewchief')
    args = handle_args()
    if control(args):
        tasks = get_tasks()
        call_tasks(tasks, args)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

# vim: set syntax=python sw=4 ts=4 expandtab :
