import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import json
import asyncio

from leaderboard_cog import Leaderboard

#Game Choice Reactions
game_choices = ["🧢", "🎲"]

#Channels IDs
premier_queue_channel = 00000000000000000
championship_queue_channel = 00000000000000000
juniora_queue_channel = 00000000000000000
casual_queue_channel = 00000000000000000

class Make_teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_vote(self, queue, target_channel, active_games, votes, key):

        embed = discord.Embed(title=f'Queue has reached 6!')
        embed.set_footer(text=f'Lets gooooo', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        embed.color = 0x83ff00
        await target_channel.send(embed=embed)
        player_tag = " ".join(player.mention for player in queue)
        await target_channel.send(f"{player_tag}\nYou have **15 minutes** to decide on your game, otherwise it will be cancelled\nThe first choice to get to 4 votes will be played. You **cannot** take back a vote.")

        choice_embed = discord.Embed(title="Choose game!", color=0xffffff)
        choice_embed.add_field(name="Captains", value="🧢", inline=True)
        choice_embed.add_field(name="Random", value="🎲", inline=True)
        choice_embed.set_footer(text="Inspired by the Sauce", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        game_choice = await target_channel.send(embed=choice_embed)
        for emote in game_choices:
            await game_choice.add_reaction(emote)


        def check(reaction, user):
            if reaction.message == game_choice:
                if reaction.emoji in game_choices:
                    if user in queue and user not in votes["🧢"] and user not in votes["🎲"]:
                        votes[reaction.emoji].append(user)
                        if len(votes["🧢"]) >= 4:
                            return True
                        elif len(votes["🎲"]) >= 4:
                            return True
                        elif len(votes["🧢"]) == 3 and len(votes["🎲"]) == 3:
                            return True

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            queue.clear()
            await target_channel.send("Game has been cancelled")
            return
        else:
            await target_channel.send("Vote made")
            if len(votes["🧢"]) >= 4:
                votes["🧢"] = []
                votes["🎲"] = []
                return await self.captain_teams(queue, target_channel, active_games, key)
            elif len(votes["🎲"]) >= 4:
                votes["🧢"] = []
                votes["🎲"] = []
                return await self.random_teams(queue, target_channel, active_games)
            elif len(votes["🧢"]) == 3 and len(votes["🎲"]) == 3:
                votes["🧢"] = []
                votes["🎲"] = []
                await target_channel.send("Tied vote! Random teams it is")
                return await self.random_teams(queue, target_channel, active_games)


    async def random_teams(self, queue, target_channel, active_games):

        random.seed(time.time())
        team_one = random.sample(queue, 3)
        for player in team_one:
            queue.remove(player)
        team_two = random.sample(queue, 3)
        for player in team_two:
            queue.remove(player)

        queue.clear()
        return await self.show_teams(team_one, team_two, target_channel, active_games)

    async def captain_teams(self, queue, target_channel, active_games, key):

        cap_one, cap_two = await self.make_captains(queue, key)
        queue.remove(cap_one)
        queue.remove(cap_two)

        captains = [cap_one, cap_two]
        team_one = [cap_one]
        team_two = [cap_two]
        teams = [team_one, team_two]
        turn_index = 0

        cap_embed = discord.Embed(title=f"Pick your teams!", color=0x0099ff)
        cap_embed.add_field(name="Captain 1", value=cap_one.name)
        cap_embed.add_field(name="Captain 2", value=cap_two.name)
        for i in range(0, len(queue)):
            cap_embed.add_field(name=f"Player {i+1}", value=queue[i].name, inline=False)
        cap_embed.set_thumbnail(url=captains[turn_index].avatar_url)
        cap_embed.set_footer(text=f"{captains[turn_index].name}'s turn to choose", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        cap_choices = await target_channel.send(embed=cap_embed)

        numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        for n in numbers:
            await cap_choices.add_reaction(n)

        def check(reaction, user):
            if reaction.message == cap_choices and user == captains[turn_index]:
                if queue[numbers.index(reaction.emoji)] != None:
                    return True

        while len(team_one) != 3 or len(team_two) != 3:

            try:
                player = await self.bot.wait_for("reaction_add", timeout=10.0, check=check)
            except asyncio.TimeoutError:
                queue.clear()
                for i in range(0, 4):
                    cap_embed.set_field_at(index=(i+2), name=f"Player {i+1}", value="TIMED OUT", inline=False)
                    cap_embed.set_footer(text=f"{captains[turn_index].name} was too slow to choose", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await cap_choices.edit(embed=cap_embed)
                new_queue = discord.Embed(title=f'Queue has been reset.', color=0xff8b00)
                new_queue.set_footer(text=f"When's the next one?...", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await target_channel.send(embed=new_queue)
                return
            else:
                position = numbers.index(player[0].emoji)
                choice = queue[position]
                queue[position] = None
                teams[turn_index].append(choice)

                cap_embed.set_field_at(index=(position +2), name=f"Player {position+1}", value=f"~~*{choice.name}*~~", inline=False)

                turn_index = (turn_index+1) % 2
                cap_embed.set_thumbnail(url=captains[turn_index].avatar_url)
                cap_embed.set_footer(text=f"{captains[turn_index].name}'s turn to choose", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await cap_choices.edit(embed=cap_embed)

        for p in queue:
            if p != None:
                teams[turn_index].append(p)

        queue.clear()
        return await self.show_teams(team_one, team_two, target_channel, active_games)

    async def make_captains(self, queue, key):

        leaderboard = await l.get_leaderboard(key)

        players = list(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))

        cap_one = None
        cap_two = None
        for p in players:
            if p[0] in queue:
                if cap_one:
                    cap_two = p[0]
                    break
                else:
                    cap_one = p[0]

        if cap_one == None:
            cap_one = random.choice(queue)
        if cap_two == None:
            queue.remove(cap_one)
            cap_two = random.choice(queue)
            queue.append(cap_one)

        return cap_two, cap_one



    async def show_teams(self, team_one, team_two, target_channel, active_games):

        match_creator = random.choice(team_one)
        teams_embed = discord.Embed(title=f'The Teams!', color=0x83ff00)
        teams_embed.add_field(name="**-Team 1-**", value=f'{" ".join(player.name for player in team_one)}',inline=False)
        teams_embed.add_field(name="**-Team 2-**", value=f'{" ".join(player.name for player in team_two)}',inline=False)
        teams_embed.add_field(name="**Match Creator:**", value=f'{match_creator.name}',inline=False)
        teams_embed.set_footer(text=f'Powered by RLI', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        await target_channel.send(embed=teams_embed)

        
        user = "RLI" + str(random.randint(1, 1000))
        password = "RLI" + str(random.randint(1, 1000))
        teams_embed.add_field(name="**Username:**", value=user, inline=True)
        teams_embed.add_field(name="**Password:**", value=password, inline=True)

        for member in team_one:
            if member.bot == False:
                await member.send(embed=teams_embed)
        for member in team_two:
            if member.bot == False:
                await member.send(embed=teams_embed)

        #await ctx.send(embed=credentials)

        active_games[user] = team_one, team_two

        queue = []
        new_queue = discord.Embed(title=f'Queue has been reset.', color=0xff8b00)
        new_queue.set_footer(text=f"When's the next one?...", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        await target_channel.send(embed=new_queue)

        return active_games

def setup(bot):
    bot.add_cog(Make_teams(bot))
    bot.remove_command("help")
    global l
    l = Leaderboard(bot)