#!/bin/sh

cp niwalaps.timer /etc/systemd/system/
systemctl enable niwalaps.timer
systemctl start niwalaps.timer
