import importlib
twospiesdata = importlib.import_module('twospiesdata')
import twospiesdata

import networkx as nx #all of these are simply to visualize the game state because looking at the adjacency list is quite taxing
import matplotlib.pyplot as plt 
import tkinter as tk
import random
import shlex


class City():
    def __init__(self, name = "Berlin"):
        self.value = 3
        self.action = False
        self.controlled = None
        self.capital = False
        self.name = name
        self.neighbours = [] #This will be an city array of neighbours

    def addNeighbour(self, neighbour):
        if neighbour not in self.neighbours:
            self.neighbours.append(neighbour)

    def getController(self):
        return self.controlled
    
    def getValue(self, player):
        Player.coverBlown(player)
        Player.changeIntel(player, self.value)
        self.value = 0

    def changeControl(self, player):
        self.controlled = player

    def getCapital(self):
        return self.capital

    def getName(self):
        return self.name

    def getAction(self):
        return self.action
    
    def getNeighbours(self):
        return self.neighbours


class Player(): #we will simply reference players as P1 and P2, using a circular queue to process turn orders in game
    def __init__(self, startCity, name):
        self.location = startCity #this is a city object
        self.lastSeen = None
        self.intel = 0
        self.actions = 0
        self.nextActions = 2
        self.cover = 1 #3 options for enumerated, 1: "Visible", 2: "Cover", 3: "DeepCover". Better for game logic as each level encompasses privileges of below level
        self.buffs = {"Encryption": False, "Strike Reports": False, "Rapid Recon": False}
        #Now we can simply reference and add buffs with fewer methods, code cleanliness
        self.alive = True
        self.name = name

    def getName(self):
        return self.name

    def getCity(self):
        return self.location
    
    def changeIntel(self, x):
        self.intel = self.intel + x

    def coverBlown(self):
        self.cover = 1
    
    def getStatus(self):
        return self.alive
    
    def lose(self):
        self.alive = False

    def control(self):
        City.changeControl(self.location, self)
        self.cover = 1

    def useAction(self):
        self.actions = self.actions - 1

    def wait(self):
        Player.useAction(self)

    def goDeep(self):
        self.cover = 3

    def move(self, city):
        self.location = city
        return (City.getController(city) == None or City.getController(city) == self)
    
    def getCover(self):
        return self.cover
    
    def prep(self):
        self.nextActions = self.nextActions + 1

    def getnextActions(self):
        return self.nextActions
    
    def getIntel(self):
        return self.intel
    
    def getActions(self):
        return self.actions
    
    def changeActions(self, num):
        self.actions = num

    def changeNextActions(self, num):
        self.nextActions = num

    def buyBuff(self, buff):
        self.buffs[buff] = True
        self.intel = self.intel + twospiesdata.IntelCost[buff]

    def getPossibleMoves(self):
        acts = []
        if self.actions == 0:
            return acts
        
        acts = acts + ["wait", "strike"]
        #originally control was in the above addition but I've realized that would allow you to control cities you already control.
        if City.getController(self.location) != self:
            acts = acts + ["control"]

        for buff in self.buffs: #abilities
            if(not self.buffs[buff] and self.intel + twospiesdata.IntelCost[buff] > 0):
                acts.append(f"Buy {buff}")
        for intelAction in ["go deep", "prep", "locate"]:#intel actions, go deep, locate, prep
            if(self.intel + twospiesdata.IntelCost[intelAction] > 0): #we don't check if we've already used this.
                acts.append(intelAction) #while this WILL lead to irrelevant branches in the MCTS and tree algorithms, it will not be comparatively computational expensive
        for city in City.getNeighbours(Player.getCity(self)):
            acts.append("move " + City.getName(city))
        return acts


