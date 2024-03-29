RED = "RED"
BLUE = "BLUE"
YELLOW = "YELLOW"
GREY = "GREY"
COLORS = [BLUE, RED, YELLOW, GREY]
MAX_DISEASE_COUNT = 3
DISEASE_CUBE_LIMIT = 24
MIN_NUM_EPIDEMIC_CARDS = 4
MAX_ACTIONS = 4
MAX_PLAYERS = 4
MAX_OUTBREAK_COUNT = 8
CURE_COUNT = 5
MAX_HAND_COUNT = 7
# Active-player-only generic actions
ACTION = "action"
MOVE_ADJACENT = "MOVE_ADJACENT"
MOVE_DIRECT_FLIGHT = "MOVE_DIRECT_FLIGHT"
MOVE_CHARTER_FLIGHT = "MOVE_CHARTER_FLIGHT"
MOVE_SHUTTLE_FLIGHT = "MOVE_SHUTTLE_FLIGHT"
BUILD_RESEARCH_STATION = "BUILD_RESEARCH_STATION"
TREAT_DISEASE = "TREAT_DISEASE"
SHARE_KNOWLEDGE = "SHARE_KNOWLEDGE"
DISCOVER_CURE = "DISCOVER_CURE"

# Abilities and nonactions
ABILITY = "ability"
DISCARD = "DISCARD"
END_TURN = "END_TURN"

# City information
STARTING_CITY = "Atlanta"
STARTING_COLOR = BLUE
CITY_LIST = {
    "San Francisco": BLUE,
    "Chicago": BLUE,
    "Atlanta": BLUE,
    "Washington": BLUE,
    "Montreal": BLUE,
    "New York": BLUE,
    "London": BLUE,
    "Madrid": BLUE,
    "Paris": BLUE,
    "Milan": BLUE,
    "St Petersburg": BLUE,
    "Essen": BLUE,
    "Los Angeles": YELLOW,
    "Miami": YELLOW,
    "Mexico City": YELLOW,
    "Bogota": YELLOW,
    "Lima": YELLOW,
    "Sao Paulo": YELLOW,
    "Santiago": YELLOW,
    "Buenos Aires": YELLOW,
    "Lagos": YELLOW,
    "Kinshasa": YELLOW,
    "Johannesburg": YELLOW,
    "Khartoum": YELLOW,
    "Cairo": GREY,
    "Algiers": GREY,
    "Riyadh": GREY,
    "Karachi": GREY,
    "Mumbai": GREY,
    "Chennai": GREY,
    "Kolkata": GREY,
    "Delhi": GREY,
    "Tehran": GREY,
    "Moscow": GREY,
    "Istanbul": GREY,
    "Baghdad": GREY,
    "Bangkok": RED,
    "Hong Kong": RED,
    "Taipei": RED,
    "Beijing": RED,
    "Seoul": RED,
    "Tokyo": RED,
    "Shanghai": RED,
    "Ho Chi Minh City": RED,
    "Manila": RED,
    "Jakarta": RED,
    "Sydney": RED,
    "Osaka": RED
}

CITY_CONNECTIONS = {
    "San Francisco": ["Chicago", "Tokyo", "Manila", "Los Angeles"],
    "Chicago": ["San Francisco", "Los Angeles", "Mexico City", "Atlanta", "Montreal"],
    "Los Angeles": ["Sydney", "Chicago", "San Francisco", "Mexico City"],
    "Mexico City": ["Bogota", "Lima", "Miami", "Los Angeles", "Chicago"],
    "Atlanta": ["Miami", "Washington", "Chicago"],
    "Montreal": ["Chicago", "New York", "Washington"],
    "Miami": ["Bogota", "Washington", "Atlanta"],
    "Washington": ["New York", "Atlanta", "Miami"],
    "New York": ["London", "Madrid", "Montreal", "Washington"],
    "Bogota": ["Mexico City", "Miami", "Lima", "Buenos Aires", "Sao Paulo"],
    "Lima": ["Mexico City", "Bogota", "Santiago"],
    "Santiago": ["Lima"],
    "Buenos Aires": ["Sao Paulo", "Bogota"],
    "Sao Paulo": ["Madrid", "Bogota", "Buenos Aires", "Lagos"],
    "Lagos": ["Kinshasa", "Khartoum", "Sao Paulo"],
    "Kinshasa": ["Khartoum", "Johannesburg", "Lagos"],
    "Johannesburg": ["Kinshasa", "Khartoum"],
    "Khartoum": ["Kinshasa", "Johannesburg", "Cairo"],
    "Cairo": ["Algiers", "Khartoum", "Istanbul", "Baghdad", "Riyadh"],
    "Riyadh": ["Cairo", "Baghdad", "Karachi"],
    "Mumbai": ["Karachi", "Chennai", "Delhi"],
    "Baghdad": ["Istanbul", "Tehran", "Karachi", "Riyadh", "Cairo"],
    "Istanbul": ["Milan", "Cairo", "Algiers", "Baghdad", "Moscow"],
    "Moscow": ["St Petersburg", "Istanbul", "Tehran"],
    "St Petersburg": ["Essen", "Istanbul", "Moscow"],
    "Essen": ["Milan", "Paris", "London", "St Petersburg"],
    "Milan": ["Istanbul", "Paris", "Essen"],
    "Paris": ["Madrid", "London", "Algiers", "Essen", "Milan"],
    "Tehran": ["Moscow", "Karachi", "Baghdad", "Delhi"],
    "Karachi": ["Mumbai", "Riyadh", "Baghdad", "Tehran", "Delhi"],
    "Delhi": ["Karachi", "Tehran", "Mumbai", "Chennai", "Kolkata"],
    "Kolkata": ["Delhi", "Chennai", "Bangkok", "Hong Kong"],
    "Bangkok": ["Chennai", "Kolkata", "Jakarta", "Ho Chi Minh City", "Hong Kong"],
    "Chennai": ["Mumbai", "Delhi", "Kolkata", "Bangkok", "Jakarta"],
    "Jakarta": ["Sydney", "Ho Chi Minh City", "Bangkok", "Chennai"],
    "Ho Chi Minh City": ["Jakarta", "Bangkok", "Hong Kong", "Manila"],
    "Hong Kong": ["Bangkok", "Ho Chi Minh City", "Kolkata", "Taipei", "Manila"],
    "Taipei": ["Manila", "Hong Kong", "Osaka", "Shanghai"],
    "Manila": ["Ho Chi Minh City", "Sydney", "Hong Kong", "Taipei", "San Francisco"],
    "Sydney": ["Los Angeles", "Jakarta", "Manila"],
    "Osaka": ["Taipei", "Tokyo"],
    "Tokyo": ["San Francisco", "Osaka", "Shanghai", "Seoul"],
    "Shanghai": ["Hong Kong", "Beijing", "Seoul", "Taipei", "Tokyo"],
    "Beijing": ["Shanghai", "Seoul"],
    "London": ["New York", "Madrid", "Paris", "Essen"],
    "Algiers": ["Madrid", "Paris", "Istanbul", "Cairo"],
    "Seoul": ["Beijing", "Shanghai", "Tokyo"],
    "Madrid": ["London", "Sao Paulo", "Paris", "New York", "Algiers"]
}
