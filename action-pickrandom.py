#!/usr/bin/env python3

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes

# imported to get type check and IDE completion
from hermes_python.ontology.dialogue.intent import IntentMessage

from api import Api
import json


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

required_slots = {
    "num_players": None
}

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

    @staticmethod
    def PickRandomBoardgameCallback(hermes: Hermes, intent_message: IntentMessage):
        if (intent_message.custom_data):
            available_slots = json.loads(intent_message.custom_data)
        
        num_players_slot = intent_message.slots.num_players.first().value or available_slots["num_players"]
        available_slots["num_players"] = num_players_slot

        if not num_players_slot:
            return hermes.publish_continue_session(intent_message.session_id,
                                                    required_slots_questions["num_players"],
                                                    ["hjwk:ElicitNumPlayers"],
                                                    custom_data=json.dumps(available_slots))
        
        hermes.publish_end_session(intent_message.session_id, "Ok, laisse moi un instant...")

    @staticmethod
    def ElicitNumPlayersCallback(hermes: Hermes, intent_message: IntentMessage):

        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "D'accord, laisse moi réfléchir...")

        # action code goes here...
        print('[Received] intent: {}'.format(
            intent_message.intent.intent_name))

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id,
            "Action 2", "Je vais vous trouver ça")

    # register callback function to its intent and start listen to MQTT bus
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intent("hjwk:PickRandomBoardgame", self.PickRandomBoardgameCallback)
            h.subscribe_intent('hjwk:ElicitNumPlayers', self.ElicitNumPlayersCallback)
            h.loop_forever()

if __name__ == "__main__":
    PickRandomBoardgame()
