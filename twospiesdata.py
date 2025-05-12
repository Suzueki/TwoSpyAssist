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
