# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config
from Components.config import ConfigSubsection, config, configfile, getConfigListEntry, ConfigYesNo, ConfigClock, ConfigInteger
# ConfigText, ConfigNumber, ConfigDirectory, ConfigSubList, ConfigEnableDisable, ConfigPassword, ConfigSelection

from Plugins.Plugin import PluginDescriptor

from Plugins.Extensions.CAMautorestart import _, PLUGIN_PATH  

from time import localtime, strftime, strptime, time
# time.localtime()..............................................returns the current date + time in local country
# time.strftime("format", <time as 9-tuple object>).............returns date and time formated as string
# time.strptime("<str>-type date and time", "formating")........returns <type 'time.struct_time'>   (i.e. 9-index <tuple> object type)

from os import path as os_path, remove as os_remove, system as os_system

from enigma import eTimer, eDVBCI_UI, eDVBCIInterfaces

#########################################################

config.plugins.camautorestart               = ConfigSubsection()
config.plugins.camautorestart.enabled       = ConfigYesNo(default=True)
config.plugins.camautorestart.scheduledtime = ConfigClock(default=0)        # the value is a list data type... it means, as example:  [17, 59]  =  what means [hour, min]
config.plugins.camautorestart.scheduleddays = ConfigInteger(default=1, limits=(1, 15))

#########################################################

