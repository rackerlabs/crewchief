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

## installation

This program only works with python 2.7.  RHEL/CentOS only have 2.6 by default, and I haven't decided the best way to work around that.  Until then, I have only created Ubuntu debs.

```
https://56ee2081dba6f397b49b-3a69b5aa1940273c4928883d8fae7b2a.ssl.cf1.rackcdn.com/crewchief_1.0_all.deb
```
