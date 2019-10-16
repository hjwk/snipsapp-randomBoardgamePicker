import requests
import random

class Api(object):
    def __init__(self, username, password, backend_url):
        self.username = username
        self.password = password
        self.backend_url = backend_url

        self.token = self.getToken()
        self.userId = self.getUserId()

        self.boardgames = None

    def getToken(self):
        payload = { 'username': self.username, 'password': self.password }
        resp = requests.post(self.backend_url + '/user/login', data=payload)

        if not resp.ok:
            print("Token could not be retrieved")
            return None

        return resp.json()['token']

    def getUserId(self):
        url = self.backend_url + '/user/current'
        user = requests.get(url,  headers={'Authentication': 'JWT ' + self.token})

        return user.json()["id"]

    def updateLibrary(self):
        if not self.boardgames:
            url = self.backend_url + '/user/current/library_games'
            library = requests.get(url, headers={'Authentication': 'JWT ' + self.token})
            if not library.ok:
                print("Token no longer valid, refreshing")
                self.token = self.getToken()
                library = requests.get(url, headers={'Authentication': 'JWT ' + self.token})

            self.boardgames = library.json()

    def getRandomBoardgames(self, numberOfPlayers, numberOfBoardgames):
        # Get boardgames
        self.updateLibrary()

        ## Filter according to number of players
        filteredGames = []
        for game in self.boardgames:
            if (game['board_game']['min_players'] <= numberOfPlayers and
                game['board_game']['max_players'] >= numberOfPlayers):
                filteredGames.append(game)

        options = random.sample(range(0, min(len(filteredGames), numberOfBoardgames)), numberOfBoardgames)
        return [ filteredGames[i]['board_game']['name'] for i in options ]

    def getMostPlayedBoardgame(self):
        # Get stats
        url = self.backend_url + '/user/' + str(self.userId) + '/stats'
        stats = requests.get(url, headers={'Authentication': 'JWT ' + self.token})

        if stats.ok:
            return stats.json()['most_played']['board_game']['name']
