# -*- coding: utf-8 -*-

from Components.Language import language
import gettext

PLUGIN_PATH          = "/usr/lib/enigma2/python/Plugins/Extensions/ChocholousekPicons/"
PluginLanguagePath   = "/usr/lib/enigma2/python/Plugins/Extensions/ChocholousekPicons/locale"
PluginLanguageDomain = "ChocholousekPicons"

def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
