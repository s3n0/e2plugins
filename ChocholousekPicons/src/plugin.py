# -*- coding: utf-8 -*-
###########################################################################
#  Enigma2 plugin, ChocholousekPicons, written by s3n0, 2018-2019
###########################################################################

###########################################################################
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop, inStandby                      # TryQuitMainLoop for the enigma2 gui restart # inStandby to detect if enigma2 is in Standby mode
###########################################################################
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
#from Components.AVSwitch import AVSwitch
from Components.Sources.StaticText import StaticText
###########################################################################
#from Components.MenuList import MenuList
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigSelection, ConfigYesNo, ConfigSet, ConfigText
###########################################################################
import urllib2
import cookielib
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass                                                                    # Legacy Python version (for example v2.7.2) that doesn't verify HTTPS certificates by default
else:
    ssl._create_default_https_context = _create_unverified_https_context    # Handle target environment that doesn't support HTTPS verification --- https://www.python.org/dev/peps/pep-0476/
###########################################################################
import threading
import re
import glob
###########################################################################
from os import system as os_system, path as os_path, makedirs as os_makedirs, remove as os_remove, listdir as os_listdir
#from commands import getstatusoutput                                       # unfortunately "commands" module is removed in Python 3.x and therefore in the future, it is better to use a more complicated "subprocess"
from subprocess import check_output, CalledProcessError
from shlex import split as shlexSplit
from datetime import datetime
from time import sleep
###########################################################################
from enigma import ePicLoad, eActionMap, eTimer, eEnv, getDesktop
sizemaxY = getDesktop(0).size().height()
sizemaxX = getDesktop(0).size().width()
###########################################################################
from Plugins.Extensions.ChocholousekPicons import _, PLUGIN_PATH            # from . import _, PLUGIN_PATH
###########################################################################



session = None

plugin_version_local  = '0.0.000000'
plugin_version_online = '0.0.000000'



###########################################################################
###########################################################################


