import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import json
import asyncio
import gspread

#Dictionaries
premier_active_games = {}
championship_active_games = {}
elite_active_games = {}
casual_active_games = {}

premier_wins = {}
championship_wins = {}
elite_wins = {}
casual_wins = {}

premier_games_played = {}
championship_games_played = {}
elite_games_played = {}
casual_games_played = {}

#Queues
premier_queue = []
championship_queue = []
elite_queue = []
casual_queue = []

premier_queue_active = True
championship_queue_active = True
elite_queue_active = True
casual_queue_active = True

premier_votes = {"🧢":[], "🎲":[]}
championship_votes = {"🧢":[], "🎲":[]}
elite_votes = {"🧢":[], "🎲":[]}
casual_votes = {"🧢":[], "🎲":[]}

#Game Choice Reactions
game_choices = ["🧢", "🎲"]

#Channels IDs
premier_queue_channel = 0000000000000000000
championship_queue_channel = 0000000000000000000
elite_queue_channel = 0000000000000000000
casual_queue_channel = 0000000000000000000

premier_queue_logs = 0000000000000000000
championship_queue_logs = 0000000000000000000
elite_queue_logs = 0000000000000000000
casual_queue_logs = 0000000000000000000

#Role IDs
premier_role = 0000000000000000000
championship_role = 0000000000000000000
elite_role = 0000000000000000000

win_channel = 0000000000000000000
leaderboard_spam = 0000000000000000000

