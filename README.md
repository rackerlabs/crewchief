# crewchief

Launch scripts after RackConnect automation is complete on a Linux cloud server.

## Installation

Currently only Red Hat 6, CentOS 6, and Ubuntu are supported.  There is also experiemental support for systemd.

stable

```
pip install https://github.com/rackerlabs/crewchief/archive/v0.5.tar.gz
```

development

```
pip install https://github.com/rackerlabs/crewchief/archive/master.tar.gz
```

## Configuration

Define your tasks as shell scripts under /etc/crewchief.d.
You can enable/disable tasks by changing the executable flag.
Once RackConnect automation is complete, crewchief will run all executable tasks.
All events are logged in syslog.
