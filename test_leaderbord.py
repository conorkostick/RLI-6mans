import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import json
import asyncio

from save_stats import save_wins, save_games

#Dictionaries
premier_wins = {}
championship_wins = {}
juniora_wins = {}
casual_wins = {}

premier_games_played = {}
championship_games_played = {}
juniora_games_played = {}
casual_games_played = {}

#Role IDs
premier_role = 00000000000000000
championship_role = 00000000000000000
juniora_role = 00000000000000000

#Channel IDs
leaderboard_spam = 00000000000000000

premier_queue_logs = 00000000000000000
championship_queue_logs = 00000000000000000
juniora_queue_logs = 00000000000000000
casual_queue_logs = 00000000000000000

#Private channel
shed_channel = 00000000000000000

class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def make_leaderboard(self, games, wins):

        leaderboard = {}
        for k, v in games.items():
            if k in wins.keys():
                leaderboard[k] = (wins[k]*1.69) - (v-wins[k])
            else:
                leaderboard[k] = -v

        return leaderboard

    async def get_leaderboard(self, key):
        if key == "premier":
            leaderboard = await self.make_leaderboard(premier_games_played, premier_wins)
            return leaderboard
        elif key == "championship":
            leaderboard = await self.make_leaderboard(championship_games_played, championship_wins)
            return leaderboard
        elif key == "juniora":
            leaderboard = await self.make_leaderboard(juniora_games_played, juniora_wins)
            return leaderboard
        elif key == "casual":
            leaderboard = await self.make_leaderboard(casual_games_played, casual_wins)
            return leaderboard


    @commands.command(name="test_leaderboard")
    async def test_leaderboard(self, ctx):

        premier_leaderboard = await sorted(self.make_leaderboard(premier_games_played, premier_wins).items(), key=lambda item: item[1], reverse=True)
        championship_leaderboard = await sorted(self.make_leaderboard(championship_games_played, championship_wins).items(), key=lambda item: item[1], reverse=True)
        juniora_leaderboard = await sorted(self.make_leaderboard(juniora_games_played, juniora_wins).items(), key=lambda item: item[1], reverse=True)
        casual_leaderboard = await sorted(self.make_leaderboard(casual_games_played, casual_wins).items(), key=lambda item: item[1], reverse=True)

        leaderboard_embed = discord.Embed(title=f"Premier Leaderboard",color=0x83ff00)
        leaderboard_embed.add_field(name=f"1:", value=f'{premier_leaderboard[0][0]}: {premier_leaderboard[0][1]:.2f}',inline=False)
        leaderboard_embed.add_field(name=f"1:", value=f'{premier_leaderboard[1][0]}: {premier_leaderboard[1][1]:.2f}',inline=False)
        await ctx.send(embed=leaderboard_embed)

        start = 2
        end = 3

        try:
            await self.bot,wait_for("reaction_add", timeout=300.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            return


    async def show_leaderboard(self, ctx, wins, games, title):

        leaderboard = await self.make_leaderboard(games, wins)

        leaderboard_embed = discord.Embed(title=f"{title} Leaderboard",color=0x83ff00)
        i=1
        for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
            leaderboard_embed.add_field(name=f"{i}:", value=f'{k.name}: {v:.2f}',inline=False)
            i+=1
        await ctx.send(embed=leaderboard_embed)


    @commands.command(name="load_test_stats")
    async def load_test_stats(self, ctx):

        if ctx.channel.id == shed_channel:

            global premier_wins
            global championship_wins
            global juniora_wins
            global everyone_wins

            member_id_dict = {}

            filenames = ["premier_wins.txt", "championship_wins.txt", "juniora_wins.txt", "casual_wins.txt"]
            dictionaries = [premier_wins, championship_wins, juniora_wins, casual_wins]

            for i in range(0, len(filenames)):
                with open(filenames[i], "r") as f:
                    try:
                        member_id_dict = json.load(f)
                    except:
                        print("Empty Text File")

                dictionary = dictionaries[i]
                for id in member_id_dict:
                    member = ctx.guild.get_member(int(id))
                    if type(member) is discord.Member:
                        dictionary[member] = member_id_dict[id]
                    else:
                        print("Potential NoneType found")

                print(f"{filenames[i]} loaded")
            await ctx.send("Wins loaded")

            global premier_games_played
            global championship_games_played
            global juniora_games_played
            global everyone_games_played

            member_id_dict = {}

            filenames = ["premier_games_played.txt", "championship_games_played.txt", "juniora_games_played.txt", "casual_games_played.txt"]
            dictionaries = [premier_games_played, championship_games_played, juniora_games_played, casual_games_played]

            for i in range(0, len(filenames)):
                with open(filenames[i], "r") as f:
                    try:
                        member_id_dict = json.load(f)
                    except:
                        print("Empty Text File")

                dictionary = dictionaries[i]
                for id in member_id_dict:
                    member = ctx.guild.get_member(int(id))
                    if type(member) is discord.Member:
                        dictionary[member] = member_id_dict[id]
                    else:
                        print("Potential NoneType found")

                print(f"{filenames[i]} loaded")
            await ctx.send("Games loaded")

        else:
            return


def setup(bot):
    bot.add_cog(Leaderboard(bot))
    bot.remove_command("help")