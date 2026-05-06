BASE_URL = "https://api.jolpi.ca/ergast/f1"
YEARS = list(range(2019, 2027))
CONTROL_TEAMS = {"Alpine", "Williams", "Haas", "AlphaTauri", "Aston Martin", "McLaren"}
TREATMENT_TEAMS = {"Mercedes", "Red Bull", "Ferrari"}
TEAM_NAME_MAP = {
    "Racing Point": "Aston Martin",
    "Toro Rosso":   "AlphaTauri",
    "RB":           "AlphaTauri",
    "Renault":      "Alpine",
    "Alfa Romeo":   "Sauber",
    "Haas F1 Team": "Haas",
    "Mercedes-AMG Petronas": "Mercedes",
    "Scuderia Ferrari": "Ferrari",
    "Red Bull Racing": "Red Bull",
    "Williams Racing": "Williams",
    "Kick Sauber": "Sauber",
    "McLaren F1 Team": "McLaren"
}

CIRCUIT_NAME_MAP = {
    'Australian Grand Prix': 'Australian GP',
    'Bahrain Grand Prix': 'Bahrain GP',
    'Chinese Grand Prix': 'Chinese GP',
    'Azerbaijan Grand Prix': 'Azerbaijan GP',
    'Spanish Grand Prix': 'Spanish GP',
    'Monaco Grand Prix': 'Monaco GP',
    'Canadian Grand Prix': 'Canadian GP',
    'French Grand Prix': 'French GP',
    'Austrian Grand Prix': 'Austrian GP',
    'British Grand Prix': 'British GP',
    'German Grand Prix': 'German GP',
    'Hungarian Grand Prix': 'Hungarian GP',
    'Belgian Grand Prix': 'Belgian GP',
    'Italian Grand Prix': 'Italian GP',
    'Singapore Grand Prix': 'Singapore GP',
    'Russian Grand Prix': 'Russian GP',
    'Japanese Grand Prix': 'Japanese GP',
    'Mexican Grand Prix': 'Mexican GP',
    'United States Grand Prix': 'United States GP',
    'Brazilian Grand Prix': 'Brazilian GP',
    'Abu Dhabi Grand Prix': 'Abu Dhabi GP',
    'Styrian Grand Prix': 'Styrian GP',
    '70th Anniversary Grand Prix': '70th Anniversary GP',
    'Tuscan Grand Prix': 'Tuscan GP',
    'Eifel Grand Prix': 'Eifel GP',
    'Portuguese Grand Prix': 'Portuguese GP',
    'Emilia Romagna Grand Prix': 'Imola GP',
    'Turkish Grand Prix': 'Turkish GP',
    'Sakhir Grand Prix': 'Sakhir GP',
    'Dutch Grand Prix': 'Dutch GP',
    'Mexico City Grand Prix': 'Mexico City GP',
    'São Paulo Grand Prix': 'São Paulo GP',
    'Qatar Grand Prix': 'Qatar GP', 
    'Saudi Arabian Grand Prix': 'Saudi Arabian GP',
    'Miami Grand Prix': 'Miami GP',
    'Las Vegas Grand Prix': 'Las Vegas GP'
}