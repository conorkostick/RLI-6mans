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
shed_channel = 000000000000000000

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


    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):

        if ctx.channel.id == premier_queue_logs:
            await self.show_leaderboard(ctx, premier_wins, premier_games_played, "Premier")
            return

        elif ctx.channel.id == championship_queue_logs:
            await self.show_leaderboard(ctx, championship_wins, championship_games_played, "Championship")
            return

        elif ctx.channel.id != leaderboard_spam:
            return

        for role in ctx.author.roles:
            if role.id == premier_role:
                await self.show_leaderboard(ctx, premier_wins, premier_games_played, "Premier")
                return

            elif role.id == championship_role:
                await self.show_leaderboard(ctx, championship_wins, championship_games_played, "Championship")
                return

            elif role.id == juniora_role:
                await self.show_leaderboard(ctx, juniora_wins, juniora_games_played, "Junior A")
                return

        await ctx.send("You aren't in a 6mans tier yet, try **>casual_leaderboard**")
        return


    @commands.command(name="casual_leaderboard", description="Shows the leaderboard")
    async def casual_leaderboard(self, ctx):

        if ctx.channel.id != leaderboard_spam:
            return

        await self.show_leaderboard(ctx, casual_wins, casual_games_played, "Casual")

    async def show_leaderboard(self, ctx, wins, games, title):

        leaderboard = await self.make_leaderboard(games, wins)

        leaderboard_embed = discord.Embed(title=f"{title} Leaderboard",color=0x83ff00)
        i=1
        for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
            leaderboard_embed.add_field(name=f"{i}:", value=f'{k.name}: {v:.2f}',inline=False)
            i+=1
        await ctx.send(embed=leaderboard_embed)



    @commands.command(name="stats")
    async def stats(self, ctx, *args):

        if ctx.channel.id != leaderboard_spam:
            return

        if not ctx.message.mentions:
            for role in ctx.author.roles:
                if role.id == premier_role:
                    await self.show_stats(ctx, ctx.message.author, premier_games_played, premier_wins, "Premier")
                    return

                elif role.id == championship_role:
                    await self.show_stats(ctx, ctx.message.author, championship_games_played, championship_wins, "Championship")
                    return

                elif role.id == juniora_role:
                    await self.show_stats(ctx, ctx.message.author, juniora_games_played, juniora_wins, "Junior A")
                    return

            await ctx.send("You aren't in a 6mans tier yet, try **>casual_stats**")
            return

        elif ctx.message.mentions:
            for role in ctx.message.mentions[0].roles:
                if role.id == premier_role:
                    await self.show_stats(ctx, ctx.message.mentions[0], premier_games_played, premier_wins, "Premier")
                    return

                elif role.id == championship_role:
                    await self.show_stats(ctx, ctx.message.mentions[0], championship_games_played, championship_wins, "Championship")
                    return

                elif role.id == juniora_role:
                    await self.show_stats(ctx, ctx.message.mentions[0], juniora_games_played, juniora_wins, "Junior A")
                    return

            await ctx.send("You aren't in a 6mans tier yet, try **>casual_stats**")
            return

    @commands.command(name="casual_stats", description="Shows the leaderboard")
    async def casual_stats(self, ctx, *args):

        if ctx.channel.id != leaderboard_spam:
            return

        if not ctx.message.mentions:
            await self.show_stats(ctx, ctx.message.author, casual_games_played, casual_wins, "Casual")

        elif ctx.message.mentions:
            await self.show_stats(ctx, ctx.message.mentions[0], casual_games_played, casual_wins, "Casual")

    async def show_stats(self, ctx, member, games_played, wins, title):

        gp = 0
        w = 0
        p = 0
        leaderboard = await self.make_leaderboard(games_played, wins)

        for player, v in games_played.items():

            if player == member:
                gp = v

                if player in wins.keys():
                    w = wins[player]

                p = leaderboard[player]

        i = 1
        for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
            if k == member:
                pos = i
                break
            i += 1

        player_embed = discord.Embed(title=f"{member.name}'s {title} Stats", color=member.color)

        player_embed.add_field(name="Games Played:", value=f"{gp}")
        player_embed.add_field(name="Wins:", value=f"{w}")
        player_embed.add_field(name="Losses:", value=f"{gp - w}")
        player_embed.add_field(name="Points:", value=f"{p:.2f}")
        if gp == 0:
            player_embed.add_field(name="Win Percentage:", value=f"0%")
            player_embed.add_field(name="Leaderboard Pos:", value="0/0")
        else:
            player_embed.add_field(name="Win Percentage:", value=f"{(w/gp)*100:.2f}%")
            player_embed.add_field(name="Leaderboard Pos:", value=f"{pos}/{len(leaderboard)}")

        await ctx.send(embed=player_embed)

    @commands.command(name="load_stats")
    async def load_stats(self, ctx):

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


    @commands.command(hidden=True, name="add_win")
    async def add_win(self, ctx, *args):
       
        players = ctx.message.mentions

        if ctx.channel.id == premier_queue_logs:
            tier = "Premier"
            for player in players:
                await self.add_wins(ctx, player, args, premier_games_played, premier_wins, tier)

        elif ctx.channel.id == championship_queue_logs:
            tier = "Championship"
            for player in players:
                await self.add_wins(ctx, player, args, championship_games_played, championship_wins, tier)

        elif ctx.channel.id == juniora_queue_logs:
            tier = "Junior A"
            for player in players:
                await self.add_wins(ctx, player, args, juniora_games_played, juniora_wins, tier)

        elif ctx.channel.id == casual_queue_logs:
            tier = "Casual"
            for player in players:
                await self.add_wins(ctx, player, args, casual_games_played, casual_wins, tier)

        else:
            return

    async def add_wins(self, ctx, player, args, games_played, wins, tier):

        if player in games_played.keys():
            if player in wins.keys():
                wins[player] += int(args[-1])

            elif player not in wins.keys():
                wins[player] = int(args[-1])

        await save_wins(wins, tier)
        await ctx.send(f"{player.name} has been given {args[-1]} win(s)")

    @commands.command(hidden=True, name="add_game")
    async def add_game(self, ctx, *args):
       
        players = ctx.message.mentions

        if ctx.channel.id == premier_queue_logs:
            tier = "Premier"
            for player in players:
                await self.add_games(ctx, player, args, premier_games_played, premier_wins, tier)

        elif ctx.channel.id == championship_queue_logs:
            tier = "Championship"
            for player in players:
                await self.add_games(ctx, player, args, championship_games_played, championship_wins, tier)

        elif ctx.channel.id == juniora_queue_logs:
            tier = "Junior A"
            for player in players:
                await self.add_games(ctx, player, args, juniora_games_played, juniora_wins, tier)

        elif ctx.channel.id == casual_queue_logs:
            tier = "Casual"
            for player in players:
                await self.add_games(ctx, player, args, casual_games_played, casual_wins, tier)

        else:
            return

    async def add_games(self, ctx, player, args, games_played, wins, tier):

        if player in games_played.keys():
            games_played[player] += int(args[-1])

        elif player not in games_played.keys():
            games_played[player] = int(args[-1])

        await save_games(games_played, tier)
        await ctx.send(f"{player.name} has played {args[-1]} extra game(s)")


def setup(bot):
    bot.add_cog(Leaderboard(bot))
    bot.remove_command("help")