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

import datetime
import os
import sys

from .Support import bcolors, Support

Support = Support()

defaultServerKey = {
	"000000":"System", 
	"000001":"Private Messages"
}
systemChannelKey = {
    "000000":"Error",
    "000001":"Error",
    "000002":"Warning",
    "000002":"Debug",
    "000004":"BackgroundTasks"
}
class Logging():
	def __init__(self, logLocation):
		self.logLocation = logLocation.rstrip("/")
		self._checkLogLocation()
		self.serverKeyLocation = "{}/ServerKey.json".format(self.logLocation)
		self.allServerLogPath = "{}/AllServer".format(self.logLocation)
		self.maxSize = 1000000 #1000000 Bytes = 1 MB
		self.serverKey = self._loadServerKey()
	
	#Checks if Log Location exits
	def _checkLogLocation(self):
		if not os.path.exists(self.logLocation):
			print("Log Location at {}{}{} doesn't exist, "
				"Exiting.".format(bcolors.BOLD, self.logLocation ,bcolors.NORMAL))
			sys.exit(1)
	
	def _loadServerKey(self):
		try:
			serverKey = Support.loadJson(self.serverKeyLocation)
		except FileNotFoundError:
			self._logPrint(True, "Warning", "ServerKey Not Found, creating new one.")
			Support.writeJson(self.serverKeyLocation, defaultServerKey)
			self.sysLog("Debug", "SeverKey Created.")
			serverKey = Support.loadJson(self.serverKeyLocation)
		except ValueError:
			self._logPrint(True, "Error", "SeverKey Corrupted, creating new one.")
			Support.writeJson(self.serverKeyLocation, defaultServerKey)
			self.sysLog("Debug", "SeverKey recreated.")
			serverKey = Support.loadJson(self.serverKeyLocation)
		return serverKey

	def sysLog(self, state, message):
		if state.lower() == "debug":
			consoleMessage = "{}{}{}".format(bcolors.GREEN, message, bcolors.NORMAL)
		elif state.lower() == "warning":
			consoleMessage = "{}{}{}".format(bcolors.WARNING, message, bcolors.NORMAL)
		elif state.lower() == "error":
			consoleMessage = "{}{}{}".format(bcolors.ERROR, message, bcolors.NORMAL)
		else:
			consoleMessage = message
		self._logPrint(True, consoleMessage, state)
		self._prepLog(True, message, "000000", state)
	
	def messageLog(self, message):
		self._logPrint(False, message)
		self._prepLog(False, message)
	
	def _logPrint(self, sysLog, message, state=None):
		#Prints message to Console
		if sysLog:
			#04/20/2020, 10:03:02 System: Error: Command Failed
			print("{} {}: {}: {}".format(self._timeStamp(), "System", 
				state.title(), message))
		else:
			printMessage = self._attachmentCheck(message)
			#04/20/2020, 10:03:02 ServerName: ChannelName: AuthorName: Hi there.
			print("{} {}: {}: {}: {}".format(self._timeStamp(), message.server.name, 
				message.channel.name, message.author.name, printMessage))
	
	#Writes the Log to file
	def _prepLog(self, sysLog, message, serverID=None, state=None):
		#Gets entry ready for writing, Similar to _logPrint
		#Gets Sever Name
		#Sets Server's Log Path
		#Gets Channel's Name
		if sysLog:
			loggedMessage = "{} {}: {}: {}".format(self._timeStamp(), "System", 
			state, message)
			serverName = self._getServerName(serverID)
			channelName = state
		else:
			printMessage = self._attachmentCheck(message)
			loggedMessage = "{} {}: {}: {}: {}".format(self._timeStamp(),
				message.server.name, message.channel.name, message.author.name,
				printMessage)
			serverName = self._getServerName(message.server.id, message)
			serverPath = "{}/{}".format(self.logLocation, serverName)
			channelName = self._getChannelName(serverPath, message)
		
		self._logWrite(channelName, serverName, loggedMessage)
	
	#Gets any attachments for logging
	def _attachmentCheck(self, message):
		if len(message.attachments) > 0:
			attachments = []
			for attach in message.attachments:
				attachments.append(attach.url)
			attachments = "\n".join(attachments)
			messageBack = "{}\nAttachments\n{}".format(message.text, attachments)
		else:
			messageBack = message.text
		return messageBack
	#Writes the log
	def _logWrite(self, channelName, serverName, logEntry):
		#Sets Log file Paths
		serverPath = "{}/{}".format(self.logLocation, serverName)
		channelPath = "{}/{}".format(serverPath, channelName)
		overAllPath = "{}/overall".format(serverPath)
		#If Log is to big, rotate it
		if self._checkFileSize(self.allServerLogPath, "AllServer_Log1.txt") > self.maxSize:
			self._rotateLog(self.allServerLogPath, "AllServer")
		if self._checkFileSize(overAllPath, "overall_log1.txt") > self.maxSize:
			self._rotateLog(overAllPath, "overall")
		if self._checkFileSize(channelPath, "{}_log1.txt".format(channelName)) > self.maxSize:
			self._rotateLog(channelPath, channelname)
		#Finally Writes the file
		Support.fileWrite("{}/AllServer_Log1.txt".format(self.allServerLogPath), 
			logEntry, failWrite=logEntry)
		Support.fileWrite("{}/overall_log1.txt".format(overAllPath), logEntry,
			failWrite=logEntry)
		Support.fileWrite("{}/{}_Log1.txt".format(channelPath, channelName), 
			logEntry, failWrite=logEntry)
		
	#Rotates the Logs	
	def _rotateLog(self, channelPath, channelName):
		#Checks how many log files there are
		logNum = len(os.listdir(channelPath))+1
		#Sets log to Read only
		os.chmod("{}/{}_log1.txt".format(channelPath, channelName), 0o444)
		#Renames the log from 1 to the next largest Log number
		os.rename("{}/{}_log1.txt".format(channelPath, channelName), 
			"{}/{}_log{}.txt".format(channelPath, channelName, logNum))
	
	#Checks Log File Size
	def _checkFileSize(self, fileDir, fileName):
		filePath = "{}/{}".format(fileDir, fileName)
		try:
			fileSize = os.stat(filePath).st_size
		except FileNotFoundError:
			fileSize = 0
		return fileSize
	#Gets the Sever's name from Key
	def _getServerName(self, serverID, messObj=None):
		#Checks if Server ID is in key
		if serverID in list(self.serverKey.keys()):
			#If ID in key then sets name to what was in key
			serverName = self.serverKey[serverID]
			if messObj != None:
				#If this is a message, check that the name is still correct
				serverNameCheck = Support.removeInvalid(messObj.server.name)
				if serverName != serverNameCheck:
					#If name not correct, Fix it and rename log folder.
					self.serverKey[serverID] = serverNameCheck
					Support.writeJson(self.serverKeyLocation,
						self.serverKey)
					os.rename("{}/{}".format(self.logLocation, serverName),
						"{}/{}".format(self.logLocation, serverNameCheck))
					serverName = serverNameCheck
		else:
			#If ID not in Key, add it.
			if messObj != None:
				serverName = Support.removeInvalid(messObj.server.name)
				self.serverKey[serverID] = serverName
				Support.writeJson(self.serverKeyLocation, self.serverKey)
		return serverName
	
	#Gets Channel's Name from Key
	def _getChannelName(self, serverPath, messObj):
		channelKey = self._getChannelKey(serverPath, messObj)
		#Checks if Channel ID is in Key
		if messObj.channel.id in list(channelKey.keys()):
			#If it is a message, checks to see if channel Name is still correct
			channelName = channelKey[messObj.channel.id]
			if messObj != None:
				channelNameCheck = Support.removeInvalid(messObj.channel.name)
				if channelName != channelNameCheck:
					#If name not correct Fix it and rename Log folder
					channelKey[messObj.channel.id] = channelNameCheck
					Support.writeJson("{}/ChannelKey.json".format(serverPath),
						channelKey)
					os.rename("{}/{}".format(serverPath, channelName), 
						"{}/{}".format(serverPath, channelNameCheck))
					_rotateLog("{}/{}".format(serverPath, channelNameCheck), 
						channelName)
					channelName = channelNameCheck
		else:
			#If ID not in Key, Add it
			if messObj != None:
				channelName = messObj.channel.name
				channelKey[messObj.channel.id] = channelName
				Support.writeJson("{}/ChannelKey.json".format(serverPath),
						channelKey)
		return channelName
				
				
	
	#Loads Channel's Key
	def _getChannelKey(self, serverPath, messObj):
		channelKeyLocation = "{}/ChannelKey.json".format(serverPath)
		channelKeyTemplate = {messObj.channel.id:messObj.channel.name}
		try:
			channelKey = Support.loadJson(channelKeyLocation)
		except FileNotFoundError:
			try:
				os.makedirs(serverPath)
			except FileExistsError:
				pass
			Support.writeJson(channelKeyLocation, {})
			self.sysLog("Warning", "Channel Key not found, new one Created.")
			channelKey = Support.loadJson(channelKeyLocation)
		except ValueError:
			os.makedirs(serverPath)
			Support.writeJson(channelKeyLocation, {})
			self.sysLog("Error", "Channel key Corrupted, new one Created.")
			channelKey = Support.loadJson(channelKeyLocation)
		return channelKey

		
	def _timeStamp(self):
		now = datetime.datetime.now()
		hour = str(now.hour)
		if int(hour) < 10:
			hour = "0" + str(hour)
		minute = str(now.minute)
		if int(minute) < 10:
			minute = "0" + str(minute)
		second = str(now.second)
		if int(second) < 10:
			second = "0" + str(second)
		year = str(now.year)
		if int(year) < 10:
			year = "0" + str(year)
		month = str(now.month)
		if int(month) < 10:
			month = "0" + str(month)
		day = str(now.day)
		if int(day) < 10:
			day = "0" + str(day)
		time = ("{m}/{d}/{y}, {h}:{min}:{s}".format(m=month, d=day, y=year, 
			h=hour, min=minute, s=second))
		return time
