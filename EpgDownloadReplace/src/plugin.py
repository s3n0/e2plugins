# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from Components.Label import Label
from Components.Sources.StaticText import StaticText

from Components.ActionMap import ActionMap

from Plugins.Plugin import PluginDescriptor
from Components.config import config
#from Components.EpgLoadSave import EpgSaveMsg               # save or load EPG data
#from Components.EpgLoadSave import EpgDeleteMsg             # flush EPG data (delete)
from enigma import eEPGCache

from time import localtime, strftime, strptime, time        # time.localtime() = current date and time in local country ; time.strftime("format", <time as 9-tuple object>) = return date and time formated as string ; # time.strptime("<str>-type date and time", "formating") = returning <type 'time.struct_time'> (9-index <tuple> object type)

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import ConfigSubsection, config, configfile, getConfigListEntry, ConfigText, ConfigYesNo, ConfigClock, ConfigInteger
## ConfigNumber, ConfigDirectory, ConfigSubList, ConfigEnableDisable, ConfigPassword, ConfigSelection

import urllib2
from os import path as os_path, remove as os_remove, system as os_system
from enigma import eTimer

config.plugins.epgdownloadreplace  =  ConfigSubsection()
config.plugins.epgdownloadreplace.enabled       = ConfigYesNo(default=False)
config.plugins.epgdownloadreplace.scheduledtime = ConfigClock(default=0)         # the output value is a list, for example: [17, 59] - it means [hour, min]
config.plugins.epgdownloadreplace.scheduleddays = ConfigInteger(default=3, limits=(1, 15))
config.plugins.epgdownloadreplace.epgonlinefile = ConfigText(default='http://examples.com/dvb/epg.dat', fixed_size=False)

# https://github.com/openatv/enigma2/blob/69bc3dfbf28d95aff4198924a944bf80367aa750/data/menu.xml
# https://github.com/openatv/enigma2/blob/c38f72b1379438489c82031ace100a137bd44c74/lib/python/Components/EpgLoadSave.py


#########################################################
#########################################################


