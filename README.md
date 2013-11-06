# crewchief

Launch scripts after Rackconnect automation is complete.  All events are logged in syslog.

## boot time script

```
/usr/share/crewchief/crewchief.py
```

## configuration

```
/etc/crewchief/crewchief.conf
```
```ini
[settings]
max_api_attempts = 10
api_wait_seconds = 60
```

## tasks directory

```
/etc/crewchief/tasks.d
```