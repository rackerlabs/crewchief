# rcrun

Launch scripts after RackConnect v2 automation is complete on a Linux cloud server.

## Installation

Currently only Red Hat 6, CentOS 6, and Ubuntu are supported.  There is also experimental support for systemd.

stable

```
pip install https://github.com/rackerlabs/rcrun/archive/2.0.tar.gz
```

development

```
pip install https://github.com/rackerlabs/rcrun/archive/master.tar.gz
```

## Configuration

Define your tasks as shell scripts under `/etc/rcrun.d`.
Once RackConnect automation is complete, rcrun will run all executable task scripts.
Any task script that is not marked as executable will be skipped.
All events are logged in syslog.