class pluginConfigurationMenu(Screen, ConfigListScreen):    
    skin = '''
        <screen name="pluginConfigurationMenu" position="center,center" size="700,500" title="EpgDownloadReplace" flags="wfNoBorder" backgroundColor="#44000000">   
            <widget name="version_txt" position="0,12" size="700,35" font="Regular;26" foregroundColor="yellow" transparent="1" halign="center" valign="center" zPosition="1" />
            <widget name="author_txt"  position="0,42" size="700,30" font="Regular;22" foregroundColor="yellow" transparent="1" halign="center" valign="center" zPosition="1" />
            
            <widget name="config" position="center,80" size="650,320" font="Regular;22" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#22000000" zPosition="1" />
            
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EpgDownloadReplace/images/btn_red.png" position="5,460" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EpgDownloadReplace/images/btn_green.png" position="140,460" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EpgDownloadReplace/images/btn_yellow.png" position="310,460" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EpgDownloadReplace/images/btn_blue.png" position="485,460" size="40,40" transparent="1" alphatest="on" zPosition="1" />
            
            <widget render="Label" source="txt_red" position="45,460" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
            <widget render="Label" source="txt_green" position="180,460" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
            <widget render="Label" source="txt_yellow" position="350,460" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
            <widget render="Label" source="txt_blue" position="525,460" size="140,40" halign="left" valign="center" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" zPosition="1" />
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
        self['version_txt'] = Label('EPG Download & Replace - v1.0')
        self['author_txt']  = Label('(https://github.com/s3n0/)')
        
        self["actions"] = ActionMap( ["SetupActions", "ColorActions"], {
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
        if makeDownloadAndReplace():
            self.session.open(MessageBox, _('Successful!'), type = MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Failed!'), type = MessageBox.TYPE_ERROR)
    
    def exitWithCfgSaveForce(self):
        self.exitWithCfgSaveCondition(True)
    
    def keyToExit(self):
        self.s = self['txt_green'].getText()
        if self.s[-1:] == '*':              # has the plugin configuration changed ... ? if so, I call the MessageBox with the option of saving or restoring the original settings for the plugin configuration
            message = _("You have changed the plugin configuration.\nDo you want to save all changes now ?")
            self.session.openWithCallback(self.exitWithCfgSaveCondition, MessageBox, message, type = MessageBox.TYPE_YESNO, timeout = 0, default = True)
        else:
            self.exitWithCfgSaveCondition(False)
    
    def exitWithCfgSaveCondition(self, condition = True):       # save or cancel changes to user plugin configuration, default = True => save configuration
        if condition:
            for x in self['config'].list:
                x[1].save() 
            configfile.save()                                   # config file /etc/enigma2/settings will saved only after the Enigma restart !  
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
        self.list.append( getConfigListEntry( _('Enable plugin:')         , config.plugins.epgdownloadreplace.enabled       ))
        self.list.append( getConfigListEntry( _('Update at (time):')      , config.plugins.epgdownloadreplace.scheduledtime ))
        self.list.append( getConfigListEntry( _('Update interval (days):'), config.plugins.epgdownloadreplace.scheduleddays ))
        self.list.append( getConfigListEntry( _('EPG online file:')       , config.plugins.epgdownloadreplace.epgonlinefile ))
        self['config'].list = self.list
        self['config'].setList(self.list)
    
    def restartEnigmaBeforeClosing(self, answer = None):
        if answer:
            self.session.open(TryQuitMainloop, 3)      # 0=Toggle Standby ; 1=Deep Standby ; 2=Reboot System ; 3=Restart Enigma ; 4=Wake Up ; 5=Enter Standby   ### WORKS after invoking and successfully completing the PLUGIN update  ### but DOES NOT WORK when calling from leaveSetupScreen(self) after picon update because an error occurs: "RuntimeError: modal open are allowed only from a screen which is modal!"
        else:
            self.close()      


#########################################################
#########################################################


def epgSave():
    epgcache = eEPGCache.getInstance()
    epgcache.save()
    print('DEBUGLINE - epgSave was executed')

def epgLoad():
    epgcache = eEPGCache.getInstance()
    epgcache.load()
    print('DEBUGLINE - epgLoad was executed')

def epgDelete():
    if os_path.exists(config.misc.epgcache_filename.value):
        os_remove(config.misc.epgcache_filename.value)      
    epgcache = eEPGCache.getInstance()
    epgcache.flushEPG()
    print('DEBUGLINE - epgDelete was executed')


###############
###############


def downloadFile(url, targetfile):
    #if os_system('wget --no-check-certificate -q -O %s %s > /dev/null 2>&1' % (targetfile, url)  ):
    try:
        response = urllib2.urlopen(url)
        with open(targetfile, 'wb') as f:
            f.write(response.read())
    except Exception as err:
        print('DEBUGLINE - epg file download failed - err:%s' % err)
        return False
    else:
        print('DEBUGLINE - epg file download successfully')
        return True

def makeDownloadAndReplace():
    if downloadFile(config.plugins.epgdownloadreplace.epgonlinefile.value, '/tmp/e'):
        epgDelete()
        os_system('mv -f /tmp/e %s' % config.misc.epgcache_filename.value)
        epgLoad()
        pockaj = eTimer()
        pockaj.callback.append(epgSave)
        pockaj.start(5000, True)     # prevention - I start saving EPG to disk a few seconds later to prevent the "epg.dat" file from being saved to disk
        #epgSave()
        return True
    else:
        return False

def checkDownloadAndReplaceEPG():
    #print('DEBUGLINE - epg - checking time ---%s---%s---' % (strftime("%H:%M", localtime()), ("%02d:%02d" % tuple(config.plugins.epgdownloadreplace.scheduledtime.value)) ) )
    if config.plugins.epgdownloadreplace.enabled.value    \
     and not (localtime().tm_mday  %  config.plugins.epgdownloadreplace.scheduleddays.value)    \
      and [ localtime().tm_hour , localtime().tm_min ]  ==  config.plugins.epgdownloadreplace.scheduledtime.value:
        makeDownloadAndReplace()

def epgFileIsLose():
    if config.plugins.epgdownloadreplace.enabled.value:
        if not os_path.isfile(config.misc.epgcache_filename.value):     # if 'epg.dat' does not exists... (default in: '/etc/enigma2/epg.dat')
            return True                                                 #     then renew the 'epg.dat' file from internet
        # but if the 'epg.dat' already exists, then check the file creation date and renew the file from internet if neccessary 
        tshift = os_path.getctime(config.misc.epgcache_filename.value) + (config.plugins.epgdownloadreplace.scheduleddays.value * 3600 * 24)       # 1 h === 3600 sec
        if time() > tshift:                                             # comparing two unix-timestamps        
            return True
        if os_path.getsize(config.misc.epgcache_filename.value) < 2000000:
            return True
    return False

#########################################################
#########################################################



def sessionStart(reason, session):
    global checkTimer
    if reason == 0:
        #print('PLUGINSTARTDEBUGLOG - sessionStart executed , reason == 0')
        if epgFileIsLose():
            makeDownloadAndReplace()
        checkTimer = eTimer()
        checkTimer.callback.append(checkDownloadAndReplaceEPG)
        checkTimer.start(60*1000, False)              # check the clock every 60 sec. (1 min.)
    elif reason == 1:
        #print('PLUGINSTARTDEBUGLOG - sessionStart executed , reason == 1')
        checkTimer.stop()

def mainStart(session, **kwargs):
    #print('PLUGINSTARTDEBUGLOG - mainStart executed , kwargs.has_key("session") = %s' % kwargs.has_key("session")  )
    session.open(pluginConfigurationMenu)

def Plugins(**kwargs):
    return [
        PluginDescriptor(name = "EPG - download & replace", description = "Download and replace 'epg.dat' file", where = PluginDescriptor.WHERE_PLUGINMENU, icon = "images/plugin.png", fnc = mainStart), # starts when the plugin is opened via Plugin-MENU
      # PluginDescriptor(where = PluginDescriptor.WHERE_MENU, fnc = menuHook),               # starts when the plugin is opened via E2-Quick-MENU
        PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionStart),   # starts AFTER the Enigma2 booting
      # PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = autoStart)          # starts DURING the Enigma2 booting
        ]


#########################################################
#########################################################

