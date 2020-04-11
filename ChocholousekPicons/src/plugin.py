# -*- coding: utf-8 -*-

###########################################################################
#  Enigma2 plugin, ChocholousekPicons, written by s3n0, 2018-2020
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
from Components.config import config, configfile, getConfigListEntry, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigSelection, ConfigYesNo, ConfigText, KEY_OK, NoSave
###########################################################################
import urllib2, ssl, cookielib
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass                                                                    # Legacy Python versions (for example v2.7.2) that doesn't verify HTTPS certificates by default
else:
    ssl._create_default_https_context = _create_unverified_https_context    # Handle target environment that doesn't support HTTPS verification --- https://www.python.org/dev/peps/pep-0476/
###########################################################################
import threading
import re
import glob
import random
###########################################################################
import os
from commands import getstatusoutput                                        # unfortunately "commands" module is removed in Python 3.x and therefore in the future, it is better to use a more complicated "subprocess"
#from subprocess import check_output, CalledProcessError                     # unfortunately "subprocess" module is supported only in Python 2.4 or newer version ... some older Enigmas as example OpenPLi-4 contains only old Python (missing subprocess module)
#from shlex import split as shlexSplit
from datetime import datetime
from time import sleep
###########################################################################
from enigma import ePicLoad, eActionMap, eTimer, eEnv, getDesktop
sizemaxY = getDesktop(0).size().height()
sizemaxX = getDesktop(0).size().width()
###########################################################################
from Plugins.Extensions.ChocholousekPicons import _, PLUGIN_PATH            # from . import _, PLUGIN_PATH
###########################################################################

config.plugins.chocholousekpicons = ConfigSubsection()

config.plugins.chocholousekpicons.picon_folder = ConfigSelection(
        default = '/usr/share/enigma2/picon' ,
        choices = [ 
            ('/usr/share/enigma2/picon'         , '/usr/share/enigma2/picon'),
            ('/usr/share/enigma2/XPicons/picon' , '/usr/share/enigma2/XPicons/picon'),
            ('/usr/share/enigma2/ZZPicons/picon', '/usr/share/enigma2/ZZPicons/picon'),
            ('/media/hdd/picon'                 , '/media/hdd/picon'),
            ('/media/hdd/XPicon/picon'          , '/media/hdd/XPicon/picon'),
            ('/media/hdd/ZZPicon/picon'         , '/media/hdd/ZZPicon/picon'),
            ('/media/usb/picon'                 , '/media/usb/picon'),
            ('/media/usb/XPpicon/picon'         , '/media/usb/XPpicon/picon'),
            ('/media/usb/ZZPicon/picon'         , '/media/usb/ZZPicon/picon'),
            ('/media/sdcard/picon'              , '/media/sdcard/picon'),
            ('/media/mmc/picon'                 , '/media/mmc/picon'),
            ('/data/picon'                      , '/data/picon'),
            ('/picon'                           , '/picon'),
            ('user_defined'                     ,_('(user defined)')  )
          ]
        )   # ---> paths are based on source code from here:  https://github.com/openatv/MetrixHD/blob/master/usr/lib/enigma2/python/Components/Renderer/MetrixHDXPicon.py
for picdir in config.plugins.chocholousekpicons.picon_folder.choices:
    if glob.glob(picdir[0] + '/*.png'):
        config.plugins.chocholousekpicons.picon_folder.default = picdir[0]      # change the default picon directory (on the first plugin start) if some picons (.PNG files) was found in some folder
        break

config.plugins.chocholousekpicons.picon_folder_user = ConfigText(default = '/', fixed_size = False)

config.plugins.chocholousekpicons.method = ConfigSelection(
        default = 'sync_tv',
        choices = [
                    ('all',           _('copy all: current will deleted')    ),
                    ('all_inc',       _('copy all: incremental update')      ),
                    ('sync_tv',       _('sync with TV userbouquets')         ),
                    ('sync_tv_radio', _('sync with TV+RADIO userbouquets')   )
                  ]
        )

config.plugins.chocholousekpicons.sats = ConfigText(default = '19.2E 23.5E', fixed_size = False)            # ConfigSubList()  /  ConfigSubDict()  /  ConfigDictionarySet()

limitedRes = [ 
                ('50x30'   ,      '"MiniPicons"   50x30'),
                ('100x60'  ,  '"InfobarPicons"   100x60'),
                ('150x90'  ,        '"HDGLASS"   150x90'),
                ('220x132' ,       '"XPicons"   220x132'),
                ('400x170' ,      '"ZZPicons"   400x170'),
                ('400x240' ,     '"ZZZPicons"   400x240'),
                ('500x300' ,                   '500x300') 
             ]
config.plugins.chocholousekpicons.resolution = ConfigSelection(
        default = '220x132',
        choices = limitedRes
        )

config.plugins.chocholousekpicons.background = ConfigSelection(
        default = None,
        choices = [( 'no_satellites_was_selected', _('first select the satellites') )]
        )



###########################################################################
###########################################################################
###########################################################################



session = None

plugin_version_local  = '0.0.000000'
plugin_version_online = '0.0.000000'



###########################################################################
###########################################################################
###########################################################################



