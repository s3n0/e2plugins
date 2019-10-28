# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/ChocholousekPicons/')
PluginLanguageDomain = "ChocholousekPicons"
PluginLanguagePath = "Extensions/ChocholousekPicons/locale"

def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
