import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import json
import asyncio

from QueueHandler_cog import premier_active_games, championship_active_games, juniora_active_games, casual_active_games
from leaderboard_cog import premier_games_played, championship_games_played, juniora_games_played, casual_games_played, premier_wins, championship_wins, juniora_wins, casual_wins
from save_stats import save_wins, save_games

#Role IDs
premier_role = 00000000000000000
championship_role = 00000000000000000
juniora_role = 00000000000000000

win_channel = 00000000000000000

class Win_reporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def win(self, ctx, *args):
        
        if ctx.channel.id != win_channel:
            return

        tier = ""

        for i in range(0, len(ctx.author.roles)):
            if ctx.author.roles[i].id == premier_role and args[0] in premier_active_games.keys():
                active_games = premier_active_games
                games_played = premier_games_played
                wins = premier_wins
                files = ["premier_games_played.txt", "premier_wins.txt"]
                tier = "Premier"
                break
            elif ctx.author.roles[i].id == championship_role and args[0] in championship_active_games.keys():
                active_games = championship_active_games
                games_played = championship_games_played
                wins = championship_wins
                files = ["championship_games_played.txt", "championship_wins.txt"]
                tier = "Championship"
                break
            elif ctx.author.roles[i].id == juniora_role and args[0] in juniora_active_games.keys():
                active_games = juniora_active_games
                games_played = juniora_games_played
                wins = juniora_wins
                files = ["juniora_games_played.txt", "juniora_wins.txt"]
                tier = "Junior A"
                break
            elif args[0] in casual_active_games:
                active_games = casual_active_games
                games_played = casual_games_played
                wins = casual_wins
                files = ["casual_games_played.txt", "casual_wins.txt"]
                tier = "Casual"        
            elif i == len(ctx.author.roles)-1:
                await ctx.send("This game does not exist!")
                return


        if ctx.author in active_games[args[0]][0]:
            for player in active_games[args[0]][0] + active_games[args[0]][1]:
                if player in games_played:
                    games_played[player] += 1
                else:
                    games_played[player] = 1

            for player in active_games[args[0]][0]:
                if player in wins:
                    wins[player] += 1
                else:
                    wins[player] = 1

            await save_wins(wins, files[1])
            await save_games(games_played, files[0])
            # await broken(ctx)

            win_embed = discord.Embed(title=f"{tier} Game: {args[0]}", color=0x83ff00)
            win_embed.add_field(name="Winning Team", value = " ".join(player.name for player in active_games[args[0]][0]), inline=False)
            win_embed.add_field(name="Losing Team", value = " ".join(player.name for player in active_games[args[0]][1]), inline=False)
            win_embed.set_footer(text=f'Powered by RLI, for RLI', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
            await ctx.send(embed=win_embed)

            del active_games[args[0]]

        elif ctx.author in active_games[args[0]][1]:
            for player in active_games[args[0]][0] + active_games[args[0]][1]:
                if player in games_played:
                    games_played[player] += 1
                else:
                    games_played[player] = 1

            for player in active_games[args[0]][1]:
                if player in wins:
                    wins[player] += 1
                else:
                    wins[player] = 1

            await save_wins(wins, files[1])
            await save_games(games_played, files[0])

            win_embed = discord.Embed(title=f"{tier} Game {args[0]}", color=0x83ff00)
            win_embed.add_field(name="Winning Team", value = " ".join(player.name for player in active_games[args[0]][1]), inline=False)
            win_embed.add_field(name="Losing Team", value = " ".join(player.name for player in active_games[args[0]][0]), inline=False)
            win_embed.set_footer(text=f'Powered by RLI, for RLI', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
            await ctx.send(embed=win_embed)

            del active_games[args[0]]

        else:
            await ctx.send("You didn't play in this game")


def setup(bot):
    bot.add_cog(Win_reporting(bot))
    bot.remove_command("help")