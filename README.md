# crewchief

Launch scripts after RackConnect automation is complete on a Linux cloud server.

## Installation

stable

```
pip install https://github.com/rackerlabs/crewchief/archive/v0.3.tar.gz
```

development

```
pip install https://github.com/rackerlabs/crewchief/archive/master.tar.gz
```

You must implement a method for automatically starting crewchief at boot time.  Example upstart and systemd files are included under the data_files directory.  Crewchief depends on the special xenfs filesystem to be mounted at /proc/xen, so ensure that it starts after that.

## Configuration

When run, crewchief will attempt to get the RackConnect automation status.  It will keep trying with an interval of api_wait_seconds until it reaches max_api_attempts.  By default this is 10 attempts with a 60 second wait interval.  This can be customized in the configuration file.

```
/etc/crewchief/crewchief.cnf
```
```ini
[main]
max_api_attempts = 10
api_wait_seconds = 60
```

Once RackConnect automation is complete, crewchief will run every executable script in the tasks.d directory.  You can enable/disable tasks by changing the executable flag.

```
/etc/crewchief/tasks.d
```

All events are logged in syslog.
