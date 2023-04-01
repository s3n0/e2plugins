# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

####################################################
#
#  EPG Export
#  Plugin to export your EPG as XMLTV files
#
#  (c) by gutemine
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
####################################################
#
#  ORIGINAL SOURCE (FORKED FROM):
#    - https://github.com/leaskovski/EPGExport/blob/master/src/plugin.py
#
#  2023-03-29 edit by s3n0:
#    - source code modified for Python3 support
#    - CONTROL file (inside the IPK file) dependencies chanded to:    python3-requests python3-backports-lzma
#
#
#
#
#
#
####################################################

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen, ConfigList
from Plugins.Plugin import PluginDescriptor
from Components.Label import Label
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, ConfigSelection, ConfigEnableDisable, ConfigSlider, NoSave, ConfigSubsection, getConfigListEntry, ConfigIP, ConfigSubList, ConfigClock
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Renderer.Picon import getPiconName
from enigma import getDesktop, eTimer, eActionMap, eEPGCache, eServiceCenter, eServiceReference,  eTimer, getDesktop, iPlayableService, eSize, eConsoleAppContainer
from Screens.InfoBar import InfoBar
from ServiceReference import ServiceReference
from twisted.web import resource, http
from twisted.internet import threads, reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.static import File
from backports import lzma
from os import path as os_path, mkdir as os_mkdir, rmdir as os_rmdir, symlink as os_symlink, readlink as os_readlink, remove as os_remove, listdir as os_listdir
import gzip
import requests
import time
import datetime
import xml.etree.ElementTree as etree
import socket
from socket import gethostname, getfqdn
from time import gmtime, strftime

# Global variables
global WebTimer
global WebTimer_conn
global EPGExportAutoStartTimer

epgexport_name        = "EPG Export"
epgexport_plugindir   = "/usr/lib/enigma2/python/Plugins/Extensions/EPGExport"
epgimport_plugindir   = "/usr/lib/enigma2/python/Plugins/Extensions/EPGImport"
epgload_plugindir     = "/usr/lib/enigma2/python/Plugins/Extensions/EPGLoad"
epgexport_version     = open(epgexport_plugindir + "/version.txt", "r").read().strip()
epgexport_description = _("Export EPG as XML")
epgexport_title       = _("%s plugin - ver. %s") % (epgexport_name, epgexport_version)
epgexport_selection   = _("EPG Selection") + " " + _("Bouquet")
epgexport_thanks      = _("%s plugin ver. %s\n\n(c) gutemine 2019\n\nSpecial Thanks to Rytec for the XMLTV Format !") % (epgexport_name, epgexport_version)

if os_path.exists("/usr/lib/enigma2/python/Plugins/Extensions/GoldenPanel/plugin.pyo"):
    os_remove("/usr/lib/enigma2/python/Plugins/Extensions/GoldenPanel/plugin.pyo")

if os_path.exists("/usr/lib/enigma2/python/Plugins/Extensions/GoldenFeed/plugin.pyo"):
    os_remove("/usr/lib/enigma2/python/Plugins/Extensions/GoldenFeed/plugin.pyo")

yes_no_descriptions = { False: _("no"), True: _("yes") }

config.plugins.epgexport = ConfigSubsection()
compr_opt = []
compr_opt.append(( "none", _("None")  ))
compr_opt.append(( "xz"  , _("xz")    ))
compr_opt.append(( "gz"  , _("gz")    ))
config.plugins.epgexport.compression = ConfigSelection(default="xz", choices=compr_opt)
with open("/proc/mounts", "r") as f:
    mounts = f.read()
save_opt = []
save_opt.append(("etc"       , "/etc/epgexport"))
save_opt.append(("volatile"  , "/var/volatile/epgexport"))
if mounts.find("/data") is not -1:
    save_opt.append(("data"  , "/data/epgexport"))
if mounts.find("/media/hdd") is not -1:
    save_opt.append(("hdd"   , "/media/hdd/epgexport"))
if mounts.find("/media/usb") is not -1:
    save_opt.append(("usb"   , "/media/usb/epgexport"))
if mounts.find("/media/sdcard") is not -1:
    save_opt.append(("sdcard", "/media/sdcard/epgexport"))
config.plugins.epgexport.epgexport = ConfigSelection(default="volatile", choices=save_opt)
channel_opt = []
channel_opt.append(("name"     , _("Channel") + " " + _("Name")  ))
channel_opt.append(("names"    , _("Channel") + _("Name")        ))
cname = _("Channel") + _("Name")
channel_opt.append(("nameslow" , cname.lower()  ))
channel_opt.append(("nameslang", cname + "." + _("Language").lower()  ))
channel_opt.append(("nameslowlang", cname.lower() + "." + _("Language").lower()  ))
channel_opt.append(("number"   , _("Channel") + " " + _("Number")  ))
channel_opt.append(("xml"      , _("Custom (%s)") % "xml" ))
config.plugins.epgexport.channelid = ConfigSelection(default="name", choices=channel_opt)
config.plugins.epgexport.twisted = ConfigYesNo(default=True)
epgserver_opt = []
epgserver_opt.append(("none" , _("disabled")    ))
epgserver_opt.append(("ip"   , _("IP Address")  ))
epgserver_opt.append(("name" , _("Server IP").replace("IP", _("Name"))  ))
config.plugins.epgexport.server   = ConfigSelection(default="none", choices=epgserver_opt)
config.plugins.epgexport.ip       = ConfigIP(default=[192, 168, 0, 100])
config.plugins.epgexport.hostname = ConfigText(default="localhost", visible_width=50, fixed_size=False)
custom_str = _("Custom (%s)") % ""
custom_str = custom_str.replace("(", "").replace(")", "").rstrip()
webif_options = []
webif_options.append(( "none", _("disabled") ))
if os_path.exists("/var/lib/dpkg/status"):
    webif_options.append(( "standard", _("Standard") ))
webif_options.append(("custom", custom_str))
config.plugins.epgexport.webinterface = ConfigSelection(default="none", choices=webif_options)
config.plugins.epgexport.port = ConfigInteger(default=4444, limits=(4000,4999))
days_options = []
for days in range(1, 31):
        days_options.append(( str(days), str(days) ))
config.plugins.epgexport.days = ConfigSelection(default="5", choices=days_options)
reload_options = []
reload_options.append(( "0", _("always") ))
for hours in range(1, 25):
        reload_options.append(( str(hours), str(hours) ))
config.plugins.epgexport.reload = ConfigSelection(default="0", choices=reload_options)
config.plugins.epgexport.daily = ConfigEnableDisable(default=False)
config.plugins.epgexport.wakeup = ConfigClock(default=( (6*60) + 45 ) * 60)
if os_path.exists("/var/lib/dpkg/status"):
    outdated = int(config.misc.epgcache_outdated_timespan.value) // 24
else:
    outdated = 0
if outdated > 7:
    outdated = 7
if outdated < 0:
    outdated = 0
outdated_options = []
outdated_options.append(( "0", _("none") ))
for days in range(1, 8):
    outdated_options.append(( str(days), str(days) ))
