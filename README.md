# Parade State - Flask Server

Use SSH to access the raspberry pi flask server. You must be connected to the same network to access the raspberry pi for SSH.

Port: (TBD) (Static)
Username: (TBD)
Password: (Written on the rasberry pi case)

The flask server is hosted on the raspberry pi using tmux.

## Accessing raspberry pi with ssh

If using cmd, SSH with the command

`ssh -l pi 192.168.198.100`

then after login,

`tmux a`

to attach to a running tmux instance. Otherwise, just call `tmux` to open an instance.

## Accessing database

Database can be accessed through a query using SQLAlchemy.

In root folder, enter the python interpreter. Then, run

`from app.models import User`

to obtain User database instance, which can be queried.

To query all:

`User.query.all()`

## Account type information

*Root* - cannot be deleted normally, has all admin rights. Password is TBD.

*Admin* - Manage user database, and control the gate. No restrictions.

*Trusted user* - Can open the gate anywhere.

*Temp user* - Can only open the gate while connected to home WiFi. Can access the site anywhere.

## DDNS service info

DDNS service is provided by FreeDNS.

Router is configured to update its public IP address every 21 days unless otherwise configured.
