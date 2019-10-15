import requests
import random

class Api(object):
    def __init__(self, username, password, backend_url):
        # get authentication token
        payload = { 'username': username, 'password': password }
        resp = requests.post(backend_url + '/user/login', data=payload)

        if not resp.ok:
            print("ERROR")

        self.token = resp.json()['token']
        self.username = username
        self.password = password
        self.backend_url = backend_url

    def getRandomBoardgames(self, numberOfPlayers, numberOfBoardgames):
        # Get boardgames
        url = self.backend_url + '/user/current/library_games'
        library = requests.get(url, headers={'Authentication': 'JWT ' + self.token})
        games = library.json()

        ## Filter according to number of players
        filteredGames = []
        for game in games:
            if (game['board_game']['min_players'] <= numberOfPlayers and
                game['board_game']['max_players'] >= numberOfPlayers):
                filteredGames.append(game)

        if len(filteredGames) <= numberOfBoardgames:
            return [ filteredGames[i]['board_game']['name'] for i in range(len(filteredGames)) ]
        else:
            options = random.sample(range(0, len(filteredGames)), numberOfBoardgames)
            return [ filteredGames[i]['board_game']['name'] for i in options ]