class pluginConfigurationMenu(Screen, ConfigListScreen):    
    
    skin = '''
        <screen name="pluginConfigurationMenu" position="center,center" size="700,350" title="CAMautorestart" flags="wfNoBorder" backgroundColor="#44000000">   
            <widget name="version_txt" position="0,12" size="700,35" font="Regular;30" foregroundColor="yellow" transparent="1" halign="center" valign="center" zPosition="1" />
            <widget name="author_txt"  position="0,44" size="700,30" font="Regular;22" foregroundColor="yellow" transparent="1" halign="center" valign="center" zPosition="1" />
            
            <widget name="config" position="center,100" size="650,200" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#22000000" zPosition="1" />
            
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CAMautorestart/images/btn_red.png"    position="5,310"   size="40,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CAMautorestart/images/btn_green.png"  position="140,310" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CAMautorestart/images/btn_yellow.png" position="310,310" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CAMautorestart/images/btn_blue.png"   position="485,310" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            
            <widget render="Label" source="txt_red"    position="45,310"  size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
            <widget render="Label" source="txt_green"  position="180,310" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
            <widget render="Label" source="txt_yellow" position="350,310" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
            <widget render="Label" source="txt_blue"   position="525,310" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
        </screen>
        '''
    
    def __init__(self, session):
        
        Screen.__init__(self, session)
        
        self.onChangedEntry = []           # list of the changed items for display configuration MENU also sets to clean during initialization
        self.list = []                     # I leave the configuration MENU list blank and fill it up later, or when I change the value (after pressing the left / right buttons)
        
        ConfigListScreen.__init__(self, self.list, session, on_change = self.changedEntry)
        
        self['txt_green']   = StaticText(_('Save & Exit'))
        self['txt_red']     = StaticText(_('Exit'))
        #self['txt_yellow']  = StaticText(_('Update plugin'))
        self['txt_blue']    = StaticText(_('Launch now'))
        self['version_txt'] = Label('CAM autorestart - plugin ver. %s' % open(PLUGIN_PATH + 'version.txt', 'r').read().strip() )
        self['author_txt']  = Label('(https://github.com/s3n0/)')
        
        self['actions'] = ActionMap( ['SetupActions', 'ColorActions'], {
            'left'  : self.keyToLeft,
            'right' : self.keyToRight,
            'blue'  : self.keyToBlue,
            'green' : self.exitWithCfgSaveForce,
            'red'   : self.keyToExit,
            'exit'  : self.keyToExit,
            'cancel': self.keyToExit
            } , -2)
        
        self.onShown.append(self.showListMenu)
    
    def keyToLeft(self):
        ConfigListScreen.keyLeft(self)
        self.showListMenu()
    
    def keyToRight(self):
        ConfigListScreen.keyRight(self)
        self.showListMenu()
    
    def keyToBlue(self):
        if doCAMrestart():
            self.session.open(MessageBox, _('Successful !'), type = MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Failed !'), type = MessageBox.TYPE_ERROR)
    
    def exitWithCfgSaveForce(self):
        self.exitWithCfgSaveCondition(True)
    
    def keyToExit(self):
        self.s = self['txt_green'].getText()
        if self.s[-1:] == '*':              # has the plugin configuration changed ... ? if so, I call the MessageBox with the option of saving or restoring the original settings for the plugin configuration
            message = _('You have changed the plugin configuration.\nDo you want to save all changes now ?')
            self.session.openWithCallback(self.exitWithCfgSaveCondition, MessageBox, message, type = MessageBox.TYPE_YESNO, timeout = 0, default = True)
        else:
            self.exitWithCfgSaveCondition(False)
    
    def exitWithCfgSaveCondition(self, condition = True):       # save or cancel changes to user plugin configuration, default = True => save configuration
        if condition:
            for x in self['config'].list:
                x[1].save() 
            config.plugins.camautorestart.enabled.save()
            config.plugins.camautorestart.scheduledtime.save()
            config.plugins.camautorestart.scheduleddays.save()
            configfile.save()                                   # config file "/etc/enigma2/settings" will stored on the hard disk, after the Enigma2-GUI restart only ! 
        else:
            for x in self['config'].list:
                x[1].cancel()
        self.close()
    
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        self['txt_green'].setText(_('Save & Exit') + '*')
    
    def showListMenu(self):
        self.list = []
        self.list.append( getConfigListEntry(  _('Enable plugin:')         ,  config.plugins.camautorestart.enabled       ) )
        self.list.append( getConfigListEntry(  _('Restart at (time):')     ,  config.plugins.camautorestart.scheduledtime ) )
        self.list.append( getConfigListEntry(  _('Restart every (days):')  ,  config.plugins.camautorestart.scheduleddays ) )
        self['config'].list = self.list
        self['config'].setList(self.list)
    
    def restartEnigmaBeforeClosing(self, answer = None):
        if answer:
            self.session.open(TryQuitMainloop, 3)           # 0=Toggle Standby; 1=Deep Standby; 2=Reboot System; 3=Restart Enigma2-GUI; 4=Wake Up; 5=Enter To Standby
        else:
            self.close()      

#########################################################

def doCAMrestart():
    slots = eDVBCIInterfaces.getInstance().getNumOfSlots()
    if slots > 0:           # if the number of DVB CI slots is greater than 0, only then will I restart the device (but only for slot 0)
        eDVBCI_UI.getInstance().setReset(0)
        return True
    else:
        print('DEBUGLINE - CAMautorestart - Error !!! The number of available DVB CI slots is equal to 0 ... or there are no slots !!! Number of DVB CI slots: %s' % slots)
        return False

def checkCurrentTime():
    print('DEBUGLINE - CAMautorestart - checking the time:  %s ==VERSUS== %s' % ( strftime("%H:%M", localtime())  ,  ("%02d:%02d" % tuple(config.plugins.camautorestart.scheduledtime.value)) )  )
    if config.plugins.camautorestart.enabled.value  \
     and not (localtime().tm_mday  %  config.plugins.camautorestart.scheduleddays.value)  \
       and ([localtime().tm_hour, localtime().tm_min]  ==  config.plugins.camautorestart.scheduledtime.value):
        foo_bar = doCAMrestart()

def newOE():
    '''
    return True ---- for commercial versions of Enigma2 core (OE 2.2+) - DreamElite, DreamOS, Merlin, ... etc.
    return False --- for open-source versions of Enigma2 core (OE 2.0 or OE-Alliance 4.x) - OpenATV, OpenPLi, VTi, ... etc.
    '''
#   return os.path.exists('/etc/dpkg')
    
    boo = False
    
    try:
        from enigma import PACKAGE_VERSION
        major, minor, patch = [ int(n) for n in PACKAGE_VERSION.split('.') ]
        if major > 4 or (major == 4 and minor >= 2):    # if major > 4 or major == 4 and minor >= 2:
            boo = True                                  #### new enigma core (DreamElite, DreamOS, Merlin, ...) ===== e2 core: OE 2.2+ ====================== (c)Dreambox core
    except Exception:
        pass
    
    try:
        from Components.SystemInfo import SystemInfo
        if 'MachineBrand' in SystemInfo.keys and 'TeamBlue' in SystemInfo['MachineBrand']:
            boo = False
    except Exception:
        pass
    
    try:
        from boxbranding import getOEVersion
        if getOEVersion().find('OE-Alliance') >= 0:
            boo = False
    except Exception:
        pass
    
    return boo

#########################################################

def sessionStart(reason, session):
    global delayTimer
    if reason == 0:
        #print('PLUGINSTARTDEBUGLOG - CAMautorestart - sessionStart executed , reason = 0')
        delayTimer = eTimer()
        if newOE():
            delayTimer_conn = delayTimer.timeout.connect(checkCurrentTime)  # eTimer for new version of Enigma2 core (OE 2.2+)
        else:
            delayTimer.callback.append(checkCurrentTime)                    # eTimer for old version of Enigma2 core (OE 2.0 / OE-Alliance 4.? open-source core)
        delayTimer.start(60*1000, False)                                    # check the clock every 60 seconds (1 minute)
        print('DEBUGLINE - CAMautorestart - the timer for the DVB CI restart has been started')
    elif reason == 1:
        #print('PLUGINSTARTDEBUGLOG - CAMautorestart - sessionStart executed , reason = 1')
        delayTimer.stop()
        delayTimer = None

def mainStart(session, **kwargs):
    print('PLUGINSTARTDEBUGLOG - CAMautorestart - mainStart executed ,  "session" in kwargs = %s' % ('session' in kwargs)  )
    session.open(pluginConfigurationMenu)

def Plugins(**kwargs):
    return [
        PluginDescriptor(name = "CAM autorestart", description = "Restarting the CAM device at the specified time", where = PluginDescriptor.WHERE_PLUGINMENU, icon = "images/plugin.png", fnc = mainStart), # starts when the plugin is opened via Plugin-MENU
      # PluginDescriptor(where = PluginDescriptor.WHERE_MENU, fnc = menuHook),               # starts when the plugin is opened via E2-Quick-MENU
        PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionStart),   # starts AFTER the Enigma2 booting
      # PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = autoStart)          # starts DURING the Enigma2 booting
        ]
