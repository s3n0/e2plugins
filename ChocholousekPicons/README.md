+ **ChocholousekPicons - plugin for updating Chocholousek's picons in Enigma2**

   >- The original intent for developing this plugin was to save free space on the device's internal disk. The plugin downloads a series of file archives (7-zip) with picons, for user-selected satellite positions. From the archives, the plugin unpacks only the necessary picons to the internal disk (depending on the service reference codes found in the "userboquet" files).

   >- Unfortunately, not all picon styles exist for all resolutions or vice versa - not all resolutions exist for every picon style (background). All picon styles are available only in picon resolution 220x132 (which can be considered the most used).
   
   >- In the new version of the plugin you can choose the method of updating the picons:   
   >
   >    1) Copy all picons (no sync)
   >    2) Sync with TV channel lists (userbouquets)
   >    3) Sync with TV + RADIO channel lists (userbouquets)
   
   >- If the archiver is not found on the system, it will be attempted to install it in two steps:
   >
   >    1) With opkg manager `opkg update && opkg install p7zip` (ie attempt to install 7-zip from your Enigma feed server)
   >    2) Attempt to download a standalone `7za` binary file
