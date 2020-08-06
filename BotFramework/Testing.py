import asyncio
import re
import sys

from .Support import Support


class TestingClient:
	def __init__(self, bot):
		self.bot = bot
		self.passes = 0
		self.fails = 0
		self.middle = 0
		self.failedTests = []
		self.currentTest = None
		self.testList = Support.loadJson(self, "Files/TestingList.json")
		self.comResult = ""
		self.version = "1.0"
	
	#Starts Running the bot and handles a KeyboardInterrupt
	def run(self, token):
		try: 
			self.bot.loop.run_until_complete(self._start())
		except KeyboardInterrupt:
			self._stop("Stopping test Via Keyboard Interrupt")
	
	def _stop(self, logMessage):
		pending = asyncio.Task.all_tasks()
		gathered = asyncio.gather(*pending)
		try:
			gathered.cancel()
			self.bot.loop.run_until_complete(gathered)
			gathered.exception()
		except:
			pass
		self.bot.loop.stop()
		self.bot.logging.sysLog("Debug", logMessage)
		sys.exit(0)
	
	
	async def _start(self):
		self.bot.logging.sysLog("Debug", "Starting Test Run...")
		results = await self._runTest()
		if len(self.failedTests) <= 0:
			self.failedTests.append("None")
		#Template: NameOfTest:{PartOfTest:ResultOfPart}
		
		finalResults=["=====================Test Results=====================",
			"Passes........: {}\n"
			"Fails.........: {}\n"
			"Neither/Middle: {}".format(self.passes, self.fails, 
				self.middle)]
		for res in results:
			finalResults.append(res)
			for parts in results[res]:
				finalResults.append("    {}: {}".format(parts, 
					results[res][parts]))
		finalResults.append("=====================Failed Tests======================")
		finalResults.append("\n".join(self.failedTests))
		finalResults="\n".join(finalResults)
		self.bot.logging.sysLog("Debug", finalResults)
		
		self._stop("Test has Concluded")
	
	async def _runTest(self):
		results = {}
		testID = 1
		for tests in list(self.testList.keys()):
			results[tests]={} #Defines this test in results
			currentTest = self.testList[tests] #Sets the current Test
			#Sets the command up so it's just passed in
			command = self.testList[tests]["Command"].format(self.bot.commandPrefix)
			#Runs the tests for this test group
			for test in list(self.testList[tests]["Tests"].keys()):
				testID += 1 #incraments testID
				#Resets the comResult Variable
				self.comResult = "{} not Ran.".format(test)
				#Gets Test Message Ready
				message = self._createMessage(command, 
					currentTest["Tests"][test][0], 
					currentTest["MultiCom"])
				#Sends test to bot
				await self._sendTest(message, testID)
				#Gets the command's results
				for result in currentTest["Tests"][test][1]:
					#if result matches expected, pass test
					if re.match(result, self.comResult):
						results[tests][test]=self._passedTest()
						break
				else:
					#else Fail it
					results[tests][test]=self._failedTest(tests, test,
						self.comResult, currentTest["Tests"][test][1])
		return results
				
	
	
	
	
	#Testing Helper Functions
	def _createMessage(self, command, arg, multiCom=False):
		if arg != "":
			if multiCom:
				message = "{}{}".format(command, arg)
			else:
				message = "{} {}".format(command, arg)
		else:
			message = command
		return message
	
	def _passedTest(self):
		testResult = "Passed Test"
		self.passes += 1
		return testResult
	
	def _failedTest(self, testGroup, test, result, expected):
		#If test was the one that was supposed to fail, pass it
		if testGroup == "Testing Commands" and test == "Failed Test":
			return self._passedTest() + " Failed"
		
		#Gets expected result(s) together
		expected = "\n or.............: ".join(expected)
		#Sets the result to failed and show the differing results
		testResult=("Failed Test\n"
			"	Result.........: {}\n"
			"	Expected Result: {}".format(result, expected))
		
		#Add one to Failed count
		self.fails += 1
		#Add failed test result to the failed list
		self.failedTests.append(testGroup + "\n    " + testResult.replace("Failed Test", 
			test))
		return testResult
	
	#Sends test to the bot to run through regular code
	async def _sendTest(self, testMessage, testID):
		message = MessageObject(testMessage, testID)
		await self.bot.on_message(message)
	
	#Testing override Functions
	async def wait_until_ready(self):
		return True
	
	async def change_presence(self, activity=None):
		return True
	
	def get_channel(self, idNum):
		return SendMessageChannel(self)




#Test Classes to replace real ones
class SendMessageChannel:
	def __init__(self, testingSelf):
		self.test = testingSelf
	async def send(self, message):
		self.test.comResult = "Say: {}".format(message)

class MessageObject():
	def __init__(self, message, testID):
		self.author = UserObject()
		self.text = message
		self.embeds = None
		self.channel = ChannelObject()
		self.server = self.channel.server
		self.id = testID
		self.attachments = []

class ChannelObject():
	def __init__(self):
		self.name = "Testing Void"
		self.server = ServerObject()
		self.id = "000005"
		self.catID = 0
		self.topic = "The Void of Testing"

class ServerObject():
	def __init__(self):
		self.name = "System"
		self.id = "000000"
		self.ownerID = "000000000000"
		self.unavailable = False

class UserObject():
	def __init__(self):
		self.name = "TestingBot" #The User name
		self.id = "000001" #The ID Number
		self.discrim = "0000" #The #8139
		self.bot = True #Bool if bot account
		self.system = False #Bool if user is system user (Discord)
		self.discordNick = "Testing Bot" #Nickname set on Discord server
		self.nick = "Testing Bot"
				
