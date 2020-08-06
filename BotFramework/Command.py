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
import datetime
import inspect

class Command:
	"""A Command class to provide methods we can use with it"""
	def __init__(self, bot, comm, *, alias=None, **options):
		self.bot = bot
		self.comm = comm
		self.desc = options.get("desc", "")
		self.type = options.get("comType", "Normal")
		self.alias = self.aliases = options.get("alias", options.get("aliases", []))
		self.listed = options.get("listed", True)
		self.func = options.get("func")
		self.subcommands = []
		bot.commands[comm] = self
		for a in self.alias:
			bot.commands[a] = self
	
	def subcommand(self, *args, **kwargs):
		"""Creates subcommands"""
		return SubCommand(self, *args, **kwargs)
	
	def __call__(self, func):
		#Make it able to be used as a decorator
		self.func = func
		return self
	
	@asyncio.coroutine
	def run(self, message):
		#Check for Command Arguements
		args = message.text.split(" ")
		if len(args) > 1:
			args = args[1:]
		argName = inspect.getfullargspec(self.func)[0][1:]
		#Checks if has enough Arguments
		if len(args) > len(argName):
			args[len(argName)-1] = " ".join(args[len(argName)-1:])
			args = args[:len(argName)]
		elif len(args) < len(argName):
			raise Exception("Not enough arguments for {}, required "
				"arguments: {}".format(self.comm, ", ".join(argName)))
		
		ann = self.func.__annotations__
		'''for x in range(0, len(argName)):
			v = args[x]
			k = argName[x]
			print("VK")
			print(v)
			print(k)
			if type(v) != ann[k]:
				try:
					v = ann[k](v)
				except:
					raise TypeError("Invalid type: got {}, {} "
						"expected".format(ann[k].__name__, v.__name__))
			args[x] = v'''
		#Checks for Subcommands
		if len(self.subcommands)>0:
			#Pops out the command and saves arguments for subcommands
			subcomm = args.pop(0)
			
			for s in self.subcommands:
				if subcomm == s.comm:
					m = message.text.split(" ")
					message.text = c[0] + " " + " ".join(c[2:])
					
					yield from s.run(message)
					break
		else:
			yield from self.func(message, *args)


class SubCommand(Command):
	#Subcommand Class
	def __init__(self, parent, comm, *, desc=""):
		self.comm = comm
		self.parent = parent
		self.bot = parent.bot
		self.subcommands = []
		self.parent.subcommands.append(self)
