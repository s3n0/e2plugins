
+ **Plugin for updating Chocholousek's picons in Enigma2.**

    - The original intent for developing this plugin was to save free space on the device's internal disk. The plugin downloads a series of Internet archives (7-zip) with piconami, for user-selected satellite positions. From the archives, the plugin unpacks only the necessary picons to the internal disk (depending on the service reference codes found in the "userboquet" files).

    - If the 7-zip archiver is not found on the system, it will be attempted to install it in two steps:
      >   (1) with opkg manager `opkg update && opkg install p7zip` (ie attempt to install 7-zip from your Enigma feed server)
      >   (2) download binary file `7za` as standalone archiver from internet

