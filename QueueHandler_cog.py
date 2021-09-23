import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import json
import asyncio

from make_teams_cog import Make_teams

#Dictionaries
premier_active_games = {}
championship_active_games = {}
juniora_active_games = {}
casual_active_games = {}

#Queues
premier_queue = []
championship_queue = []
juniora_queue = []
casual_queue = []

premier_votes = {"🧢":[], "🎲":[]}
championship_votes = {"🧢":[], "🎲":[]}
juniora_votes = {"🧢":[], "🎲":[]}
casual_votes = {"🧢":[], "🎲":[]}

#Game Choice Reactions
game_choices = ["🧢", "🎲"]

#Channels IDs
premier_queue_channel = 00000000000000000
championship_queue_channel = 00000000000000000
juniora_queue_channel = 00000000000000000
casual_queue_channel = 00000000000000000

premier_queue_logs = 00000000000000000
championship_queue_logs = 00000000000000000
juniora_queue_logs = 00000000000000000
casual_queue_logs = 00000000000000000

#Role IDs
premier_role = 00000000000000000
championship_role = 00000000000000000
juniora_role = 00000000000000000

leaderboard_spam = 00000000000000000

class QueueHandler(commands.Cog, name="Queue Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='q', aliases=['queue', "Q", "solo"], description='Allows a user to join the queue.')
    async def queue(self, ctx):

        player = ctx.author

        if ctx.channel.id == premier_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the premier queue at the same time")
                return
            await self.add_to_queue(ctx, premier_queue, premier_queue_channel, player, premier_active_games, premier_votes, "premier")

        elif ctx.channel.id == championship_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the championship queue at the same time")
                return
            await self.add_to_queue(ctx, championship_queue, championship_queue_channel, player, championship_active_games, championship_votes, "championship")

        elif ctx.channel.id == juniora_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the Junior A queue at the same time")
                return
            await self.add_to_queue(ctx, juniora_queue, juniora_queue_channel, player, juniora_active_games, juniora_votes, "juniora")

        elif ctx.channel.id == casual_queue_channel:
            if ctx.author in premier_queue or ctx.author in championship_queue or ctx.author in juniora_queue:
                await ctx.send("Sorry! you can't be in a tiered queue and the Casual queue at the same time")
                return
            await self.add_to_queue(ctx, casual_queue, casual_queue_channel, player, casual_active_games, casual_votes, "casual")

        else:
            return

    async def add_to_queue(self, ctx, queue, queue_channel, player, active_games, votes, key):

        if player in queue:
            await ctx.send(f'You are already in the queue!')
            return

        queue.append(player)
        target_channel = get(ctx.guild.channels, id=queue_channel)

        if len(queue) < 6:
            if len(queue) == 1:
                embed = discord.Embed(title=f'{len(queue)} player do be in the queue!')
                embed.set_footer(text='Inspired by JengaBenga', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
            else:   
                embed = discord.Embed(title=f'{len(queue)} players are in the queue!')
                embed.set_footer(text=f'{str(6-len(queue))} more needed!', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
            embed.color = 0xff8b00  
            embed.description = f'{player.mention} has joined the queue.'
            await target_channel.send(embed=embed)

        elif len(queue) == 6:

            new_queue = []
            for i in range(0, 6):
                new_queue.append(queue[i])
            queue.clear()

            active_games = await mt.create_vote(new_queue, target_channel, active_games, votes, key)


    @commands.command(name="leave",aliases=["leave_queue", "l", "Leave", "L"], description="Lets the user leave the queue.")
    async def leave(self, ctx):

        player = ctx.author
        
        if ctx.channel.id == premier_queue_channel:
            await self.leave_queue(ctx, premier_queue, premier_queue_channel, player)

        elif ctx.channel.id == championship_queue_channel:
            await self.leave_queue(ctx, championship_queue, championship_queue_channel, player)

        elif ctx.channel.id == juniora_queue_channel:
            await self.leave_queue(ctx, juniora_queue, juniora_queue_channel, player)

        elif ctx.channel.id == casual_queue_channel:
            await self.leave_queue(ctx, casual_queue, casual_queue_channel, player)
        
        else:
            return

    async def leave_queue(self, ctx, queue, queue_channel, player):

        if player not in queue:
            await ctx.send("You are not currently in the queue.")
        queue.remove(player)
        if len(queue) == 1:
            leave_embed = discord.Embed(title=f'{len(queue)} player do be in the queue')
            leave_embed.set_footer(text='Inspired by JengaBenga', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        else:
            leave_embed = discord.Embed(title=f'{len(queue)} players are in the queue')
            leave_embed.set_footer(text=f'{str(6-len(queue))} more needed!', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        leave_embed.description = f'{player.mention} has left the queue.'
        leave_embed.color = 0xffffff
        target_channel = get(ctx.guild.channels, id=queue_channel)
        await target_channel.send(embed=leave_embed)


    @commands.command(name="status", description="Displays current status of the queue.")
    async def status(self, ctx):
        
        if ctx.channel.id == premier_queue_channel:
            await self.show_status(ctx, premier_queue)

        elif ctx.channel.id == championship_queue_channel:
            await self.show_status(ctx, championship_queue)

        elif ctx.channel.id == juniora_queue_channel:
            await self.show_status(ctx, juniora_queue)

        elif ctx.channel.id == casual_queue_channel:
            await self.show_status(ctx, casual_queue)
        
        else:
            return
        
    async def show_status(self, ctx, queue):
        queue_embed = discord.Embed(title=f'{len(queue)} players are in the queue')
        queue_embed.description = (" ".join(player.mention for player in queue))
        queue_embed.color = 0xff8b00
        queue_embed.set_footer(text=f'{str(6-len(queue))} more needed!', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        await ctx.send(embed=queue_embed)


    @commands.command(name="remove", description="Removes a player from a queue", hidden=True)
    async def remove(self, ctx):

        players = ctx.message.mentions

        if ctx.channel.id == premier_queue_logs:
            for player in players:
                await self.leave_queue(ctx, premier_queue, premier_queue_channel, player)

        elif ctx.channel.id == championship_queue_logs:
            for player in players:
                await self.leave_queue(ctx, championship_queue, championship_queue_channel, player)

        elif ctx.channel.id == juniora_queue_logs:
            for player in players:
                await self.leave_queue(ctx, juniora_queue, juniora_queue_channel, player)

        elif ctx.channel.id == casual_queue_logs:
            for player in players:
                await self.leave_queue(ctx, casual_queue, casual_queue_channel, player)
        
        else:
            return

    @commands.command(hidden=True, name="add")
    async def add(self, ctx):
       
        players = ctx.message.mentions

        if ctx.channel.id == premier_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, premier_queue, premier_queue_channel, player, premier_active_games, premier_votes, "premier")

        elif ctx.channel.id == championship_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, championship_queue, championship_queue_channel, player, championship_active_games, championship_votes, "championship")

        elif ctx.channel.id == juniora_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, juniora_queue, juniora_queue_channel, player, juniora_active_games, juniora_votes, "juniora")

        elif ctx.channel.id == casual_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, casual_queue, casual_queue_channel, player, casual_active_games, casual_votes, "casual")
        else:
            return


    @commands.command()
    async def premier_all(self, ctx):

        member_percentage = {}
        member_points = {}
        i = 0

        with open("premier_games_played.txt", "r") as f:
            member_games = json.load(f)

        with open("premier_wins.txt", "r") as f:
            member_wins = json.load(f)

        for member in member_games.keys():
            print(member)
            if member in member_wins:
                member_percentage[member] = member_wins[member] / member_games[member]
                member_points[member] = (member_wins[member]*1.69) - (member_games[member] - member_wins[member])

            elif member not in member_wins:
                member_percentage[member] = 0
                await ctx.send(f"Exception!\n\n<@!{int(member)}>: {member_games[member]}, 0, 0 -- {-int(member_games[member])}")
                i += 1

        for k, v in sorted(member_points.items(), key=lambda item: item[1], reverse=True):
            await ctx.send(f"<@!{int(k)}>: {member_games[k]}, {member_wins[k]}, {round(member_percentage[k], 2)} -- {member_points[k]}\n")
            i += 1

        await ctx.send(f"{i} players")

    @commands.command()
    async def championship_all(self, ctx):

        member_percentage = {}
        member_points = {}
        i = 0

        with open("championship_games_played.txt", "r") as f:
            member_games = json.load(f)

        with open("championship_wins.txt", "r") as f:
            member_wins = json.load(f)

        for member in member_games.keys():
            print(member)
            if member in member_wins:
                member_percentage[member] = member_wins[member] / member_games[member]
                member_points[member] = (member_wins[member]*1.69) - (member_games[member] - member_wins[member])

            elif member not in member_wins:
                member_percentage[member] = 0
                await ctx.send(f"Exception!\n\n<@!{int(member)}>: {member_games[member]}, 0, 0 -- {-int(member_games[member])}")
                i += 1

        for k, v in sorted(member_points.items(), key=lambda item: item[1], reverse=True):
            await ctx.send(f"<@!{int(k)}>: {member_games[k]}, {member_wins[k]}, {round(member_percentage[k], 2)} -- {member_points[k]}\n")
            i += 1

        await ctx.send(f"{i} players")  

    @commands.command()
    async def force_random(self, ctx):
        for i in range(0, 3):
            premier_votes["🎲"].append(i)
    @commands.command()
    async def force_captains(self, ctx):
        for i in range(0, 3):
            premier_votes["🧢"].append(i)
            juniora_votes["🧢"].append(i)
    @commands.command()
    async def force_tie(self, ctx):
        for i in range(0, 3):
            if i % 2 == 0:
                premier_votes["🧢"].append(i)
            premier_votes["🎲"].append(i)

def setup(bot):
    bot.add_cog(QueueHandler(bot))
    bot.remove_command("help")
    global mt
    mt = Make_teams(bot)