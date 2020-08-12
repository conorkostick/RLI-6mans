import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import json

#Dictionaries
senior_active_games = {}
intermediate_active_games = {}
juniora_active_games = {}
casual_active_games = {}

senior_wins = {}
intermediate_wins = {}
juniora_wins = {}
casual_wins = {}

senior_games_played = {}
intermediate_games_played = {}
juniora_games_played = {}
casual_games_played = {}

#Queues
senior_queue = []
intermediate_queue = []
juniora_queue = []
casual_queue = []

senior_queue_active = True
intermediate_queue_active = True
juniora_queue_active = True
casual_queue_active = True

#Channels IDs
senior_queue_channel = XXXXXXXXXXXXX
intermediate_queue_channel = XXXXXXXXXXXXX
juniora_queue_channel = XXXXXXXXXXXXX
casual_queue_channel = XXXXXXXXXXXXX

senior_queue_logs = XXXXXXXXXXXXX
intermediate_queue_logs = XXXXXXXXXXXXX
juniora_queue_logs = XXXXXXXXXXXXX
casual_queue_logs = XXXXXXXXXXXXX

#Role IDs
senior_role = XXXXXXXXXXXXX
intermediate_role = XXXXXXXXXXXXX
juniora_role = XXXXXXXXXXXXX

win_channel = XXXXXXXXXXXXX
leaderboard_spam = XXXXXXXXXXXXX

