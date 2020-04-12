## **ChocholousekPicons**

### **About:**

   >- Plugin was developed for updating Chocholousek's picons in Enigma2 set-top box
   >- The original intent for developing this plugin was to save free space on the device's internal disk. The plugin downloads a series of file archives (7-zip) with picons, for user-selected satellite positions. From the archives, the plugin unpacks only the necessary picons to the internal disk (depending on the service reference codes found in the "userboquet" files).

   >- Unfortunately, not all picon styles exist for all resolutions or vice versa - not all resolutions exist for every picon style (background). All picon styles are available only in picon resolution 220x132 (which can be considered the most used).
   
   >- In the new version of the plugin you can choose the method of updating the picons:   
   >
   >    - Copy all picons: Delete all current picons as first
   >    - Copy all picons: Incremental update (copy only new picons or picons with different file size)
   >    - Sync with TV channel lists (userbouquet files)
   >    - Sync with TV+RADIO channel lists (userbouquet files)
   
   >- If the archiver is not found on the system, it will be attempted to install it in two steps:
   >
   >    1. Download and install 7-zip via the package manager (i.e. attempt to install 7-zip from your Enigma feed server)
   >    2. Attempt to download a standalone `7za` binary file from the internet

### **How to un/install:**

   >- OE 2.0 / OE Alliance Core 4.x based Enigma (ATV, PLi, VTi, etc.) using the **.ipk** installation package:
   ```shell
   opkg remove <package_name>      # to uninstall package
   opkg install <package_name>     # to install package
   
   # Example:
   
   ver="$(wget --proxy off --no-check-certificate -O - https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/src/version.txt)"
   pkg="enigma2-plugin-extensions-chocholousek-picons_${ver}_all.ipk"
   
   opkg remove ${pkg:0:45}
   wget --proxy off --no-check-certificate -O "/tmp/${pkg}" "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/released_build/${pkg}"
   opkg install /tmp/$pkg
   init 4; sleep 5; init 3         # fast restart
   ```
   
   >- OE 2.2+ based Enigma (DreamElite, DreamOS, Merlin, etc.) using the **.deb** installation package:
   ```shell
   dpkg -r <package_name>          # to uninstall package
   dpkg -i <package_name>          # to install package

   # Example:
   
   ver="$(wget --proxy off --no-check-certificate -O - https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/src/version.txt)"
   pkg="enigma2-plugin-extensions-chocholousek-picons_${ver}_all.deb"
   
   dpkg -r ${pkg:0:45}
   wget --proxy off --no-check-certificate -O "/tmp/${pkg}" "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/released_build/${pkg}"
   dpkg -i /tmp/$pkg
   systemctl stop enigma2; sleep 5; systemctl start enigma2         # fast restart
   ```