class mainConfigScreen(Screen, ConfigListScreen):

    if sizemaxX > 1900:    # Full-HD or higher
        skin = '''
        <screen name="mainConfigScreen" position="center,center" size="1100,800" title="Chocholousek picons" flags="wfNoBorder" backgroundColor="#44000000">

            <widget name="config"      position="center,100" size="1000,600" font="Regular;30" itemHeight="32" scrollbarMode="showOnDemand" backgroundColor="#22000000" />
            
            <widget name="version_txt" position="0,0" size="1100,60"  font="Regular;42" foregroundColor="yellow" transparent="1" halign="center" valign="center" />
            <widget name="author_txt"  position="0,60" size="1100,40" font="Regular;28" foregroundColor="yellow" transparent="1" halign="center" valign="center" />

            <widget name="previewImage" position="100,350" size="500,300" zPosition="1" alphatest="blend" transparent="1" backgroundColor="transparent" />

            <ePixmap pixmap="skin_default/buttons/red.png"    position="25,755"  size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/green.png"  position="200,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="470,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/blue.png"   position="775,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />

            <widget render="Label" source="txt_red"    position="65,755"  size="280,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_green"  position="240,755" size="280,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_yellow" position="510,755" size="280,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_blue"   position="815,755" size="280,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" />
        </screen>'''
    else:                   # HD-ready or lower
        skin = '''
        <screen name="mainConfigScreen" position="center,center" size="850,600" title="Chocholousek picons" flags="wfNoBorder" backgroundColor="#44000000">

            <widget name="config"      position="center,70" size="800,460" font="Regular;22" itemHeight="24" scrollbarMode="showOnDemand" backgroundColor="#22000000" />
            
            <widget name="version_txt" position="0,0"  size="850,40" font="Regular;26" foregroundColor="yellow" transparent="1" halign="center" valign="center" />
            <widget name="author_txt"  position="0,40" size="850,30" font="Regular;16" foregroundColor="yellow" transparent="1" halign="center" valign="center" />

            <widget name="previewImage" position="70,225" size="500,300" zPosition="1" alphatest="blend" transparent="1" backgroundColor="transparent" />

            <ePixmap pixmap="skin_default/buttons/red.png"    position="20,560"  size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/green.png"  position="165,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="370,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/blue.png"   position="605,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />

            <widget render="Label" source="txt_red"    position="55,560"  size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_green"  position="200,560" size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_yellow" position="405,560" size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
            <widget render="Label" source="txt_blue"   position="640,560" size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" />
        </screen>'''

    def __init__(self, session):

        Screen.__init__(self, session)
        #self.session = session          # this is not necessary, this is done already during class initialization - Screen.__init__

        self.onChangedEntry = []
        self.list = []

        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        self.lineHeight = 1             # for text height auto-correction on dmm-enigma2 (0 = enable auto-correction ; 1 = disable auto-correction)

        self['previewImage'] = Pixmap()

        self['txt_red']      = StaticText(_('Exit'))
        self['txt_green']    = StaticText(_('Save & Exit'))
        self['txt_yellow']   = StaticText(_('Update plugin'))
        self['txt_blue']     = StaticText(_('Update picons'))

        global plugin_version_local
        self['version_txt']  = Label('Chocholousek picons - plugin ver.%s' % plugin_version_local)
        self['author_txt']   = Label('(https://github.com/s3n0)')

        self['actions'] = ActionMap( ['SetupActions', 'ColorActions'],
        {
            'left'  : self.keyToLeft,
            'right' : self.keyToRight,
            'yellow': self.keyToUpdatePlugin,
            'blue'  : self.keyToUpdatePicons,
            'green' : self.exitWithSave,
            'red'   : self.exitWithoutSave,
            'cancel': self.keyToExit,
            'ok'    : self.keyToOk
        }, -2)

        self.bin7zip = None             # path to directory with '7z' or '7za' executable binary file
        self.chochoContent = None       # content of the file "id_for_permalinks*.log" - downloaded from google.drive

        #self.onShown.append(self.rebuildConfigList)
        #self.onLayoutFinish.append(self.layoutFinished)

        #self.prepareSetup()

        self.layoutFinishTimer = eTimer()
        if newOE():
            i = mainConfigScreen.skin.index('font=')
            self.skin = mainConfigScreen.skin[ : i ] + mainConfigScreen.skin[ i+34 : ]
            self.layoutFinishTimer_conn = self.layoutFinishTimer.timeout.connect(self.prepareSetup)     # eTimer for newer versions (OE2.5)

            #self.l.setFont(0,gFont("Regular",30))
            #self.l.setItemHeight(32)
            
            #self['config'].setFont(0, gFont("Regular", 30))
            #self['config'].setItemHeight(32)
            
            #self["config"].l.setValueFont(gFont("Regular", 30))
            #self["config"].l.setItemHeight(32)
        else:
            self.skin = mainConfigScreen.skin
            self.layoutFinishTimer.callback.append(self.prepareSetup)                                   # eTimer for older versions (OE2.0)
        self.layoutFinishTimer.start(200, True)

        #self.onLayoutFinish.append(self.check7zip)      # this line is no longer useful ... Screen is still not ready to call MessageBox in check7zip()

    def prepareSetup(self):

        self.loadChochoContent()

        config.plugins.chocholousekpicons = ConfigSubsection()
        config.plugins.chocholousekpicons.piconFolder = ConfigSelection(default = '/usr/share/enigma2/picon',
                choices = [ ('/usr/share/enigma2/picon','/usr/share/enigma2/picon'),
                            ('/media/hdd/picon','/media/hdd/picon'),
                            ('/media/usb/picon','/media/usb/picon'),
                            ('/picon','/picon'),
                            ('/usr/share/enigma2/XPicons/picon','/usr/share/enigma2/XPicons/picon'),
                            ('/usr/share/enigma2/ZZPicons/picon','/usr/share/enigma2/ZZPicons/picon'),
                            ('(user defined)' , _('(user defined)')  )
                          ]
                        )     # --- all folders are from source code, here:   https://github.com/openatv/MetrixHD/blob/master/usr/lib/enigma2/python/Components/Renderer/MetrixHDXPicon.py
        config.plugins.chocholousekpicons.piconFolderUser = ConfigText(default = '/')
        # change the default picon directory + set this found entry, if some .png files will found in some folder:
        if config.plugins.chocholousekpicons.piconFolder.value != '(user defined)':
            for picdir in config.plugins.chocholousekpicons.piconFolder.choices:
                if glob.glob(picdir[0] + '/*.png'):
                    config.plugins.chocholousekpicons.piconFolder.default = picdir[0]
                    config.plugins.chocholousekpicons.piconFolder.setValue(picdir[0])
                    break
        config.plugins.chocholousekpicons.method = ConfigSelection(default = 'sync_tv', 
                choices = [ ('all', _('copy all picons (no sync)')), ('sync_tv', _('sync with TV userbouquets')), ('sync_tv_radio', _('sync with TV+RADIO userbouquets')) ]   )
        config.plugins.chocholousekpicons.usersats = ConfigSet(default = ['23.5E','19.2E'] , choices = self.getAllSat() )
        config.plugins.chocholousekpicons.resolution = ConfigSelection(default = '220x132',
                choices = [ ('50x30','50x30'), ('100x60','100x60'), ('150x90','150x90'), ('220x132','220x132'), ('400x170','(ZZPicons) 400x170'), ('400x240','400x240'), ('500x300','500x300') ]     )
        config.plugins.chocholousekpicons.background = ConfigSelection(default = 'black',
                choices = [ (s, s) for s in self.getAllBckByUserCfg( config.plugins.chocholousekpicons.usersats.value, config.plugins.chocholousekpicons.resolution.value ) ]   )

        self.downloadPreviewPicons()
        self.rebuildConfigList()

    def getCursorEntry(self):
        return self["config"].getCurrent()[0]

    def getCursorValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def keyToLeft(self):
        ConfigListScreen.keyLeft(self)
        self.rebuildConfigList()

    def keyToRight(self):
        ConfigListScreen.keyRight(self)
        self.rebuildConfigList()

    def keyToOk(self):
        k = self.getCursorEntry()
        if k == _('Satellite positions'):
            self.session.openWithCallback(self.satellitesConfigScreenReturn, satellitesConfigScreen, self.getAllSat())
        elif k == _('User defined folder'):
            self.keyOK()
    
    def satellitesConfigScreenReturn(self, retval):
        if retval:
            self.loadChochoContent()        # if there has been a change in the necessary satellites settings, then I need to rescan the available picon styles (by default picon resolution)
            self.reloadAvailableBackgrounds()
            self.changedEntry()
            self.rebuildConfigList()

    def keyToUpdatePicons(self):
        if self.bin7zip:
            self.session.open(piconsUpdateJobScreen, self.chochoContent, self.bin7zip)
        else:
            self.check7zip()

    def keyToUpdatePlugin(self):
        global pluginUpdateDo, plugin_version_local
        if pluginUpdateDo():
            message = _("The plugin has been updated to the new version.\nA quick reboot is required.\nDo a quick reboot now ?")
            self.session.openWithCallback(self.restartEnigmaOrCloseScreen, MessageBox, message, type = MessageBox.TYPE_YESNO, default = False)
        else:
            message = _("Plugin version is up to date.\n\n"
                        "Installed version: %s") % (plugin_version_local)
            self.session.open(MessageBox, message, type = MessageBox.TYPE_INFO, timeout = 10)

    def exitWithSave(self):
        self.exitWithConditionalSave(True)

    def exitWithoutSave(self):
        self.exitWithConditionalSave(False)

    def keyToExit(self):
        if self['txt_green'].getText().endswith('*'):       # plugin configuration changed...? if so, then I invoke the MessageBox with the option to save or restore the original settings in the plugin configuration
            message = _("You have changed the plugin configuration.\nDo you want to save all changes now ?")
            self.session.openWithCallback(self.exitWithConditionalSave, MessageBox, message, type = MessageBox.TYPE_YESNO, timeout = 0, default = True)
        else:
            self.exitWithConditionalSave(False)

    def exitWithConditionalSave(self, condition=True):      # save or cancel changes made to the plugin's user configuration, default=True -> to save the configuration
        if condition:
            for x in self['config'].list:
                x[1].save()
            configfile.save()                               # '/etc/enigma2/settings' - the configuration file will be saved only when the Enigma is stopped or restarted
        else:
            for x in self['config'].list:
                x[1].cancel()
        self.close()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
        self['txt_green'].setText(_('Save & Exit') + '*')
        k = self.getCursorEntry()
        if k == _('Picon resolution'):
            self.reloadAvailableBackgrounds()               # reload all available backgrounds/styles for the new changed picon resolution
        #elif k == _('Picon background'):
        #    self.showPreviewImage()

    def rebuildConfigList(self):
        self.list = []
        self.list.append(getConfigListEntry( _('Picon folder')    ,  config.plugins.chocholousekpicons.piconFolder ))
        if config.plugins.chocholousekpicons.piconFolder.value == '(user defined)':
            self.list.append(getConfigListEntry( _('User defined folder'), config.plugins.chocholousekpicons.piconFolderUser ))
        self.list.append(getConfigListEntry( _('Picon update method'), config.plugins.chocholousekpicons.method    ))
        self.list.append(getConfigListEntry( _('Satellite positions'), config.plugins.chocholousekpicons.usersats  ))
        self.list.append(getConfigListEntry( _('Picon resolution') , config.plugins.chocholousekpicons.resolution  ))
        self.list.append(getConfigListEntry( _('Picon background') , config.plugins.chocholousekpicons.background , _('Choose picon design')  ))
        
        self['config'].list = self.list
        self['config'].setList(self.list)           # self['config'].setList(self.list)
        
        self.showPreviewImage()

    def restartEnigmaOrCloseScreen(self, answer = None):
        if answer:
            self.session.open(TryQuitMainloop, 3)   # 0=Toggle Standby ; 1=Deep Standby ; 2=Reboot System ; 3=Restart Enigma ; 4=Wake Up ; 5=Enter Standby   ### FUNGUJE po vyvolani a uspesnom dokonceni aktualizacie PLUGINu   ### NEFUNGUJE pri zavolani z funkcie leaveSetupScreen(self) po aktualizacii picon lebo vyhodi chybu: RuntimeError: modal open are allowed only from a screen which is modal!
        else:
            self.close()

    def showPreviewImage(self):
        self['previewImage'].instance.setPixmapFromFile(self.getPreviewImagePath())
        self['previewImage'].instance.setScale(0)

    def getPreviewImagePath(self):
        imgpath = PLUGIN_PATH + 'images/nova-cz-' + config.plugins.chocholousekpicons.background.value + '-' + config.plugins.chocholousekpicons.resolution.value + '.png'
        if os_path.isfile(imgpath):
            return imgpath
        else:
            return PLUGIN_PATH + 'images/image_not_found.png'

    def downloadPreviewPicons(self):
        """
        download preview picons if neccessary, i.e. download archive file into the plugin folder and extract all preview picons
        the online version will be detected from the http request header
        the  local version will be detected from the existing local file
        archive filename example:         nova-cz-(all)_by_chocholousek_(191020).7z         (the parentheses will replace by underline characters)
        files inside the archive file:    nova-cz-transparent-220x132.png ; nova-cz-gray-400x240.png
        """
        self.check7zip()
        if not self.bin7zip:
            return

        localfilenamefull = glob.glob(PLUGIN_PATH + 'nova-cz-*.7z')
        if localfilenamefull:
            localfilenamefull = localfilenamefull[0]                                                # simple converting the list type to string type
        else:
            localfilenamefull = '___(000000).7z'                                                    # version 000000 as very low version means to download a preview images from internet in next step
        url = 'https://drive.google.com/uc?export=download&id=1wX6wwhTf2dJ30Pe2GWb20UuJ6d-HjERA'    # .7z archive with preview images (NOVA channel picons for all styles but not for all resolutions)
        try:
            rq = urllib2.urlopen(url)
        except urllib2.URLError as e:
            print('Error %s when reading from URL: %s' % (e.reason, url))
        except Exception as e:
            print('Error: %e, URL: %s' % (e, url))
        else:
            onlinefilename = rq.headers['Content-Disposition'].split('"')[1].replace('(','_').replace(')','_')      # get file name from html header and replace the parentheses by underline characters
            if onlinefilename[-10:-4] > localfilenamefull[-10:-4]:                                  # comparsion, for example as the following:   '191125' > '191013'
                self.deleteFile(localfilenamefull)
                localfilenamefull = PLUGIN_PATH + onlinefilename
                data = rq.read()
                with open(localfilenamefull, 'w') as f:
                    f.write(data)

                # extracting .7z archive (picon preview images):
                self.deleteFile(PLUGIN_PATH + 'images/nova-cz-*.png')
                status, out = getstatusoutput('%s e -y -o%s %s nova-cz-*.png' % (self.bin7zip, PLUGIN_PATH + 'images', localfilenamefull) )
                
                # check the status error and clean the archive file (will be filled with a short note)
                if status == 0:
                    print('MYDEBUGLOGLINE - Picon preview files v.%s were successfully updated. The archive file was extracted into the plugin directory.' % localfilenamefull[-10:-4] )
                    with open(localfilenamefull, 'w') as f:
                        f.write('This file was cleaned by the plugin algorithm. It will be used to preserve the local version of the picon preview images.')
                elif status == 32512:
                    print('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:  opkg update && opkg install p7zip\n' % status)
                    self.deleteFile(localfilenamefull)
                elif status == 512:
                    print('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, localfilenamefull) )
                    self.deleteFile(localfilenamefull)
                else:
                    print('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
                    self.deleteFile(localfilenamefull)

    def deleteFile(self, directorymask):
        lst = glob.glob(directorymask)
        if lst:
            for file in lst:
                os_remove(file)

    def check7zip(self):
        if not self.find7zip():
            message = _('The 7-zip archiver was not found on your system.\nThere is possible to update the 7-zip archiver now in two steps:\n\n(1) try to install via package manager "opkg install p7zip"\n...or...\n(2) try to download the binary file "7za" (standalone archiver) from the internet\n\nDo you want to try it now?')
            self.session.openWithCallback(self.download7zip, MessageBox, message, type = MessageBox.TYPE_YESNO, default = True)

    def find7zip(self):
        if os_path.isfile('/usr/bin/7za'):
            self.bin7zip = '/usr/bin/7za'
            return True
        elif os_path.isfile('/usr/bin/7z'):
            self.bin7zip = '/usr/bin/7z'
            return True
        else:
            self.bin7zip = ''
            return False

    def download7zip(self, result):
        if result:
            os_system('opkg update > /dev/null 2>&1')
            if not os_system('opkg list | grep p7zip > /dev/null 2>&1'):   # if no error received from opkg manager, then...
                os_system('opkg install p7zip')
                self.message = _('The installation of the 7-zip archiver from the Enigma2\nfeed server was successful.')
            else:
                arch = self.getChipsetArch()
                if 'mips' in arch:
                    filename = '7za_mips32el'
                elif 'arm' in arch:
                    filename = '7za_cortexa15hf-neon-vfpv4'
                elif 'aarch64' in arch:
                    filename = '7za_aarch64'
                elif 'sh4' in arch or 'sh_4' in arch:
                    filename = '7za_sh4'
                else:
                    filename = 'ERROR_-_UNKNOWN_CHIPSET_ARCHITECTURE'
                #if not os_system('wget -q --no-check-certificate -O /usr/bin/7za "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/7za/%s" > /dev/null 2>&1' % filename):  # if no error received from os_system, then...
                if downloadFile('https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/7za/%s' % filename , '/usr/bin/7za'):
                    os_system('chmod 755 /usr/bin/7za')
                    if os_system('/usr/bin/7za'):                   # let's try to execute the binary file cleanly    # if some error number was received from the 7za executed binary file, then...
                        os_remove('/usr/bin/7za')                   # remove the binary file on error - because of a incorect binary file for the chipset architecture !!!
                    else:
                        self.message = _('Installation of standalone "7za" (7-zip) archiver was successful.')
            if self.find7zip():
                self.session.open(MessageBox, self.message, type = MessageBox.TYPE_INFO)        # MessageBox with message about successful installation - either a standalone binary file or an ipk package
            else:
                self.session.open(MessageBox, _('Installation of 7-zip archiver failed!'), type = MessageBox.TYPE_ERROR)

    def getChipsetArch(self):
        '''
        detecting chipset architecture
        mips32el, armv7l, armv7a-neon, armv7ahf, armv7ahf-neon, cortexa9hf-neon, cortexa15hf-neon-vfpv4, aarch64, sh4, sh_4
        '''
        status, out = getstatusoutput('opkg print-architecture | grep -E "arm|mips|cortex|aarch64|sh4|sh_4"')       # returns a pair of data, the first is an error code (0 if there are no problems) and the second is std.output (complete command-line / Shell text output)
        if status == 0:
            return out.replace('arch ','').replace('\n',' ')        # return architectures by OPKG manager, such as:  'mips32el 16 mipsel 46'

        t = re.findall('isa\s*:\s*(.*)\n+', open('/proc/cpuinfo','r').read() )
        if t:
            return t[0]                                             # return list type converted to a string value, like as:  'mips1 mips2 mips32r1'

        status, out = getstatusoutput('uname -m')
        if status == 0:
            return out                                              # return architectures from system, like as:  'mips'

        print('MYDEBUGLOGLINE - Error! Could not get information about chipset-architecture! Returning an empty string!')
        return ''

    #def createDefaultPiconDir(self):
    #   if not os_path.exists('/usr/share/enigma2/picon'):
    #       os_makedirs('/usr/share/enigma2/picon')

    ###########################################################################

    def loadChochoContent(self):
        self.downloadChochoFile()
        path = glob.glob(PLUGIN_PATH + 'id_for_permalinks*.log')
        if path:
            with open(path[0],'r') as f:            # full path-name as the string from list index 0
                txt = f.read()
        else:
            txt = ''
            print('MYDEBUGLOGLINE - Warning! The file %s was not found on the internet but also on the internal disk.' % (PLUGIN_PATH + 'id_for_permalinks*.log'))
        self.chochoContent = txt

    def downloadChochoFile(self):
        '''
        checking new online version, download if neccessary and load the content from file with the list of all IDs for google.drive download
        the online version will be detected from the http request header
        the  local version will be detected from the existing local file
        file name example:   id_for_permalinks191017.log
        example entry from inside the file:   1xmITO0SouVDTrATgh0JauEpIS7IfIQuB              piconblack-220x132-13.0E_by_chocholousek_(191016).7z                              bin   16.3 MB    2018-09-07 19:40:54
        '''
        url = 'https://drive.google.com/uc?export=download&id=1oi6F1WRABHYy8utcgaMXEeTGNeznqwdT'    # id_for_permalinks191017.log -- means the chochoFile for the chochoContent value :)

        pathlist = glob.glob(PLUGIN_PATH + 'id_for_permalinks*.log')
        if pathlist:
            localfilenamefull = pathlist[0]                                             # string converted as from list[0]
        else:
            localfilenamefull = PLUGIN_PATH + 'id_for_permalinks000000.log'             # low version, to force update the file (as the first download)

        try:
            rq = urllib2.urlopen(url)
        except urllib2.URLError as err:
            print('Error %s when reading from URL: %s' % (err.reason, url)  )
        except Exception:
            print('Error when reading URL: %s' % url)
        else:
            onlinefilename = rq.headers['Content-Disposition'].split('"')[1]            # get filename from html header
            if onlinefilename[-10:-4] > localfilenamefull[-10:-4]:                      # comparsion, for example as the following:   '191125' > '191013'
                txt = rq.read()
                with open(PLUGIN_PATH + onlinefilename, 'w') as f:
                    f.write(txt)
                if os_path.exists(localfilenamefull):
                    os_remove(localfilenamefull)
                print('MYDEBUGLOGLINE - file id_for_permalinks*.log was updated to new version: %s' % onlinefilename)

    def reloadAvailableBackgrounds(self):
        '''
        reload all available picon-backgrounds (picon-styles)
        by user selected configuration
        (by user configuration in the plugin MENU)
        '''
        config.plugins.chocholousekpicons.background = ConfigSelection( default = None ,   # default = config.plugins.chocholousekpicons.background.value  ,
          choices = [ (s, s) for s in self.getAllBckByUserCfg( config.plugins.chocholousekpicons.usersats.value, config.plugins.chocholousekpicons.resolution.value ) ]    )     # !!!! ( _(s),s ) biela/white nenajde subor s pikonami v slovencine:)
    
    def contentByUserCfgSatRes(self, satellites, resolution):
        result = []
        for line in self.chochoContent.splitlines():
            if resolution in line:
                for sat in satellites:
                    if sat in line:
                        result.append(line)
                        continue
        return '\n'.join(result)            # return = a very long string with "\n" newlines

    def getAllBckByUserCfg(self, sats, res):
        userdata = self.contentByUserCfgSatRes(sats, res)
        return sorted(list(set(  re.findall('.*picon(.*)-%s-.*' % (res), userdata)  )))    # using the set() to remove duplicites and the sorted() to sort the list by ASCII

    def getAllSat(self): # Satellites
        lst = re.findall('.*piconblack-220x132-(.*)_by_chocholousek_.*\n+', self.chochoContent)
        lst.sort(key = self.fnSort)
        #print('MYDEBUGLOGLINE - getAllSat = %s' % lst)
        return lst

    def fnSort(self, s):
        if s[0].isdigit():
            if s.endswith('E'):
                return float(s[:-1]) + 500
            if s.endswith('W'):
                return float(s[:-1]) + 1000
        else:
            return 0

    #def getAllRes(self):       # all picon resolutions
    #    tmp = list(set(re.findall('.*picon.*-([0-9]+x[0-9]+)-23\.5.*\n+', self.chochoContent)))
    #    tmp = [int(x) for x in tmp]     # simple sort method for numeric strings (better as the .sort() method)
    #    return tmp

    #def getAllBck(self):       # all picon backgrounds (styles)
    #    return re.findall('.*picon(.*)-220x132-23\.5.*\n+', self.chochoContent)


###########################################################################
###########################################################################


class satellitesConfigScreen(Screen, ConfigListScreen):

    if sizemaxX > 1900:    # Full-HD or higher
        skin = '''
        <screen name="satellitesConfigScreen" position="center,center" size="450,900" title="Satellite positions" flags="wfNoBorder" backgroundColor="#44000000">
            <widget name="config"    position="center,120" size="350,700" font="Regular;30" itemHeight="32" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#22000000" />
            <widget name="title_txt" position="center,40"  size="350,60"  font="Regular;42" foregroundColor="yellow" transparent="1" halign="center" valign="top" />
            
            <ePixmap pixmap="skin_default/buttons/green.png" position="25,854" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <widget render="Label" source="txt_green"        position="65,854" size="250,46" halign="left" valign="center" font="Regular;28" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''
    else:                   # HD-ready or lower
        skin = '''
        <screen name="satellitesConfigScreen" position="center,center" size="350,600" title="Satellite positions" flags="wfNoBorder" backgroundColor="#44000000">
            <widget name="config"    position="center,70" size="300,470" font="Regular;22" itemHeight="23" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#22000000" />
            <widget name="title_txt" position="center,20" size="300,40"  font="Regular;24" foregroundColor="yellow" transparent="1" halign="center" valign="top" />
            
            <ePixmap pixmap="skin_default/buttons/green.png" position="20,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <widget render="Label" source="txt_green"        position="55,560" size="140,40" halign="left" valign="center" font="Regular;22" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''

    def __init__(self, session, satList):

        self.allSat = satList

        Screen.__init__(self, session)

        self.onChangedEntry = []
        self.list = []

        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        self.lineHeight = 1             # for text height auto-correction on dmm-enigma2 (0 = enable auto-correction ; 1 = disable auto-correction)

        self['title_txt'] = Label(_('Select satellites:'))
        self['txt_green'] = StaticText(_('OK'))

        self["actions"] = ActionMap( ["SetupActions", "ColorActions"], 
        {
            'left'  : self.keyToLeft,
            'right' : self.keyToRight,
            'green' : self.keyToExit,
            'ok'    : self.keyToExit,
            'cancel': self.keyToExit
        }, -2)

        if newOE():
            i = satellitesConfigScreen.skin.index('font')
            self.skin = satellitesConfigScreen.skin[ : i ] + satellitesConfigScreen.skin[ i+34 : ]
        else:
            self.skin = satellitesConfigScreen.skin
        
        self.onShown.append(self.rebuildConfigList)

    def keyToLeft(self):
        ConfigListScreen.keyLeft(self)
        self.switchSelectedSat()
        self.rebuildConfigList()

    def keyToRight(self):
        ConfigListScreen.keyRight(self)
        self.switchSelectedSat()
        self.rebuildConfigList()

    def switchSelectedSat(self):
        selected = self['config'].getCurrent()[0]                               # value example:   '23.5E'
        if selected in config.plugins.chocholousekpicons.usersats.value:        # list example:    ['19.2E', '23.5E']
            config.plugins.chocholousekpicons.usersats.value.remove(selected)
        else:
            config.plugins.chocholousekpicons.usersats.value.append(selected)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        self['txt_green'].setText(_('OK') + '*')

    def rebuildConfigList(self):
        self.list = []
        for sat in self.allSat:
            if sat in config.plugins.chocholousekpicons.usersats.value:
                self.list.append(  getConfigListEntry( sat, ConfigYesNo(default=True)  ) )
            else:
                self.list.append(  getConfigListEntry( sat, ConfigYesNo(default=False) ) )
        self['config'].list = self.list
        self['config'].setList(self.list)           # self['config'].setList(self.list)

    def keyToExit(self):
        self.s = self['txt_green'].getText()
        if self.s[-1:] == '*':                      # plugin configuration changed...?
            self.close(True)
        else:
            self.close(False)


###########################################################################
###########################################################################


class piconsUpdateJobScreen(Screen):

    skin = '''
        <screen name="piconsUpdateJobScreen" position="center,center" size="''' + str(sizemaxX - 80) + ',' + str(sizemaxY - 80) + '''" title="picons update in progress" flags="wfNoBorder" backgroundColor="#22000000">
            <widget name="logWindow" position="center,center" size="''' + str(sizemaxX - 180) + ',' + str(sizemaxY - 180) + '''" font="Regular;''' + (str(26) if sizemaxX > 1900 else str(18)) + '''" transparent="0" foregroundColor="white" backgroundColor="#11330000" zPosition="3" />
        </screen>'''

    def __init__(self, session, chochoContent, bin7zip):

        self.chochoContent = chochoContent
        self.bin7zip = bin7zip

        Screen.__init__(self, session)
        #self.session = session          # this is not necessary, this is done already during class initialization - Screen.__init__

        self['logWindow'] = ScrollLabel('LOG:\n')
        self['logWindow'].scrollbarmode = "showOnDemand"
        
        self['actions'] = ActionMap( ['SetupActions','DirectionActions'], {
            "up"    :  self["logWindow"].pageUp,
            "left"  :  self["logWindow"].pageUp,
            "down"  :  self["logWindow"].pageDown,
            "right" :  self["logWindow"].pageDown
            }, -1)
        
        self.piconCounters = {'added' : 0, 'changed' : 0, 'removed' : 0}
        self.startTime = datetime.now()
        
        self.th = threading.Thread(target = self.threadProcess)
        self.th.daemon = True
        self.th.start()             # start thread process
        self.onClose.append(self.th.join)
        
        #self.onLayoutFinish.append(self.mainFunc)
        #self.onShown.append(self.mainFunc)
        #self.onClose.append(self.nazov_funkcie)
        
    def threadProcess(self):
        
        boo, msg = self.mainFunc()
        # boo = True ------ close the class Screen with some error
        # boo = False ----- close the class Screen without error
        # msg = <string> -- warning/sucessful message for MessageBox()
        
        if boo:
            type = MessageBox.TYPE_ERROR
            if not msg:
                msg = _('Some errors has occurred !')
        else:
            type = MessageBox.TYPE_INFO
            if not msg:
                msg = _('Done !') + '\n' + _('(%s added / %s changed / %s removed)') % (self.piconCounters['added'] , self.piconCounters['changed'] , self.piconCounters['removed'])
        self.writeLog(msg)
        sleep(3)
        
        self.session.open(MessageBox, msg, type)
        
        self['logWindow'].hide()                    # for smoother transition from MessageBox window to plugin initial menu (without flashing 'logWindow')
        self.close()
    
    def mainFunc(self):
        
        # 1) Ocheckuje sa internetové pripojenie
        if os_system('ping -c 1 www.google.com > /dev/null 2>&1'):          #  removed the argument -w 1 due to incompatibility with SatDreamGr enigma image
            return True, _("Internet connection is not available !")
        else:
            self.writeLog(_('Internet connection is OK.'))

        # 2) Vytvorí sa zoznam dostupných userbouquets súborov "/etc/enigma2/userbouquet.*.tv"
        #    prípadne aj "/etc/enigma2/userbouquet.*.radio" súborov    
        self.bouqet_list = []
        if config.plugins.chocholousekpicons.method.value == 'sync_tv':
            self.bouqet_list = glob.glob('/etc/enigma2/userbouquet.*.tv')
        if config.plugins.chocholousekpicons.method.value == 'sync_tv_radio':
            self.bouqet_list.extend(glob.glob('/etc/enigma2/userbouquet.*.radio'))
        if config.plugins.chocholousekpicons.method.value != 'all' and not self.bouqet_list:
            return True, _('No userbouquet files found !\nPlease check the folder /etc/enigma2 for the userbouquet files.')

        # 3) Skontroluje sa existencia zložky s pikonami na disku (ak zložka neexistuje, vytvorí sa nová)
        if config.plugins.chocholousekpicons.piconFolder.value == '(user defined)':
            self.piconDIR = config.plugins.chocholousekpicons.piconFolderUser.value
        else:
            self.piconDIR = config.plugins.chocholousekpicons.piconFolder.value
        if not os_path.exists(self.piconDIR):
            os_makedirs(self.piconDIR)
        #if not os_path.exists(self.piconDIR):
        #    return True, _('The configured picon folder does not exist!\nPlease check the picon folder in plugin configuration.\nCurrent picon folder: %s') % (self.piconDIR)
        
        if 'sync' in config.plugins.chocholousekpicons.method.value:
        # 4.A) Vytvorí sa zoznam serv.ref.kódov nájdených vo všetkych userbouquet súboroch v set-top boxe (vytiahnem z nich len servisné referenčné kódy)        
            self.writeLog(_('Preparing a list of picons from userbouquet files.'))
            self.SRC_in_Bouquets = ''
            for bq_file in self.bouqet_list:
                self.SRC_in_Bouquets += open(bq_file,'r').read()
                #with open(bq_file) as f:
                #    self.SRC_in_Bouquets += f.read()
            self.SRC_in_Bouquets = re.findall('.*#SERVICE\s([0-9a-fA-F]+_0_[0-9a-fA-F_]+0_0_0).*\n*', self.SRC_in_Bouquets.replace(":","_") )
            self.SRC_in_Bouquets = list(set(self.SRC_in_Bouquets))              # remove duplicate items ---- converting to <set> and then again back to the <list>
            self.writeLog(_('...done.'))
        else:
        # 4.B) Vytvorí sa fiktívny t.j. prázdny zoznam SRC kódov z userbouquet zoznamov, aby v ďalšiom kroku boli všetky aktuálne pikony na lokálnom disku vymazané (metóda bez synchronizácie pikon s userbouquets)
            self.SRC_in_Bouquets = []
        
        # 5) Vytvorí sa zoznam picon uložených na lokálnom disku (v internom flash-disku alebo na externom USB či HDD) - včetne veľkostí týchto súborov !
        self.writeLog(_('Preparing a list of picons from the picon directory on the local disk.'))
        self.SRC_in_HDD = {}
        dir_list = glob.glob(self.piconDIR + '/*.png')
        if dir_list:
            for path_N_file in dir_list:
                self.SRC_in_HDD.update( { path_N_file.split("/")[-1].split(".")[0]  :   int(os_path.getsize(path_N_file))  } )     # os.stat.st_time('/etc/enigma2/'+filename)

        # 6) Vymažú sa neexistujúce picon-súbory na disku v set-top-box-e, ktoré sú zbytočné, nakoľko neexistujú tiež v žiadnom userbouquet súbore a teda na disku budú iba zavadziať
        self.writeLog(_('Deleting unneccessary picons from local disk...'))
        self.SRC_to_Delete = list(  set(self.SRC_in_HDD.keys()) - set(self.SRC_in_Bouquets)  )
        for src in self.SRC_to_Delete:
            os_remove(self.piconDIR + '/' + src + '.png')       # v OpenATV nedostavam v adresaroch aj znak lomitka naviac, takze ho tu musim pridavat
            #os_remove(self.piconDIR + src + '.png')            # v OpenPLi dostavam v adresaroch aj znak lomitka naviac, takze ho tu netreba pridavat
            self.piconCounters['removed'] += 1
        self.writeLog(_('...%s picons deleted.') % self.piconCounters['removed'] )
        
        # 7) Pripraví sa zoznam názvov všetkých súborov .7z na sťahovanie z internetu - podľa konfigurácie pluginu
        self.filesForDownload = []
        for sat in config.plugins.chocholousekpicons.usersats.value:            # example:  ['19.2E','23.5E']
            self.filesForDownload.append('picon%s-%s-%s_by_chocholousek' % (config.plugins.chocholousekpicons.background.value , config.plugins.chocholousekpicons.resolution.value , sat)   )
        
        # 8) Ďalej sa v cykle stiahnú z internetu a spracujú sa všetky používateľom zafajknuté archívy s piconami - spracuvávajú sa po jednom (pre viac družíc - postupne každý jeden archív sa stiahne a spracuje)
        self.writeLog(_('The process started...') + ' ' + _('(downloading and extracting all necessary picons)')  )
        self.writeLog('#' * 40)
        for count, fname in enumerate(self.filesForDownload, 1):
            s = ' %s / %s ' % (count, len(self.filesForDownload))
            self.writeLog('-' * 16 + s.ljust(20,'-'))
            self.proceedArchiveFile(fname)
        self.writeLog('#' * 40)
        self.writeLog(_('...the process is complete.') + ' ' + _('(downloading and extracting all necessary picons)')  )
        
        # 9) Nakoniec sa zobrazí výsledok celého procesu do konzoly a zavolá sa "ukončovacia procedúra" (metóda) pod aktuálnou triedou, určenou na updatovanie pikon
        if self.piconCounters['added'] or self.piconCounters['changed']:
            message = _('After updating the picons you may need to restart the Enigma (GUI).') + '\n' + _('(%s added / %s changed / %s removed)') % (self.piconCounters['added'] , self.piconCounters['changed'] , self.piconCounters['removed'])
        else:
            message = _('No picons added or changed.') + '\n' + _('(%s added / %s changed / %s removed)') % (self.piconCounters['added'] , self.piconCounters['changed'] , self.piconCounters['removed'])
        return False, message
    
    def proceedArchiveFile(self, search_filename):

        # 1. Vyhľadanie google.drive ID - kódu v "chochoContent", pre konkrétny súbor (pre potrebu jeho následovného stiahnutia)
        found = []
        for line in self.chochoContent.splitlines():
            if search_filename in line:
                found = line.split()
                break
        if not found:
            self.writeLog(_('Download ID for file %s was not found!') % search_filename)
            return
        url_link = 'https://drive.google.com/uc?export=download&id=' + found[0]
        dwn_filename = found[1].replace('(','_').replace(')','_')               # replace the filename mask by new original archive filename and replace the parentheses by underline characters

        # 2. Stiahnutie archívu z internetu (súboru s piconami) do zložky "/tmp"
        self.writeLog(_('Trying download the file archive... %s') % dwn_filename)
        if not downloadFile(url_link, '/tmp/' + dwn_filename):
            self.writeLog(_('...file download failed !'))
            return
        else:
            self.writeLog(_('...file download successful.'))
        
        # 3. Načítanie zoznamu všetkých .png súborov z archívu, včetne ich atribútov (veľkostí súborov)
        #self.writeLog(_('Browse the contents of the downloaded archive file.'))
        self.SRC_in_Archive = self.getPiconListFromArchive('/tmp/' + dwn_filename)
        if not self.SRC_in_Archive:
            self.writeLog(_('Error! No picons found in the downloaded archive file!'))
            return          # navratenie vykonavania kodu z tohto podprogramu pre spracovanie dalsieho archivu/suboru s piconami v poradi

        # 4. Rozbalenie pikon zo stiahnutého archívu
        self.writeLog(_('Extracting files from the archive...'))
        if 'all' == config.plugins.chocholousekpicons.method.value:
            #### Ak používateľ zvolil v plugin-konfigurácii metódu aktualizácie všetkých pikon - kópiou pikon z archívu) tak...
            self.piconCounters['added'] += len(self.SRC_in_Archive)
            self.extractAllPiconsFromArchive('/tmp/' + dwn_filename)
            self.writeLog(_('...%s picons was extracted from the archive.') % len(self.SRC_in_Archive))
        else:        
            #### V prípade metódy synchronizácie, prebehne rozbalenie a prepísanie iba potrebných picon (podľa listu potrebných piconiek)
            # (A) ak meno súboru na disku už existuje, tak potom porovnam veľkosť týchto dvoch súborov a ak sa nezhodujú tak súbor nakopírujem (prepíšem) z archívu na disk
            # (B) ak meno súboru na disku ešte vôbec neexistuje, tak súbor jednoducho nakopírujem z archívu na disk
            self.writeLog(_('Preparing picon list for extracting (missing files and files of different sizes).'))
            self.SRC_to_Extract = []
            # Zaujímam sa iba o tie picony z archívu, ktoré sa nachádzajú zároveň v zozname SRC_in_Bouquets a zároveň v zozname SRC_in_Archive
            # Tzn. že budem prechádzať len zoznam zhodných pikon v archíve + v bouquets ... zoznam zhodných prvkov získam pomocou operácie s množinami:  set(A) & set(B)
            for src in set(self.SRC_in_Archive) & set(self.SRC_in_Bouquets):
                if src in self.SRC_in_HDD:                                  # ak sa uz konkretna pikona z archivu nachadza na HDD, tak...
                    if self.SRC_in_HDD[src] != self.SRC_in_Archive[src]:    # porovnam este velkosti tychto dvoch pikon (Archiv VS. HDD) a ak su velkosti picon odlisne...
                        self.SRC_to_Extract.append(src)                     # tak pridam tuto pikonu na zoznam kopirovanych pikon (zoznam pikon na extrahovanie)
                        self.piconCounters['changed'] += 1
                    else:
                        pass
                else:                                                       # ak sa pikona zo zoznamu "potrebnych" este nenachadza na HDD, tak...
                    self.SRC_to_Extract.append(src)                         # musim tuto pikonu pridat na zoznam kopirovanych (zoznam pikon na extrahovanie)
                    self.piconCounters['added'] += 1
                self.SRC_in_Bouquets.remove(src)                            # tuto pikonu uz viac nebudem musiet kopirovat na HDD, ak by sa nachadzala dalsia kopia aj v inych stiahnutych archivoch, takze ju odstranim zo zoznamu SRC_in_Bouquets
            # Extrahovanie vybraných konkrétnych pikon (len v prípade, že sú tam nejaké pikony na extrahovanie)
            if self.SRC_to_Extract:
                self.extractCertainPiconsFromArchive('/tmp/' + dwn_filename , self.SRC_to_Extract)
            self.writeLog(_('...%s picons was extracted from the archive.') % len(self.SRC_to_Extract))
        os_remove('/tmp/' + dwn_filename)

    def getPiconListFromArchive(self, archiveFile = ''):
        #t = subprocess.Popen([self.bin7zip, 'l', archiveFile], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        #status, out = t.returncode, t.communicate()[0]
        status, out = getstatusoutput('%s l %s' % (self.bin7zip, archiveFile) )     # returns a pair of data, the first is an error code (0 if there are no problems) and the second is std.output (complete command-line / Shell text output)
        if status == 0:
            out = out.splitlines()
            tmp = {}
            i = -3
            while not "-----" in out[i]:
                # vycucnem udaje z vystupu Shell-u, vsetky subory (jednotlivo po riadkoch):
                # index: 0----------------19 20-25    26-----38               53-------------------------->
                # out:   2018-07-14 14:48:53 ....A          797               CONTROL/postinst
                fdatetime, fattr, fsize, fpath = out[i][0:19] , out[i][20:25] , out[i][26:38] , out[i][53:]
                if fattr[0] != 'D':         # retreive all files with a full path, but no individual directories from the list
                    tmp.update({  fpath.split('/')[-1].split('.')[0]  :  int(fsize)  })            # { "service_reference_code_<as_a_string-dictionary_key>"  :  file_size_<as_a_integer> }
                i -= 1
            return tmp
        elif status == 32512:
            self.writeLog('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:  opkg update && opkg install p7zip\n' % status)
        elif status == 512:
            self.writeLog('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, archiveFile) )
        else:
            self.writeLog('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out) )
        return ''         # return the empty string on any errors !
    
    def extractCertainPiconsFromArchive(self, archiveFile, SRC_list):
        with open('/tmp/picons-to-extraction.txt', 'w') as f:
            f.write('.png\n'.join(SRC_list) + '.png\n')
        status, out = getstatusoutput('%s e -y -o%s %s @/tmp/picons-to-extraction.txt' % (self.bin7zip, self.piconDIR, archiveFile)  )
        os_remove('/tmp/picons-to-extraction.txt')
        if status == 0:
            return True
        elif status == 32512:
            self.writeLog('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:  opkg update && opkg install p7zip\n' % status)
        elif status == 512:
            self.writeLog('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, archiveFile) )
        else:
            self.writeLog('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
        return False
    
    def extractAllPiconsFromArchive(self, archiveFile):
        status, out = getstatusoutput('%s e -y -o%s %s' % (self.bin7zip, self.piconDIR, archiveFile) )
        if status == 0:
            return True
        elif status == 32512:
            self.writeLog('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package:  opkg update && opkg install p7zip\n' % status)
        elif status == 512:
            self.writeLog('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, archiveFile) )
        else:
            self.writeLog('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
        return False

    def writeLog(self, msg = ''):
        print(msg)
        self['logWindow'].appendText('\n[' + str(( datetime.now() - self.startTime).total_seconds()).ljust(10,"0")[:6] + '] ' + msg)
        self['logWindow'].lastPage()


###########################################################################
###########################################################################


def findHostnameAndNewPlugin():
    '''
    return "" ----- if a new online version was not found
    return URL ---- if a new online version was found
    '''
    global plugin_version_local, plugin_version_online
    url_lnk = ''
    url_list = ['https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/released_build/', 'http://aion.webz.cz/ChocholousekPicons/']        # pozor ! je dolezite zachovat na konci retazca vo web.adresach vzdy aj lomitko, pre dalsie korektne pouzivanie tohoto retazca v algoritme
    for hostname in url_list:
        try:
            url_handle = urllib2.urlopen(hostname + 'version.txt')
        except urllib2.URLError as err:
            print('Error %s when reading from URL %s' % (err.reason, hostname + 'version.txt')  )
        except Exception:
            print('Error when reading URL %s' % hostname + 'version.txt')
        else:
            plugin_version_online = url_handle.read().strip()
            if plugin_version_online > plugin_version_local:    # Python 2.7 dokaze porovnat aj dva retazce... poradie porovnavania dvoch <str> je postupnostou hodnot znakov ASCII kodov v poradi z lava do prava a paradoxom v porovnani je, ze male znaky ASCII maju vyssiu hodnotu a preto su v porovnani <str> na vyssiej urovni ! v mojom pripade sa vsak jedna o cislice a tie su v ASCII kode rovnake (kod 0x30 az 0x39)
                url_lnk = hostname
                break
    return url_lnk

def pluginUpdateDo():
    '''
    return True ----- if a new version was successfull downloaded and installed
    return False ---- if a new version was not found
    '''
    global plugin_version_local, plugin_version_online
    url_host = findHostnameAndNewPlugin()
    if url_host:
        url_host = url_host + 'enigma2-plugin-extensions-chocholousek-picons_' + plugin_version_online + '_all.ipk'
        dwn_file = '/tmp/' + url_host.split('/')[-1]
        if downloadFile(url_host, dwn_file):
            os_system("opkg install --force-reinstall %s > /dev/null 2>&1" % dwn_file)
            print('New plugin version was installed ! old ver.:%s , new ver.:%s' % (plugin_version_local, plugin_version_online)  )
            plugin_version_local = plugin_version_online
            return True
        else:
            return False
    else:
        print('New plugin version is not available - local ver.:%s , online ver.:%s' % (plugin_version_local, plugin_version_online)  )
        return False


###########################################################################
###########################################################################


def downloadFile(url, targetfile):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    cookie_jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)
    try:
        req = urllib2.Request(url, data=None, headers=headers)
        handler = urllib2.urlopen(req)
        if 'drive.google' in url:
            for c in cookie_jar:
                if c.name.startswith('download_warning'):                    # in case of drive.google download a virus warning message is possible (for some downloads)
                    url = url.replace('&id=','&confirm=%s&id=' % c.value)    # and then it's necessary to add a parameter with confirmation of the warning message
                    req = urllib2.Request(url, data=None, headers=headers)
                    handler = urllib2.urlopen(req)
                    break
        data = handler.read()
        with open(targetfile, 'wb') as f:
            f.write(data)
    except urllib2.HTTPError as e:
        print("HTTP Error: %s, URL: %s" % (e.code, url))
        return False
    except urllib2.URLError as e:
        print("URL Error: %s, URL: %s" % (e.reason, url))
        return False
    except IOError as e:
        print("I/O Error: %s, File: %s" % (e.reason, targetfile))
        return False
    except Exception as e:
        print("File download error: %s, URL: %s" % (e.message, url))
        return False
    return True

def getstatusoutput(cmd):
    try:
        t =  0 , check_output(shlexSplit(cmd))
    except CalledProcessError as e:
        t = e.returncode , e.message
    except Exception as e:
        t = -1 , e.message
    except:
        t = -1 , ''
    return t

def newOE():
    '''
    return True --- if Enigma is a newer OE version (OpenDreambox - OE2.5, ...)
    return False -- if Enigma is a older OE version (OpenATV, OpenPLi, VTi, ...)
    '''
    ####return os_path.exists('/etc/dpkg')
    try:
        from enigma import PACKAGE_VERSION
        major, minor, patch = [ int(n) for n in PACKAGE_VERSION.split('.') ]
        if major > 4 or major == 4 and minor >= 2:
            retval = True                       # newer OE version (OpenDreambox - OE2.5, ...)
        else:
            retval = False                      # older OE version (OpenATV, OpenPLi, VTi, ...)
    except:
        retval = False
    return retval


###########################################################################
###########################################################################


def pluginMenu(session, **kwargs):                          # starts when the plugin is opened via Plugin-MENU
    print('PLUGINSTARTDEBUGLOG - pluginMenu executed')
    global plugin_version_local
    plugin_version_local = open(PLUGIN_PATH + 'version.txt','r').read().strip()
    session.open(mainConfigScreen)

def sessionStart(reason, session):                         # starts after the Enigma2 (the session) booting
    if reason == 0:
        print('PLUGINSTARTDEBUGLOG - sessionStart executed, reason == 0')
        #session = kwargs['session']
    if reason == 1:
        print('PLUGINSTARTDEBUGLOG - sessionStart executed, reason == 1')
        session = None

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            where = PluginDescriptor.WHERE_SESSIONSTART,
            needsRestart = False,
            fnc = sessionStart),
        PluginDescriptor(
            where = PluginDescriptor.WHERE_PLUGINMENU,
            name = "Chocholousek picons",
            description = "Download and update Chocholousek picons",
            icon = "images/plugin.png",
            needsRestart = False,
            fnc = pluginMenu)
        ]