config.plugins.epgexport.outdated = ConfigSelection(default=str(outdated), choices=outdated_options)
bouquet_options = []
for bouquet in os_listdir("/etc/enigma2"):
    if bouquet.startswith("userbouquet.") and bouquet.endswith(".tv"):
        with open("/etc/enigma2/%s" % bouquet,"r") as f:
            name = f.readline()
        name = name.replace("#NAME ", "").replace(" (TV)", "").rstrip()
        bouquet_options.append(( name.lower(), name ))
fav = False
for bouquet in bouquet_options:
    if bouquet[0] == "favorites":
        fav = True
if not fav: # prevent crashes if default not found ...
    bouquet_options.append(( "favorites", _("Favorites") ))
bouquet_options.sort()
config.plugins.epgexport.bouquets = ConfigSubList()
bouquet_length = len(bouquet_options)
for x in range(bouquet_length):
    config.plugins.epgexport.bouquets.append(ConfigSubsection())
    config.plugins.epgexport.bouquets[x].export      = ConfigYesNo(default=False)
    config.plugins.epgexport.bouquets[x].name        = ConfigText(default="")
    config.plugins.epgexport.bouquets[x].name.value  = bouquet_options[x][0]
    config.plugins.epgexport.bouquets[x].name.save()

YELLOWC = "\033[33m"
ENDC = "\033[m"

def cprint(text):
    with open("/tmp/epgexport.log", "a") as f:
        f.write(strftime("%x %X", gmtime()) + " - " + text + "\n")

def checkLastUpdate():
    update_file_name = "/etc/epgexport/LastUpdate.txt"
    update = True
    if not os_path.exists("/etc/epgexport/epgexport.channels.xml.xz"):
        return update
    if not os_path.exists("/etc/epgexport/epgexport.xz"):
        return update
    if os_path.exists(update_file_name):
        # Used to check server validity
        date_format = "%Y-%m-%d %H:%M:%S"
        allowed_delta = 3600*int(config.plugins.epgexport.reload.value)
        now = int(time.time())
        cprint("now %d" % now)
        x = open(update_file_name, "r")
        Last = x.readline()
        x.close()
        LastTime = Last.strip("\n")
        file_date = 0
        try:
            FileDate = datetime.datetime.strptime(LastTime, date_format)
            file_date = int(FileDate.strftime("%s"))
        except:
            pass
        cprint("File Date %d" % file_date)
        delta = (now - file_date)
        cprint("delta seconds %d" % delta)
        if delta <= allowed_delta:
            update = False
    return update

def exportLastUpdate():
    now = datetime.datetime.now()
    # always use current date and time
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    cprint("date: %s" % date)
    update_file_name = "/etc/epgexport/LastUpdate.txt"
    f = open(update_file_name, "w")
    f.write(date)
    f.write("\n")
    f.close()

Session = None
Servicelist = None
epg_bouquet = None
bouquet_name = None

epgexport_string = """<?xml version="1.0" encoding="latin-1"?>
<sources>
<mappings>
<channel name="epgexport.channels.xml.xz">
   <url>http://localhost/epgexport.channels.xml.xz</url>
</channel>
</mappings>
<sourcecat sourcecatname="EPG Export XMLTV">
<source type="gen_xmltv" nocheck="1" channels="epgexport.channels.xml.xz">
<description>EPG Export Channels (xz) (c) gutemine 2019</description>
   <url>http://localhost/epgexport.xz</url>
</source>
</sourcecat>
</sources>"""

sz_w = getDesktop(0).size().width()

def startEPGExport(session, **kwargs):
    servicelist = kwargs.get("servicelist", None)
    if servicelist is None:
        if InfoBar is not None:
            InfoBarInstance = InfoBar.instance
            if InfoBarInstance is not None:
                servicelist = InfoBarInstance.servicelist
    global Servicelist
    Servicelist = servicelist
    session.open(EPGExportConfiguration)

def cleanepgexport(keep=True):
    if os_path.exists("/etc/epgexport/LastUpdate.txt"):
        os_remove("/etc/epgexport/LastUpdate.txt")
    if os_path.exists("/etc/epgexport/epgexport.channels.xml"):
        os_remove("/etc/epgexport/epgexport.channels.xml")
    if os_path.exists("/etc/epgexport/epgexport.channels.xml.gz"):
        os_remove("/etc/epgexport/epgexport.channels.xml.gz")
    if os_path.exists("/etc/epgexport/epgexport.channels.xml.xz"):
        os_remove("/etc/epgexport/epgexport.channels.xml.xz")
    if os_path.exists("/etc/epgexport/epgexport"):
        os_remove("/etc/epgexport/epgexport")
    if os_path.exists("/etc/epgexport/epgexport.gz"):
        os_remove("/etc/epgexport/epgexport.gz")
    if os_path.exists("/etc/epgexport/epgexport.xz"):
        os_remove("/etc/epgexport/epgexport.xz")
    if os_path.exists("/etc/epgexport/custom.channels.xml"):
        os_remove("/etc/epgexport/custom.channels.xml")
    if not keep and os_path.exists("/etc/epgexport"):
        os_rmdir("/etc/epgexport")

def fixepgexport():
    save_path = config.plugins.epgexport.epgexport.value
    if save_path == "etc":
        if os_path.islink("/etc/epgexport"):
            os_remove("/etc/epgexport")
            os_mkdir("/etc/epgexport", mode=0o777)
        cprint("is /etc/epgexport")
    elif save_path == "volatile":
        if not os_path.islink("/etc/epgexport"):
            cleanepgexport()
        if not os_path.exists("/var/volatile/epgexport"):
            os_mkdir("/var/volatile/epgexport", mode=0o777)
        if not os_path.exists("/etc/epgexport"):
            os_symlink("/var/volatile/epgexport", "/etc/epgexport")
        else:
            source = os_readlink("/etc/epgexport")
            if source != "/var/volatile/epgexport":
                os_remove("/etc/epgexport")
                os_symlink("/var/volatile/epgexport", "/etc/epgexport")
        cprint("is /var/volatile/epgexport")
    elif save_path == "data":
        if not os_path.islink("/etc/epgexport"):
            cleanepgexport()
        if not os_path.exists("/data/epgexport"):
            os_mkdir("/data/epgexport", mode=0o777)
        if not os_path.exists("/etc/epgexport"):
            os_symlink("/data/epgexport", "/etc/epgexport")
        else:
            source=os_readlink("/etc/epgexport")
            if source != "/data/epgexport":
                os_remove("/etc/epgexport")
                os_symlink("/data/epgexport", "/etc/epgexport")
        cprint("is /data/epgexport")
    elif save_path=="hdd":
        if not os_path.islink("/etc/epgexport"):
            cleanepgexport()
        if not os_path.exists("/media/hdd/epgexport"):
            os_mkdir("/media/hdd/epgexport", mode=0o777)
        if not os_path.exists("/etc/epgexport"):
            os_symlink("/media/hdd/epgexport", "/etc/epgexport")
        else:
            source=os_readlink("/etc/epgexport")
            if source != "/media/hdd/epgexport":
                os_remove("/etc/epgexport")
                os_symlink("/media/hdd/epgexport", "/etc/epgexport")
        cprint("is /media/hdd/epgexport")
    elif save_path == "usb":
        if not os_path.islink("/etc/epgexport"):
            cleanepgexport()
        if not os_path.exists("/media/usb/epgexport"):
            os_mkdir("/media/usb/epgexport", mode=0o777)
        if not os_path.exists("/etc/epgexport"):
            os_symlink("/media/usb/epgexport", "/etc/epgexport")
        else:
            source=os_readlink("/etc/epgexport")
            if source != "/media/usb/epgexport":
                os_remove("/etc/epgexport")
                os_symlink("/media/usb/epgexport","/etc/epgexport")
        cprint("is /media/usb/epgexport")
    elif save_path == "sdcard":
        if not os_path.islink("/etc/epgexport"):
            cleanepgexport()
        if not os_path.exists("/media/sdcard/epgexport"):
            os_mkdir("/media/sdcard/epgexport", mode=0o777)
        if not os_path.exists("/etc/epgexport"):
            os_symlink("/media/sdcard/epgexport", "/etc/epgexport")
        else:
            source=os_readlink("/etc/epgexport")
            if source != "/media/sdcard/epgexport":
                os_remove("/etc/epgexport")
                os_symlink("/media/sdcard/epgexport", "/etc/epgexport")
        cprint("is /media/sdcard/epgexport")
    else:   # none
        if os_path.islink("/etc/epgexport"):
            os_remove("/etc/epgexport")
        else:
            cleanepgexport()
        cprint("is none")

