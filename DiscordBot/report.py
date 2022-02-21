from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    BROAD_CAT_IDENTIFIED = auto()
    SPECIFIC_CAT_IDENTIFIED = auto()
    FINAL_MESSAGE = auto()
    REPORT_COMPLETE = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
        self.broadCategory = None
        self.specificCategory = None
        self.optionalMessage = None
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            reply =  "Enter `1` for Misinformation\n"
            reply += "Enter `2` for Dangerous or Illegal Content\n"
            reply += "Enter `3` for Harrassemnt or Abuse.\n"
            reply += "Enter `4` for More Options\n"
            reply += "Enter `5` for I don't want to see this content"
            self.state = State.BROAD_CAT_IDENTIFIED
            return ["Great, I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "What is the reason you are reporting this message? (Choose from below.)\n" + reply]
          
        if self.state == State.BROAD_CAT_IDENTIFIED:
            # TODO: store this information about what broad category of abuse the message falls under
            self.broadCategory = message.content
            self.state = State.SPECIFIC_CAT_IDENTIFIED
            if message.content == '1':
                reply =  "Enter `1` for Elections\n"
                reply += "Enter `2` for Covid-19\n"
                reply += "Enter `3` for Other Health or Medical\n"
                reply += "Enter `4` for Climate Change\n"
                reply += "Enter `5` for Gun Violence\n"
                reply += "Enter `6` for Other"
                return ["What kind of misinformation is this? (Choose from below).\n" + reply]
            if message.content == '2':
                reply =  "Enter `1` for Expresses intentions of self-harm or suicide\n"
                reply += "Enter `2` for Expresses intentions for harming others\n"
                reply += "Enter `3` for Dangerous or Violent Organizations\n"
                reply += "Enter `4` for Child Sexual Abuse Materials\n"
                reply += "Enter `5` for Human Trafficking\n"
                reply += "Enter `6` for Sale of Illegal Goods"
                return ["What kind of dangerous or illegal content is this? (Choose from below).\n" + reply]
            if message.content == '3':
                reply =  "Enter `1` for Hate Speech or Symbols\n"
                reply += "Enter `2` for Bullying\n"
                reply += "Enter `3` for Sexual Harrassment\n"
                reply += "Enter `4` for Stalking\n"
                return ["What kind of harrassement of abuse is this? (Choose from below).\n" + reply]
            if message.content == '4':
                reply =  "Enter `1` for Spam\n"
                reply += "Enter `2` for Copy Right Infringement\n"
                reply += "Enter `3` for Impersonation\n"
                reply += "Enter `4` for Other\n"
                return ["Here are more options: (Choose from below).\n" + reply]
        
        if self.state == State.SPECIFIC_CAT_IDENTIFIED:
            self.specificCategory = message.content
            reply = ""
            if (self.broadCategory == '1') and (self.specificCategory == '2'):
                reply = "\n\nAlso, here is the link to visit the CDC website for the latest information on Covid-19: https://www.cdc.gov/coronavirus/2019-ncov/index.html" 
            self.state = State.FINAL_MESSAGE
            return["If you would like to add more information to your report, here is space to do so. Enter your message when you are ready to proceed." + reply]
        
        if self.state == State.FINAL_MESSAGE:
            self.optionalMessage = message.content
            self.state = State.REPORT_COMPLETE
            if self.broadCategory == '1':
                return["Thank you for your report. We will send this to our fact-checking partners and when misinformation is confimed, we will limit the content's distribution and warn other users."]
            if self.broadCategory== '2':
                return["Thank you for your report. It will be reviewed by our content moderation team, who will decide future action, including any necessary reports to law enforcement. Thank you for trying to keep our platform safe."]
            return["Thank you for your report. It will be reviewed by our content moderation team, who will decide future action, including if the post should be removed or the user banned."]

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    

