from firebase_config import db

# Premier League Teams
teams = [
    {"name": "Arsenal", "short_name": "ARS"},
    {"name": "Aston Villa", "short_name": "AVL"},
    {"name": "Chelsea", "short_name": "CHE"},
    {"name": "Liverpool", "short_name": "LIV"},
    {"name": "Man City", "short_name": "MCI"},
    {"name": "Man Utd", "short_name": "MUN"},
    {"name": "Newcastle", "short_name": "NEW"},
    {"name": "Tottenham", "short_name": "TOT"},
]

print("📦 Adding teams...")
for team in teams:
    db.collection('teams').add(team)
    print(f"✅ Added {team['name']}")

# Players
players = [
    {"name": "Bukayo Saka", "team": "Arsenal", "position": "Midfielder", "price": 9.0, "goals": 12, "assists": 8},
    {"name": "Erling Haaland", "team": "Man City", "position": "Forward", "price": 14.0, "goals": 18, "assists": 3},
    {"name": "Mohamed Salah", "team": "Liverpool", "position": "Midfielder", "price": 12.5, "goals": 15, "assists": 10},
    {"name": "Cole Palmer", "team": "Chelsea", "position": "Midfielder", "price": 10.5, "goals": 14, "assists": 9},
    {"name": "Alexander Isak", "team": "Newcastle", "position": "Forward", "price": 8.5, "goals": 11, "assists": 2},
    {"name": "Son Heung-min", "team": "Tottenham", "position": "Midfielder", "price": 9.5, "goals": 10, "assists": 7},
    {"name": "Bruno Fernandes", "team": "Man Utd", "position": "Midfielder", "price": 8.0, "goals": 6, "assists": 8},
    {"name": "Ollie Watkins", "team": "Aston Villa", "position": "Forward", "price": 9.0, "goals": 13, "assists": 9},
    {"name": "David Raya", "team": "Arsenal", "position": "Goalkeeper", "price": 5.5, "goals": 0, "assists": 0},
    {"name": "Alisson Becker", "team": "Liverpool", "position": "Goalkeeper", "price": 5.5, "goals": 0, "assists": 0},
    {"name": "Virgil van Dijk", "team": "Liverpool", "position": "Defender", "price": 6.0, "goals": 2, "assists": 1},
    {"name": "William Saliba", "team": "Arsenal", "position": "Defender", "price": 5.5, "goals": 1, "assists": 0},
    {"name": "Trent Alexander-Arnold", "team": "Liverpool", "position": "Defender", "price": 7.5, "goals": 1, "assists": 6},
    {"name": "Ben White", "team": "Arsenal", "position": "Defender", "price": 5.5, "goals": 1, "assists": 3},
    {"name": "Phil Foden", "team": "Man City", "position": "Midfielder", "price": 8.5, "goals": 11, "assists": 7},
    {"name": "Dominic Solanke", "team": "Tottenham", "position": "Forward", "price": 7.5, "goals": 9, "assists": 4},
]

print("\n📦 Adding players...")
for player in players:
    player['total_points'] = 0
    player['selected_by'] = 0
    db.collection('players').add(player)
    print(f"✅ Added {player['name']}")

print("\n🎉 Database seeded successfully!")