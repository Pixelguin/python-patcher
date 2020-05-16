from __future__ import unicode_literals

try:
	from typing import List, Optional, Dict, Set, Any, Callable
except:
	pass  # Just needed for pycharm comments

import os
import sys

# Python 2/3 input() function fix
try: input = raw_input
except NameError: pass

from installConfiguration import SubModConfig, FullInstallConfiguration
import main as gui_main
import common
import logger
import gameScanner
import uminekoInstaller
import uminekoNScripterInstaller
import higurashiInstaller


def userAskYesNo(choiceText):
	# type: (str) -> bool
	while True:
		print("\n---- {} ----".format(choiceText))

		response = input("(Please type 'y' or 'n', then hit enter)\n>>")
		if len(response) > 0:
			if response[0] in 'yY':
				return True
			elif response[0] in 'nN':
				return False

		print("Invalid response, please type 'y' or 'n' ")


def userPickFromList(choices, overallDescription, customFormatter=None):
	# type: (List[Any], str, Callable[[Any], str]) -> Any

	if customFormatter is None:
		customFormatter = lambda x: x

	# If only one choice, just return that choice
	if len(choices) == 1:
		return choices[0]

	while True:
		print("\n---- {} ----".format(overallDescription))
		i = 1
		for choice in choices:
			print("{}) {}".format(i, customFormatter(choice)))
			i += 1

		# Collect response from the user. If it's invalid, loop again.
		try:
			return choices[int(input("(Type the number of your choice, then hit enter)\n>>")) - 1]
		except:
			print("Invalid response, please try again.")
			continue


# This code is an excerpt from InstallerGUI.try_start_install(...)
def tryGetFullInstallConfig(subMod, installPath):
	# type: (SubModConfig, str) -> List[FullInstallConfiguration]
	fullInstallConfigs = None
	if os.path.isdir(installPath):
		fullInstallConfigs = gameScanner.scanForFullInstallConfigs([subMod], possiblePaths=[installPath])

	# If normal scan fails, then scan the path using the more in-depth 'scanUserSelectedPath(...)' function
	if not fullInstallConfigs:
		fullInstallConfigs, errorMessage = gameScanner.scanUserSelectedPath([subMod], installPath)
		print(errorMessage)

	return fullInstallConfigs


def askUserOptions(subModToInstall):
	# type: (SubModConfig) -> None
	# Separate the radio and checkbox options
	radioOptions = {}  # a dict of str -> [ModOption], grouped by mod option type. Order of list should be the same as in the JSON.
	checkBoxOptions = []  # a plain list of ModOption objects which are of checkbox type

	for option in subModToInstall.modOptions:
		if not option.isRadio:
			checkBoxOptions.append(option)
		else:
			if option.group not in radioOptions:
				radioOptions[option.group] = []

			radioOptions[option.group].append(option)

	# Ask the user about each check box option
	for option in checkBoxOptions:
		option.value = userAskYesNo(
			"""Would you like to enable option [{}]?
			Description: [{}]""".format(option.name, option.description)
		)

	# Ask the user about each group of radio options
	def customFormatter(option):
		return "[{}]:\n{}\n".format(option.name, option.description)

	for (optionGroupName, optionList) in radioOptions.items():
		chosenRadioOption = userPickFromList(optionList, "Please choose [{}]".format(optionGroupName),
		                                     customFormatter=customFormatter)
		chosenRadioOption.value = True


if __name__ == "__main__":
	sys.stdout = logger.Logger(common.Globals.LOG_FILE_PATH)
	logger.setGlobalLogger(sys.stdout)
	sys.stderr = logger.StdErrRedirector(sys.stdout)
	gui_main.check07thModServerConnection()
	common.Globals.scanForExecutables()
	modList = gui_main.getModList()
	subModList = gui_main.getSubModConfigList(modList) #type: List[SubModConfig]

	# Get a list of unique game names
	uniqueGameNames = []
	seenGameNames = set()
	for subMod in subModList:
		if subMod.modName not in seenGameNames:
			seenGameNames.add(subMod.modName)
			uniqueGameNames.append(subMod.modName)

	# Ask the user which game they want to install
	gameName = userPickFromList(uniqueGameNames, "Please choose the game you want to mod")

	# Get a list of variants with that name
	modVariants = [subMod for subMod in subModList if subMod.modName == gameName] #type: List[SubModConfig]

	# Ask the user which submod they want to install
	subModToInstall = userPickFromList(modVariants, "Please choose which variant to install") #type: SubModConfig

	# Ask the user where they want to install the game
	while True:
		installPath = input(
			"\n---- Please copy and paste the game path below ----\nIt should contain one of {}\nDO NOT include the quotation characters [\"] or ['] in your path!\nExample: C:\\Program Files\\Steam\\steamapps\\common\\Umineko (for Umineko Question Arcs)\n>>".format(subModToInstall.identifiers)
		)

		print("Validating [{}]".format(installPath))
		fullInstallConfigList = tryGetFullInstallConfig(subModToInstall, installPath)
		if fullInstallConfigList:
			fullInstallConfig = fullInstallConfigList[0] #type: FullInstallConfiguration
			break
		else:
			print("---- Invalid game path, please try again ----")

	# Ask the user what options they want to install
	# Note: this function directly modifies the submod's options
	askUserOptions(subModToInstall)

	# Summarize install choices (print submod and path)
	print("\n--------- INSTALL CONFIRMATION ---------")
	print("This will PERMANENTLY modify files in the game folder:")
	print(fullInstallConfig.installPath)
	print("Please take a backup of this folder if you have custom scripts, sprites, voices etc. or wish to revert to unmodded later.")
	print("------------------------------------------")
	print("You have chosen to install [{}], variant [{}]".format(subModToInstall.modName, subModToInstall.subModName))
	print("The mod will install to [{}]".format(fullInstallConfig.installPath))
	lastGroup = None
	for option in subModToInstall.modOptions:
		if option.group != lastGroup:
			lastGroup = option.group
			print("\n  {}:".format(option.group))
		print("  {:>24}: {}".format(option.name, option.value))

	# Do one final confirmation before starting the install
	if not userAskYesNo("Start the install with these settings?"):
		input("Install Stopped! Press ENTER to quit")
		exit(-1)

	# Begin the install
	installFunction = {
		"higurashi": higurashiInstaller.main,
		"umineko": uminekoInstaller.mainUmineko,
		"umineko_nscripter": uminekoNScripterInstaller.main
	}.get(subModToInstall.family, None)

	if installFunction:
		installFunction(fullInstallConfig)
	else:
		print(
			"Submod family is not recognised, the script may be out of date."
			"Please ask us to update it."
		)
