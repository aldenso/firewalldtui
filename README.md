# firewalldtui

This is a python based tui menu to administer firewalld for really lazy people.
Is tested with python2 and needs python2-pythondialog.

Install the requirements:

```text
yum install dialog
pip install python2-pythondialog
```

Doesn't work with virtualenv.

Features enabled so far:
Get status/version, services actions, ports, masquerade, reloads, runtime to permanent and few zones actions.