#####################################
# class for Autostart of EPG Export #
#####################################
class EPGExportAutoStartTimer:

    def __init__(self, session):
        self.session = session
        self.EPGExportTimer = eTimer()
        if os_path.exists("/var/lib/dpkg/status"):
            self.EPGExportTimer_conn = self.EPGExportTimer.timeout.connect(self.onEPGExportTimer)
        else:
            self.EPGExportTimer.callback.append(self.onEPGExportTimer)
        self.update()

    def getWakeTime(self):
        if config.plugins.epgexport.daily.value:
            clock = config.plugins.epgexport.wakeup.value
            nowt = time.time()
            now = time.localtime(nowt)
            return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday,
                        clock[0], clock[1], 0, 0, now.tm_yday, now.tm_isdst)))
        else:
            cprint("automatic epg exporting is disabled")
            return -1

    def update(self, atLeast=0):
        self.EPGExportTimer.stop()
        wake = self.getWakeTime()
        now = int(time.time())
        if wake > 0:
            if wake < now + atLeast:
                # Tomorrow.
                wake += 24 * 3600
            next = wake - now
            self.EPGExportTimer.startLongTimer(next)
            cprint("WakeUpTime now set to %d seconds (now=%d)" % (next, now))
        else:
            wake = -1

    def onEPGExportTimer(self):
        self.EPGExportTimer.stop()
        now = int(time.time())
        cprint("onTimer occured at %d" % now)
        wake = self.getWakeTime()
        # If we're close enough, we're okay...
        atLeast = 0
        if wake - now < 60:
            self.autoEPGExport()
            atLeast = 60
        # restart timer for next day ...
        self.update(atLeast)

    def autoEPGExport(self):
        cprint("automatic epg export starts")
        EPGExport(None, config.plugins.epgexport.compression.value, True, True)

def sessionstart(reason, **kwargs):
        if reason == 0 and "session" in kwargs:
            session = kwargs.get("session", None)
            fixepgexport()
            if config.plugins.epgexport.webinterface.value == "standard":
                cprint("STANDARD WEBIF")
                from Plugins.Extensions.WebInterface.WebChilds.Toplevel import addExternalChild, File
                # source XMLTV file is uncompressed
                addExternalChild( ("epgexport.sources.xml", EPGExportSource(), "epgexport.sources.xml", "1", True) )
                # timestamp for server check
                addExternalChild( ("LastUpdate.txt", EPGExportLastUpdate(), "LastUpdate.txt", "1", True) )
                # channels XMLTV file
                addExternalChild( ("epgexport.channels.xml", EPGExportChannels(), "epgexport.channels.xml", "1", True) )
                # channels XMLTV xz file
                addExternalChild( ("epgexport.channels.xml.xz", EPGExportChannels(), "epgexport.channels.xml.xz", "1", True) )
                # channels XMLTV gz file
                addExternalChild( ("epgexport.channels.xml.gz", EPGExportChannels(), "epgexport.channels.xml.gz", "1", True) )
                # programs XMLTV file
                addExternalChild( ("epgexport", EPGExportPrograms(), "epgexport", "1", True) )
                # programs XMLTV xz file
                addExternalChild( ("epgexport.xz", EPGExportPrograms(), "epgexport.xz", "1", True) )
                # programs XMLTV gz file
                addExternalChild( ("epgexport.gz", EPGExportPrograms(), "epgexport.gz", "1", True) )
            elif config.plugins.epgexport.webinterface.value == "custom":
                # run Custom Webinterface
                if config.plugins.epgexport.twisted.value:
                    cprint("CUSTOM WEBIF TWISTED")
                    threads.deferToThread(startingCustomEPGExternal).addCallback(lambda ignore: finishedCustomEPGExternal())
                else:
                    cprint("CUSTOM WEBIF THREAD")
                    global WebTimer
                    global WebTimer_conn
                    WebTimer = eTimer()
                    if not os_path.exists("/var/lib/opkg/status"):
                            WebTimer_conn = WebTimer.timeout.connect(startingCustomEPGExternal)
                    else:
                            WebTimer.callback.append(startingCustomEPGExternal)
                    WebTimer.start(5000, True)
            else:
                cprint("NO Webinterface at all")
            ##################################
            # Autostart of EPG Export
            ##################################
            global EPGExportAutoStartTimer
            cprint("AUTOSTART TIMER")
            EPGExportAutoStartTimer = EPGExportAutoStartTimer(session)

def startingCustomEPGExternal():
    resourceSource   = EPGExportSource()
    resourceLast     = EPGExportLastUpdate()
    resourceChannels = EPGExportChannels()
    resourcePrograms = EPGExportPrograms()

    root = Resource()
    root.putChild(b"epgexport.sources.xml", resourceSource)
    root.putChild(b"LastUpdate.txt", resourceLast)
    root.putChild(b"epgexport.channels.xml", resourceChannels)
    root.putChild(b"epgexport.channels.xml.gz", resourceChannels)
    root.putChild(b"epgexport.channels.xml.xz", resourceChannels)
    root.putChild(b"epgexport", resourcePrograms)
    root.putChild(b"epgexport.gz", resourcePrograms)
    root.putChild(b"epgexport.xz", resourcePrograms)

    factory = Site(root)
    port = int(config.plugins.epgexport.port.value)
    reactor.listenTCP(port, factory)
    try:
        reactor.run()
    except:
        pass

#def b2s(s):             # converting data type... `string` to `bytes`... if the variable is `string`
#    if isinstance(s, str):
#        return bytes(s, 'utf8')
#    else:
#        return s

