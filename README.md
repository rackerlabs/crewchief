# crewchief

Launch scripts after Rackconnect automation is complete on a Linux cloud server.

## installation

stable

```
pip install https://github.com/rackerlabs/crewchief/archive/v0.2.tar.gz
```

development

```
pip install https://github.com/rackerlabs/crewchief/archive/master.tar.gz
```

## configuration

If installed via pip, you must implement a method for automatically starting crewchief at boot time.

When run, crewchief will attempt to get the Rackconnect automation status.  It will keep trying with an interval of api_wait_seconds until it reaches max_api_attempts.

```
/etc/crewchief/crewchief.ini
```
```ini
[main]
max_api_attempts = 10
api_wait_seconds = 60
```

All events are logged in syslog.

Once Rackconnect automation is complete, crewchief will run every executable script in the tasks.d directory.  You can enable/disable tasks by changing the executable flag.

```
/etc/crewchief/tasks.d
```
