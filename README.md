# crewchief

Launch scripts after Rackconnect automation is complete.  All events are logged in syslog.

## boot time script

```
/usr/share/crewchief/crewchief.py
```

## configuration

```
/etc/crewchief/crewchief.ini
```
```ini
[main]
max_api_attempts = 10
api_wait_seconds = 60
```

## tasks directory

```
/etc/crewchief/tasks.d
```

## tasks readme

```
/etc/crewchief/tasks.d/README
```

```
RACKCONNECT CREWCHIEF

During boot, crewchief will check the Rackconnect automation status.
Once that is complete, it will execute the files in this directory.
You can enable/disable files in this directory by changing the executable flag.
```