class Game():
    def __init__(self, mapName): #AllRoadsLeadToBerlinEdges, AllRoadsLeadToBerlinData
        self.map = mapName #this will later be set to the game map from data
        self.playerList = []
        self.turns = 0
        self.logdump = []
        self.active = True
        self.cities = {} #useless at initialization (we overwrite it several times), crucial when set

    def createCities(self):
        cities = {}
        for edge1, edge2 in getattr(twospiesdata, self.map + "Edges"):
            cities[edge1] = City(name = edge1) #undirected graph, so while this isn't exactly efficient,
            cities[edge2] = City(name = edge2) #it's the simplest way. There are max 50 edges anyway

        self.cities = cities

    def createRoads(self):
        cities = self.cities
        for edge1, edge2 in getattr(twospiesdata, self.map + "Edges"):
            cities[edge1].addNeighbour(cities[edge2])
            cities[edge2].addNeighbour(cities[edge1])

        self.cities = cities

    def displayMap(self):
        for city in self.cities.values():
            print(f"{city.name}: {[neighbour.name for neighbour in city.neighbours]}")

    def createPlayers(self):
        player_data = getattr(twospiesdata, self.map + "Data")
        for player_name, city_name in player_data.items():
            start_city = self.cities.get(city_name)
            if start_city:
                x = Player(start_city, player_name)
                self.playerList.append(x)
                City.changeControl(start_city, x)

    def showGameStateAdv(self):
        # Initialize window
        window = tk.Tk()
        window.title("Game State")

        canvas_width = 800
        canvas_height = 600
        canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg='white')
        canvas.pack()

        # Assign random positions to cities
        city_positions = {}
        margin = 100
        for city_name in self.cities:
            x = random.randint(margin, canvas_width - margin)
            y = random.randint(margin, canvas_height - margin)
            city_positions[city_name] = (x, y)

        # Draw roads (edges)
        for city in self.cities.values():
            x1, y1 = city_positions[city.name]
            for neighbour in city.neighbours:
                x2, y2 = city_positions[neighbour.name]
                canvas.create_line(x1, y1, x2, y2, fill='gray')

        # Draw cities (nodes)
        radius = 20
        for city_name, (x, y) in city_positions.items():
            city = self.cities[city_name]
            color = "lightblue"
            if city.controlled == "Player1":
                color = "red"
            elif city.controlled == "Player2":
                color = "green"

            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline='black')
            canvas.create_text(x, y, text=city_name, font=('Arial', 10), fill='black')

        # Draw player positions
        for i, player in enumerate(self.playerList):
            px, py = city_positions[player.location.name]
            offset = -30 if i == 0 else 30  # Offset player labels to avoid overlap
            canvas.create_text(px, py + offset, text=f"P{i + 1}", fill='darkorange', font=('Arial', 12, 'bold'))

        # Start GUI loop
        window.mainloop()

    def showGameStateBasic(self):
        G = nx.Graph()

        # Add nodes for all cities
        for city in self.cities.values():
            G.add_node(city.name)

        # Add edges (bidirectional roads)
        for city in self.cities.values():
            for neighbour in city.neighbours:
                G.add_edge(city.name, neighbour.name)

        # Use spring layout
        pos = nx.spring_layout(G, seed=42)

        # Draw cities
        node_colors = []
        for city in self.cities.values():
            # Optional: color based on control
            if city.controlled == "Player1":
                node_colors.append('red')
            elif city.controlled == "Player2":
                node_colors.append('green')
            else:
                node_colors.append('lightblue')

        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1000, font_size=10, edge_color='gray')

        cols = ['yellow', 'green']
        # Highlight player locations
        for i, player in enumerate(self.playerList):
            city_name = player.location.name
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=[city_name],
                node_color=cols[i],
                node_size=1300,
                edgecolors='black'
            )

        plt.title("Game State: City Network and Player Locations")
        plt.axis('off')
        plt.show(block = False)
    
    def useUpAction(self):
        Player.useAction(self.playerList[self.turns % len(self.playerList)])

    def control(self):
        Player.control(self.playerList[self.turns % len(self.playerList)])

    def strike(self):
        p = self.playerList[self.turns % len(self.playerList)]
        print(f"{p} has attempted a strike in {Player.getCity(p)}!")
        for target in self.playerList:
            if target != p and Player.getCity(target) == Player.getCity(p) and Player.getStatus(target):
                Player.lose(target)
                print(f"{Player.getName(p)} has struck down {Player.getName(target)} at {City.getName(Player.getCity(p))}!")

    def wait(self):
        pass

    def goDeep(self):#25 intel
        Player.goDeep(self.playerList[self.turns % len(self.playerList)])

    def move(self, city):
        if not Player.move(self.playerList[self.turns % len(self.playerList)], city):
            if Player.getStatus(City.getController(city)) and Player.getCover(self.playerList[self.turns % len(self.playerList)]) != 3:
                print(f"{self.playerList[self.turns % len(self.playerList)]}'s COVER IS BLOWN")
        #put a player function in, should blow cover if controlled by any OTHER player and NOT deepcover. we got a little conditional right here

    def locate(self): #10 intel
        for player in self.playerList:
            if player != self.playerList[self.turns % len(self.playerList)] and Player.getStatus(player) and Player.getCover(player) < 3 and not Player.getBuff(player, "Encryption"):
                #for now print out the city, later incorporate this into the possible locations
                print(f"{player} is in city {Player.getCity(player)}")
                Player.coverBlown(player)
        print("All enemies have been located or are in deepcover.")

    def prep(self): #40 intel
        Player.prep(self.playerList[self.turns % len(self.playerList)])
        Player.changeIntel(self.playerList[self.turns % len(self.playerList)], getattr(twospiesdata, "IntelCost")["prep"])

    def purchaseBuff(self, buff):
        Player.buyBuff(self.playerList[self.turns % len(self.playerList)], buff)

    def endTurn(self):
        for player in self.playerList:
            if player != self.playerList[self.turns % len(self.playerList)] and self.playerList[self.turns % len(self.playerList)].getStatus():
                if Player.getCity(player) == Player.getCity(self.playerList[self.turns % len(self.playerList)]):
                    Player.coverBlown(self.playerList[self.turns % len(self.playerList)])
    
    def getPossibleActions(self):
        return Player.getPossibleMoves(self.playerList[self.turns % len(self.playerList)])

    def inToAction(self, command):
        tokens = shlex.split(command)
        match tokens:
            case ["Buy", *item]:
                Game.purchaseBuff(self, " ".join(item))
            case ["move", *location]:
                city_name = " ".join(location)
                city = self.cities.get(city_name)
                self.move(city)
            case ["wait"]:
                Game.wait(self)
            case ["control"]:
                Game.control(self)
            case ["strike"]:
                Game.strike(self)
            case ["locate"]:
                Game.locate(self)
            case ["prep"]:
                Game.prep(self)
            case ["go", "deep"]:
                Game.goDeep(self)
        Game.useUpAction(self)

    def commandDict(self, command):
        funcDict = {"wait" : Game.wait, #if anyone ever reads this, this is not a good use of function dicts but 
                    "control": Game.control, #I think it's quite funny. if only it worked for move and buy
                    "strike": Game.strike, 
                    "end turn": Game.endTurn,
                    "move" : Game.move,
                    "buy" : Game.purchaseBuff,
                    "locate": Game.locate,
                    "go deep": Game.goDeep,
                    "prep": Game.prep
                    } #I hate this but I love it
        #implement the intel actions,
        #moves_ 
        #locate, deepcover,
        try:
            funcDict[command](self)
        except:
            funcDict[command](self, command[5:]) if command[0:4] == "move" else funcDict[command](self, command[4:])#so python-pilled with this. as opposed to c-cored.

    def turn(self, currentPlayer):
        while(Player.getActions(currentPlayer) > 0):
            print(f"\n=== Player {Player.getName(currentPlayer)}'s Turn ===")
            print(f"Current Location: {City.getName(Player.getCity(currentPlayer))}")
            print(f"Available Actions: {Player.getActions(currentPlayer)}")
            print(f"Intel: {Player.getIntel(currentPlayer)}")
            print(f"Turn number: {self.turns}")

            #Here's the logic for the model to 'learn' by 'playing'
            if Player.getName(currentPlayer) == "Player1": #my turn
                x = Player.getPossibleMoves(currentPlayer)
                print(x)
                num = int(input("Select an action!")) - 1
                Game.inToAction(self, x[num])

            if Player.getName(currentPlayer) == "Player2": #model's turn
                x = Player.getPossibleMoves(currentPlayer)
                num = random.randint(1, len(x)) - 1 #erratic model actually managed to get me because I misread vienna as venice while testing.
                print(x[num]) #can't believe I lost to a seed
                Game.inToAction(self, x[num])
                #here the model will have a choice to 'branch out'

            if self.activePlayers() == 1:
                self.active = False
                break


    def turnWrapper(self):
        currentPlayer = self.playerList[self.turns % len(self.playerList)] #this would get insanely messy as opposed to all the other helper functions.
        #luckily python passes EVERYTHING by reference here so this works. converting this to c would be a nightmare

        print("here!")
        # Set actions
        Player.changeActions(currentPlayer, Player.getnextActions(currentPlayer))

        Player.changeNextActions(currentPlayer, 2)

        if City.getAction(Player.getCity(currentPlayer)):  # Bonus for city with special action
            Player.changeActions(currentPlayer, Player.getActions(currentPlayer) + 1)

        #give intel based on cities and bonus cities
        for city in self.cities.values():
            if City.getController(city) == currentPlayer:
                Player.changeIntel(currentPlayer, 3 if City.getCapital(city) else 1) #just some ternary practice. I hate it though
        City.getValue(Player.getCity(currentPlayer), currentPlayer)
        Game.turn(self, currentPlayer)

        print("TURN ENDING NOW!")

        Game.endTurn(self)

        self.turns = self.turns + 1
        
    def activePlayers(self):
        return sum(1 for p in self.playerList if Player.getStatus(p)) #this is a funny line that pretty much only works for finding the number of True's in a list 

    def getWinner(self):
        for player in self.playerList:
            if Player.getStatus(player): #there is exactly one winner. while this could easily be extended to a team-style two spies, that's not really the focus of this project
                return player #so we can just return the first alive player as the game loop only concludes if there are 2 or more players

    def gameLoop(self):
        while self.activePlayers() > 1: #this is simple because it's simple
            self.turnWrapper()

    
        winner = self.getWinner()
        print(f"\n Player {Player.getName(winner)} wins the game!") #due to the nature of the game state, there will ALWAYS be a winner.
        #no conditionals required. 

A = Game("AllRoadsLeadToBerlin")
A.createCities()
A.createRoads()
A.displayMap()
A.createPlayers()
A.showGameStateBasic()
A.gameLoop()
