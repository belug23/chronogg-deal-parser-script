#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

from chronogg_parser import ChronoGGParser # pylint: disable=all; noqa
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = ChronoGGParser.script_name
Website = "https://github.com/belug23/"
Description = "Grab infromation about the current Chrono GG site and display a text in the chat"
Creator = "Belug"
Version = ChronoGGParser.version


chad_bot = ChronoGGParser()
# Ugly StreamLab part, just map functions to the class
def ScriptToggled(state):
    return chad_bot.scriptToggled(state)

def Init():
    chad_bot.setParent(Parent)  #  noqa injected by streamlabs chatbot
    return chad_bot.setConfigs()

def Execute(data):
    return chad_bot.execute(data)

def ReloadSettings(jsonData):
    return chad_bot.setConfigs()

def OpenReadMe():
    return chad_bot.openReadMe()

def Tick():
    return chad_bot.tick()
