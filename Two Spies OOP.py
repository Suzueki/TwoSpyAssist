import importlib
twospiesdata = importlib.import_module('twospiesdata')
import twospiesdata

import tkinter as tk #Required for basic GU. Removed other graphing utilities
from tkinter import messagebox #Required for win message

import random #This may or not be necessary based on the actual shutdown and bonus city mechanics. Reverse engineering required.
import shlex #Why would I parse when I can have it done for me? getting shlexy?
from PIL import Image, ImageTk #Purely for the psychological aspect in that it feels better when there's a background

class City():
    def __init__(self, name = "Berlin"):
        self.value = 3
        self.action = False
        self.controlled = None
        self.capital = False
        self.name = name
        self.neighbours = [] #This will be an city array of neighbours
        self.x = twospiesdata.CityCoordinates[name][0] + twospiesdata.horizontalOffset
        self.y = twospiesdata.CityCoordinates[name][1] + twospiesdata.verticalOffset

    def addNeighbour(self, neighbour):
        if neighbour not in self.neighbours:
            self.neighbours.append(neighbour)

    def deleteRoads(self):
        self.neighbours = [] #effectively removes all neighbours

    def deleteRoad(self, badCity): #wish python had overloading rn
        try:
            self.neighbours.remove(badCity)
        except: #this try-catch is pretty irrelevant but I just don't want an error
            pass

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

    def getBuff(self, buff):
        return self.buffs[buff]

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
    
    def getCities(self):
        return self.cities

    def createRoads(self):
        cities = self.cities
        for edge1, edge2 in getattr(twospiesdata, self.map + "Edges"):
            cities[edge1].addNeighbour(cities[edge2])
            cities[edge2].addNeighbour(cities[edge1])

        self.cities = cities

    def removeRoads(self, removeCity):
        for city in self.cities.values():
            if removeCity == city:
                City.deleteRoads(city)
            else:
                City.deleteRoad(city, removeCity)

    def choice(self):
        select = {}
        for city in self.cities.values(): #Provides a dictionary of most well-linked cities
            for neighbour in City.getNeighbours(city):
                if neighbour in select:
                    select[neighbour] = select[neighbour] + 1
                else:
                    select[neighbour] = 1 
        min_value = min(select.values())
        selected = [key for key, value in select.items() if value == min_value]
        return random.choice(selected) #allows us to randomly remove the least linked city

    def designateBonusCity(self):
        select = {}
        for city in self.cities: #Provides a dictionary of most well-linked cities
            for neighbour in City.getNeighbours(city): #Linked-ness is a measure of how many edges they have to other nodes
                if neighbour in select:
                    select[neighbour] = select[neighbour] + 1
                else:
                    select[neighbour] = 1 
        v = max(select.values())
        selected = [key for key, value in select.items() if value == v]
        return random.choice(selected)

    def progressMap(self):
        #pseudorandom(? requires inspection of original game) function to pick a city
        #should not cut any players out, only exists to provide an eventual convergence
        #for the game state
        #This gives us two main advantages. #1, it mirrors the actual game
        #2, it provides a finite number of states
        #and eventually any tree-search algorithms have a base case
        if not (self.turns % 10):
            x = Game.choice(self)
            Game.removeRoads(self, x)
            print(f"Shutting down {City.getName(x)}")
        if not (self.turns % 5):
            pass
        if not (self.turns % 5):
            pass

    def displayMap(self):
        for city in self.cities.values():
            print(f"{city.name}: {[neighbour.name for neighbour in city.neighbours]}")

    def getPlayerList(self):
        return self.playerList

    def createPlayers(self):
        player_data = getattr(twospiesdata, self.map + "Data")
        for player_name, city_name in player_data.items():
            start_city = self.cities.get(city_name)
            if start_city:
                x = Player(start_city, player_name)
                self.playerList.append(x)
                City.changeControl(start_city, x)

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
    
    def getCurrentPlayer(self):
        return self.playerList[self.turns % len(self.playerList)]
    
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

    def getTurns(self):
        return self.turns
        
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

    def changeGameStatus(self):
        self.active = not self.active

    def removeCity(self, toRemove):
        pass
        


class TwoSpiesGUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.title("Two Spies in Python with Tkinter")
        self.width = 600
        self.height = 815
        self.geometry("1500x950")
        self.canvasList = {}
        self.makeCanvas()
        self.after(0, self.step)

    def turn(self, game, currentPlayer):
        while(Player.getActions(currentPlayer) > 0):
            print(f"\n=== Player {Player.getName(currentPlayer)}'s Turn ===")
            print(f"Current Location: {City.getName(Player.getCity(currentPlayer))}")
            print(f"Available Actions: {Player.getActions(currentPlayer)}")
            print(f"Intel: {Player.getIntel(currentPlayer)}")
            print(f"Turn number: {Game.getTurns(game)}")

            #Here's the logic for the model to 'learn' by 'playing'
            if Player.getName(currentPlayer) == "Player1": #my turn
                x = Player.getPossibleMoves(currentPlayer)
                print(x)
                num = int(input("Select an action!")) - 1
                Game.inToAction(game, x[num])

            if Player.getName(currentPlayer) == "Player2": #model's turn
                x = Player.getPossibleMoves(currentPlayer)
                num = random.randint(1, len(x)) - 1 #erratic model actually managed to get me because I misread vienna as venice while testing.
                print(x[num]) #can't believe I lost to a seed
                Game.inToAction(game, x[num])
                #here the model will have a choice to 'branch out'

            if Game.activePlayers(game) == 1:
                Game.changeGameStatus(game)
                break

    def turnWrapper(self):
        Game.progressMap(self.game)
        game = self.game
        currentPlayer = Game.getPlayerList(self.game)[Game.getTurns(game) % len(Game.getPlayerList(self.game))] #this would get insanely messy as opposed to all the other helper functions.
        #luckily python passes EVERYTHING by reference here so this works. converting this to c would be a nightmare

        print("here!")
        # Set actions
        Player.changeActions(currentPlayer, Player.getnextActions(currentPlayer))

        Player.changeNextActions(currentPlayer, 2)

        if City.getAction(Player.getCity(currentPlayer)):  # Bonus for city with special action
            Player.changeActions(currentPlayer, Player.getActions(currentPlayer) + 1)

        #give intel based on cities and bonus cities
        for city in Game.getCities(game).values():
            if City.getController(city) == currentPlayer:
                Player.changeIntel(currentPlayer, 3 if City.getCapital(city) else 1) #just some ternary practice. I hate it though
        City.getValue(Player.getCity(currentPlayer), currentPlayer)
        self.turn(self.game, currentPlayer)

        print("TURN ENDING NOW!")
        Game.endTurn(game)
        game.turns = game.turns + 1

    def makeCanvas(self):
        for player in self.game.getPlayerList():
            c = tk.Canvas(self, width=self.width, height=self.height, bg="white")
            c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvasList[player.getName()] = c

    def drawMaps(self):
        for player in Game.getPlayerList(self.game):
            if player == Game.getCurrentPlayer(self.game):
                self.drawActiveMap(player)
            else:
                self.drawInactiveMap(player)

    def drawDefaultMap(self, player):
        bg = Image.open("assets_task_01jvjjnjhwfbnv7azqtmqv36y2_1747601589_img_0.jpg")
        bg_resized = bg.resize((self.width, self.height))
        memoryRetainer = ImageTk.PhotoImage(bg_resized)

        canvas = self.canvasList[player.getName()]
        canvas.bg_image = memoryRetainer #this is so dumb but it literally needs this  
        canvas.delete("all") #because of how python handles memory
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.bg_image)

        # Drawing the city edges (roads)
        for city in self.game.cities.values():
            x1, y1 = city.x, city.y
            for neighbor in city.neighbours:
                x2, y2 = neighbor.x, neighbor.y
                canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)

        # Drawing the city nodes
        radius = 10
        for city in self.game.cities.values():
            x, y = city.x, city.y

            # Determine control color
            if city.controlled:
                if city.controlled.name == "Player1":
                    fill_color = "red"
                elif city.controlled.name == "Player2":
                    fill_color = "green"
                else:
                    fill_color = "blue"
            else:
                fill_color = "gray"

            # Draw city circle
            canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=fill_color, outline="black"
            )

            # Draw city names
            canvas.create_text(x, y - radius - 10, text=city.name, font=("Arial", 10), fill="black")
        return canvas

    def drawActiveMap(self, player):
        canvas = self.drawDefaultMap(player)
        #this draws the current player location
        x = twospiesdata.CityCoordinates[City.getName(Player.getCity(player))][0]
        y = twospiesdata.CityCoordinates[City.getName(Player.getCity(player))][1]
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill = "white", outline = "black")
        
        #draws action and intel 
        #draws dump of all player info for now, we remake this later
        canvas.create_rectangle(0, 700, 300, 850, fill = "white", outline = "black")
        infodump = f"Actions: {Player.getActions(player)}. Intel: {Player.getIntel(player)}. Turns = {Game.getTurns(self.game)}"
        canvas.create_text(0, 700, text = infodump, font = "Arial", fill = "black")
        canvas.create_text(0,800, text = Player.getPossibleMoves(player), fill = "black")
        #draws actions in bottom (without buttons)
        
        #draws turn number

    def drawInactiveMap(self, player):
        self.drawDefaultMap(player)
        canvas = self.drawDefaultMap(player)
        x = twospiesdata.CityCoordinates[City.getName(Player.getCity(player))][0]
        y = twospiesdata.CityCoordinates[City.getName(Player.getCity(player))][1]
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill = "white", outline = "black")
        

    def step(self):
        self.drawMaps()
        # 1) If game over, stop
        if self.game.activePlayers() <= 1:
            messagebox.showinfo("Game Over", f"{self.game.getWinner().name} wins!")
            self.after(3000, self.destroy)
            return

        # 2) Advance one “unit” of game logic
        #    e.g. if human: wait for a button press to call game.inToAction
        #         if AI: pull from a background thread or just do one AI move
        self.turnWrapper()

        # 4) Schedule next step
        self.after(100, self.step)

    #redraw_map, update_action_list, update_log methods here …

class MCTS(): 
    def __init__(self):
        pass

class POMDP(): #while this class is called POMDP, it should actually be POMCP
    def __init__(self): #because POMDP is just the 'problem' to solve. dp sounds better than cp.
        pass

class RegretMinimizer(): #CFR!!! I LOVE NASH EQUILIBRIUMS
    def __init__(self):
        pass

class NeuralNet():
    def __init__(self): #not sure if I'll do this, getting training data would be difficult
        pass

if __name__ == "__main__":
    game = Game("AllRoadsLeadToBerlin")
    game.createCities()
    game.createRoads()
    game.createPlayers()
    app = TwoSpiesGUI(game)
    app.mainloop()