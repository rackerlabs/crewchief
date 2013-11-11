# crewchief

Launch scripts after Rackconnect automation is complete on a Linux cloud server.  All events are logged in syslog.

## configuration

During boot, crewchief attempts to get the Rackconnect automation status.  It will keep trying with an interval of api_wait_seconds until it reaches max_api_attempts.

```
/etc/crewchief/crewchief.ini
```
```ini
[main]
max_api_attempts = 10
api_wait_seconds = 60
```

## tasks directory

Once Rackconnect automation is complete, crewchief will execute the files in this directory.  You can enable/disable files by changing the executable flag.

```
/etc/crewchief/tasks.d
```

## installation

```
pip install https://github.com/rackerlabs/crewchief/archive/master.tar.gz
```