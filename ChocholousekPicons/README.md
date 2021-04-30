## **Chocholousek Picons - Enigma2 plugin**

* Plugin was developed for downloading + updating Chocholousek's picons in Enigma2 set-top box

* The original intent for developing this plugin was to save free space on the device's internal disk. The plugin downloads a series of file archives (7-zip) with picons, for user-selected satellite positions. From the archives, the plugin unpacks only the necessary picons to the internal disk (depending on the service reference codes found in the "userboquet" files).

* Unfortunately, not all picon styles exist for all resolutions or vice versa - not all resolutions exist for every picon style (background). All picon styles are available only in picon resolution 220x132 (which can be considered the most used).
   
* In the new version of the plugin you can choose the method of updating the picons:
  * Sync with TV channel lists (userbouquet.\*.tv files)
  * Sync with TV+RADIO channel lists (userbouquet.\*.tv|\*.radio files)
  * Copy all picons: Delete all current picons as first
  * Copy all picons: Incremental update (copy only new picons or replace picons only with a different file size)
   
* If the 7-zip archiver is not found in your Enigma2, it will be attempted to install it in two steps:
  * 1.Download and install 7-zip via the package manager (i.e. attempt to install 7-zip from your Enigma feed server)
  * 2.Attempt to download a standalone `7za` binary file from the internet

## **How to un/install plugin (via Shell)**

### **Online shell-script (automatic .ipk / .deb selection):**
  ```shell
  # install - the latest released version of the plugin:  (warning ! the plugin configuration will be deleted !)
  wget -qO- --no-check-certificate "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/online-setup" | bash -s install
  
  # uninstall:
  wget -qO- --no-check-certificate "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/online-setup" | bash -s uninstall
  
  # delete (reset) plugin configuration from the Enigma2:
  wget -qO- --no-check-certificate "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/online-setup" | bash -s del-config
  ```

### **Enigma2 based on OE 2.0 and OE Alliance 4.x core (ATV, PLi, VTi, BlackHole, TeamBlue, etc.) - using the ".ipk" installation package:**
  ```shell
  opkg install <path_to_ipk-file>                             # install the package
  
  opkg remove enigma2-plugin-extensions-chocholousek-picons   # uninstall the package (the plugin package name is 'enigma2-plugin-extensions-chocholousek-picons')
  ```
  
### **Enigma2 based on OE 2.2 core or newer (DreamElite, DreamOS, Merlin, etc.) - using the ".deb" installation package:**
  ```shell
  dpkg -i <path_to_deb-file>                                  # install the package
  
  dpkg -r enigma2-plugin-extensions-chocholousek-picons       # uninstall the package (the plugin package name is 'enigma2-plugin-extensions-chocholousek-picons')
  ```