class QueueHandler(commands.Cog, name="Queue Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.queue_active = True

    @commands.command(name='q', aliases=['queue'], description='Allows a user to join the queue.')
    async def queue(self, ctx):

        player = ctx.author

        if ctx.channel.id == senior_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the Senior queue at the same time")
                return
            await self.add_to_queue(ctx, senior_queue, senior_queue_channel, player, senior_queue_active, senior_active_games)

        elif ctx.channel.id == intermediate_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the Intermediate queue at the same time")
                return
            await self.add_to_queue(ctx, intermediate_queue, intermediate_queue_channel, player, intermediate_queue_active, intermediate_active_games)

        elif ctx.channel.id == juniora_queue_channel:
            if ctx.author in casual_queue:
                await ctx.send("Sorry! you can't be in the Casual queue and the Junior A queue at the same time")
                return
            await self.add_to_queue(ctx, juniora_queue, juniora_queue_channel, player, juniora_queue_active, juniora_active_games)

        elif ctx.channel.id == casual_queue_channel:
            if ctx.author in senior_queue or ctx.author in intermediate_queue or ctx.author in juniora_queue:
                await ctx.send("Sorry! you can't be in a tiered queue and the Casual queue at the same time")
                return
            await self.add_to_queue(ctx, casual_queue, casual_queue_channel, player, casual_queue_active, casual_active_games)

        else:
            return

    async def add_to_queue(self, ctx, queue, queue_channel, player, queue_active, active_games):

        if queue_active:

            if player in queue:
                await ctx.send(f'You are already in the queue!')
                return

            queue.append(player)
            target_channel = get(ctx.guild.channels, id=queue_channel)

            if len(queue) < 6:
                if len(queue) == 1:
                    embed = discord.Embed(title=f'{len(queue)} player is in the queue!') 
                else:   
                    embed = discord.Embed(title=f'{len(queue)} players are in the queue!')
                embed.color = 0xff8b00  
                embed.description = f'{player.mention} has joined the queue.'
                embed.set_footer(text=f'{str(6-len(queue))} more needed!', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await target_channel.send(embed=embed)

            elif len(queue) == 6:

                queue_active = False

                embed = discord.Embed(title=f'Queue has reached 6!')
                embed.set_footer(text=f'Lets gooooo', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                embed.color = 0x83ff00
                await target_channel.send(embed=embed)
                await target_channel.send(" ".join(player.mention for player in queue))

                match_creator = random.sample(queue, 1)
                team_one = random.sample(queue, 3)
                for player in team_one:
                    queue.remove(player)
                team_two = random.sample(queue, 3)
                for player in team_two:
                    queue.remove(player)


                teams_embed = discord.Embed(title=f'The Teams!', color=0x83ff00)
                teams_embed.add_field(name="**-Team 1-**", value=f'{" ".join(player.name for player in team_one)}',inline=False)
                teams_embed.add_field(name="**-Team 2-**", value=f'{" ".join(player.name for player in team_two)}',inline=False)
                teams_embed.add_field(name="**Match Creator:**", value=f'{" ".join(player.name for player in match_creator)}',inline=False)
                teams_embed.set_footer(text=f'Powered by RLI', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await target_channel.send(embed=teams_embed)

                user = "RLI" + str(random.randint(1, 1000))
                password = "RLI" + str(random.randint(1, 1000))
                credentials = discord.Embed(title=f'**Here are your lobby details**', color=0x83ff00)
                credentials.add_field(name=f'Username:', value=user)
                credentials.add_field(name=f'Password:', value=password)
                credentials.set_footer(text=f'{" ".join(player.name for player in match_creator)} to make the match', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                for member in team_one:
                   await member.send(embed=credentials)
                for member in team_two:
                   await member.send(embed=credentials)

                #await ctx.send(embed=credentials)

                active_games[user] = team_one, team_two

                queue = []
                new_queue = discord.Embed(title=f'Queue has been reset.', color=0xff8b00)
                new_queue.set_footer(text=f"When's the next one?...", icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
                await target_channel.send(embed=new_queue)

                queue_active = True


    @commands.command(name="leave",aliases=["leave_queue"], description="Lets the user leave the queue.")
    async def leave(self, ctx):

        player = ctx.author
        
        if ctx.channel.id == senior_queue_channel:
            await self.leave_queue(ctx, senior_queue, senior_queue_channel, player)

        elif ctx.channel.id == intermediate_queue_channel:
            await self.leave_queue(ctx, intermediate_queue, intermediate_queue_channel, player)

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
        leave_embed = discord.Embed(title=f'{len(queue)} players are in the queue')
        leave_embed.description = f'{player.mention} has left the queue.'
        leave_embed.color = 0xffffff
        leave_embed.set_footer(text=f'{str(6-len(queue))} more needed!', icon_url=f'https://cdn.discordapp.com/emojis/607596209254694913.png?v=1')
        target_channel = get(ctx.guild.channels, id=queue_channel)
        await target_channel.send(embed=leave_embed)


    @commands.command(name="status", description="Displays current status of the queue.")
    async def status(self, ctx):
        
        if ctx.channel.id == senior_queue_channel:
            await self.show_status(ctx, senior_queue)

        elif ctx.channel.id == intermediate_queue_channel:
            await self.show_status(ctx, intermediate_queue)

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
    async def remove(self, ctx, *, member: discord.Member):

        player = ctx.message.mentions[0]

        if ctx.channel.id == senior_queue_logs:
            await self.leave_queue(ctx, senior_queue, senior_queue_channel, player)

        elif ctx.channel.id == intermediate_queue_logs:
            await self.leave_queue(ctx, intermediate_queue, intermediate_queue_channel, player)

        elif ctx.channel.id == juniora_queue_logs:
            await self.leave_queue(ctx, juniora_queue, juniora_queue_channel, player)

        elif ctx.channel.id == casual_queue_logs:
            await self.leave_queue(ctx, casual_queue, casual_queue_channel, player)
        
        else:
            return

    @commands.command(hidden=True, name="add")
    async def add(self, ctx):
       
        player = ctx.message.mentions[0]

        if ctx.channel.id == senior_queue_logs:
            await self.add_to_queue(ctx, senior_queue, senior_queue_channel, player, senior_queue_active, senior_active_games)

        elif ctx.channel.id == intermediate_queue_logs:
            await self.add_to_queue(ctx, intermediate_queue, intermediate_queue_channel, player, intermediate_queue_active, intermediate_active_games)

        elif ctx.channel.id == juniora_queue_logs:
            await self.add_to_queue(ctx, juniora_queue, juniora_queue_channel, player, juniora_queue_active, juniora_active_games)

        elif ctx.channel.id == casual_queue_logs:
            await self.add_to_queue(ctx, casual_queue, casual_queue_channel, player, casual_queue_active, casual_active_games)

        else:
            return

    @commands.command(hidden=True, name="add_win")
    async def add_win(self, ctx, *args):
       
        player = ctx.message.mentions[0]

        if ctx.channel.id == senior_queue_logs:
            tier = "Senior"
            await self.add_wins(ctx, player, args, senior_games_played, senior_wins, tier)

        elif ctx.channel.id == intermediate_queue_logs:
            tier = "Intermediate"
            await self.add_wins(ctx, player, args, intermediate_games_played, intermediate_wins, tier)

        elif ctx.channel.id == juniora_queue_logs:
            tier = "Junior A"
            await self.add_wins(ctx, player, args, juniora_games_played, juniora_wins, tier)

        elif ctx.channel.id == casual_queue_logs:
            tier = "Casual"
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
        await ctx.send(f"{ctx.message.mentions[0]} has been given {args[-1]} win(s)")

    @commands.command(hidden=True, name="add_game")
    async def add_game(self, ctx, *args):
       
        player = ctx.message.mentions[0]

        if ctx.channel.id == senior_queue_logs:
            tier = "Senior"
            await self.add_games(ctx, player, args, senior_games_played, senior_wins, tier)

        elif ctx.channel.id == intermediate_queue_logs:
            tier = "Intermediate"
            await self.add_games(ctx, player, args, intermediate_games_played, intermediate_wins, tier)

        elif ctx.channel.id == juniora_queue_logs:
            tier = "Junior A"
            await self.add_games(ctx, player, args, juniora_games_played, juniora_wins, tier)

        elif ctx.channel.id == casual_queue_logs:
            tier = "Casual"
            await self.add_games(ctx, player, args, casual_games_played, casual_wins, tier)

        else:
            return

    async def add_games(self, ctx, player, args, games_played, wins, tier):

        if player in games_played.keys():
            games_played[player] += int(args[-1])

        elif player not in games_played.keys():
            games_played[player] = int(args[-1])

        await self.save_games(games_played, tier)
        await ctx.send(f"{ctx.message.mentions[0]} has played {args[-1]} extra game(s)")


    @commands.command(name="win", description="Allows player to report win.")
    async def win(self, ctx, *args):
        
        if ctx.channel.id != win_channel:
            return

        tier = ""

        for i in range(0, len(ctx.author.roles)):
            if ctx.author.roles[i].id == senior_role and args[0] in senior_active_games.keys():
                active_games = senior_active_games
                games_played = senior_active_games
                wins = senior_wins
                tier = "Senior"
                break
            elif ctx.author.roles[i].id == intermediate_role and args[0] in intermediate_active_games.keys():
                active_games = intermediate_active_games
                games_played = intermediate_games_played
                wins = intermediate_wins
                tier = "Intermediate"
                break
            elif ctx.author.roles[i].id == juniora_role and args[0] in juniora_active_games.keys():
                active_games = juniora_active_games
                games_played = juniora_games_played
                wins = juniora_wins
                tier = "Junior A"
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

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):

        if ctx.channel.id != leaderboard_spam:
            return

        for role in ctx.author.roles:
            if role.id == senior_role:
                await self.show_leaderboard(ctx, senior_wins, "Senior")
                return

            elif role.id == intermediate_role:
                await self.show_leaderboard(ctx, intermediate_wins, "Intermediate")
                return

            elif role.id == juniora_role:
                await self.show_leaderboard(ctx, juniora_wins, "Junior A")
                return

        await ctx.send("You aren't in a 6mans tier yet, try **>casual_leaderboard**")
        return


    @commands.command(name="casual_leaderboard", description="Shows the leaderboard")
    async def casual_leaderboard(self, ctx):

        if ctx.channel.id != leaderboard_spam:
            return

        await self.show_leaderboard(ctx, casual_wins, "Casual")

    async def show_leaderboard(self, ctx, wins, title):

        leaderboard_embed = discord.Embed(title=f"{title} Leaderboard",color=0x83ff00)
        i=1
        for k, v in sorted(wins.items(), key=lambda item: item[1], reverse=True):
            leaderboard_embed.add_field(name=f"{i}:", value=f'{k.name}: {str(v)}',inline=False)
            i+=1
        await ctx.send(embed=leaderboard_embed)


    @commands.command(name="stats")
    async def stats(self, ctx, *args):

        if ctx.channel.id != leaderboard_spam:
            return

        if not ctx.message.mentions:
            for role in ctx.author.roles:
                if role.id == senior_role:
                    await self.show_stats(ctx, ctx.message.author, senior_games_played, senior_wins, "Senior")
                    return

                elif role.id == intermediate_role:
                    await self.show_stats(ctx, ctx.message.author, intermediate_games_played, intermediate_wins, "Intermediate")
                    return

                elif role.id == juniora_role:
                    await self.show_stats(ctx, ctx.message.author, juniora_games_played, juniora_wins, "Junior A")
                    return

            await ctx.send("You aren't in a 6mans tier yet, try **>casual_stats**")
            return

        elif ctx.message.mentions:
            for role in ctx.message.mentions[0].roles:
                if role.id == senior_role:
                    await self.show_stats(ctx, ctx.message.mentions[0], senior_games_played, senior_wins, "Senior")
                    return

                elif role.id == intermediate_role:
                    await self.show_stats(ctx, ctx.message.mentions[0], intermediate_games_played, intermediate_wins, "Intermediate")
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

        for player in games_played.keys():
            if player == member:
                gp = games_played[player]

        for player in wins.keys():
            if player == member:
                w = wins[player]

        player_embed = discord.Embed(title=f"{member.name}'s {title} Stats", color=member.color)

        player_embed.add_field(name="Games Played:", value=f"{gp}")
        player_embed.add_field(name="Wins:", value=f"{w}")
        player_embed.add_field(name="Losses:", value=f"{gp - w}")
        if gp == 0:
            player_embed.add_field(name="Win Percentage", value=f"0%")
        else:
            player_embed.add_field(name="Win Percentage", value=f"{(w/gp)*100}%")

        await ctx.send(embed=player_embed)

    async def save_wins(self, wins, tier):

        if tier == "Senior":
            wins = senior_wins
            filename = "senior_wins.txt"

        elif tier == "Intermediate":
            wins = intermediate_wins
            filename = "intermediate_wins.txt"

        elif tier == "Junior A":
            wins = juniora_wins
            filename = "juniora_wins.txt"

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

        if tier == "Senior":
            games_played = senior_games_played
            filename = "senior_games_played.txt"

        elif tier == "Intermediate":
            games_played = intermediate_games_played
            filename = "intermediate_games_played.txt"

        elif tier == "Junior A":
            games_played = juniora_games_played
            filename = "juniora_games_played.txt"

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
        global senior_wins
        global intermediate_wins
        global juniora_wins
        global everyone_wins

        member_id_dict = {}

        filenames = ["senior_wins.txt", "intermediate_wins.txt", "juniora_wins.txt", "casual_wins.txt"]
        dictionaries = [senior_wins, intermediate_wins, juniora_wins, casual_wins]

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
        global senior_games_played
        global intermediate_games_played
        global juniora_games_played
        global everyone_games_played

        member_id_dict = {}

        filenames = ["senior_games_played.txt", "intermediate_games_played.txt", "juniora_games_played.txt", "casual_games_played.txt"]
        dictionaries = [senior_games_played, intermediate_games_played, juniora_games_played, casual_games_played]

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
        
    @commands.command(name="players")
    async def players(self, ctx):

        with open("games_played.txt", "r") as f:
            member_id_dict = json.load(f)

        string = ""
        i = 0

        for k, v in sorted(member_id_dict.items(), key=lambda item: item[1], reverse=True):
            string += f"<@!{int(k)}> : {v}\n"
            i += 1

        await ctx.send(string)
        await ctx.send(f"{i} players")

def setup(bot):
    bot.add_cog(QueueHandler(bot))
    bot.remove_command("help")