def finishedCustomEPGExternal():
    cprint("Custom Webinterface Finished!!!")

def Plugins(**kwargs):
    return [ PluginDescriptor(name=epgexport_name, description=epgexport_description, where = PluginDescriptor.WHERE_PLUGINMENU, icon="epgexport.png", fnc=startEPGExport),
             PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart, needsRestart=False)  ]

sz_w = getDesktop(0).size().width()

class EPGExportConfiguration(Screen, ConfigListScreen):

    if sz_w == 1920:
        skin = """
        <screen position="center,170" size="1200,870" title="EPGExport" >
        <widget name="logo" position="20,10" size="150,60" transparent="1" alphatest="on" />
            <widget backgroundColor="#9f1313" font="Regular;24" halign="center" name="buttonred" position="190,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <widget backgroundColor="#1f771f" font="Regular;24" halign="center" name="buttongreen" position="440,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <widget backgroundColor="#a08500" font="Regular;24" halign="center" name="buttonyellow" position="690,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <widget backgroundColor="#18188b" font="Regular;24" halign="center" name="buttonblue" position="940,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <eLabel backgroundColor="grey" position="20,80" size="1160,1" />
                <widget name="config" enableWrapAround="1" position="20,90" scrollbarMode="showOnDemand" size="1160,680" />
                <eLabel backgroundColor="grey" position="20,780" size="1160,1" />
        <widget name="statustext" position="20,790" size="1160,70" font="Regular;36" halign="center" valign="center" foregroundColor="white"/>
        </screen>"""
    else:
        skin = """
        <screen position="center,120" size="820,580" title="EPGExport" >
        <widget name="logo" position="10,10" size="100,40" transparent="1" alphatest="on" />
            <widget backgroundColor="#9f1313" font="Regular;18" halign="center" name="buttonred" position="120,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <widget backgroundColor="#1f771f" font="Regular;18" halign="center" name="buttongreen" position="295,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <widget backgroundColor="#a08500" font="Regular;18" halign="center" name="buttonyellow" position="470,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <widget backgroundColor="#18188b" font="Regular;18" halign="center" name="buttonblue" position="645,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <eLabel backgroundColor="grey" position="10,60" size="800,1" />
            <widget name="config" enableWrapAround="1" position="10,70" size="800,450" scrollbarMode="showOnDemand" />
                <eLabel backgroundColor="grey" position="10,530" size="800,1" />
        <widget name="statustext" position="10,535" size="800,40" font="Regular;24" halign="center" valign="center" foregroundColor="white"/>
        </screen>"""

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.skin = EPGExportConfiguration.skin
        self.session = session
        self.onShown.append(self.setWindowTitle)
        # explicit check on every entry
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.refreshLayout)
        self["statustext"] = Label("")
        self["logo"] = Pixmap()
        self["buttonred"] = Label(_("Exit"))
        self["buttongreen"] = Label(_("Save"))
        self["buttonyellow"] = Label(_("Downloading"))
        self["buttonblue"] = Label(_("Select")+" "+_("Bouquets"))
        self["actions"] = ActionMap(["SetupActions", "ColorActions", "ChannelSelectEPGActions", "InfobarTeletextActions"],{"ok": self.save,  "exit": self.cancel, "cancel": self.cancel, "red": self.cancel, "green": self.save, "yellow": self.yellow_key, "blue": self.blue_key, "showEPGList": self.about, "startTeletext": self.getText })

    def setWindowTitle(self):
        self["logo"].instance.setPixmapFromFile("%s/epgexport.png" % epgexport_plugindir)
        if config.plugins.epgexport.compression.value == "xz":
            self["buttonyellow"].setText( _("Downloading") + " (xz)")
        elif config.plugins.epgexport.compression.value == "gz":
            self["buttonyellow"].setText( _("Downloading") + " (gz)")
        else:
            self["buttonyellow"].setText( _("Downloading") )
        self.setTitle(epgexport_title)

    def save(self):
        self["statustext"].setText(_("Saving") + " " + _("Configuration") + " " + _("..."))
        if config.plugins.epgexport.channelid.value == "xml" and not os_path.exists("/etc/epgexport/custom.channels.xml"):
            config.plugins.epgexport.channelid.value = "name"

        for x in self["config"].list:
            if len(x) > 1:
                x[1].save()

        if config.plugins.epgexport.server.value != "none":
            if config.plugins.epgexport.server.value == "ip":
                host = "%d.%d.%d.%d" % tuple(config.plugins.epgexport.ip.value)
            else:
                host = config.plugins.epgexport.hostname.value
            epg_string = epgexport_string.replace("localhost", host)
            if config.plugins.epgexport.compression.value == "xz":
                epg_string = epgexport_string.replace("localhost", host)
            elif config.plugins.epgexport.compression.value == "gz":
                epg_string = epgexport_string.replace("localhost",host).replace("xz", "gz")
            else:
                epg_string = epgexport_string.replace("localhost",host).replace(".xz", "").replace("(xz) ", "")
            # add port for custom webinterface
            if config.plugins.epgexport.webinterface.value == "custom":
                port = config.plugins.epgexport.port.value
                epg_string = epg_string.replace("/epgexport", ":%s/epgexport" % port)
            if not os_path.exists("/etc/epgimport"):
                os_mkdir("/etc/epgimport", mode=0o777)
            f = open("/etc/epgimport/epgexport.sources.xml", "w+")
            f.write(epg_string)
            f.close()
            if not os_path.exists("/etc/epgload"):
                os_mkdir("/etc/epgload", mode=0o777)
            f = open("/etc/epgload/epgexport.sources.xml", "w+")
            f.write(epg_string)
            f.close()
        else:
            if os_path.exists("/etc/epgimport/epgexport.sources.xml"):
                os_remove("/etc/epgimport/epgexport.sources.xml")
            if os_path.exists("/etc/epgload/epgexport.sources.xml"):
                os_remove("/etc/epgload/epgexport.sources.xml")
        fixepgexport()
        self.close(True)

    def cancel(self):
        self["statustext"].setText(_("Leaving") + " " + _("Configuration") + " " + _("..."))
        for x in self["config"].list:
            if len(x) > 1:
                x[1].cancel()
        self.close(False)

    def createSetup(self):
        # init only on first run
        self.refreshLayout(True)

    def refreshLayout(self, first=False):
        self.list = []
        self.list.append((("* * * ") + _("Electronic Program Guide") + " " + _("XML") + " * * *", ))
        self.list.append(getConfigListEntry(_("Location"), config.plugins.epgexport.epgexport))
        self.list.append(getConfigListEntry(_("EPG") + " " + _("Download") + " (" + _("Days") + ")", config.plugins.epgexport.days))
        self.list.append(getConfigListEntry(_("EPG") + " " + _("Update") + " (" + _("hours") + ")", config.plugins.epgexport.reload))
        self.list.append(getConfigListEntry(_("Keep outdated EPG (in hours)").replace(_("hours"), _("Days")), config.plugins.epgexport.outdated))
        self.list.append(getConfigListEntry(_("daily") + " " + _("EPG") + " " + _("Download"), config.plugins.epgexport.daily))
        if config.plugins.epgexport.daily.value:
            self.list.append(getConfigListEntry(_("daily") + " " + _("StartTime"), config.plugins.epgexport.wakeup))
        self.list.append(getConfigListEntry(_("Compression"), config.plugins.epgexport.compression))
        self.list.append(getConfigListEntry(_("Channel") + " " + _("ID"), config.plugins.epgexport.channelid))
        self.list.append(getConfigListEntry(_("Twisted") + " " + _("Background"), config.plugins.epgexport.twisted))
        self.list.append((("* * * ") + _("Source") + " " + _("XML") + " * * *",))
        self.list.append(getConfigListEntry(_("OpenWebIf Picon Location"), config.plugins.epgexport.server))
        if config.plugins.epgexport.server.value == "ip":
            self.list.append(getConfigListEntry(_("IP Address"), config.plugins.epgexport.ip))
        if config.plugins.epgexport.server.value == "name":
            self.list.append(getConfigListEntry(_("Server IP").replace("IP",_("Name")), config.plugins.epgexport.hostname))
        self.list.append((("* * * ") + _("Configuration for the Webinterface") + " * * *",))
        self.list.append(getConfigListEntry(_("Select") + " (" + _("Restart GUI") + ")", config.plugins.epgexport.webinterface))
        if config.plugins.epgexport.webinterface.value == "custom":
            self.list.append(getConfigListEntry(_("Server IP").replace("IP", _("Port")), config.plugins.epgexport.port))

        if first:
            self.menuList = ConfigList(self.list)
            self.menuList.list = self.list
            self.menuList.l.setList(self.list)
            self["config"] = self.menuList
            self["config"].onSelectionChanged.append(self.selectionChanged)
        else:
            self.menuList.list = self.list
            self.menuList.l.setList(self.list)

    def selectionChanged(self):
        choice = self["config"].getCurrent()
        current = choice[1]
        hostname = config.plugins.epgexport.hostname
        ip = config.plugins.epgexport.ip
        if current == ip:
            self["buttonyellow"].setText(_("Server IP"))
        elif current == hostname:
            self["buttonyellow"].setText(_("Hostname"))
        else:
            if config.plugins.epgexport.compression.value == "xz":
                self["buttonyellow"].setText(_("Downloading") + " (xz)")
            elif config.plugins.epgexport.compression.value == "gz":
                self["buttonyellow"].setText(_("Downloading") + " (gz)")
            else:
                self["buttonyellow"].setText(_("Downloading"))

    def changedEntry(self):
        choice = self["config"].getCurrent()
        current = choice[1]
        hostname = config.plugins.epgexport.hostname
        if config.plugins.epgexport.channelid.value == "xml" and not os_path.exists("/etc/epgexport/custom.channels.xml"):
            config.plugins.epgexport.channelid.value = "name"
        if choice != None:
            if current != hostname:
                self.refreshLayout()

    def yellow_key(self):
        choice = self["config"].getCurrent()
        current = choice[1]
        hostname = config.plugins.epgexport.hostname
        ip = config.plugins.epgexport.ip
        if current == ip:
            ip = self.getIP()
            lip = ip.split(".")
            # make tuple by hand ...
            localip = [ int(lip[0]), int(lip[1]), int(lip[2]), int(lip[3]) ]
            config.plugins.epgexport.ip.value = localip
            self.refreshLayout()
        elif current == hostname:
            hostname = gethostname()
            fullname = getfqdn(hostname)
            config.plugins.epgexport.hostname.value = fullname
            self.refreshLayout()
        else:
            selected = 0
            for x in range(bouquet_length):
                if config.plugins.epgexport.bouquets[x].export.value:
                    selected += 1
            if selected < 1:
                for x in range(bouquet_length):
                    if config.plugins.epgexport.bouquets[x].name.value == "favorites":
                        config.plugins.epgexport.bouquets[x].export.value = True
                        config.plugins.epgexport.bouquets[x].export.save()
                        cprint("nothing selected, means Favorites")
            fixepgexport()
            self["statustext"].setText(_("EPG") + " " + _("Downloading"))
            if config.plugins.epgexport.twisted.value:
                threads.deferToThread(self.startingEPGExport).addCallback(lambda ignore: self.finishedEPGExport())
            else:
                self.startingEPGExport()
                self.finishedEPGExport()

    def startingEPGExport(self):
        self["statustext"].setText(_("EPG") + " " + _("Downloading") + " " + _("..."))
        EPGExport(self, config.plugins.epgexport.compression.value, True, True)

    def finishedEPGExport(self):
        loaded = ""
        for x in range(bouquet_length):
            if config.plugins.epgexport.bouquets[x].export.value:
                loaded += "%s\n" % config.plugins.epgexport.bouquets[x].name.value
        if config.plugins.epgexport.compression.value == "xz":
            self.session.open(MessageBox, _("EPG") + " " + _("Downloading") + " (xz):\n\n" + loaded.upper() + "\n" + _("Execution finished!!"), MessageBox.TYPE_INFO)
        elif config.plugins.epgexport.compression.value == "gz":
            self.session.open(MessageBox, _("EPG") + " " + _("Downloading") + " (gz):\n\n" + loaded.upper()+"\n" + _("Execution finished!!"), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _("EPG") + " " + _("Downloading") + ":\n\n" + loaded.upper() + "\n\n" + _("Execution finished!!"), MessageBox.TYPE_INFO)

    def about(self):
        self.session.open(MessageBox, epgexport_thanks, MessageBox.TYPE_INFO)

    def getText(self):
        cprint("CLEANING EXPORT")
        cleanepgexport(True)
        self.session.open(MessageBox, _("EPG") + " " + _("Download") + " " + _("Cache") + " " + _("Reset"), MessageBox.TYPE_INFO)

    def getIP(self):
        ip = None
        lip = "localhost"
        if os_path.exists("/var/lib/dpkg/status"):
            from Components.Network import iNetworkInfo
            ifaces = iNetworkInfo.getConfiguredInterfaces()
            for iface in ifaces.itervalues():
                ip = iface.getIpv4()
                if not ip:
                    ip = iface.getIpv6()
            if ip is not None:
                lip = ip.getAddress()
        else:
            from Components.Network import iNetwork
            ifaces = iNetwork.getConfiguredAdapters()
            for iface in ifaces:
                ip = iNetwork.getAdapterAttribute(iface, "ip")
                if not ip or len(ip) != 4:
                    continue
            if ip is not None:
                lip = '.'.join(str(x) for x in ip)
        cprint("local ip %s" % (lip))
        return lip

    def blue_key(self):
        self.session.open(EPGExportSelection)

