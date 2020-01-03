## **ChocholousekPicons**

### **About:**

   >- Plugin was developed for updating Chocholousek's picons in Enigma2 set-top box
   >- The original intent for developing this plugin was to save free space on the device's internal disk. The plugin downloads a series of file archives (7-zip) with picons, for user-selected satellite positions. From the archives, the plugin unpacks only the necessary picons to the internal disk (depending on the service reference codes found in the "userboquet" files).

   >- Unfortunately, not all picon styles exist for all resolutions or vice versa - not all resolutions exist for every picon style (background). All picon styles are available only in picon resolution 220x132 (which can be considered the most used).
   
   >- In the new version of the plugin you can choose the method of updating the picons:   
   >
   >    - Copy all picons: Delete all current picons as first
   >    - Copy all picons: Incremental update (copy only new picons or changed picons)
   >    - Sync with TV channel lists (userbouquets)
   >    - Sync with TV+RADIO channel lists (userbouquets)   
   
   >- If the archiver is not found on the system, it will be attempted to install it in two steps:
   >
   >    1. Download and install 7-zip via the package manager (i.e. attempt to install 7-zip from your Enigma feed server)
   >    2. Attempt to download a standalone `7za` binary file from the internet

### **How to un/install:**

   >- For OE2.0 based Enigma (ATV, PLi, VTi, etc.) use the *.ipk* installation package:
   ```shell
   opkg remove <package_name>      # to uninstall package
   opkg install <package_name>     # to install package
   
   # Example:
   wget --no-check-certificate -O /tmp/enigma2-plugin-extensions-chocholousek-picons_2.0.191126_all.ipk https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/released_build/enigma2-plugin-extensions-chocholousek-picons_2.0.191126_all.ipk
   opkg remove enigma2-plugin-extensions-chocholousek-picons
   opkg install /tmp/*.ipk
   ```
   
   >- For OE2.5+ based Enigma (OpenDreambox) use the *.deb* installation package:
   ```shell
   dpkg -r <package_name>          # to uninstall package
   dpkg -i <package_name>          # to install package

   # Example:
   wget --no-check-certificate -O /tmp/enigma2-plugin-extensions-chocholousek-picons_2.0.191126_all.deb https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/released_build/enigma2-plugin-extensions-chocholousek-picons_2.0.191126_all.deb
   dpkg -r enigma2-plugin-extensions-chocholousek-picons
   dpkg -i /tmp/*.deb
   ```
