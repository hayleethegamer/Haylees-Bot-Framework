'''Copyright (C) 2020  Hayleethegamer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>'''

import asyncio
import os
import sys

from .Logging import Logging
from .Support import Support
from .APITranslation import APITranslator
from .Command import Command



#Default Settings
defaultSettings = {
	"Restart":{
		"Restarted":False,
		"RestartChannel":{}
	},
	"BackgroundTasks":{
		"AutoChange":{
			"status":False,
			"time":60
		},
		"AutoGame":{
			"games":[],
			"status":False,
			"game":"",
			"time":60
		}
	},
	"NonCommandsOff":[],
	"NSFW":[],
	"Status":{
		"Name":None,
		"Type":0,
		"URL": None
	}
}

#Coloring for logs	
			
class Bot():
	def __init__(self, commandPrefix, **options):
		self.commandPrefix = commandPrefix #Sets the Command Prefix 
		self.testing = options.get("testing", False) #Enables or disables the testing Mode
		#Sets owner ID(s), if none Given, set to blank Set
		self.ownerIDs = options.get("ownerIDs", set())
		#sets where the log files are, defaults to working Directory "Logs" folder
		self.logging = Logging(options.get("logLocation", "{}/Logs/".format(os.getcwd())))
		self.loop = asyncio.get_event_loop() #Sets up Event Loop
		self.ready = False #defines Ready, will be set to True when Ready
		self.settings = self._loadSettings(options.get("settings")) #Loads Settings
		#Allows user to load Custom Global Variables of any kind
		self.otherVars = options.get("otherVars")
		#A Link the bot will automatically send if errors in commands occure
		self.bugReport = options.get("bugReport")
		#Sets the listed of Trusted role ID numbers, blank list if none provided
		self.trustedIDs = options.get("TrustedIDs", [])
		#Sets the blank command List for further use
		self.commands = {}
		
		
		self.name = None #Bot's own Discord Username
		self.id = None #The Bot's own Discord ID Number, set later by API Translator
		self.APIVersion = "5.0" #API Version
		self.APIMaker = "Hayleethegamer" #API Maker
		self.pythonVersion = "{}.{}.{}".format(sys.version_info[0], 
			sys.version_info[1],sys.version_info[2]) #Python Version
		
		#Sets up Translator
		self.translator = APITranslator(self)
		
		
	def _loadSettings(self, settingsFile=None):
		#If no settings file given, load Defaults
		if settingsFile == None:
			settings = defaultSettings
			self.logging.sysLog("Debug", "Default Settings Loaded")
		else:
			#Try to load Settings file given, if failed, exit.
			try:
				settings = Support.loadJson(self, settingsFile)
				self.logging.sysLog("Debug", "Settings Loaded")
			except FileNotFoundError:
				self.logging.sysLog("Error", "Settings not found, Exiting.")
				self._stop()
			except ValueError:
				self.logging.sysLog("Error", "Settings file corrupted, Exiting.")
				self._stop()
		return settings
	
	#Stops the bot gracefully
	def _stop(self):
		self.ready = False
		pending = asyncio.Task.all_tasks()
		gathered = asyncio.gather(*pending)
		try:
			gathered.cancel()
			self.loop.run_until_complete(gathered)
			gathered.exception()
		except:
			pass
		self.loop.stop()
		self.logging.sysLog("Status", "Clean up done, Closing")
		sys.exit(0)
	#Starts Running the bot and handles a KeyboardInterrupt
	def run(self, token):
		try:
			#self.loop.run_until_complete(self._start(token))
			self._start(token)
		except (KeyboardInterrupt):
			self.logging.sysLog("Status", "Keyboard Interrupt Detected, stopping...")
			self._stop()
	#Starts running the bot
	def _start(self, token):
		self.logging.sysLog("Status", "Starting...")
		self.translator.run(token)
		
	
	
	#Default Events
	@asyncio.coroutine
	def bot_ready(self):
		#When Ready to use
		self.logging.sysLog("Status", "Connected!")
		self.logging.sysLog("Status", "API Version: {} ".format(self.APIVersion))
		self.logging.sysLog("Status", "Username: {}".format(self.name))
		self.logging.sysLog("Status", "ID: {}".format(self.id))
		self.logging.sysLog("Status", "Discord.py "
			"Version: {}".format(self.translator.version))
		self.logging.sysLog("Status", "Python Version: {}".format(self.pythonVersion))
		self.logging.sysLog("Status", "Process ID: {}".format(str(os.getpid())))
		self.logging.sysLog("Status", "Ready to go!")
		yield from self.on_ready()
	@asyncio.coroutine
	def on_ready(self):
		#For other On Ready
		pass
	@asyncio.coroutine
	def on_message(self, message):
		#Chat Messages
		self.logging.messageLog(message)
		yield from self.otherCommands(message)
		yield from self.process_commands(message)
	@asyncio.coroutine
	def on_error(self,error):
		#Here but not in
		print("Ignoring exception {}".format(error))
		print(traceback.format_exc())
		yield from self._errorHandleing()
	@asyncio.coroutine
	def otherCommands(self, message):
		#A place holder for other commands that might not work with the command framework.
		pass
	@asyncio.coroutine
	def process_commands(self, message):
		#Processes command
		#If Message not from Self
		if message.author.id != self.id:
			#If Message is command.
			if message.text.startswith(self.commandPrefix):
				#Gets command's name
				commandName = message.text[len(self.commandPrefix):]
				comSplit = commandName.split(" ")
				comName = comSplit.pop(0).lower().replace("\r","")
				if comName in self.commands:
					yield from self.commands[comName].run(message)
	
	def command(self, *args, **kwargs):
		#Returns command Class
		return Command(self, *args, **kwargs)
	
	
	async def sendMessage(self, message, sentMessage):
		await self.translator.sendMessage(message.channel.id, sentMessage)
	
	#Restrictions
	#Only Mods (people with Manage Message permissions for the channel) can use these commands
	def modOnly(self, func):
		#Manage Message = mod
		pass
	#Only the Bot's owner can use commands with this restriction
	def ownerOnly(self, func):
		async def __decorator(message):
			if message.author.ID in self.ownerIDs:
				return await func(message)
		return __decorator
	#Only Trusted People can use these commands
	def trustedOnly(self, func):
		async def __decorator(message):
			if self.trustedID in message.author.roles:
				return await func(message)
		return __decorator
	#NSFW Check
	def nsfwCheck(func):
		async def __decorator(message):
			if message.channel.id in self.settings["NSFW"]:
				return await func(ctx)
			else:
				await self.sendMessage(bot, 
					"NSFW is disabled in this channel.")
		return __decorator
	#A Function to check if NSFW is allowed mid function rather than as a dectorator
	def nsfwMidCheck(messageObj):
		if messageObj.other.channel.id in self.settings["NSFW"]:
			return True
		else:
			return False
