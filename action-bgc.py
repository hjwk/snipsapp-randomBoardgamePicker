#!/usr/bin/env python3

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes

# imported to get type check and IDE completion
from hermes_python.ontology.dialogue.intent import IntentMessage

from api import Api
from util import *

CONFIG_INI = "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

required_slots_questions = {
    "num_players": "Combien de joueurs ?",
}

class PickRandomBoardgame(object):
    def __init__(self):
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
            self.apiHandler = Api(self.config.get("secret").get("username"),
                              self.config.get("secret").get("password"),
                              self.config.get("global").get("backend_api"))
        except Exception:
            self.config = None

        self.numberOfBoardgames = 3
        self.lastNumPlayers = 2
        self.lastNumBoardgames = 3

        self.start_blocking()

    def GenerateBoardgamesAnswer(self, boardgames, num_players):
        if len(boardgames) == 0:
            return "Vous n'avez pas de jeu qui se joue à {}".format(num_players)

        answer = "Vous pourriez jouer à "
        for i in range(len(boardgames)):
            answer += boardgames[i]
            if i < len(boardgames) - 2:
                answer += ", "
            elif i == len(boardgames) - 2:
                answer += " ou à "
        
        return answer

    def PickRandomBoardgameCallback(self, hermes: Hermes, intent_message: IntentMessage):
        num_players_slot = extractSlot(intent_message.slots, "numberOfPlayers")
        num_boardgames_slot = extractSlot(intent_message.slots, "numberOfPropositions")
        numberOfBoardgames = num_boardgames_slot if num_boardgames_slot else self.numberOfBoardgames

        if not num_players_slot:
            return hermes.publish_continue_session(intent_message.session_id,
                                                    required_slots_questions["num_players"],
                                                    ["hjwk:ElicitNumPlayers"],
                                                    custom_data=str(numberOfBoardgames))

        hermes.publish_end_session(intent_message.session_id, "")

        boardgames = self.apiHandler.getRandomBoardgames(num_players_slot, numberOfBoardgames)
        hermes.publish_start_session_notification(intent_message.site_id, self.GenerateBoardgamesAnswer(boardgames, num_players_slot), "")
        self.lastNumBoardgames = numberOfBoardgames
        self.lastNumPlayers = num_players_slot

    def ElicitNumPlayersCallback(self, hermes: Hermes, intent_message: IntentMessage):
        hermes.publish_end_session(intent_message.session_id, "")

        numPlayers = extractSlot(intent_message.slots, "numberOfPlayers")
        numberOfBoardgames = int(intent_message.custom_data)
        boardgames = self.apiHandler.getRandomBoardgames(numPlayers, numberOfBoardgames)    
        hermes.publish_start_session_notification(intent_message.site_id, self.GenerateBoardgamesAnswer(boardgames, numPlayers), "")
        self.lastNumBoardgames = numberOfBoardgames
        self.lastNumPlayers = numPlayers

    def RepeatPickRandomCallback(self, hermes: Hermes, intent_message: IntentMessage):
        hermes.publish_end_session(intent_message.session_id, "")

        boardgames = self.apiHandler.getRandomBoardgames(self.lastNumPlayers, self.lastNumBoardgames)
        answer = self.GenerateBoardgamesAnswer(boardgames, self.lastNumPlayers)
        hermes.publish_start_session_notification(intent_message.site_id, answer, "")

    def FavouriteBoardgame(self, hermes: Hermes, intent_message: IntentMessage):
        hermes.publish_end_session(intent_message.session_id, "")
        favouriteBoardgame = self.apiHandler.getMostPlayedBoardgame()
        hermes.publish_start_session_notification(intent_message.site_id, "Votre jeu préféré est {}".format(favouriteBoardgame), "")

    def PossessedBoardgames(self, hermes: Hermes, intent_message: IntentMessage):
        hermes.publish_end_session(intent_message.session_id, "")
        numberOfOwnedBoardgames = self.apiHandler.getNumberOfBoardgames()
        hermes.publish_start_session_notification(intent_message.site_id, "Vous possédez {} jeux".format(numberOfOwnedBoardgames), "")

    # register callback function to its intent and start listen to MQTT bus
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intent("hjwk:PickRandomBoardgame", self.PickRandomBoardgameCallback)
            h.subscribe_intent('hjwk:ElicitNumPlayers', self.ElicitNumPlayersCallback)
            h.subscribe_intent('hjwk:FavouriteBoardgame', self.FavouriteBoardgame)
            h.subscribe_intent('hjwk:PossessedBoardgames', self.PossessedBoardgames)
            h.subscribe_intent('hjwk:RepeatPickRandom', self.RepeatPickRandomCallback)
            h.loop_forever()

if __name__ == "__main__":
    PickRandomBoardgame()
