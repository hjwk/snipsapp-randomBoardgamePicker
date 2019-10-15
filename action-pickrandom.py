#!/usr/bin/env python3

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes

# imported to get type check and IDE completion
from hermes_python.ontology.dialogue.intent import IntentMessage

from api import Api


CONFIG_INI = "config.ini"

# if this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
#
# hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

required_slots_questions = {
    "num_players": "Ok, mais pour combien de joueurs ?",
}

def extractSlot(slots, slot):
    if (slots.slot):
        return slots.slot.first().value
    
    return None

class PickRandomBoardgame(object):
    """class used to wrap action code with mqtt connection
       please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except Exception:
            self.config = None

        self.apiHandler = Api(self.config.get("secret").get("username"),
                              self.config.get("secret").get("password"),
                              self.config.get("global").get("backend_api"))

        self.start_blocking()

    def PickRandomBoardgameCallback(self, hermes: Hermes, intent_message: IntentMessage):
        num_players_slot = extractSlot(intent_message.slots, "players")
        if not num_players_slot:
            return hermes.publish_continue_session(intent_message.session_id,
                                                    required_slots_questions["num_players"],
                                                    ["hjwk:ElicitNumPlayers"])
        
        hermes.publish_end_session(intent_message.session_id, "Ok, laisse moi un instant...")

        boardgames = self.apiHandler.getRandomBoardgames(num_players_slot)
        if len(boardgames) == 0:
            return hermes.publish_start_session_notification(intent_message.site_id, "Désolé mais vous n'avez pas de jeu qui se joue à {}".format(num_players_slot))

        hermes.publish_start_session_notification(intent_message.site_id, "Vous pourriez jouer à {}".format(boardgames[0]))

    def ElicitNumPlayersCallback(self, hermes: Hermes, intent_message: IntentMessage):

        # terminate the session before we perform the api call to bgc
        hermes.publish_end_session(intent_message.session_id, "D'accord, laisse moi réfléchir...")
        
        num_players_slot = extractSlot(intent_message.slots, "players")
        boardgames = self.apiHandler.getRandomBoardgames(num_players_slot)
        if len(boardgames) == 0:
            return hermes.publish_start_session_notification(intent_message.site_id, "Désolé mais vous n'avez pas de jeu qui se joue à {}".format(num_players_slot))

        hermes.publish_start_session_notification(intent_message.site_id, "Que pensez-vous de {}".format(boardgames[0]))

    # register callback function to its intent and start listen to MQTT bus
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intent("hjwk:PickRandomBoardgame", self.PickRandomBoardgameCallback)
            h.subscribe_intent('hjwk:ElicitNumPlayers', self.ElicitNumPlayersCallback)
            h.loop_forever()

if __name__ == "__main__":
    PickRandomBoardgame()
