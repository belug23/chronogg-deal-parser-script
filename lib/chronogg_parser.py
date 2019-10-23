import clr # pylint: disable=all; noqa .net system
import codecs
import json
import os
import sys
import datetime


class ChronoGGParser(object):
    """ 
    Because I hate coding with only functions and using Global variables.
    Here is the chrono gg deal parser.
    This will download chrono GG deal information and display a message with
    the infromation to the chat.
    """
    script_name = "Chrono GG deal parser"
    config_file = "config.json"
    application_name = 'Chrono GG deal parser'
    version = '1.0.0'

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.settings = {}
        self.parent = None
        # Store a python datetime of the deal's end date
        self.last_deal_end = None
        # Store the last parsed deal
        self.last_deal = None

    def setParent(self, parent):
        self.parent = parent

    def setConfigs(self):
        self.loadSettings()

    def download_deal(self):
        url = self.settings['chronoGGApiURL']
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        result = self.parent.GetRequest(url,headers)
        self.last_deal = json.loads(json.loads(result)['response'])
        # Ugly but I can't use packages and make it easy for users, so ugly code it is
        self.last_deal_end = datetime.datetime.strptime(self.last_deal['end_date'][:-1], "%Y-%m-%dT%H:%M:%S.%f" )

    def loadSettings(self):
        """
            This will parse the config file if present.
            If not present, set the settings to some default values
        """
        try:
            with codecs.open(os.path.join(self.base_path, '..', self.config_file), encoding='utf-8-sig', mode='r') as file:
                self.settings = json.load(file, encoding='utf-8-sig')
        except Exception:
            self.settings = {
                "liveOnly": False,
                "command": "!chronogg",
                "partnerID": "PartnerID",
                "permission": "Everyone",
                "useCooldown": True,
                "useCooldownMessages": False,
                "cooldown": 60,
                "onCooldown": "{user}, {command} is still on cooldown for {cd} minutes!",
                "userCooldown": 180,
                "onUserCooldown": "{user}, {command} is still on user cooldown for {cd} minutes!",
                "chronoGGApiURL": "https://api.chrono.gg/deals/",
                "outputMessage": "Today on chrono GG you can find the game '{game_name}' for {platforms} at {sale_price} ({discount} off of {normal_price}). The time is ticking, only {time_left} if left, more information at {chrono_url}"
            }

    def scriptToggled(self, state):
        """
            Do an action if the state change. Like sending an announcement message
        """
        return

    def execute(self, data):
        """
            Parse the data sent from the bot to see if we need to do something.
        """
        # If it's from chat and the live setting correspond to the live status
        
        if self.canParseData(data):
            command = self.settings["command"].lower()
            if data.GetParam(0).lower() == command:
                if not self.isOnCoolDown(data, command):
                    return self.parseDeal(data, command)
        return
    
    def canParseData(self, data):
        return (
            data.IsChatMessage() and
            (
                (self.settings["liveOnly"] and self.parent.IsLive()) or 
                (not self.settings["liveOnly"])
            )
        )
    
    def isOnCoolDown(self, data, command):
        if (
            self.settings["useCooldown"] and
            (self.parent.IsOnCooldown(self.script_name, command) or
            self.parent.IsOnUserCooldown(self.script_name, command, data.User))
        ):
            self.sendOnCoolDownMessage(data, command)
            return True
        else:
            return False
    
    def sendOnCoolDownMessage(self, data, command):
        if self.settings["useCooldownMessages"]:
            commandCoolDownDuration = self.parent.GetCooldownDuration(self.script_name, command)
            userCoolDownDuration = self.parent.GetUserCooldownDuration(self.script_name, command, data.User)

            if commandCoolDownDuration > userCoolDownDuration:
                cdi = commandCoolDownDuration
                message = self.settings["onCooldown"]
            else:
                cdi = userCoolDownDuration
                message = self.settings["onUserCooldown"]
            
            cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
            self.sendMessage(data, message, command=command, cd=cd)
    
    def is_ended(self):
        now = datetime.datetime.utcnow()
        time_left = self.last_deal_end - now
        # If the time delta is negative, it's ended
        return time_left < datetime.timedelta(0)

    
    def parseDeal(self, data, command):
        if not self.last_deal or self.is_ended():
            self.download_deal()
        self.sendMessage(data, self.settings['outputMessage'], command)

    def setCoolDown(self, data, command):
        if self.settings["useCooldown"]:
            self.parent.AddUserCooldown(self.script_name, command, data.User, self.settings["userCooldown"])
            self.parent.AddCooldown(self.script_name, command, self.settings["cooldown"])
    
    def get_time_left(self):
        now = datetime.datetime.utcnow()
        time_left = self.last_deal_end - now
        return (datetime.datetime.min + time_left).time().strftime('%H:%M:%S')


    def sendMessage(self, data, message, command=None, cd="0"):
        if command is None:
            command = self.settings["command"]

        outputMessage = message.format(
            user=data.UserName,
            cost=str(None),  # not used
            currency=self.parent.GetCurrencyName(),
            command=command,
            cd=cd,
            time_left=self.get_time_left(),
            chrono_url='https://www.chrono.gg/' + self.settings['partnerID'],
            game_name=self.last_deal['name'],
            normal_price=self.last_deal['normal_price'],
            discount=self.last_deal['discount'],
            sale_price=self.last_deal['sale_price'],
            platforms=', '.join(self.last_deal['platforms']),
        )
        self.parent.SendStreamMessage(outputMessage)

    def tick(self):
        """
        not used, here for maybe future projects.
        """
        return
    
    def openReadMe(self):
        location = os.path.join(os.path.dirname(__file__), "README.txt")
        if sys.platform == "win32":
            os.startfile(location)  # noqa windows only
        else:
            import subprocess
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, location])
        return
