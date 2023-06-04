from os import listdir, path

from . import _
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigBoolean, configfile

from .BackupManager import BackupManagerautostart
from .ImageManager import ImageManagerautostart
from .IPKInstaller import IpkgInstaller
from .ScriptRunner import ScriptRunnerAutostart
from .SwapManager import SwapAutostart
from .IPKInstaller import IpkgInstaller

config.misc.restorewizardrun = ConfigBoolean(default=False)

#	On plugin initialisation (called by StartEnigma). language will be assigned as follows if config.misc.firstrun.value:
#	Default language en_GB (OpenBh) is set by SetupDevices called by StartEnigma
#	If no backup, the languagewizard will be inserted by Plugin into the wizards.
#	If backup, then language will be set here from config.osd.language if in backup, else default language
#

def setLanguageFromBackup(backupfile):
	print("[OBH plugin][setLanguageFromBackup] backupfile", backupfile)
	import tarfile

	try:
		tar = tarfile.open(backupfile)
		member = tar.getmember("etc/enigma2/settings")
	except KeyError:
		print("[OBH plugin][setLanguageFromBackup] language selected failed")
		tar.close()
		return

	for line in tar.extractfile(member):
		line = line.decode()
		if line.startswith("config.osd.language"):
			languageToSelect = line.strip().split("=")[1]
			print("[OBH plugin][setLanguageFromBackup] language selected", languageToSelect)
			from Components.Language import language
			language.InitLang()
			language.activateLanguage(languageToSelect)
			config.misc.languageselected.value = 0		# 0 means found
			config.misc.languageselected.save()
			break
	tar.close()


def checkConfigBackup():
	try:
		devmounts = []
		list = []
		files = []
		for dir in ["/media/%s/backup" % media for media in listdir("/media/") if path.isdir(path.join("/media/", media))]:
			devmounts.append(dir)
		if len(devmounts):
			for devpath in devmounts:
				if path.exists(devpath):
					try:
						files = listdir(devpath)
					except:
						files = []
				else:
					files = []
				if len(files):
					for file in files:
						if file.endswith(".tar.gz") and "bh" in file.lower():
							list.append((path.join(devpath, file)))
		if len(list):
			print("[RestoreWizard] Backup Image:", list[0])
			backupfile = list[0]
			if path.isfile(backupfile):
				setLanguageFromBackup(backupfile)
			return True
		else:
			return None
	except IOError as e:
		print("[OpenBh] unable to use device (%s)..." % str(e))
		return None


if config.misc.firstrun.value and not config.misc.restorewizardrun.value:
	if checkConfigBackup() is None:
		backupAvailable = 0
	else:
		backupAvailable = 1


def BHMenu(session):
	from .import ui
	return ui.BHMenu(session)


def UpgradeMain(session, **kwargs):
	session.open(BHMenu)


def startSetup(menuid):
	if menuid != "setup":
		return []
	return [(_("BH"), UpgradeMain, "bh_menu", 1010)]


def RestoreWizard(*args, **kwargs):
	from .RestoreWizard import RestoreWizard
	return RestoreWizard(*args, **kwargs)


def LanguageWizard(*args, **kwargs):
	from Screens.LanguageSelection import LanguageWizard
	return LanguageWizard(*args, **kwargs)

def BackupManager(session):
	from .BackupManager import OpenBhBackupManager
	return OpenBhBackupManager(session)


def BackupManagerMenu(session, **kwargs):
	session.open(BackupManager)


def ImageManager(session):
	from ImageManager import OpenBhImageManager
	return OpenBhImageManager(session)


def ImageMangerMenu(session, **kwargs):
	session.open(ImageManager)


def H9SDmanager(session):
	from .H9SDmanager import H9SDmanager
	return H9SDmanager(session)


def H9SDmanagerMenu(session, **kwargs):
	session.open(H9SDmanager)


def MountManager(session):
	from .MountManager import OpenBhDevicesPanel
	return OpenBhDevicesPanel(session)


def MountManagerMenu(session, **kwargs):
	session.open(MountManager)


def ScriptRunner(session):
	from .ScriptRunner import OpenBhScriptRunner
	return OpenBhScriptRunner(session)


def ScriptRunnerMenu(session, **kwargs):
	session.open(ScriptRunner)


def SwapManager(session):
	from .SwapManager import OpenBhSwap
	return OpenBhSwap(session)


def SwapManagerMenu(session, **kwargs):
	session.open(SwapManager)


def filescan_open(list, session, **kwargs):
	filelist = [x.path for x in list]
	session.open(IpkgInstaller, filelist)  # list


def filescan(**kwargs):
	from Components.Scanner import Scanner, ScanPath
	return Scanner(mimetypes=["application/x-debian-package"],
				paths_to_scan=[
					ScanPath(path="ipk", with_subdirs=True),
					ScanPath(path="", with_subdirs=False),
				],
				name="Ipkg",
				description=_("Install extensions."),
				openfnc=filescan_open)


def Plugins(**kwargs):
	plist = [PluginDescriptor(needsRestart=False, fnc=startSetup)]
	if config.scriptrunner.showinextensions.value:
		plist.append(PluginDescriptor(name=_("Script runner"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=ScriptRunnerMenu))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=SwapAutostart))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=ImageManagerautostart))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=BackupManagerautostart))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=ScriptRunnerAutostart))
	if config.misc.firstrun.value and not config.misc.restorewizardrun.value and backupAvailable == 0:
		plist.append(PluginDescriptor(name=_("Language Wizard"), where=PluginDescriptor.WHERE_WIZARD, needsRestart=False, fnc=(1, LanguageWizard)))
	if config.misc.firstrun.value and not config.misc.restorewizardrun.value and backupAvailable == 1:
		plist.append(PluginDescriptor(name=_("Restore wizard"), where=PluginDescriptor.WHERE_WIZARD, needsRestart=False, fnc=(4, RestoreWizard)))
	plist.append(PluginDescriptor(name=_("Ipkg"), where=PluginDescriptor.WHERE_FILESCAN, needsRestart=False, fnc=filescan))
	return plist
