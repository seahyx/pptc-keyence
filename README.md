# Our Home's Web Remote Gate

Use SSH to access the raspberry pi that is controlling the home gate. You must be connected to the home wifi to access the raspberry pi for SSH.

Port: 192.168.198.100 (Static)
Username: pi
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
*Root* - cannot be deleted normally, has all admin rights. Password is home WiFi password, reversed.

*Admin* - Manage user database, and control the gate. No restrictions.

*Trusted user* - Can open the gate anywhere.

*Temp user* - Can only open the gate while connected to home WiFi. Can access the site anywhere.

## DDNS service info
DDNS service is provided by FreeDNS.

Home router is configured to update its public IP address every 21 days unless otherwise configured.