class EPGExport(Screen):

    def __init__(self, main, compressed="xz", channels=True, programs=True):
        self.main = main
        self.compressed = compressed
        self.channels = channels
        self.programs = programs
        self.cur_event = None
        self.cur_service = None
        self.offs = 0
        self.epgcache = eEPGCache.getInstance()
        self.time_base = int(time.time())-int(config.plugins.epgexport.outdated.value) * 60 * 24
        self.time_epoch = int(config.plugins.epgexport.days.value) * 60 * 24
        self.slist = None
        self.tree = None
        global Servicelist
        if Servicelist is None:
            InfoBarInstance = InfoBar.instance
            if InfoBarInstance is not None:
                Servicelist = InfoBarInstance.servicelist
        cprint("servicelist: %s" % Servicelist)
        new = checkLastUpdate()
        if new:
            if config.plugins.epgexport.channelid.value == "xml":
                if os_path.exists("/etc/epgexport/custom.channels.xml"):
                    cprint("loading custom.channels.xml")
                    if self.main is not None:
                        self.main["statustext"].setText(_("Custom (%s)") % ("xml" + " " + _("Channels") + " " + _("Downloading") + " " + _("...")))
                    epgtree = etree.parse("/etc/epgexport/custom.channels.xml")
                    self.tree = epgtree.getroot()
                else:
                    cprint("custom.channels.xml not found")
                    if self.main is not None:
                        self.main["statustext"].setText(_("Custom (%s)") % ("xml" + " " + _("not found")))
                    return
