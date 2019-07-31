#!/bin/sh


log_file="/tmp/epg_upload.log"
local_file="/etc/enigma2/epg.dat"
online_file="ftp://example-site.com/files/epg.dat"     # ...check username and password below, for FTP connection...
xuser="any_username"
xpass="any_password"


# for sure I will test the functionality and presence of the necessary "curl" in the system!
if [ ! "$(curl --version)" ]
then
	echo `date`": curl command NOT found (NOT installed)... please install it first: 'opkg install curl'" >> $log_file
	exit
fi



# I will only upload the $local_file (EPG data) only if it exists and is larger than 65 kB
if [ -f "$local_file" ] && [ $(stat -c%s "$local_file") -gt 65000 ]           #  -gt = GreaterThan       # -lt = LesserThan
then
	#### Warning: If you do not have "curl" installed on your Linux set-top box, install it - via Telnet / SSH:   opkg update && opkg install curl
	curl --insecure --ftp-ssl -u $xuser:$xpass -T $local_file $online_file
	echo `date`": $local_file file was uploaded" >> $log_file
else
	echo `date`": $local_file file for upload was not found" >> $log_file
fi
