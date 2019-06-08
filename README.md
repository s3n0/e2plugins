+ **EPG - download & replace**

   > - simple enigma2 plugin to download & replace '/etc/enigma2/epg.dat' file
   > - best would be to upload '/etc/enigma2/epg.dat' file to some free file hosting server from another set-top box, where the EPG-Refresh plugin is always active to create fresh EPG data for all channels (not just those that the set-top box user has watched over the last few days)
   > - to upload '/etc/enigma2/epg.dat' file to some server, for example once every 2-3 days, it is advisable to use the bash script, which is located in the plugin folder - schedule it to run via CRON service eg. every night or after completing the EPG-Refresh plugin task
   > - How-To install the plugin EpgDownloadReplace:
   ``` 
       mkdir -p /tmp/x
       wget -O /tmp/x/master.zip --no-check-certificate https://github.com/s3n0/e2plugins/archive/master.zip
       unzip /tmp/x/master.zip 'e2plugins-master/EpgDownloadReplace/*' -d /tmp/x
       mv -f /tmp/x/e2plugins-master/EpgDownloadReplace /usr/lib/enigma2/python/Plugins/Extensions
       init 4 && init 3       # or simple:   reboot
   ```
   > - How-To remove the plugin EpgDownloadReplace:
   ``` 
       rm -fr /usr/lib/enigma2/python/Plugins/Extensions/EpgDownloadReplace
       init 4 && init 3       # or simple:   reboot
   ```
