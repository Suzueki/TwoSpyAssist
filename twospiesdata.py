IntelCost = {"prep": -40, 
             "locate": -10,
             "go deep": -25,
             "strike": -0, 
             "move": -0, 
             "wait": -0, 
             "control": -0,
             "Encryption": -25,
             "Strike Reports": -10,
             "Rapid Recon": -40,
             "end turn": 0}

AllRoadsLeadToBerlinEdges = [
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

AllRoadsLeadToBerlinData = {
    "Player1": "Stockholm",
    "Player2": "Budapest"
}

horizontalOffset = 0
verticalOffset = 0
CityCoordinates = {
    "Amsterdam": (215, 360),
    "Berlin":(305,395),
    "Brussels": (175,435),
    "Budapest":(450,500),
    "Geneva":(200,505),
    "Monaco":(200,585),
    "Paris":(105,465),
    "Kyiv":(585,415),
    "Moscow":(625,260),
    "Vienna":(365,505),
    "Venice":(300,565),
    "Warsaw":(465,400),
    "Stockholm":(375,215),
    "London":(110,365),
    "Rome":(310,645),
    "Istanbul":(590,645)

}