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


'''
	This file is due to bad experiences relying directly on a Discord Library. 
	This file basically is a translation layer between the bot framework and the Library.
	In short should the libary/API change, or a new one be needed, all interactions with it it
	are in more or less one place for easy fixing.
'''
import discord


class APITranslator:
	def __init__(self, bot):
		self.bot = bot
		self.client = DiscordClient(bot, loop=self.bot.loop)
		self.version = "{} {}.{}.{}".format(discord.version_info[3], 
			discord.version_info[0], discord.version_info[1], discord.version_info[2])
		
	def run(self, token):
		self.client.run(token)
	
	async def waitUntilReady(self):
		return await self.client.wait_until_ready()
	
	async def changeStartGame(self):
		gameSettings = self.bot.settings["game"]
		game = discord.Game(name=gameSettings["Name"], url=gameSettings["URL"], 
			type=gameSettings["Type"])
		await self.client.change_presence(activity=game)
	async def changeGame(self, gameName):
		game = discord.Game(name=gameName, url=None, 
			type=None)
		await self.client.change_presence(activity=game)
	async def sendMessage(self, channelID, message):
		channel = self.client.get_channel(channelID)
		await channel.send(message)

class DiscordClient(discord.Client):
	def __init__(self, bot, *, loop=None, **options):
		self.bot = bot
		super().__init__(loop=None, **options)
	async def on_ready(self):
		self.bot.name = self.user.name
		self.bot.id = self.user.id
		await self.bot.bot_ready()
	async def on_message(self, disMessage):
		message = MessageObject(disMessage, self.bot)
		await self.bot.on_message(message)
		
class MessageObject():
	def __init__(self, message, bot=None):
		self.author = UserObject(message.author, bot)
		self.text = message.content
		self.embeds = message.embeds
		self.channel = ChannelObject(message.channel)
		self.server = self.channel.server
		self.id = message.id
		self.attachments = []
		for attach in message.attachments:
			self.attachments.append(AttachmentObject(attach))

class AttachmentObject():
	def __init__(self, attachment):
		self.id = attachment.id
		self.size = attachment.size
		self.height = attachment.height
		self.width = attachment.width
		self.filename = attachment.filename
		self.url = attachment.url

class ChannelObject():
	def __init__(self, channel):
		self.name = channel.name
		self.server = ServerObject(channel.guild)
		self.id = channel.id
		self.catID = channel.category_id
		self.topic = channel.topic

class ServerObject():
	def __init__(self, server):
		self.name = server.name
		self.id = server.id
		self.ownerID = server.owner_id
		self.unavailable = server.unavailable

class UserObject():
	def __init__(self, member, bot=None):
		self.name = member.name #The User name
		self.id = member.id #The ID Number
		self.discrim = member.discriminator #The #8139
		self.bot = member.bot #Bool if bot account
		self.system = member.system #Bool if user is system user (Discord)
		self.discordNick = member.nick #Nickname set on Discord server
		if bot != None: #Checks for a custom nickname set in bot
			nickList = bot.otherVars["customNicks"]
			if self.id in nickList:
				randNick = [random.choice(nickList), self.discordNick]
				self.nick = random.choice(randNick)
			else:
				self.nick = self.discordNick
		else:
			self.nick = self.discordNick
				
		

		