#           cprint("tree %s" % self.tree)
            cprint("extracting ...")
            self.startingEPGExport()
        else:
            cprint("still valid ...")
            if self.main is not None:
                self.main["statustext"].setText(_("EPG") + " " + _("Download") + " " + _("Reload") + " " + _("Finished"))

    def startingEPGExport(self):
        cprint("starting EPG export ...")
        lang = config.osd.language.value
        sp = []
        sp = lang.split("_")
        self.language = sp[0].lower()
        # use current bouquet if none is found ...
        global Servicelist
        bouquet = Servicelist.getRoot()
        serviceHandler = eServiceCenter.getInstance()
        info = serviceHandler.info(bouquet)
        bouquet_name = info.getName(bouquet)
        cprint("DEFAULT bouquet %s" % bouquet_name)
        all_bouquets = Servicelist.getBouquetList()
        self.services = []
        for bouquets in all_bouquets:
            bt = tuple(bouquets)
            bouquet_name = bt[0].replace(" (TV)","").replace(" (Radio)","").lower()
            cprint("CHECKS bouquet %s" % bouquet_name)
            for x in range(bouquet_length):
                if bouquet_name == config.plugins.epgexport.bouquets[x].name.value and config.plugins.epgexport.bouquets[x].export.value:
                    bouquet = bouquets[1]
                    cprint("FOUND bouquet %s" % bouquet_name)
                    self.services = self.services+self.getBouquetServices(bouquet)
        if self.channels:
            self.exportChannels()
        if self.programs:
            cprint("extracting ...")
            exportLastUpdate()
            self.extractEPG()
            self.exportEPG()

    def getBouquetServices(self, bouquet):
        services = [ ]
        Servicelist = eServiceCenter.getInstance().list(bouquet)
        if not Servicelist is None:
            while True:
                service = Servicelist.getNext()
                if not service.valid(): #check if end of list
                    break
                if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker): #ignore non playable services
                    continue
                services.append(ServiceReference(service))
        return services

    def extractEPG(self):
        self.cur_event = None
        self.cur_service = None
        test = [ (service.ref.toString(), 0, self.time_base, self.time_epoch) for service in self.services ]
#       print("test: %s" % test)
        test.insert(0, 'XRnITBDSE')     # N = ServiceName, n = short ServiceName

        epg_data = self.queryEPG(test)
        self.program = [ ]
        tmp_list = None
        service = None
        for x in epg_data:
            if service is None or service.ref != ServiceReference(x[0]).ref:
                if tmp_list is not None:
                    self.program.append((service, tmp_list[0][0] is not None and tmp_list or None))

                # Dont use the service return from the EPG query because it wont have a number
                # so search it from the services list that we used to build the query
                try:
                    service = next(s for s in self.services if s.ref == ServiceReference(x[0]).ref)
                    cprint("extractEPG found: %s" % str(service))
                except Exception as e:
                    cprint("extractEPG exception: %s" % str(e))

                tmp_list = [ ]
            tmp_list.append((x[2], x[3], x[4], x[5], x[6], x[7]))
        if tmp_list and len(tmp_list):
            self.program.append((service, tmp_list[0][0] is not None and tmp_list or None))

    def queryEPG(self, list, buildFunc=None):
        if self.epgcache is not None:
            if buildFunc is not None:
                return self.epgcache.lookupEvent(list, buildFunc)
            else:
                return self.epgcache.lookupEvent(list)
        return [ ]

    def exportChannels(self):
        xmltv_string = self.generateChannels()
        xml_file_name = "/etc/epgexport/epgexport.channels.xml"
        if self.compressed == "xz":
            f = lzma.open(xml_file_name + ".xz", "wb")
        elif self.compressed == "gz":
            f = gzip.open(xml_file_name + ".gz", "wb")
        else:
            f = open(xml_file_name, "wb")
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xmltv_string)
        f.close()

    def exportEPG(self):
        xmltv_string = self.generateEPG()
        xml_file_name = "/etc/epgexport/epgexport"
        if self.compressed == "xz":
            f = lzma.open(xml_file_name + ".xz", "wb")
        elif self.compressed == "gz":
            f = gzip.open(xml_file_name + ".gz", "wb")
        else:
            f = open(xml_file_name, "wb")
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xmltv_string)
        f.close()

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def channelNumber(self, service):
        if hasattr(service, "ref") and service.ref and "0:0:0:0:0:0:0:0:0" not in service.ref.toString():
            numservice = service.ref
            num = numservice and numservice.getChannelNum() or None
            if num is not None:
                return num
        return None

    def channelID(self, service):
        service_name = service.getServiceName().encode("ascii", "ignore")
        service_id = service_name.decode().replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace(".", "").replace("+", "").replace("_", "").replace("/", "").replace("Â", "").replace("�", "")
        service_id = self.b2s(service_id)
        service_ref = service.ref.toString()
        service_num = self.channelNumber(service)
        if self.tree is not None:
            # fallback is nameslang
            channel_id = service_id + "." + self.language
            for child in self.tree:
                if child.text == service_ref:
                    if len(child.attrib["id"]) > 0:
                        # first find will win because
                        # good custom file has only one find
                        channel_id = child.attrib["id"]
                        break
            # cprint("NOT found %s channel_id %s" % (service_ref, channel_id))
        elif config.plugins.epgexport.channelid.value == "names":
            channel_id = service_id
        elif config.plugins.epgexport.channelid.value == "nameslang":
            channel_id = service_id + "." + self.language
        elif config.plugins.epgexport.channelid.value == "nameslow":
            channel_id = service_id.lower()
        elif config.plugins.epgexport.channelid.value == "nameslowlang":
            channel_id = service_id.lower() + "." + self.language
        elif config.plugins.epgexport.channelid.value == "number" and service_num:
            channel_id = str(service_num)
        else:   # default = channel name
            channel_id = service_name
        return self.b2s(channel_id)

    def piconURL(self, service):
        picon_url = None
        if config.plugins.epgexport.server.value != "none":
            picon_file = getPiconName(service)
            if picon_file:
                if config.plugins.epgexport.server.value == "ip":
                    host = "%d.%d.%d.%d" % tuple(config.plugins.epgexport.ip.value)
                else:
                    host = config.plugins.epgexport.hostname.value
                picon_url = "http://" + host + ":80/picon/" + os_path.basename(picon_file)
        return picon_url

    def generateChannels(self):
        cprint("Building XMLTV channel list file")
        sp = []
        root = etree.Element('channels')
        # write all channel id's and service references at beginning of file
        for service in self.services:
            service_name = service.getServiceName().replace('Â', '').replace('�', '')
            service_ref = service.ref.toString()
            sp = service_ref.split("::")
            service_ref = sp[0]
            if len(service_name) > 0 and service_ref.find("//") is -1 and service_ref.find("BOUQUET") is -1:
                service_id = self.channelID(service)
                xmltv_channel = etree.SubElement(root, "channel")
                xmltv_channel.set('id', service_id)
                xmltv_channel.text = service_ref
        # etree.tostring has no pretty print to make indent in xml
        self.indent(root)
        cprint("Building XMLTV channel list file, completed")
        #cprint("service_name = %s,%s / service_id = %s %s / service_ref = %s %s" % ( service_name,type(service_name) , service_id,type(service_id) , service_ref,type(service_ref)    ) )
        return etree.tostring(root, encoding='utf-8')

    def getTimezoneOffset(self):
        from datetime import datetime
        from datetime import timedelta
        # utc time
        ts = time.time()
        # local time == (utc time + utc offset)
        tl = time.localtime()

        # summertime is not needed ...
