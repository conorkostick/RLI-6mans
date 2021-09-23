import json

async def save_wins(wins, filename):

    member_id_dict = {}
    for member in wins:
        member_id_dict[member.id] = wins[member]

    with open(filename, "w") as f:
        json.dump(member_id_dict, f)
    print(f"{filename} saved")

async def save_games(games_played, filename):

    member_id_dict = {}
    for member in games_played:
        member_id_dict[member.id] = games_played[member]

    with open(filename, "w") as f:
        json.dump(member_id_dict, f)
    print(f"{filename} saved")