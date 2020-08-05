import BotFramework

class bot:
	def __init__(self):
		self.bot = BotFramework.Bot(commandPrefix="!") #Creates the bot with the command Prefix "!" can change prefix to anything.
		self.bot.on_ready = self.on_ready #Overwrites the on_ready in the bot, which is why it's there, for extra ready stuff, there is a second one that prints
		#and logs a bunch of info, bot_ready if you wish to not have that.
		self._runBot() #Starts the bot, could also do it directly if you want.
	async def on_ready(self):
		print("Extra ready stuff Started!")
	def _runBot(self):
		self.bot.run("BotDiscordTokenHere")
	