#       td = timedelta(minutes=int(tl.tm_isdst)*60)
#       cprint("summer time delta %s" % td)
#       offset = datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts) - td

        offset = datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)
        # make nice string form XMLTV local time offset ...
        delta = str(offset).rstrip("0").replace(":", "")
        if abs(int(delta)) < 1000:
            if int(delta) > 0:
                local_offset = '+0' + delta
            else:
                local_offset = '-0' + delta
        else:
            if int(delta) > 0:
                local_offset = '+' + delta
            else:
                local_offset = '-' + delta
        cprint("local offset: %s" % local_offset)
        return local_offset

    def generateEPG(self):
        cprint("Building XMLTV electronic program guide file")
        root = etree.Element('tv')
        generator_info_name = 'EPG Export Plugin (c) gutemine 2019'
        generator_info_url = 'https://sourceforge.net/projects/gutemine/'
        root.set('generator-info-name', generator_info_name)
        root.set('generator-info-url', generator_info_url)
        cn = 0
        for service in self.services:
            service_name = service.getServiceName().replace('Â', '').replace('�', '')
            service_ref = service.ref.toString()
            if len(service_name) > 0 and service_ref.find("//") is -1:
                service_id = self.channelID(service)
                xmltv_channel = etree.SubElement(root, 'channel')
                xmltv_channel.set('id', service_id)
                xmltv_cname = etree.SubElement(xmltv_channel, 'display-name', lang=self.language)
                xmltv_cname.text = service_name
                service_picon = self.piconURL(service_ref)
                if service_picon:
                    xmltv_cicon = etree.SubElement(xmltv_channel, 'icon')
                    xmltv_cicon.set('src', service_picon)
                cn += 1
        cprint("channel number: %d" % cn)

        local_time_offset = self.getTimezoneOffset()
        en = 0
        for program in self.program:
            if program[1] is not None:
                service = program[0]
                service_name = service.getServiceName().replace('Â', '').replace('�', '')
                service_ref = service.ref.toString()
                if len(service_name) > 0 and service_ref.find("//") is -1:
                    service_id = self.channelID(service)
                    for event in program[1]:
                        prog = dict()
                        title = self.b2s(event[1]).strip()
                        start = int(event[2])
                        duration = int(event[3])
                        subtitletext = self.b2s(event[4]).strip()
                        description = self.b2s(event[5]).strip()
                        stop = start + duration
                        start_time = time.strftime('%Y%m%d%H%M00', time.localtime(start))
                        stop_time  = time.strftime('%Y%m%d%H%M00', time.localtime(stop))
#                       cprint(">>> %s" % title)
#                       cprint(">>>>>> %s" % subtitletext)
#                       cprint(">>>>>>>>> %" % description)
                        xmltv_program = etree.SubElement(root, 'programme')
                        xmltv_program.set('start',start_time + ' ' + local_time_offset)
                        xmltv_program.set('stop', stop_time + ' ' + local_time_offset)
                        xmltv_program.set('channel', service_id)

                        en += 1

                        if title != None:
                            title_text = self.b2s(title).split('. ')
                            title = etree.SubElement(xmltv_program, 'title', lang=self.language)
                            title.text = self.b2s(title_text[0]).strip()
                            if len(subtitletext) > 1:
                                subtitle = etree.SubElement(xmltv_program, 'sub-title', lang=self.language)
                                subtitle.text = self.b2s(subtitletext)
                            else:
                                if len(title_text) > 1:
                                    subtitle = etree.SubElement(xmltv_program, 'sub-title', lang=self.language)
                                    subtitle.text = self.b2s(title_text[1]).strip()

                        if description != None:
                            if len(description) > 1:
                                desc = etree.SubElement(xmltv_program, 'desc', lang=self.language)
                                desc.text = self.b2s(description)
        cprint("event number: %d" % en)

        # etree.tostring has no pretty print to make indent in xml
        self.indent(root)
        if self.main is not None:
            self.main["statustext"].setText(_("EPG") + " " + _("Download") + " " + _("Channels") + ": %d " % cn + _("EPG") + " " + _("Info") + " " + _("Details") + ": %d" % en)
        return etree.tostring(root, encoding='utf-8')

    def b2s(self, s):       # converting data type... `bytes` to `string`... if the variable is `bytes`
        if isinstance(s, bytes):
            return s.decode('utf8')
        else:
            return s

class EPGExportSource(resource.Resource):

    def render_GET(self, req):
        cprint("SOURCE REQUEST ...")
#       cprint(req)
        sources = ""
        if os_path.exists("/etc/epgload/epgexport.sources.xml"):
            f = open("/etc/epgload/epgexport.sources.xml", "r")
            sources = f.read()
            f.close()
        elif os_path.exists("/etc/epgimport/epgexport.sources.xml"):
            f = open("/etc/epgimport/epgexport.sources.xml", "r")
            sources = f.read()
            f.close()
        else:
            pass
        cprint("sources: %s" % sources)
        req.setResponseCode(http.OK)
        req.setHeader("Content-type", "text/html")
        req.setHeader("charset", "UTF-8")
        return sources

class EPGExportLastUpdate(resource.Resource):

    # always return current date for a web request
    def render_GET(self, req):
        cprint("last update request ...")
