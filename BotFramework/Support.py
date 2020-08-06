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

import json
import os
from pathlib import Path

class bcolors:
	PURPLE = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	WARNING = YELLOW
	RED = '\033[91m'
	ERROR = RED
	NORMAL = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class Support:	
	def writeJson(self, filePath, data):
		with open(filePath,"w") as data_files:
			json.dump(data,data_files,indent=4,separators=(',', ':'))
	
	def loadJson(self, filePath):
		with open(filePath) as data_files:
			data = json.load(data_files)
		return data
	
	def removeInvalid(self, start):
		#Removes characters that are largely considered invalid in file names
		invalidCharacters = ["?", "/", ":", "*", '"', "<", ">", "|","\\"]
		for invalid in invalidCharacters:
			if invalid in start:
				start = start.replace(invalid,"")
		return start
	
	def fileWrite(self, filePath, write, fileCreate=True, failWrite=None):
		try:
			with open(filePath, "a") as f:
				result = f.write(write+"\n")
			return result
		except FileNotFoundError:
			if fileCreate:
				self.createFile(filePath, failWrite)
				with open(filePath, "a") as f:
					result = f.write(write+"\n")
				return result
			else:
				raise FileNotFoundError
	def fileRead(self, filePath, fileCreate=False, failWrite=None):
		try:
			with open(file, "r") as f:
				result = f.read()
			return result
		except FileNotFoundError:
			if fileCreate:
				self.createFile(file,failWrite)
				with open(file, "r") as f:
					result = f.read()
				return result
			else:
				raise FileNotFoundError
	def createFile(self, filePath, failWrite):
		try:
			dirPath = Path(filePath)
			dirSplit = filePath.split("/")
			directory = "/".join(dirSplit[0:len(dirSplit)-1])
			try:
				os.makedirs(directory)
			except FileExistsError:
				pass
			dirPath.touch(exist_ok=False)
			if failWrite:
				with open(filePath, "w") as f:
					result = f.write(failWrite + "\n")
				return result
		except FileExistsError:
			pass