class mainConfigScreen(Screen, ConfigListScreen):
    
    if sizemaxX > 1900:    # Full-HD or higher
        skin = '''
        <screen name="mainConfigScreen" position="center,center" size="1200,800" title="Chocholousek picons" flags="wfNoBorder" backgroundColor="#44000000">

            <widget name="config"       position="center,100"    size="1100,600" font="Regular;30" itemHeight="32" scrollbarMode="showOnDemand" backgroundColor="#1F000000" enableWrapAround="1" />

            <widget name="version_txt"  position="0,0"           size="1200,60"  font="Regular;42" foregroundColor="yellow" transparent="1" halign="center" valign="center" />
            <widget name="author_txt"   position="0,60"          size="1200,40"  font="Regular;28" foregroundColor="yellow" transparent="1" halign="center" valign="center" />

            <widget name="previewImage" position="100,390"       size="500,300"  zPosition="1" alphatest="blend" transparent="1" backgroundColor="transparent" />

            <ePixmap pixmap="skin_default/buttons/red.png"    position="25,755"  size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/green.png"  position="200,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="500,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/blue.png"   position="840,755" size="30,46" transparent="1" alphatest="on" zPosition="1" />

            <widget render="Label" source="txt_red"           position="65,755"  size="300,46" halign="left" valign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="txt_green"         position="240,755" size="300,46" halign="left" valign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="txt_yellow"        position="540,755" size="300,46" halign="left" valign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="txt_blue"          position="880,755" size="300,46" halign="left" valign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''
    else:                   # HD-ready or lower
        skin = '''
        <screen name="mainConfigScreen" position="center,center" size="850,600" title="Chocholousek picons" flags="wfNoBorder" backgroundColor="#44000000">

            <widget name="config"       position="center,70"     size="800,460" font="Regular;22" itemHeight="24" scrollbarMode="showOnDemand" backgroundColor="#1F000000" enableWrapAround="1" />

            <widget name="version_txt"  position="0,0"           size="850,40" font="Regular;26" foregroundColor="yellow" transparent="1" halign="center" valign="center" />
            <widget name="author_txt"   position="0,40"          size="850,30" font="Regular;16" foregroundColor="yellow" transparent="1" halign="center" valign="center" />

            <widget name="previewImage" position="70,225" size="500,300" zPosition="1" alphatest="blend" transparent="1" backgroundColor="transparent" />

            <ePixmap pixmap="skin_default/buttons/red.png"    position="20,560"  size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/green.png"  position="165,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="370,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="skin_default/buttons/blue.png"   position="605,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />

            <widget render="Label" source="txt_red"           position="55,560"  size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="txt_green"         position="200,560" size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="txt_yellow"        position="405,560" size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="txt_blue"          position="640,560" size="180,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''
    
    def __init__(self, session):
        
        Screen.__init__(self, session)
        #self.session = session                 # this is not necessary, this is done already during class initialization - Screen.__init__
        
        self.onChangedEntry = []
        self.list = []
        
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        
        self.lineHeight = 1                     # for text height auto-correction on dmm-enigma2 (1 = enable auto-correction ; 0 = disable auto-correction)
        self.lineheight = 1
        
        self['previewImage'] = Pixmap()
        
        self['txt_red']      = StaticText(_('Exit'))
        self['txt_green']    = StaticText(_('Save & Exit'))
        self['txt_yellow']   = StaticText(_('Update plugin'))
        self['txt_blue']     = StaticText(_('Update picons'))
        
        global plugin_version_local
        self['version_txt']  = Label('Chocholousek picons - plugin ver.%s' % plugin_version_local)
        self['author_txt']   = Label('(https://github.com/s3n0)')
        
        self['actions'] = ActionMap( ['ColorActions', 'DirectionActions', 'OkCancelActions'] ,
        {
                'left'  : self.keyToLeft,
                'right' : self.keyToRight,
                'ok'    : self.keyToOk,
                'yellow': self.keyToPluginUpdate,
                'blue'  : self.keyToPiconsUpdate,
                'green' : self.exitWithSave,
                'red'   : self.exitWithoutSave,
                'cancel': self.keyToExit
        }, -2)
        
        self.bin7zip = None                     # path to directory with '7z' or '7za' executable binary file
        self.chochoContent = None               # content of the file "id_for_permalinks*.log" - downloaded from google.drive
        
        if newOE() or os.path.isfile('/etc/opkg/nn2-feed.conf'):            # NewEnigma2 (based on OpenDreambox) firmware with OE 2.0 core - uses some new SKIN modules, therefore it's necessary to leave the FONT in the configList widget
            i = mainConfigScreen.skin.index('font=')
            self.skin = mainConfigScreen.skin[:i] + mainConfigScreen.skin[i+34:]                        # ConfigListScreen/ConfigScreen (widget "config") - under OE2.5 unfortunately the font style is configured with a new method and the original font attribute in OE2.5 is considered as error
        else:
            self.skin = mainConfigScreen.skin
            
        self.layoutFinishTimer = eTimer()
        if newOE():
            self.layoutFinishTimer_conn = self.layoutFinishTimer.timeout.connect(self.prepareSetup)     # eTimer for new version of Enigma2 core (OE 2.2+)
        else:
            self.layoutFinishTimer.callback.append(self.prepareSetup)                                   # eTimer for old version of Enigma2 core (OE 2.0 / OE-Alliance 4.? open-source core)
        self.layoutFinishTimer.start(200, True)
        
        #self.onShown.append(self.rebuildConfigList)
        #self.onLayoutFinish.append(self.prepareSetup)
    
    def prepareSetup(self):
        self.loadChochoContent()        
        self.check7zip()
        if self.bin7zip:
            self.downloadPreviewPicons()            
        self.changeAvailableBackgrounds()
        self.rebuildConfigList()
    
    def rebuildConfigList(self):
        self.list = []
        self.list.append(getConfigListEntry( _('Picon folder')  ,  config.plugins.chocholousekpicons.picon_folder ))
        if config.plugins.chocholousekpicons.picon_folder.value == 'user_defined':
            self.list.append(getConfigListEntry( _('User defined folder'), config.plugins.chocholousekpicons.picon_folder_user ))
        self.list.append(getConfigListEntry( _('Picon update method') , config.plugins.chocholousekpicons.method  ))
        self.list.append(getConfigListEntry( _('Satellite positions') , NoSave(ConfigSelection(default = config.plugins.chocholousekpicons.sats.value, choices = [config.plugins.chocholousekpicons.sats.value])) ))  # only display of selected satellites (without object configuration effect)
        self.list.append(getConfigListEntry( _('Picon resolution') , config.plugins.chocholousekpicons.resolution ))
        self.list.append(getConfigListEntry( _('Picon background') , config.plugins.chocholousekpicons.background , _('Choose picon design')  ))        
        
        listWidth = self['config'].l.getItemSize().width()
        self['config'].list = self.list
        self['config'].l.setSeperation(listWidth / 3)                       # fix the size of seperator in some new SKINs (for example in OE2.5)
        self["config"].l.setList(self.list)
        
        #self['config'].list = self.list
        #self['config'].setList(self.list)
        
        self.showPreviewImage()
    
    def getCursorTitle(self):
        return self["config"].getCurrent()[0]
    
    def getCursorObject(self):
        return self["config"].getCurrent()[1]
    
    def getCursorObjectAsText(self):
        return str(self["config"].getCurrent()[1].getText())
    
    def keyToLeft(self):
        ConfigListScreen.keyLeft(self)
        #if self.getCursorTitle() != _('User defined folder'):
        #    self.rebuildConfigList()
    
    def keyToRight(self):
        ConfigListScreen.keyRight(self)
        #if self.getCursorTitle() != _('User defined folder'):
        #    self.rebuildConfigList()
    
    def keyToOk(self):
        k = self.getCursorTitle()
        if k == _('Satellite positions'):
            self.session.openWithCallback(self.satellitesConfigScreenReturn, satellitesConfigScreen, self.getAllSat() )
        elif k == _('User defined folder'):
            ConfigListScreen.keyOK(self)        # self['config'].handleKey(KEY_OK)          # self.keyOK()
    
    def satellitesConfigScreenReturn(self, retval):
        if retval:
            #self.loadChochoContent()
            self.changeAvailableBackgrounds()   # if there has been a change in the necessary satellites settings, then I need to rescan the available picon styles (by default picon resolution)
            self.changedEntry()
            self.rebuildConfigList()
    
    def keyToPiconsUpdate(self):
        if self.bin7zip:
            if config.plugins.chocholousekpicons.background.value != 'no_picons':
                self.session.open(piconsUpdateJobScreen, self.chochoContent, self.bin7zip)
        else:
            self.check7zip()
    
    def keyToPluginUpdate(self):
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
        if self['txt_green'].getText().endswith('*'):           # plugin configuration changed...? if so, then I invoke the MessageBox with the option to save or restore the original settings in the plugin configuration
            message = _("You have changed the plugin configuration.\nDo you want to save all changes now ?")
            self.session.openWithCallback(self.exitWithConditionalSave, MessageBox, message, type = MessageBox.TYPE_YESNO, timeout = 0, default = True)
        else:
            self.exitWithConditionalSave(False)
    
    def exitWithConditionalSave(self, condition=True):          # save or cancel changes made to the plugin's user configuration, default=True -> to save the configuration
        if condition:
            for x in self['config'].list:
                x[1].save()
            config.plugins.chocholousekpicons.sats.save()       # the satellite selection is not in the ["config"].list and therefore after changing the satellites through another Screen class, so I have to save the satellites to disk additionally
            configfile.save()                                   # '/etc/enigma2/settings' - the configuration file will be saved only when the Enigma is stopped or restarted
        else:
            for x in self['config'].list:
                x[1].cancel()
        self.close()
    
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
        self['txt_green'].setText(_('Save & Exit') + '*')
        k = self.getCursorTitle()
        if k == _('Picon resolution'):
            self.changeAvailableBackgrounds()               # reload all available backgrounds/styles for the new changed picon resolution
        #elif k == _('Picon background'):
        #    self.showPreviewImage()
        
        if self.getCursorTitle() != _('User defined folder'):
            self.rebuildConfigList()                        # config list rebuild - is allowed only if the cursor is not at ConfigText (picon folder configuration by user input), because left/arrow RCU buttons are neccessary to move the cursor inside ConfigText
    
    def restartEnigmaOrCloseScreen(self, answer = None):
        if answer:
            self.session.open(TryQuitMainloop, 3)   # 0=Toggle Standby ; 1=Deep Standby ; 2=Reboot System ; 3=Restart Enigma ; 4=Wake Up ; 5=Enter Standby   ### FUNGUJE po vyvolani a uspesnom dokonceni aktualizacie PLUGINu   ### NEFUNGUJE pri zavolani z funkcie leaveSetupScreen(self) po aktualizacii picon lebo vyhodi chybu: RuntimeError: modal open are allowed only from a screen which is modal!
        else:
            self.close()
    
    def showPreviewImage(self):
        self['previewImage'].instance.setPixmapFromFile(self.getPreviewImagePath())
        self['previewImage'].instance.setScale(0)
    
    def getPreviewImagePath(self):
        imgpath = PLUGIN_PATH + 'images/filmbox-premium-' + config.plugins.chocholousekpicons.background.value + '-' + config.plugins.chocholousekpicons.resolution.value + '.png'
        if os.path.isfile(imgpath):
            return imgpath
        else:
            return PLUGIN_PATH + 'images/image_not_found.png'
    
    def downloadPreviewPicons(self):
        '''
        download preview picons if neccessary, i.e. download archive file into the plugin folder and extract all preview picons
        the online file version will be detected from the current chochoContent (from the preloaded "id_for_permalinks*.log" file on the plugin-configuration Screen initialization)
        the  local file version will be detected from the existing local file
        archive filename example:  filmbox-premium-(all)_by_chocholousek_(191020).7z         (the parentheses will replace by underline characters)
        files inside the archive file: filmbox-premium-transparent-220x132.png ;  filmbox-premium-gray-400x240.png ;  ...
        '''
        for line in self.chochoContent.splitlines():
            if 'filmbox-premium-' in line:
                r = line.split()
                url = 'https://drive.google.com/uc?export=download&id=' + r[0]
                new_file = PLUGIN_PATH + r[1]
                break
        
        l = glob.glob(PLUGIN_PATH + 'filmbox-premium-*.7z')
        current_file = l[0] if l else PLUGIN_PATH + 'foo-bar(000000).7z'            # version 000000 as very low version means to download a preview images from internet in next step (if the files does not exists on HDD)
        
        if new_file[-10:-4] > current_file[-10:-4]:                                 # comparsion, for example as the following:  '191125' > '191013'
            if not downloadFile(url, new_file):                                     # .7z archive with preview images (channel picons for the one and the same TV-channel)
                print('Picons preview file download failed ! (URL = %s)' % url)
                return
            self.deleteFiles(current_file)
            self.deleteFiles(PLUGIN_PATH + 'images/filmbox-premium-*.png')
            # extracting .7z archive (picon preview images):
            status, out = runShell('%s e -y -o%s "%s" *.png' % (self.bin7zip, PLUGIN_PATH + 'images', new_file))
            # check the status error and clean the archive file (will be filled with a short note)
            if status == 0:
                print('Picon preview files v.%s were successfully updated. The archive file was extracted into the plugin directory.' % new_file[-10:-4] )
                with open(new_file, 'w') as f:
                    f.write('This file was cleaned by the plugin algorithm. It will be used to preserve the local version of the picon preview images.')
            elif status == 32512:
                print('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package "p7zip".\n' % status)
                self.deleteFiles(new_file)
            elif status == 512:
                print('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, new_file) )
                self.deleteFiles(new_file)
            else:
                print('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
                self.deleteFiles(new_file)
    
    def deleteFiles(self, mask):
        lst = glob.glob(mask)
        if lst:
            for file in lst:
                os.remove(file)
    
    ###########################################################################
    
    def loadChochoContent(self):
        self.downloadChochoFile()
        path = glob.glob(PLUGIN_PATH + 'id_for_permalinks*.log')
        if path:
            self.chochoContent = open(path[0],'r').read()               # glob returns a list type variable, so I need to  translate list to string
            print('MYDEBUGLOGLINE - The %s file has been successfully loaded to memory.' % (PLUGIN_PATH + 'id_for_permalinks*.log'))
        else:
            self.chochoContent = ''
            print('MYDEBUGLOGLINE - Warning ! The file %s was not found !' % (PLUGIN_PATH + 'id_for_permalinks*.log'))
    
    def downloadChochoFile(self):
        '''
        1. check if there is a new version of the file on the internet and download if so
        2. then the content from the saved file is loaded into memory
        --- the     new/online file version will be retrieved from the HTTP header - with the helping of function downloadFile()
        --- the  current/local file version will be retrieved from the existing local file name
        file name example:    "id_for_permalinks191017.log"
        example of a line from inside the file:    "1xmITO0SouVDTrATgh0JauEpIS7IfIQuB        piconblack-220x132-13.0E_by_chocholousek_(191016).7z       bin      16.3 MB      2018-09-07 19:40:54"
        '''        
        l = glob.glob(PLUGIN_PATH + 'id_for_permalinks*.log')
        current_filename = l[0] if l else PLUGIN_PATH + 'id_for_permalinks000000.log'               # low version, to force update the file (the first download at all, if the file does not exists !)
        
        url = 'https://drive.google.com/uc?export=download&id=1oi6F1WRABHYy8utcgaMXEeTGNeznqwdT'    # id_for_permalinks191017.log -- means the chochoFile for the chochoContent value :)
        new_filename = downloadFile(url, PLUGIN_PATH, False)                                        # as the first - to test the online file only ... and return their file name as string (if online file will found)
        if new_filename:
            if new_filename[-10:-4] > current_filename[-10:-4]:                                     # Python <string> comparison like as <integer>, for example as the following:   '191125' > '191013'
                self.deleteFiles(current_filename)
                downloadFile(url, PLUGIN_PATH)
                print('MYDEBUGLOGLINE - file "id_for_permalinks*.log" was updated to new version: %s' % new_filename[-10:-4])
        else:
            print('MYDEBUGLOGLINE - file "id_for_permalinks*.log" not found on the internet ! (url = %s)' % url)
    
    def changeAvailableBackgrounds(self):
        '''
        change all available picon-backgrounds (picon-styles)
        by the user selected configuration (in the plugin config-menu)
        '''
        bckg_list = self.backgroundsByUserCfg( config.plugins.chocholousekpicons.sats.getValue().split() , config.plugins.chocholousekpicons.resolution.getValue() )
        if bckg_list:
            config.plugins.chocholousekpicons.background = ConfigSelection( default = bckg_list[0], choices = [(s, s) for s in bckg_list] )
        else:
            config.plugins.chocholousekpicons.background = ConfigSelection( default = 'no_picons', choices = [('no_picons', _('No picons found for selected resolution and satellites !') )]  )
    
    def backgroundsByUserCfg(self, sats, res):
        usrcontent = self.contentByUserCfg(sats, res)        
        backgrounds = sorted(list(set(  re.findall('.*picon(.*)-%s-.*' % (res), usrcontent)  )))          # using the set() to remove duplicites and the sorted() to sort the list by ASCII
        for b in backgrounds:
            for s in sats:
                if not 'picon{}-{}-{}_'.format(b, res, s) in usrcontent:
                    backgrounds.remove(b)             # check if all satellites from usrcontent contains also all backgrounds, if not, then delete the background from the available list of backgrounds
                    break
        return backgrounds
    
    def contentByUserCfg(self, satellites, resolution):
        result = []
        for line in self.chochoContent.splitlines():
            if resolution in line:
                for sat in satellites:
                    if '-{}_'.format(sat) in line:
                        result.append(line)
        return '\n'.join(result)
    
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
    
    def check7zip(self):
        if not self.find7zip():
            message = _('The 7-zip archiver was not found on your system.\nThere is possible to update the 7-zip archiver now in two steps:\n\n(1) try to install via the Enigma package manager\n...or...\n(2) try to download the binary file "7za" (standalone archiver) from the internet\n\nDo you want to try it now?')
            self.session.openWithCallback(self.downNinst7zip, MessageBox, message, type = MessageBox.TYPE_YESNO, default = True)
    
    def find7zip(self):
        if os.path.isfile('/usr/bin/7za') or os.path.islink('/usr/bin/7za'):
            self.bin7zip = '/usr/bin/7za'
            return True
        elif os.path.isfile('/usr/bin/7z') or os.path.islink('/usr/bin/7z'):
            self.bin7zip = '/usr/bin/7z'
            return True
        else:
            self.bin7zip = ''
            return False
    
    def downNinst7zip(self, confirmed):
        if confirmed:
            if os.path.exists('/etc/dpkg') and not os.system('dpkg -l p7zip > /dev/null 2>&1'):                             # if no error received from os.system (package manager), then...
                os.system('dpkg -i p7zip')
                message = _('The installation of the 7-zip archiver from the Enigma2\nfeed server was successful.')
            elif os.path.exists('/etc/opkg') and not os.system('opkg update > /dev/null && opkg list | grep -q p7zip'):     # if no error received from os.system (package manager), then...
                os.system('opkg install p7zip')
                message = _('The installation of the 7-zip archiver from the Enigma2\nfeed server was successful.')
            else:
                arch = self.getChipsetArch()
                if 'mips' in arch:                          # MIPS (always 32bit)
                    fname = '7za_mips32el'
                elif 'aarch64' in arch or 'arm64' in arch:  # ARM 64bit (Aarch64)
                    fname = '7za_aarch64'
                elif 'arm' in arch or 'cortexa15' in arch:  # ARM 32bit
                    fname = '7za_cortexa15hf-neon-vfpv4'
                elif 'sh4' in arch or 'sh_4' in arch:       # SH4
                    fname = '7za_sh4'
                else:
                    fname = 'ERROR_-_UNKNOWN_CHIPSET_ARCHITECTURE'
                #if not os.system('wget -q --no-check-certificate -O /usr/bin/7za "https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/7za/%s" > /dev/null 2>&1' % fname) \ # if no error received from os.system, then... \
                if downloadFile('https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons/7za/%s' % fname, '/usr/bin/7za')  \
                or downloadFile('http://cdn.jsdelivr.net/gh/s3n0/e2plugins/ChocholousekPicons/7za/%s' % fname, '/usr/bin/7za')  \
                or downloadFile('http://aion.webz.cz/ChocholousekPicons/7za/%s' % fname, '/usr/bin/7za')  :
                    os.system('chmod a+x /usr/bin/7za')
                    if os.system('/usr/bin/7za'):               # let's try to execute the binary file cleanly ... if the error number from the 7za executed binary file is not equal to zero, then...
                        os.remove('/usr/bin/7za')               # remove the binary file (because of an incorect binary file for the chipset architecture !)
                    else:
                        message = _('Installation of standalone "7za" (7-zip) archiver was successful.')
            
            if self.find7zip():
                self.downloadPreviewPicons()                    # !!!! if the installation of the 7-zip archiver was successful, I will try again to download the preview picons (.7z file from the internet), because at the beginning of the class it wasn't possible to download the preview picons - because of the non-existent 7-zip archiver
                self.showPreviewImage()                         # the Screen layer is already up, so, I may show the image into the screen widget
                self.session.open(MessageBox, message, type = MessageBox.TYPE_INFO)             # MessageBox with message about successful installation - either a standalone binary file or an ipk package
            else:
                self.session.open(MessageBox, _('Installation of 7-zip archiver failed!'), type = MessageBox.TYPE_ERROR)
    
    def getChipsetArch(self):
        '''
        detecting chipset architecture
        mips32el, armv7l, armv7a-neon, armv7ahf, armv7ahf-neon, cortexa9hf-neon, cortexa15hf-neon-vfpv4, aarch64, sh4, sh_4
        '''
        cmd = 'dpkg --print-architecture' if os.path.exists('/etc/dpkg') else 'opkg print-architecture'
        status,out = runShell(cmd + ' | grep -iE "arm|mips|cortex|aarch64|sh4|sh_4"')           # returns a pair of data, the first is an error code (0 if there are no problems) and the second is std.output (complete command-line / Shell text output)
        if status == 0:
            return out.lower().replace('arch ','').replace('\n',' ')    # return architectures by the Enigma package manager, like as:  'mips32el 16 mipsel 46'
        
        status,out = runShell('uname -m')
        if status == 0:
            return out.lower()                                          # return architectures from system, like as:  'mips'
        
        print('MYDEBUGLOGLINE - Error! Could not get information about chipset-architecture! Returning an empty string!')
        return ''



###########################################################################
###########################################################################
###########################################################################



class satellitesConfigScreen(Screen, ConfigListScreen):
    
    if sizemaxX > 1900:    # Full-HD or higher
        skin = '''
        <screen name="satellitesConfigScreen" position="center,center" size="450,900" title="Satellite positions" flags="wfNoBorder" backgroundColor="#44000000">
            <widget name="config"    position="center,120" size="350,700" font="Regular;30" itemHeight="32" scrollbarMode="showOnDemand" backgroundColor="#1F000000" enableWrapAround="1" />
            <widget name="title_txt" position="center,40"  size="350,60"  font="Regular;42" foregroundColor="yellow" transparent="1" halign="center" valign="top" />
            
            <ePixmap pixmap="skin_default/buttons/green.png" position="25,854" size="30,46" transparent="1" alphatest="on" zPosition="1" />
            <widget  render="Label" source="txt_green"       position="65,854" size="250,46" halign="left" valign="center" font="Regular;30" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''
    else:                   # HD-ready or lower
        skin = '''
        <screen name="satellitesConfigScreen" position="center,center" size="350,600" title="Satellite positions" flags="wfNoBorder" backgroundColor="#44000000">
            <widget name="config"    position="center,70" size="300,470" font="Regular;22" itemHeight="23" scrollbarMode="showOnDemand" backgroundColor="#1F000000" enableWrapAround="1" />
            <widget name="title_txt" position="center,20" size="300,40"  font="Regular;24" foregroundColor="yellow" transparent="1" halign="center" valign="top" />
            
            <ePixmap pixmap="skin_default/buttons/green.png" position="20,560" size="30,40" transparent="1" alphatest="on" zPosition="1" />
            <widget  render="Label" source="txt_green"       position="55,560" size="140,40" halign="left" valign="center" font="Regular;22" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>'''
    
    def __init__(self, session, allSat):
        
        self.allSat = allSat
        
        Screen.__init__(self, session)
        
        self.onChangedEntry = []
        self.list = []
        
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        
        self.lineHeight = 1             # for text height auto-correction on dmm-enigma2 (0 = enable auto-correction ; 1 = disable auto-correction)
        self.lineheight = 1
        
        self['title_txt'] = Label(_('Select satellites:'))
        self['txt_green'] = StaticText(_('Apply'))

        self['actions'] = ActionMap( ['ColorActions', 'DirectionActions', 'OkCancelActions'] ,
        {
                'left'  : self.keyToPageUp,
                'right' : self.keyToPageDown,
                'ok'    : self.keyToOk,
                'green' : self.keyToExit
        }, -2)
        
        self.onShown.append(self.rebuildConfigList)
        
        if newOE() or os.path.isfile('/etc/opkg/nn2-feed.conf'):            # NewEnigma2 firmware (based on OpenDreambox) with OE 2.0 core - uses some new SKIN modules and therefore it's necessary to leave the FONT in the configList widget
            ### remove first found item "font=....itemHeght=...." from the widget "config"
            ### # ConfigListScreen/ConfigScreen (widget "config") - under OE2.5 unfortunately the font style is configured with a new method and the original font attribute in OE2.5 is considered as error
            s = satellitesConfigScreen.skin
            i = s.index('font')
            s = s[:i] + s[i+34:]
            ### increase width of the Screen layer and width of the "config" widget (for differences in the Screen layer of the OpenDreambox Enigma - OE2.5)
            i = s.index('size')                     # first match is the size of main Screen frame
            y = s[i+10 : i+13]
            s = s[:i] + 'size="' + y + s[i+9:]
            i = s.index('size', i+20)               # second match is the size of widget "config"
            y = s[i+10 : i+13]
            s = s[:i] + 'size="' + y + s[i+9:]
            #i = s.index('size', i+20)              # third match is the size of my own title for window Screen
            #y = s[i+10 : i+13]
            #s = s[:i] + 'size="' + y + s[i+9:]
            self.skin = s
        else:
            self.skin = satellitesConfigScreen.skin
    
    def keyToOk(self):
        self.switchSelectedSat()
        self.changedEntry()
    
    def keyToPageUp(self):
        self['config'].pageUp()                             # self["config"].pageUp (.pageDown) cannot be called directly from ["actions"] because the BlackHole Enigma does not allow this, so there is another function on the left/right buttons to call .pageUp / .pageDown
        
    def keyToPageDown(self):
        self['config'].pageDown()                           # self["config"].pageUp (.pageDown) cannot be called directly from ["actions"] because the BlackHole Enigma does not allow this, so there is another function on the left/right buttons to call .pageUp / .pageDown
    
    def switchSelectedSat(self):
        sel = self['config'].getCurrent()[0]                                # example:  '23.5E 19.2E 13.0E'            ...another example:   '13.0E'
        sats = config.plugins.chocholousekpicons.sats.getValue().split()    # example:  ['23.5E', '19.2E', '13.0E']    ...another example:   ['13.0E']
        sats.remove(sel) if sel in sats else sats.append(sel)
        config.plugins.chocholousekpicons.sats.setValue(' '.join(sats))     # set the new value as the string (converted from a list variable)
    
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        self['txt_green'].setText(_('Apply') + '*')
        self.rebuildConfigList()

    def rebuildConfigList(self):
        
        self.list = []
        for sat in self.allSat:
            self.list.append(getConfigListEntry(sat, NoSave(ConfigYesNo( default = sat in config.plugins.chocholousekpicons.sats.getValue().split() ))))
        
        listWidth = self['config'].l.getItemSize().width()
        self['config'].list = self.list
        self['config'].l.setSeperation(listWidth / 2)                       # fix the size of seperator in some new SKINs (for example in OE2.5)
        self["config"].l.setList(self.list)

        #self['config'].list = self.list
        #self['config'].setList(self.list)
    
    def keyToExit(self):
        s = self['txt_green'].getText()
        if s[-1:] == '*':                       # plugin configuration changed ... ?
            self.close(True)
        else:
            self.close(False)



###########################################################################
###########################################################################
###########################################################################



class piconsUpdateJobScreen(Screen):

    skin = '''
        <screen name="piconsUpdateJobScreen" position="center,center" size="''' + str(sizemaxX - 80) + ',' + str(sizemaxY - 80) + '''" title="picons update in progress" flags="wfNoBorder" backgroundColor="#22000000">
            <widget name="logWindow" position="center,center" size="''' + str(sizemaxX - 180) + ',' + str(sizemaxY - 180) + '''" font="Regular;''' + (str(28) if sizemaxX > 1900 else str(20)) + '''" transparent="0" foregroundColor="white" backgroundColor="#11330000" zPosition="1" />
        </screen>'''

    def __init__(self, session, chochoContent, bin7zip):

        self.chochoContent = chochoContent
        self.bin7zip = bin7zip

        Screen.__init__(self, session)
        #self.session = session          # this is not necessary, this is done already during class initialization - Screen.__init__

        self['logWindow'] = ScrollLabel('LOG:\n')
        self['logWindow'].scrollbarmode = "showOnDemand"
        
        self['actions'] = ActionMap( ['DirectionActions'] ,
        {
                'up'    :  self['logWindow'].pageUp,
                'left'  :  self['logWindow'].pageUp,
                'down'  :  self['logWindow'].pageDown,
                'right' :  self['logWindow'].pageDown
        }, -1)
        
        self.piconUpdateReturn = _('No operation ! Picon update failed !'), MessageBox.TYPE_ERROR           # error boolean, error message
        self.piconCounters = {'added' : 0, 'changed' : 0, 'removed' : 0}
        self.startTime = datetime.now()
        
        self.th = threading.Thread(target = self.thProcess)
        self.th.daemon = True
        self.th.start()
        
        self.thStopCheckingTimer = eTimer()
        if newOE():
            self.thStopCheckingTimer_conn = self.thStopCheckingTimer.timeout.connect(self.thStopChecking)   # eTimer for new version of Enigma2 core (OE 2.2+)
        else:
            self.thStopCheckingTimer.callback.append(self.thStopChecking)                                   # eTimer for old version of Enigma2 core  (OE 2.0 / OE-Alliance 4.? open-source core)
        self.thStopCheckingTimer.start(1000, False)
        
        #self.onShown.append(self.func_name)
        #self.onLayoutFinish.append(self.func_name)
        #self.onClose.append(self.func_name)
    
    def thStopChecking(self):
        if not self.th.is_alive():
            self.thStopCheckingTimer.stop()
            self.th.join()                                      # close the finished "th" thread
            msg, type = self.piconUpdateReturn
            self.writeLog(msg)
            if type == MessageBox.TYPE_ERROR:
                sleep(8)
            else:
                sleep(4)
            self['logWindow'].hide()                            # for smoother transition from MessageBox window to plugin initial menu (without flashing 'logWindow')
            self.session.open(MessageBox, msg, type)            
            self.close()
    
    def thProcess(self):
        #### start a separate thread in the background + waiting for it to finish
        boo, msg = self.mainFunc()
        # boo = True ----------- picons updating function was ended with error
        # boo = False ---------- picons updating function was ended without error
        # msg = <type 'str'> --- returned string - as the result of the process, as warning / sucessful info message (for the MessageBox purpose)
        if boo:
            type = MessageBox.TYPE_ERROR
            if not msg:
                msg = _('Some errors has occurred !')
        else:
            type = MessageBox.TYPE_INFO
            if not msg:
                msg = _('Done !') + '\n' + _('(%s added / %s changed / %s removed)') % (self.piconCounters['added'] , self.piconCounters['changed'] , self.piconCounters['removed'])
        self.piconUpdateReturn = msg, type
        #### end of the thread process
    
    def mainFunc(self):        
        
        # 1) Ocheckuje sa internetové pripojenie
        if os.system('ping -c 1 www.google.com > /dev/null 2>&1'):          #  removed the argument -w 1 due to incompatibility with SatDreamGr enigma image
            return True, _("Internet connection is not available !")
        else:
            self.writeLog(_('Internet connection is OK.'))
        
        # 2) Skontroluje sa existencia zložky s pikonami na lokalnom disku (ak zložka neexistuje, vytvorí sa nová !)
        if config.plugins.chocholousekpicons.picon_folder.value == 'user_defined':
            self.piconDIR = config.plugins.chocholousekpicons.picon_folder_user.value.strip()
            if self.piconDIR.endswith('/'):
                self.piconDIR = self.piconDIR[:-1]
        else:
            self.piconDIR = config.plugins.chocholousekpicons.picon_folder.value
        if not os.path.exists(self.piconDIR):
            try:
                os.makedirs(self.piconDIR)
            except OSError as e:
                return True, _('Error creating directory %s:\n%s') % (self.piconDIR, str(e))
        
        # 3) Vytvorí sa zoznam dostupných userbouquets súborov "/etc/enigma2/userbouquet.*.tv"
        #    prípadne aj "/etc/enigma2/userbouquet.*.radio" súborov    
        self.bouquet_files = []
        if config.plugins.chocholousekpicons.method.value == 'sync_tv':
            self.bouquet_files = glob.glob('/etc/enigma2/userbouquet.*.tv')
        if config.plugins.chocholousekpicons.method.value == 'sync_tv_radio':
            self.bouquet_files = glob.glob('/etc/enigma2/userbouquet.*.tv')
            self.bouquet_files.extend(glob.glob('/etc/enigma2/userbouquet.*.radio'))
        if ('sync' in config.plugins.chocholousekpicons.method.value) and not self.bouquet_files:
            return True, _('No userbouquet files found !\nPlease check the folder /etc/enigma2 for the userbouquet files.')
        #self.storeVarInFile('bouquet_files', self.bouquet_files)
        
        # 4) Vytvorí sa zoznam picon umiestnených na lokálnom disku (v internom flash-disku alebo na externom USB/HDD) - včetne veľkostí týchto súborov !
        self.writeLog(_('Preparing a list of picons from the picon directory on the local disk.'))
        self.SRC_in_HDD = {}
        dir_list = glob.glob(self.piconDIR + '/*.png')
        if dir_list:
            for path_N_file in dir_list:
                self.SRC_in_HDD.update( { path_N_file[:-4].split("/")[-1]  :  int(os.path.getsize(path_N_file))  } )
        #self.storeVarInFile('SRC_in_HDD', self.SRC_in_HDD)
        
        # 5) Vytvorenie zoznamu SRC kódov z userbouquet súborov
        if 'sync' in config.plugins.chocholousekpicons.method.value:
            # 5.A) Vytvorí sa zoznam serv.ref.kódov z patričných userbouquet súborov (podľa predvytvoreného zoznamu *.tv alebo aj *.radio) - sú poterbné pre synchronizáciu picon
            self.writeLog(_('Preparing a list of picons from userbouquet files...'))
            s = ''
            for bq_file in self.bouquet_files:
                with open(bq_file, 'r') as f:
                    s += f.read()
            self.SRC_in_Bouquets = re.findall('.*#SERVICE\s([0-9a-fA-F]+_0_[0-9a-fA-F_]+0_0_0).*\n*', s.replace(":","_") )
            self.SRC_in_Bouquets = list(set(self.SRC_in_Bouquets))              # remove duplicate items ---- converting to <set> and then again back to the <list>
            self.writeLog(_('...done.'))
        else:
            # 5.B) Vytvorí sa fiktívny t.j. prázdny zoznam SRC kódov z userbouquet zoznamov, aby v ďalšiom kroku boli všetky aktuálne pikony na lokálnom disku vymazané (metóda 'all' pre vymazanie všetkých aktuálnych picon a nakopírovanie nových picon)
            self.SRC_in_Bouquets = []
        #self.storeVarInFile('SRC_in_bouquets', self.SRC_in_Bouquets)
        
        # 6) Vymažú sa neexistujúce a nepotrebné picon-súbory na lokálnom disku (v set-top boxe) pre synchronizáciu (pri použití metód 'sync_tv' a 'sync_tv_radio')
        #    alebo sa vymažú všetky súbory na lokálnom disku (v prípade metódy 'all' bude obsahom SRC_in_Bouquets prázdny list, takže sa vymažú všetky picony na HDD)
        #    avšak v prípade metódy "all_inc" (increment update) bude celá následovná funkcia zmazovania súborov z disku ignorovaná
        if not 'all_inc' in config.plugins.chocholousekpicons.method.value:
            self.writeLog(_('Deleting unnecessary picons from local disk...'))
            self.SRC_to_Delete = list(  set(self.SRC_in_HDD.keys()) - set(self.SRC_in_Bouquets)  )            
            for src in self.SRC_to_Delete:
                os.remove(self.piconDIR + '/' + src + '.png')
                del self.SRC_in_HDD[src]                                        # po vymazaní súbory z HDD samozrejme ihneď aktualizujem tiež výpis súborov na HDD (obsah premennej SRC_in_HDD)
                self.piconCounters['removed'] += 1
            self.writeLog(_('...%s picons deleted.') % self.piconCounters['removed'])
        #self.storeVarInFile('SRC_to_Delete', self.SRC_to_Delete)
        
        # 7) Pripraví sa zoznam názvov všetkých súborov .7z na sťahovanie z internetu - podľa konfigurácie pluginu
        self.filesForDownload = []
        for SAT in config.plugins.chocholousekpicons.sats.getValue().split():   #  =  ['13.0E', '19.2E', '23.5E']
            self.filesForDownload.append('picon%s-%s-%s_by_chocholousek' % (config.plugins.chocholousekpicons.background.value , config.plugins.chocholousekpicons.resolution.value , SAT)   )
        # doplnenie zoznamu stahovania o doplnkove online zdroje pikon tretiej strany:
        if os.path.isfile('/etc/enigma2/3rd_party_picons.ini'):                 # picon sources of the third party... the example of file-content: "http://example.com/iptv/my-picons.7z"
            with open('/etc/enigma2/3rd_party_picons.ini', 'r') as f:
                l = f.read().splitlines()
            self.filesForDownload += [ s for s in l if s.strip() and not s.startswith('#') ]            # add a new created list to an existing list (nothing will be added if the new list remains empty)
        #self.storeVarInFile('filesForDownload', self.filesForDownload)
        
        # 8) Ďalej sa v cykle stiahnú z internetu a spracujú sa všetky používateľom zafajknuté archívy s piconami - spracuvávajú sa po jednom (pre viac družíc - postupne každý jeden archív sa stiahne a spracuje)
        self.writeLog(_('The process started...') + ' ' + _('(downloading and extracting all necessary picons)')  )
        self.writeLog('#' * 40)
        for count, fname in enumerate(self.filesForDownload, 1):
            s = ' %s / %s ' % (count, len(self.filesForDownload))
            self.writeLog('-' * 16 + s.ljust(20,'-'))
            self.proceedArchiveFile(fname)
        self.writeLog('#' * 40)
        self.writeLog(_('...the process is complete.') + ' ' + _('(downloading and extracting all necessary picons)')  )
        
        # 9) Nakoniec sa zobrazí výsledok celého procesu
        if self.piconCounters['added'] or self.piconCounters['changed']:
            message = _('After updating the picons you may need to restart the Enigma (GUI).') + '\n' + _('(%s added / %s changed / %s removed)') % (self.piconCounters['added'] , self.piconCounters['changed'] , self.piconCounters['removed'])
        else:
            message = _('No picons added or changed.') + '\n' + _('(%s added / %s changed / %s removed)') % (self.piconCounters['added'] , self.piconCounters['changed'] , self.piconCounters['removed'])
        return False, message
    
    def proceedArchiveFile(self, url_id):
        
        # 1. Príprava downloadovaciej URL adresy + názvu súboru pre uloženie na disk
        if "://" in url_id:
            # (a) - ak sa jedná o alternatívny zdroj s pikonami a nie o ID kod pre Chocholousek - drive.google...
            url_link = url_id
            dwn_filename = url_id.split('/')[-1]
        else:
            # (b) - vyhľadanie google.drive ID - kódu v "chochoContent", pre konkrétny súbor (pre potrebu jeho následovného stiahnutia)
            found = []
            for line in self.chochoContent.splitlines():
                if url_id in line:
                    found = line.split()
                    break
            if not found:
                self.writeLog(_('Download ID for file %s was not found!') % url_id)
                return
            url_link = 'https://drive.google.com/uc?export=download&id=' + found[0]
            dwn_filename = found[1]     # .replace('(','_').replace(')','_')        # replace the filename mask by new original archive filename and replace the parentheses by underline characters

        # 2. Stiahnutie archívu z internetu (súboru s piconami) do zložky "/tmp"
        self.writeLog(_('Trying download the file archive... %s') % dwn_filename)
        if not downloadFile(url_link, '/tmp/' + dwn_filename):
            self.writeLog(_('...file download failed !!!'))
            return
        else:
            self.writeLog(_('...file download successful.'))
        
        # 3. Načítanie zoznamu všetkých .png súborov z archívu, včetne ich atribútov (veľkostí súborov)
        #self.writeLog(_('Browse the contents of the downloaded archive file.'))
        self.SRC_in_Archive = self.getPiconListFromArchive('/tmp/' + dwn_filename)
        if not self.SRC_in_Archive:
            self.writeLog(_('Error! No picons found in the downloaded archive file!'))
            return          # navratenie vykonavania kodu z tohto podprogramu pre spracovanie dalsieho archivu/suboru s piconami v poradi
        #self.storeVarInFile('SRC_in_Archive--%s' % dwn_filename, self.SRC_in_Archive)

        # 4. Rozbalenie pikon zo stiahnutého archívu
        self.writeLog(_('Extracting files from the archive...'))
        
        if 'all' == config.plugins.chocholousekpicons.method.value:
        #### Ak používateľ zvolil v plugin-konfigurácii metódu zmazania všetkých pikon a nahratia všetkých nových pikon (metóda 'all'), tak ...
            self.piconCounters['added'] += len(self.SRC_in_Archive)
            self.extractAllPiconsFromArchive('/tmp/' + dwn_filename)
            self.writeLog(_('...%s picons were extracted from the archive.') % len(self.SRC_in_Archive))
        
        else:
        #### V prípade metód synchronizačných / kontrolovaných t.j. 'sync_tv', 'sync_tv_radio' alebo 'all_inc' prebehne rozbalenie a prepísanie iba patričných picon (podľa predvytvoreneho zoznamu)
            self.SRC_for_Extract = []
            # V prípade dvoch metód userbouquet synchronizácie t.j. 'sync_tv' a 'sync_tv_radio' sa zaujímam len o tie picony z archívu, ktoré sa nachádzajú zároveň v zozname SRC_in_Bouquets a zároveň v zozname SRC_in_Archive
            # Čiže vytvorím zoznam zhodných prvkov pomocou operácie s množinami:   set(A) & set(B)
            if 'sync' in config.plugins.chocholousekpicons.method.value:
                M = set(self.SRC_in_Archive) & set(self.SRC_in_Bouquets)
            # V prípade metódy inkrementalného kopírovania 'all_inc', budem prechádzať úplne všetky rozbalované pikony a testovať, či sa už nachádzajú na HDD a ak áno, zistím, či je potrebné ich kopírovať (rozdielná veľkosť oboch súborov)
            elif 'all_inc' == config.plugins.chocholousekpicons.method.value:
                M = self.SRC_in_Archive
            # ďalej budem prechádzať v cykle už iba cieľový SRC-zoznam a zisťovať, či je potrebné tieto pikony z archívu aj nakopírovať
            for src in M:
                if src in self.SRC_in_HDD:                                  # ak uz sa pikona rozbalena z archivu nachadza na HDD, tak...
                    if self.SRC_in_HDD[src] != self.SRC_in_Archive[src]:    # porovnam este velkosti tychto dvoch pikon (Archiv VS. HDD) a ak su velkosti picon odlisne...
                        self.SRC_for_Extract.append(src)                    # tak pridam tuto pikonu na zoznam kopirovanych pikon (zoznam pikon na extrahovanie)
                        self.piconCounters['changed'] += 1
                else:                                                       # ak sa pikona zo zoznamu "potrebnych" este nenachadza na HDD, tak...
                    self.SRC_for_Extract.append(src)                        # tiez musim tuto pikonu pridat na zoznam kopirovanych (zoznam pikon na extrahovanie)
                    self.piconCounters['added'] += 1
            
            # Extrahovanie vybraných pikon (len v prípade, že sa našli nejaké pikony pre extrahovanie)
            if self.SRC_for_Extract:
                self.extractCertainPiconsFromArchive('/tmp/' + dwn_filename , self.SRC_for_Extract)
                # subory, ktore budu teraz pridane alebo prepisane z archivu do HDD, uz viac krat nebudem musiet kopirovat a zistovat v dalsich cykloch (v dalsich rozbalenych balickoch s pikonami),
                # preto tieto subory aktualizujem aj v zozname SRC_in_HDD pre urychlenie procesu, aby sa v dalsich cykloch tieto subory ignorovali (budu vyrozumene ako existujuci subor na HDD so zhodnou velkostou)
                for k in self.SRC_for_Extract:
                    self.SRC_in_HDD[k] = self.SRC_in_Archive[k]             #self.SRC_in_Bouquets.remove(k)
            self.writeLog(_('...%s picons were extracted from the archive.') % len(self.SRC_for_Extract))
        
        #self.storeVarInFile('SRC_for_Extract--%s' % dwn_filename, self.SRC_for_Extract)
        os.remove('/tmp/' + dwn_filename)
    
    def extractCertainPiconsFromArchive(self, archiveFile, SRC_list):
        with open('/tmp/picons-to-extraction.txt', 'w') as f:
            f.write('.png\n'.join(SRC_list) + '.png\n')
        status, out = runShell('%s e -y -o%s "%s" @/tmp/picons-to-extraction.txt' % (self.bin7zip, self.piconDIR, archiveFile)  )
        os.remove('/tmp/picons-to-extraction.txt')
        if status == 0:
            return True
        else:
            self.writeLog7zipError(status, archiveFile, out)
            return False
    
    def extractAllPiconsFromArchive(self, archiveFile):
        status, out = runShell('%s e -y -o%s "%s" *.png' % (self.bin7zip, self.piconDIR, archiveFile) )
        if status == 0:
            return True
        else:
            self.writeLog7zipError(status, archiveFile, out)
            return False
    
    def getPiconListFromArchive(self, archiveFile):
        status, out = runShell('%s l "%s"' % (self.bin7zip, archiveFile) )   # returns a pair of data, the first is an error code (0 if there are no problems) and the second is std.output (complete command-line / Shell text output)
        if status == 0:
            out = out.splitlines()
            tmp = {}
            i = -3
            while not "-----" in out[i]:
                # processing files obtained at Shell output:
                # column:  Date       Time      Attr   Size       Compressed  Name
                # index:   0****************19  20*25  26*****38  39******52  53**********************************************>
                # out:     2019-12-05 10:16:06  ....A      26824       57902  filmbox-premium-freezeframe-400x240.png
                fsize, fpath = out[i][26:38].strip(), out[i][53:].strip()
                #if fattr[0] != 'D':                    # retreive all files with a full path, but no individual directories !
                if fpath.lower().endswith('.png'):      # retreive all files with a full path, but only if the file path contains '.png' string
                    tmp.update( {fpath.split('/')[-1].split('.')[0]  :  int(fsize)} )        # {"service_reference_code" : file_size}
                i -= 1
            return tmp
        else:
            self.writeLog7zipError(status, archiveFile, out)
        return ''         # return the empty string on any errors !
    
    def writeLog7zipError(self, status, archiveFile, out):
        if status == 32512:
            self.writeLog('Error %s !!! The 7-zip archiver was not found. Please check and install the enigma package "p7zip".\n' % status)
        elif status == 512:
            self.writeLog('Error %s !!! Archive file not found. Please check the correct path to directory and check the correct file name: %s\n' % (status, archiveFile) )
        else:
            self.writeLog('Error %s !!! Can not execute 7-zip archiver in the command-line shell for unknown reason.\nShell output:\n%s\n' % (status, out)  )
    
    def writeLog(self, msg = ''):
        print(msg)
        timestamp = str((datetime.now() - self.startTime).total_seconds()).ljust(10,"0")[:6]        # pri operacii odcitania casu za pomoci datetime, ziskame novy objekt - datetime.timedelta(), ktory uz mozme prevadzat na sekundy s metodou .total_seconds()
        self['logWindow'].appendText('\n[%s] %s' % (timestamp, msg))
        self['logWindow'].lastPage()

    #def storeVarInFile(self, fname, data):
    #    with open('/tmp/___%s.log' % fname, 'w') as f:
    #        f.write('\n'.join(data))



###########################################################################
###########################################################################
###########################################################################



def findHostnameAndNewPlugin():
    '''
    return "" ----- if a new online version was not found
    return URL ---- if a new online version was found
    '''
    global plugin_version_local, plugin_version_online
    server_list = ['https://github.com/s3n0/e2plugins/raw/master/ChocholousekPicons',
                   'http://cdn.jsdelivr.net/gh/s3n0/e2plugins/ChocholousekPicons',          # HTTP download - fuse and SSL prevention in some Enigma distributions
                   'http://aion.webz.cz/ChocholousekPicons']
    result = ''
    for url in server_list:
        try:
            url_handle = urllib2.urlopen(url + '/src/version.txt')
        except urllib2.URLError as err:
            print('Error: %s , while trying to fetch URL: %s' % (err, url + '/src/version.txt'))
        except Exception as err:
            print('Error: %s , while trying to fetch URL: %s' % (err, url + '/src/version.txt'))
        else:
            plugin_version_online = url_handle.read().strip()
            if plugin_version_online > plugin_version_local:
                result = url
                break # to start the plugin update process
    return result

def pluginUpdateDo():
    '''
    return True ----- if a new version was successfull downloaded and installed
    return False ---- if a new version was not found
    '''
    global plugin_version_local, plugin_version_online
    host = findHostnameAndNewPlugin()
    if host:
        pckg_name = 'enigma2-plugin-extensions-chocholousek-picons_' + plugin_version_online + ('_all.deb' if os.path.exists('/etc/dpkg') else '_all.ipk')
        dwn_url   =  host + '/released_build/' + pckg_name
        dwn_file  = '/tmp/' + pckg_name
        if downloadFile(dwn_url, dwn_file):
            if pckg_name.endswith('.deb'):
                os.system('dpkg --force-all -r %s > /dev/null 2>&1' % pckg_name.split('_',1)[0])
                os.system('dpkg --force-all -i %s > /dev/null 2>&1' % dwn_file)
            else:
                os.system('opkg --force-reinstall install %s > /dev/null 2>&1' % dwn_file)
            print('New plugin version was installed ! old ver.:%s , new ver.:%s' % (plugin_version_local, plugin_version_online)  )
            plugin_version_local = plugin_version_online            
            os.remove(dwn_file)
            return True
        else:
            return False
    else:
        print('New plugin version is not available - local ver.:%s , online ver.:%s' % (plugin_version_local, plugin_version_online)  )
        return False



###########################################################################
###########################################################################
###########################################################################



def downloadFile(url, storagepath='', savefile=True):
    
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/74.0'}           # 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    
    cookie_jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)
    
    #ctx = ssl.create_default_context()                 # urllib2 does not verify server certificate by default - but this is not true anymore for Python 2.7.9 or newer versions !
    #ctx.check_hostname = False                         # .create_default_context() method does not work in versions earlier than Python 2.6 ! has been added since Python 2.6 and later
    #ctx.verify_mode = ssl.CERT_NONE                    # example of use:    handler = urllib2.urlopen(req, timeout=20, context=ctx)
    
    try:
        req = urllib2.Request(url, data=None, headers=headers)
        handler = urllib2.urlopen(req, timeout=20)
        if 'drive.google' in url:
            for c in cookie_jar:
                if c.name.startswith('download_warning'):                    # in case of drive.google download a virus warning message is possible (for some downloads)
                    url = url.replace('&id=', '&confirm=%s&id=' % c.value)   # and then it's necessary to add a parameter with confirmation of the warning message
                    req = urllib2.Request(url, data=None, headers=headers)
                    handler = urllib2.urlopen(req, timeout=20)
                    break
        
        if storagepath.endswith('/') or storagepath == '':
            if 'content-disposition' in handler.headers:
                storagepath = storagepath + handler.headers['content-disposition'].split('"')[1]    # get filename from html header
            else:    
                storagepath = '/tmp/unknown_file_' + datetime.now().strftime('%s')                  # unix-timestamp: '/tmp/unknown_file_1586625400'
                #storagepath = '/tmp/unknown_file_{:0>6}____'.format(random.randint(0,150000))      # random number
        
        if savefile:                                    # skip writting the file to disk - if it's a file test
            data = handler.read()
            with open(storagepath, 'wb') as f:
                f.write(data)
    
    except Exception as e:
        print('File download error: %s , URL: %s , storagepath: %s' % (str(e), url, storagepath) )
        return False
    
    except:
        return False
    
    if savefile:
        return True                                     # return True, if all done (file is saved on disk, no testing purpose)
    else:
        return storagepath                              # return the file name - if it's a file test

def newOE():
    '''
    return True ---- for commercial versions of Enigma2 core (OE 2.2+) - DreamElite, DreamOS, Merlin, ... etc.
    return False --- for open-source versions of Enigma2 core (OE-Alliance 4.x) - OpenATV, OpenPLi, VTi, ... etc.
    '''
    #return os.path.exists('/etc/dpkg')
    try:
        from enigma import PACKAGE_VERSION
        major, minor, patch = [ int(n) for n in PACKAGE_VERSION.split('.') ]
        if major > 4 or (major == 4 and minor >= 2):    # if major > 4 or major == 4 and minor >= 2:
            retval = True                               #### new enigma core (DreamElite, DreamOS, Merlin, ...) ===== e2 core: OE 2.2+ ====================== (c)Dreambox core
        else:
            retval = False                              #### old enigma core (OpenATV, OpenPLi, VTi, ...) =========== e2 core: OE 2.0 / OE-Alliance 4.x ===== open-source core
    except ImportError:
        retval = False                                  #### on import error it means OE 2.0 core
    
    return retval

def runShell(cmd):
    try:
        t = getstatusoutput(cmd)
    except Exception as e:
        t = -1 , e.message
    except:
        t = -1 , ''
    return t

#def runShell(cmd):
#    try:
#        t =  0 , check_output(shlexSplit(cmd))
#    except CalledProcessError as e:
#        t = e.returncode , e.message
#    except Exception as e:
#        t = -1 , e.message
#    except:
#        t = -1 , ''
#    return t

#def runShell(cmd):
#    retCODE = os.system(cmd + ' > /tmp/redirected_output 2>&1')     # redirecting stdout and stderr to a temporary file
#    retOUT = open('/tmp/redirected_output', 'r').read()
#    os.remove('/tmp/redirected_output')
#    return retCODE, retOUT



###########################################################################
###########################################################################
###########################################################################



def pluginMenu(session, **kwargs):              # starts when the plugin is opened via Plugin-MENU
    print('PLUGINSTARTDEBUGLOG - pluginMenu executed')
    global plugin_version_local
    plugin_version_local = open(PLUGIN_PATH + 'version.txt','r').read().strip()
    session.open(mainConfigScreen)

def Plugins(**kwargs):
    if sizemaxX > 1900:
        logo_img = 'images/plugin_fhd.png'
    else:
        logo_img = 'images/plugin.png'
    return [ PluginDescriptor(
                where = PluginDescriptor.WHERE_PLUGINMENU,
                name = 'Chocholousek picons',
                description = 'Download and update Chocholousek picons',
                icon = logo_img,
                needsRestart = False,
                fnc = pluginMenu)  ]