#       cprint(req)
        now=datetime.datetime.now()
        date=now.strftime('%Y-%m-%d')
        cprint("last update: %s" % date)
        req.setResponseCode(http.OK)
        req.setHeader('Content-type', 'text/html')
        req.setHeader('charset', 'UTF-8')
        return date

class EPGExportChannels(resource.Resource):

    def render_GET(self, req):
        cprint("CHANNELS REQUEST: %s" % req.uri)
        channels = ""
        new = checkLastUpdate()
        if req.uri.find("epgexport.channels.xml.xz") is not -1:
            if new or not os_path.exists("/etc/epgexport/epgexport.channels.xml.xz"):
                # web request for xz file
                cprint("EXPORTING CHANNELS xz")
                EPGExport(None,"xz",True, False)
            f = open("/etc/epgexport/epgexport.channels.xml.xz", "rb")
        elif req.uri.find("epgexport.channels.xml.gz") is not -1:
            if new or not os_path.exists("/etc/epgexport/epgexport.channels.xml.gz"):
                # web request for gz file
                cprint("EXPORTING CHANNELS gz")
                EPGExport(None, "gz", True, False)
            f = open("/etc/epgexport/epgexport.channels.xml.gz", "rb")
        else:
            if new or not os_path.exists("/etc/epgexport/epgexport.channels.xml"):
                # web request for uncompressed file
                cprint("EXPORTING CHANNELS")
                EPGExport(None,"none",True, False)
            f = open("/etc/epgexport/epgexport.channels.xml", "rb")
        channels = f.read()
        f.close()
        req.setResponseCode(http.OK)
        req.setHeader('Content-type', 'text/html')
        req.setHeader('charset', 'UTF-8')
        return channels

class EPGExportPrograms(resource.Resource):

    def render_GET(self, req):
        cprint("PROGRAMS REQUEST: %s" % req.uri)
        programs = ""
        new = checkLastUpdate()
        if req.uri.find("epgexport.xz") is not -1:
            if new or not os_path.exists("/etc/epgexport/epgexport.xz"):
                # web request for xz file
                cprint("EXPORTING PROGRAMS xz")
                EPGExport(None, "xz", False, True)
            f = open("/etc/epgexport/epgexport.xz", "rb")
        elif req.uri.find("epgexport.gz") is not -1:
            if new or not os_path.exists("/etc/epgexport/epgexport.gz"):
                # web request for gz file
                cprint("EXPORTING PROGRAMS gz")
                EPGExport(None, "gz", False, True)
            f = open("/etc/epgexport/epgexport.gz", "rb")
        else:
            if new or not os_path.exists("/etc/epgexport/epgexport"):
                # web request for uncompressed file
                cprint("EXPORTING PROGRAMS")
                EPGExport(None, "none", False, True)
            f = open("/etc/epgexport/epgexport", "rb")
        programs = f.read()
        f.close()
        req.setResponseCode(http.OK)
        req.setHeader('Content-type', 'text/html')
        req.setHeader('charset', 'UTF-8')
        return programs

class EPGExportSelection(Screen, ConfigListScreen):

    if sz_w == 1920:
        skin = """
        <screen position="center,170" size="1200,710" title="EPGExport Selection" >
        <widget name="logo" position="20,10" size="150,60" transparent="1" alphatest="on" />
            <widget backgroundColor="#9f1313" font="Regular;24" halign="center" name="buttonred" position="190,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <widget backgroundColor="#1f771f" font="Regular;24" halign="center" name="buttongreen" position="440,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <widget backgroundColor="#a08500" font="Regular;24" halign="center" name="buttonyellow" position="690,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <widget backgroundColor="#18188b" font="Regular;24" halign="center" name="buttonblue" position="940,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="230,60" valign="center" />
                <eLabel backgroundColor="grey" position="20,80" size="1160,1" />
                <widget name="config" enableWrapAround="1" position="20,90" scrollbarMode="showOnDemand" size="1160,610" />
        </screen>"""
    else:
        skin = """
        <screen position="center,120" size="820,480" title="EPGExport Selection" >
        <widget name="logo" position="10,10" size="100,40" transparent="1" alphatest="on" />
            <widget backgroundColor="#9f1313" font="Regular;16" halign="center" name="buttonred" position="120,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <widget backgroundColor="#1f771f" font="Regular;16" halign="center" name="buttongreen" position="295,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <widget backgroundColor="#a08500" font="Regular;16" halign="center" name="buttonyellow" position="470,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <widget backgroundColor="#18188b" font="Regular;16" halign="center" name="buttonblue" position="645,10" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" size="165,40" valign="center" />
                <eLabel backgroundColor="grey" position="10,60" size="800,1" />
            <widget name="config" enableWrapAround="1" position="10,70" size="800,400" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.skin = EPGExportSelection.skin
        self.session = session
        self.onShown.append(self.setWindowTitle)
        # explicit check on every entry
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self["logo"] = Pixmap()
        self["buttonred"] = Label(_("Exit"))
        self["buttongreen"] = Label(_("Save"))
        self["buttonyellow"] = Label(_("Reset"))
        self["buttonblue"] = Label(_("About"))
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
                        "ok"    : self.save,
                        "exit"  : self.cancel,
                        "cancel": self.cancel,
                        "red"   : self.cancel,
                        "green" : self.save,
                        "yellow": self.resetting,
                        "blue"  : self.about      })
        selected = 0
        for x in range(bouquet_length):
            if config.plugins.epgexport.bouquets[x].export.value:
                selected += 1
        if selected < 1:
            self.resetting()
        self.createSetup()

    def setWindowTitle(self):
        self["logo"].instance.setPixmapFromFile("%s/epgexport.png" % epgexport_plugindir)
        self.setTitle(epgexport_selection)

    def save(self):
        selected = 0
        for x in range(bouquet_length):
            if config.plugins.epgexport.bouquets[x].export.value:
                selected += 1
        if selected < 1:
            self.resetting()
        for x in range(bouquet_length):
            config.plugins.epgexport.bouquets[x].export.save()
            config.plugins.epgexport.bouquets[x].name.save()
        self.close(True)

    def cancel(self):
        for x in range(bouquet_length):
            config.plugins.epgexport.bouquets[x].export.cancel()
            config.plugins.epgexport.bouquets[x].name.cancel()
        self.close(False)

    def createSetup(self):
        self.list = []
        for x in range(bouquet_length):
            self.list.append(getConfigListEntry(bouquet_options[x][1], config.plugins.epgexport.bouquets[x].export))
        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def changedEntry(self):
        choice = self["config"].getCurrent()
        current = choice[1]
        if choice != None:
            self.createSetup()

    def resetting(self):
        for x in range(bouquet_length):
            config.plugins.epgexport.bouquets[x].export.value = False
            if config.plugins.epgexport.bouquets[x].name.value == "favorites":
                config.plugins.epgexport.bouquets[x].export.value = True
                cprint("nothing selected, means Favorites")
            config.plugins.epgexport.bouquets[x].export.save()
            config.plugins.epgexport.bouquets[x].name.save()
        self.createSetup()

    def about(self):
            self.session.open(MessageBox, epgexport_thanks, MessageBox.TYPE_INFO)