class QueueHandler(commands.Cog, name="Queue Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.queue_active = True

    @commands.command(name='q', aliases=['queue', "Q"], description='Allows a user to join the queue.')
    async def queue(self, ctx):

        player = ctx.author

        if ctx.channel.id == premier_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the premier queue at the same time")
                return
            await self.add_to_queue(ctx, premier_queue, premier_queue_channel, player, premier_queue_active, premier_active_games, premier_votes, premier_games_played, premier_wins)

        elif ctx.channel.id == championship_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the championship queue at the same time")
                return
            await self.add_to_queue(ctx, championship_queue, championship_queue_channel, player, championship_queue_active, championship_active_games, championship_votes, championship_games_played, championship_wins)

        elif ctx.channel.id == elite_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the Junior A queue at the same time")
                return
            await self.add_to_queue(ctx, elite_queue, elite_queue_channel, player, elite_queue_active, elite_active_games, elite_votes, elite_games_played, elite_wins)

        elif ctx.channel.id == casual_queue_channel:
            if ctx.author in premier_queue or ctx.author in championship_queue or ctx.author in elite_queue:
                await ctx.send("Sorry! you can't be in a tiered queue and the Casual queue at the same time")
                return
            await self.add_to_queue(ctx, casual_queue, casual_queue_channel, player, casual_queue_active, casual_active_games, casual_votes, casual_games_played, casual_wins)

        else:
            return

    async def add_to_queue(self, ctx, queue, queue_channel, player, queue_active, active_games, votes, games, wins):

        if queue_active:

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

                queue_active = False

                new_queue = []
                for i in range(0, 6):
                    new_queue.append(queue[i])
                queue.clear()

                embed = discord.Embed(title=f'Queue has reached 6!')
                embed.set_footer(text=f'Lets gooooo', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                embed.color = 0x83ff00
                await target_channel.send(embed=embed)
                player_tag = " ".join(player.mention for player in new_queue)
                await target_channel.send(f"{player_tag}\nYou have **10 minutes** to decide on your game, otherwise it will be cancelled\nThe first choice to get to 4 votes will be played. You **cannot** take back a vote.")

                choice_embed = discord.Embed(title="Choose game!", color=0xffffff)
                choice_embed.add_field(name="Captains", value="🧢", inline=True)
                choice_embed.add_field(name="Random", value="🎲", inline=True)
                choice_embed.set_footer(text="Inspired by the Sauce", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                game_choice = await target_channel.send(embed=choice_embed)
                for emote in game_choices:
                    await game_choice.add_reaction(emote)


                def check(reaction, user):
                    if reaction.message == game_choice:
                        if reaction.emoji in game_choices and user in new_queue and user not in votes[reaction.emoji]:
                            votes[reaction.emoji].append(user)
                            if len(votes["🧢"]) >= 4:
                                return True
                            elif len(votes["🎲"]) >= 4:
                                return True
                            elif len(votes["🧢"]) == 3 and len(votes["🎲"]) == 3:
                                return True

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=900.0, check=check)
                except asyncio.TimeoutError:
                    new_queue.clear()
                    await target_channel.send("Game has been cancelled")
                    return
                else:
                    await target_channel.send("Vote made")
                    if len(votes["🧢"]) >= 4:
                        votes["🧢"] = []
                        votes["🎲"] = []
                        await self.captain_teams(new_queue, target_channel, queue_active, active_games, games, wins)
                    elif len(votes["🎲"]) >= 4:
                        votes["🧢"] = []
                        votes["🎲"] = []
                        await self.random_teams(new_queue, target_channel, queue_active, active_games)
                    elif len(votes["🧢"]) == 3 and len(votes["🎲"]) == 3:
                        votes["🧢"] = []
                        votes["🎲"] = []
                        await target_channel.send("Tied vote! Random teams it is")
                        await self.random_teams(new_queue, target_channel, queue_active, active_games)
        else:
            return

    async def random_teams(self, queue, target_channel, queue_active, active_games):

        random.seed(time.time())
        team_one = random.sample(queue, 3)
        for player in team_one:
            queue.remove(player)
        team_two = random.sample(queue, 3)
        for player in team_two:
            queue.remove(player)

        queue.clear()
        await self.show_teams(team_one, team_two, target_channel, active_games, queue_active)

    async def captain_teams(self, queue, target_channel, queue_active, active_games, games, wins):

        cap_one, cap_two = self.make_captains(queue, games, wins)
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
                player = await self.bot.wait_for("reaction_add", timeout=600.0, check=check)
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

                cap_embed.set_field_at(index=(position +2), name=f"Player {position+1}", value="TAKEN", inline=False)

                turn_index = (turn_index+1) % 2
                cap_embed.set_thumbnail(url=captains[turn_index].avatar_url)
                cap_embed.set_footer(text=f"{captains[turn_index].name}'s turn to choose", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await cap_choices.edit(embed=cap_embed)

        for p in queue:
            if p != None:
                teams[turn_index].append(p)

        queue.clear()
        await self.show_teams(team_one, team_two, target_channel, active_games, queue_active)

    def make_captains(self, queue, games, wins):

        points = {}

        for player in queue:
            if player in wins:
                points[player] = (wins[player]*1.42) - (games[player] - wins[player])
            elif player in games:
                points[player] = 0-(games[player])
            else:
                points[player] = 0

        captains = list(sorted(points.items(), key=lambda item: item[1], reverse=True))
        cap_one = captains[0][0]
        cap_two = captains[1][0]
        return cap_two, cap_one



    async def show_teams(self, team_one, team_two, target_channel, active_games, queue_active):

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
                try:
                    await member.send(embed=teams_embed)
                except:
                    print("Could not dm")
        for member in team_two:
            if member.bot == False:
                try:
                    await member.send(embed=teams_embed)
                except:
                    print("Could not dm")

        #await ctx.send(embed=credentials)

        active_games[user] = team_one, team_two

        queue = []
        new_queue = discord.Embed(title=f'Queue has been reset.', color=0xff8b00)
        new_queue.set_footer(text=f"When's the next one?...", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        await target_channel.send(embed=new_queue)

        queue_active = True


    @commands.command(name="leave",aliases=["leave_queue", "l", "Leave", "L"], description="Lets the user leave the queue.")
    async def leave(self, ctx):

        player = ctx.author
        
        if ctx.channel.id == premier_queue_channel:
            await self.leave_queue(ctx, premier_queue, premier_queue_channel, player)

        elif ctx.channel.id == championship_queue_channel:
            await self.leave_queue(ctx, championship_queue, championship_queue_channel, player)

        elif ctx.channel.id == elite_queue_channel:
            await self.leave_queue(ctx, elite_queue, elite_queue_channel, player)

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

        elif ctx.channel.id == elite_queue_channel:
            await self.show_status(ctx, elite_queue)

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

        elif ctx.channel.id == elite_queue_logs:
            for player in players:
                await self.leave_queue(ctx, elite_queue, elite_queue_channel, player)

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
                await self.add_to_queue(ctx, premier_queue, premier_queue_channel, player, premier_queue_active, premier_active_games, premier_votes, premier_games_played, premier_wins)

        elif ctx.channel.id == championship_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, championship_queue, championship_queue_channel, player, championship_queue_active, championship_active_games, championship_votes, championship_games_played, championship_wins)

        elif ctx.channel.id == elite_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, elite_queue, elite_queue_channel, player, elite_queue_active, elite_active_games, elite_votes, elite_games_played, elite_wins)

        elif ctx.channel.id == casual_queue_logs:
            for player in players:
                await self.add_to_queue(ctx, casual_queue, casual_queue_channel, player, casual_queue_active, casual_active_games, casual_votes, casual_games_played, casual_wins)
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

        elif ctx.channel.id == elite_queue_logs:
            tier = "Elite"
            for player in players:
                await self.add_wins(ctx, player, args, elite_games_played, elite_wins, tier)

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

        await self.save_wins(wins, tier)
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

        elif ctx.channel.id == elite_queue_logs:
            tier = "Elite"
            for player in players:
                await self.add_games(ctx, player, args, elite_games_played, elite_wins, tier)

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

        await self.save_games(games_played, tier)
        await ctx.send(f"{player.name} has played {args[-1]} extra game(s)")


    @commands.command(name="win", description="Allows player to report win.")
    async def win(self, ctx, *args):
        
        if ctx.channel.id != win_channel:
            return

        tier = ""

        for i in range(0, len(ctx.author.roles)):
            if ctx.author.roles[i].id == premier_role and args[0] in premier_active_games.keys():
                active_games = premier_active_games
                games_played = premier_games_played
                wins = premier_wins
                tier = "Premier"
                break
            elif ctx.author.roles[i].id == championship_role and args[0] in championship_active_games.keys():
                active_games = championship_active_games
                games_played = championship_games_played
                wins = championship_wins
                tier = "Championship"
                break
            elif ctx.author.roles[i].id == elite_role and args[0] in elite_active_games.keys():
                active_games = elite_active_games
                games_played = elite_games_played
                wins = elite_wins
                tier = "Elite"
                break
            elif args[0] in casual_active_games:
                active_games = casual_active_games
                games_played = casual_games_played
                wins = casual_wins
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

            await self.save_wins(wins, tier)
            await self.save_games(games_played, tier)

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

            await self.save_wins(wins, tier)
            await self.save_games(games_played, tier)

            win_embed = discord.Embed(title=f"{tier} Game {args[0]}", color=0x83ff00)
            win_embed.add_field(name="Winning Team", value = " ".join(player.name for player in active_games[args[0]][1]), inline=False)
            win_embed.add_field(name="Losing Team", value = " ".join(player.name for player in active_games[args[0]][0]), inline=False)
            win_embed.set_footer(text=f'Powered by RLI, for RLI', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
            await ctx.send(embed=win_embed)

            del active_games[args[0]]

        else:
            await ctx.send("You didn't play in this game")

    @commands.command(name="leaderboard", aliases=["lb"])
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

            elif role.id == elite_role:
                await self.show_leaderboard(ctx, elite_wins, elite_games_played, "Elite")
                return

        await ctx.send("You aren't in a 6mans tier yet, try **>casual_leaderboard**")
        return


    @commands.command(name="casual_leaderboard", description="Shows the leaderboard")
    async def casual_leaderboard(self, ctx):

        if ctx.channel.id != leaderboard_spam:
            return

        await self.show_leaderboard(ctx, casual_wins, casual_games_played, "Casual")

    async def show_leaderboard(self, ctx, wins, games, title):

        leaderboard = {}
        for k, v in games.items():
            if k in wins.keys():
                leaderboard[k] = (wins[k]*1.42) - (v-wins[k])
            else:
                leaderboard[k] = -v

        leaderboard_embed = discord.Embed(title=f"{title} Leaderboard",color=0x83ff00)
        i=1
        for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
            leaderboard_embed.add_field(name=f"{i}:", value=f'{k.name}: {v:.2f}',inline=False)
            i+=1
        await ctx.send(embed=leaderboard_embed)

    @commands.command(name="rlb", aliases=["dogs"])
    async def rlb(self, ctx):

        if ctx.channel.id == premier_queue_logs:
            await self.reverse_leaderboard(ctx, premier_wins, premier_games_played, "Premier")
            return

        elif ctx.channel.id == championship_queue_logs:
            await self.reverse_leaderboard(ctx, championship_wins, championship_games_played, "Championship")
            return

        elif ctx.channel.id != leaderboard_spam:
            return

        for role in ctx.author.roles:
            if role.id == premier_role:
                await self.reverse_leaderboard(ctx, premier_wins, premier_games_played, "Premier")
                return

            elif role.id == championship_role:
                await self.reverse_leaderboard(ctx, championship_wins, championship_games_played, "Championship")
                return

            elif role.id == elite_role:
                await self.reverse_leaderboard(ctx, elite_wins, elite_games_played, "Elite")
                return

        await ctx.send("You aren't in a 6mans tier yet, try **>casual_leaderboard**")
        return

    async def reverse_leaderboard(self, ctx, wins, games, title):

        leaderboard = {}
        for k, v in games.items():
            if k in wins.keys():
                leaderboard[k] = (wins[k]*1.42) - (v-wins[k])
            else:
                leaderboard[k] = -v

        leaderboard_embed = discord.Embed(title=f"Reverse {title} Leaderboard",color=0x83ff00)
        i=len(leaderboard)
        for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=False):
            leaderboard_embed.add_field(name=f"{i}:", value=f'{k.name}: {v:.2f}',inline=False)
            i-=1
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

                elif role.id == elite_role:
                    await self.show_stats(ctx, ctx.message.author, elite_games_played, elite_wins, "Elite")
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

                elif role.id == elite_role:
                    await self.show_stats(ctx, ctx.message.mentions[0], elite_games_played, elite_wins, "Elite")
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
        leaderboard = {}

        for player, v in games_played.items():
            
            if player in wins.keys():
                leaderboard[player] = (wins[player]*1.42) - (v-wins[player])
            else:
                leaderboard[player] = -v

            if player == member:
                gp = v

                if player in wins.keys():
                    w = wins[player]

                p = leaderboard[player]

        i = 1
        for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
            if k == member:
                pos = i
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

    async def save_wins(self, wins, tier):

        if tier == "Premier":
            wins = premier_wins
            filename = "premier_wins.txt"

        elif tier == "Championship":
            wins = championship_wins
            filename = "championship_wins.txt"

        elif tier == "Elite":
            wins = elite_wins
            filename = "elite_wins.txt"

        elif tier == "Casual":
            wins = casual_wins
            filename = "casual_wins.txt"

        member_id_dict = {}
        for member in wins:
            member_id_dict[member.id] = wins[member]

        with open(filename, "w") as f:
            json.dump(member_id_dict, f)
        print(f"{tier} wins saved")

    async def save_games(self, games_played, tier):

        if tier == "Premier":
            games_played = premier_games_played
            filename = "premier_games_played.txt"

        elif tier == "Championship":
            games_played = championship_games_played
            filename = "championship_games_played.txt"

        elif tier == "Elite":
            games_played = elite_games_played
            filename = "elite_games_played.txt"

        elif tier == "Casual":
            games_played = casual_games_played
            filename = "casual_games_played.txt"

        member_id_dict = {}
        for member in games_played:
            member_id_dict[member.id] = games_played[member]

        with open(filename, "w") as f:
            json.dump(member_id_dict, f)
        print(f"{tier} games saved")

    @commands.command(name="load_wins")
    async def load_wins(self, ctx):
        global premier_wins
        global championship_wins
        global elite_wins
        global everyone_wins

        member_id_dict = {}

        filenames = ["premier_wins.txt", "championship_wins.txt", "elite_wins.txt", "casual_wins.txt"]
        dictionaries = [premier_wins, championship_wins, elite_wins, casual_wins]

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

    @commands.command(name="load_games")
    async def load_games(self, ctx):
        global premier_games_played
        global championship_games_played
        global elite_games_played
        global everyone_games_played

        member_id_dict = {}

        filenames = ["premier_games_played.txt", "championship_games_played.txt", "elite_games_played.txt", "casual_games_played.txt"]
        dictionaries = [premier_games_played, championship_games_played, elite_games_played, casual_games_played]

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


    @commands.command()
    async def publish_leaderboard(self, ctx):

        gc = gspread.service_account(filename="PATH TO LOCAL FILE")

        if ctx.channel.id == 00000000000000000000:
            sh = gc.open("RLI-6mans").worksheet("Premier")
            i = 3
            for player in premier_games_played:

                if player in premier_wins:
                    player_points = (premier_wins[player]*1.42) - (premier_games_played[player] - premier_wins[player])
                    player_wins = premier_wins[player]
                else:
                    player_points = 0 - premier_games_played[player]
                    player_wins = 0

                sh.update_acell(f"B{i}", str(player.name))
                sh.update_acell(f"C{i}", str(premier_games_played[player]))
                sh.update_acell(f"D{i}", str(player_wins))
                sh.update_acell(f"F{i}", str(player_points))
                i += 1
                time.sleep(5)


            sh = gc.open("RLI-6mans").worksheet("Championship")
            i = 3
            for player in championship_games_played:

                if player in championship_wins:
                    player_points = (championship_wins[player]*1.42) - (championship_games_played[player] - championship_wins[player])
                    player_wins = championship_wins[player]
                else:
                    player_points = 0 - championship_games_played[player]
                    player_wins = 0

                sh.update_acell(f"B{i}", str(player.name))
                sh.update_acell(f"C{i}", str(championship_games_played[player]))
                sh.update_acell(f"D{i}", str(player_wins))
                sh.update_acell(f"F{i}", str(player_points))
                i += 1
                time.sleep(5)

            sh = gc.open("RLI-6mans").worksheet("Elite")
            i = 3
            for player in elite_games_played:

                if player in elite_wins:
                    player_points = (elite_wins[player]*1.42) - (elite_games_played[player] - elite_wins[player])
                    player_wins = elite_wins[player]
                else:
                    player_points = 0 - elite_games_played[player]
                    player_wins = 0

                sh.update_acell(f"B{i}", str(player.name))
                sh.update_acell(f"C{i}", str(elite_games_played[player]))
                sh.update_acell(f"D{i}", str(player_wins))
                sh.update_acell(f"F{i}", str(player_points))
                i += 1
                time.sleep(5)

            await ctx.send("Leaderboards posted to <LINK TO PUBLIC GOOGLE SPREADSHEET>")


def setup(bot):
    bot.add_cog(QueueHandler(bot))
    bot.remove_command("help")