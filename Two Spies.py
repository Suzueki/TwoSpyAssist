import networkx as nx
import matplotlib.pyplot as plt

def visualize(MapName):# ONLY FOR VISUALLY CHECKING NODES ARE ALL CONNECTED FROM EDGE LIST
    G = nx.Graph()
    # Add nodes
    for city in mapping:
        G.add_node(city)
    # Add edges
    for edge in edgeListList[MapName]: #"All Roads Lead to Berlin"
        G.add_edge(edge[0], edge[1])

    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Layout for visual spacing

    # Draw nodes, edges, and labels
    nx.draw_networkx_nodes(G, pos, node_color='Yellow', node_size=800)
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_labels(G, pos, font_size=5)

    # Highlight the start and end cities
    nx.draw_networkx_nodes(G, pos, nodelist=[stage.firstCity], node_color='green', node_size=1000, label='Start City')
    nx.draw_networkx_nodes(G, pos, nodelist=[stage.secondCity], node_color='red', node_size=1000, label='End City')

    plt.title("Graph: All Roads Lead to Berlin")
    plt.axis('off')
    plt.legend(scatterpoints=1)
    plt.show()

mapping = {"Amsterdam":0,
           "Belgrade":1,
           "Berlin":2,
           "Brussels":3,
           "Budapest":4,
           "Geneva":5,
           "Istanbul":6,
           "Kyiv":7,
           "London":8,
           "Moscow":9,
           "Monaco":10,
           "Paris":11,
           "Rome":12,
           "Stockholm":13,
           "Venice":14,
           "Vienna":15,
           "Warsaw":16}
invmapping = {0: "Amsterdam",
           1: "Belgrade",
           2: "Berlin",
           3: "Brussels",
           4: "Budapest",
           5: "Geneva",
           6: "Istanbul",
           7: "Kyiv",
           8: "London",
           9: "Moscow",
           10: "Monaco",
           11: "Paris",
           12: "Rome",
           13: "Stockholm",
           14: "Venice",
           15: "Vienna",
           16: "Warsaw"}
A = [
    ("Amsterdam", "Stockholm"),
    ("Amsterdam", "Berlin"),
    ("Amsterdam", "Brussels"),
    ("Brussels", "Berlin"),
    ("Brussels", "Paris"),
    ("Berlin", "Stockholm"),
    ("Berlin", "Warsaw"),
    ("Berlin", "Budapest"),
    ("Berlin", "Venice"),
    ("Berlin", "Geneva"),
    ("Geneva", "Venice"),
    ("Geneva", "Monaco"),
    ("Geneva", "Paris"),
    ("Budapest", "Vienna"),
    ("Budapest", "Warsaw"),
    ("Budapest", "Kyiv"),
    ("Paris", "Monaco"),
    ("Kyiv", "Warsaw"),
    ("Kyiv", "Moscow"),
    ("Monaco", "Venice"),
    ("Moscow", "Warsaw"),
    ("Moscow", "Stockholm"), 
    ("Vienna", "Venice")
]

edgeListList = {
    "All Roads Lead to Berlin": A
}

StageData = {
    "All Roads Lead to Berlin": ({"P1": "Stockholm", "P2": "Budapest"})
}

class Player:
    def __init__(self, id, city, intel = 0, cover = False, deepCover = False):
        self.id = id
        self.city = city
        self.intel = intel
        self.cover = cover
        self.deepCover = deepCover
        self.encrypt = False
        self.comm = False
        self.report = False
        self.actions = 2

    def getId(self):
        return self.id
    
    def getCity(self):
        return self.city
    
    def newTurn(self, inc):
        self.actions = 2
        self.intel = self.intel + inc

    def useAction(self):
        self.actions = self.actions - 1


class City:
    def __init__(self, cityName, controller = 0, value = 3, bonus = 0):
        self.cityName = cityName
        self.controller = controller
        self.value = value
        self.bonus = bonus

    def getName(self):
        return self.cityName
    
    def control(self, player):
        self.controller == Player.getId(player)

    def capital(self):
        self.value = 10

    def intelPickup(self):
        self.bonus = 10

    
class Stage:
    def __init__(self, mapName, firstCity, secondCity):
        self.firstCity = firstCity
        self.secondCity = secondCity
        self.matrix = Stage.createGrid(Stage.createBoard(), edgeListList[mapName])

    def access(self, x, y):
        return self.matrix[x][y]

    @staticmethod
    def createGrid(board, edgeList):
        for edge in edgeList:
            board[mapping[edge[0]]][mapping[edge[1]]] = 1
            board[mapping[edge[1]]][mapping[edge[0]]] = 1
        return board

    @staticmethod
    def createBoard():
        return [[0 for _ in range(17)] for _ in range(17)]
    
    def displayMatrix(self):
        for i in range(17):
            print(self.matrix[i])

    def removeCity(self, city):
        number = mapping[city]
        for i in range(17):
            self.matrix[i][number] = 0
            self.matrix[number][i] = 0
        
class Game:
    def __init__(self, Mapname):
        self.turnNo = 0
        self.stage = Stage(Mapname, StageData[Mapname]["P1"], StageData[Mapname]["P2"])
        cityList = {}
        for key in mapping:
            cityList[key] = City(key)
        cityList[StageData[Mapname]["P1"]] = City(StageData[Mapname]["P1"], 1)
        cityList[StageData[Mapname]["P2"]] = City(StageData[Mapname]["P2"], 2)
        self.cities = cityList
        self.player1 = Player(1)
        self.player2 = Player(2)

    def showMat(self):
        Stage.displayMatrix(self.stage)

    def showBoard(self):
        G = nx.Graph()

        # Add nodes with controller-based color attributes
        color_map = []
        for cityName, city in self.cities.items():
            G.add_node(cityName)
            if city.controller == 1:
                color_map.append('blue')
            elif city.controller == 2:
                color_map.append('red')
            else:
                color_map.append('gray')

        # Add edges based on adjacency matrix
        for i in range(17):
            for j in range(i+1, 17):
                if self.stage.matrix[i][j] == 1:
                    city1 = invmapping[i]
                    city2 = invmapping[j]
                    G.add_edge(city1, city2)

        # Draw the graph
        pos = nx.spring_layout(G, seed=42)  # Stable layout
        nx.draw(G, pos, node_color=color_map, with_labels=True, node_size=800, font_size=9, edge_color='black')
        plt.title("City Network")
        plt.show()

    def swapTurns():
        pass

    def possibleMoves(self, player):
        c = []
        for i in range(17):
            if Stage.access(self.stage, mapping[City.getName(Player.getCity(player))],i) == 1:
                c.append(City.getName(Player.getCity(player)))
        return c

    def moveTo(self, player, destination):
        current_city = mapping[Player.getCity(player)]
        dest_city = mapping[destination]

        if self.stage.matrix[current_city][dest_city] == 1:
            player.city = destination
            Player.useAction(player)
            print(f"{player.id} moved to {destination}.")
        else:
            print(f"Invalid move: {destination} is not adjacent to {player.city}.")

    def turn(self):
        pass

    def control(self):
        pass

    def strike(Player1, Player2):
        if(Player.getCity(Player1) == Player.getCity(Player2)):
            print("Game over! Player1 wins.")
        else:
            print("Target not in ")
        pass

    def wait(self, player):
        Player.useAction(player)

    def goDeep():
        pass

    def locate(self, ):
        pass

    def prep():
        pass
    
    def buy():
        pass #strike reports, communications, encryption



# Create a Game instance
Example = Game("All Roads Lead to Berlin")
Example.showMat()
Example.showBoard()



