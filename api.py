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

    def authorizedGetRequest(self, url):
        return requests.get(url, headers={'Authentication': 'JWT ' + self.token})

    def getToken(self):
        payload = { 'username': self.username, 'password': self.password }
        url = self.backend_url + '/user/login'
        resp = requests.post(url, data=payload)

        if not resp.ok:
            print("Token could not be retrieved")
            return None

        return resp.json()['token']

    def getUserId(self):
        url = self.backend_url + '/user/current'
        user = self.authorizedGetRequest(url)

        if not user.ok:
            print("UserId could not be retrieved")
            return None

        return user.json()["id"]

    def updateLibrary(self):
        if not self.boardgames:
            url = self.backend_url + '/user/current/library_games'
        library = self.authorizedGetRequest(url)
            if not library.ok:
                print("Token no longer valid, refreshing")
                self.token = self.getToken()
            library = self.authorizedGetRequest(url)

            self.boardgames = library.json()

    def getRandomBoardgames(self, numberOfPlayers, numberOfBoardgames):
        # Get boardgames
        self.updateLibrary()

        ## Filter according to number of players
        filteredGames = []
        for game in self.boardgames:
            if (game['board_game']['min_players'] <= numberOfPlayers and
                game['board_game']['max_players'] >= numberOfPlayers):
                filteredGames.append(game['board_game']['name'])

        numberOfBoardgames = numberOfBoardgames if numberOfBoardgames > 0 else 3

        if len(filteredGames) < numberOfBoardgames:
            return filteredGames
        else:
            options = random.sample(range(0, len(filteredGames)), numberOfBoardgames)
            return [ filteredGames[i] for i in options ]

    def getMostPlayedBoardgame(self):
        # Get stats
        url = self.backend_url + '/user/' + str(self.userId) + '/stats'
        stats = self.authorizedGetRequest(url)

        if stats.ok:
            return stats.json()['most_played']['board_game']['name']

    def getNumberOfBoardgames(self):
        #Get stats
        url = self.backend_url + '/user/' + str(self.userId) + '/stats'
        stats = self.authorizedGetRequest(url)

        if stats.ok:
            return stats.json()['owned']