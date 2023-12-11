
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from itertools import cycle
from threading import Thread

import discord
from discord.ext import commands, tasks
from flask import Flask 

from shop import Shop

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="TE ", intents=intents)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

economy_data = {}

# Check if the economy_data.json file exists and load it
if os.path.isfile('economy_data.json'):
    with open('economy_data.json', 'r') as file:
        economy_data = json.load(file)
shop_instance = Shop('shop_items.json')

@bot.command(name='balance')
async def balance(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    member_id = str(member.id)

    if member_id in economy_data:
        balance = economy_data[member_id]["balance"]
    else:
        balance = 0
        economy_data[member_id] = {"balance": balance}

    await ctx.send(f"{member.name} has a balance of {balance} breads.")

@bot.command(name='award')
@commands.has_permissions(administrator=True)
async def award(ctx, member: discord.Member, amount: int):
    member_id = str(member.id)

    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0}

    economy_data[member_id]["balance"] += amount
    await ctx.send(f"""Awarded {amount} breads to {member.name}. New balance is 
    {economy_data[member_id]
    ['balance']} breads.""")

    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.command(name='deduct')
@commands.has_permissions(administrator=True)
async def deduct(ctx, member: discord.Member, amount: int):
    member_id = str(member.id)

    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0}

    economy_data[member_id]["balance"] -= amount
    await ctx.send
    (f"""Deducted {amount} breads from {member.name}. New 
    balance is {economy_data[member_id]
    ['balance']} breads.""")

with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

# Save the economy data to a file upon bot shutdown
@bot.event
async def on_disconnect():
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"""This command is on cooldown. Please 
        try again in {round(error.retry_after, 2)} seconds.""")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have permission to do that.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("I couldn't find that member.")
    else:
        await ctx.send(f"An error occurred: {error}")

@bot.command(name='additem')
@commands.has_permissions(administrator=True)
async def add_item(ctx, member: discord.Member, item_name: str, quantity: int = 1):
    member_id = str(member.id)

    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0, "inventory": {}}

    if item_name not in economy_data[member_id].get("inventory", {}):
        economy_data[member_id]["inventory"][item_name] = 0

    economy_data[member_id]["inventory"][item_name] += quantity
    await ctx.send(f"Added {quantity} of {item_name} to {member.name}'s inventory.")
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.command(name='removeitem')
@commands.has_permissions(administrator=True)
async def remove_item(ctx, member: discord.Member, item_name: str, quantity: int = 1):
    member_id = str(member.id)

    if member_id in economy_data and item_name in economy_data[member_id].get(
        "inventory", {}):
        economy_data[member_id]["inventory"][item_name] -= quantity
        if economy_data[member_id]["inventory"][item_name] <= 0:
            del economy_data[member_id]["inventory"][item_name]  
        await ctx.send(f"""Removed {quantity} of {item_name} 
        from {member.name}'s inventory.""")
    else:
        await ctx.send(f"{member.name} does not have that item in their inventory.")

with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.tree.command(name='inventory')
async def display_inventory(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    member_id = str(member.id)

    if member_id in economy_data and "inventory" in economy_data[member_id]:
        inventory = economy_data[member_id]["inventory"]
        inventory_list = "\n".join(f"{item}: {quantity}" for 
                                   item, quantity in inventory.items())
        message = f"{member.name}'s inventory:\n{inventory_list}"
    else:
        message = f"{member.name} has an empty inventory."

    await ctx.send(message)

@bot.command(name='shopadd')
@commands.has_permissions(administrator=True)
async def shop_add(ctx, item_name: str, price: int, quantity: int):
    shop_instance.add_item(item_name, price, quantity)
    await ctx.send(f"""Added {quantity} of {item_name} to the 
    shop at {price} breads each.""")
@bot.command(name='shopremove')
@commands.has_permissions(administrator=True)
async def shop_remove(ctx, item_name: str, quantity: int):
    if shop_instance.remove_item(item_name, quantity):
        await ctx.send(f"Removed {quantity} of {item_name} from the shop.")
    else:
        await ctx.send("""Could not remove item from the shop. 
        Please check the item name and quantity.""")
        
@bot.command(name='shop')
async def shop_list(ctx):
    embeds = discord.Embed(title= "Shop" , description="""Keycard: Price: 100,
    Computer: Price: 150,
    Potion: Price: 50,
    Shoutout: Price: 1000,
    Custom Channel: Price: 1500,
    Toasty Economy bot user role: Price: 1000,
    Farewell Toasty role: Price 1000
    Use TE purchase, to buy items, and TE buy for roles and 
    others!""", color= discord.Color.blue())
    await ctx.send(embed=embeds)
    

@bot.command(name='steal')
async def steal(ctx):
    player_id = str(ctx.author.id)
    
    # Ensure that the player is in the economy_data and has a computer
    if player_id not in economy_data or "inventory" not in economy_data[player_id] or \
    economy_data[player_id]["inventory"].get(
        "computer", 0) <= 0:
        await ctx.send("You need a computer to steal from others.")
        return
    
    # Exclude the command issuer and players with zero or undefined balance
    potential_targets = {member_id: data for member_id, data 
                         in economy_data.items() if member_id != player_id and 
                         data.get("balance", 0) > 0}
    if not potential_targets:
        await ctx.send("There are no players with a balance to steal from.")
        return
    # Randomly select a target player
    target_id = random.choice(list(potential_targets.keys()))
    target_data = potential_targets[target_id] # Get the data of the target
    # Determine the success chance and the amount to steal
    success_chance = 0.05  # 5% chance to succeed
    max_amount = min(100, target_data["balance"])  # Maximum amount to steal
    amount_to_steal = random.randint(1, max_amount)
    # Perform the theft
    if random.random() < success_chance:
        # Successful theft
        economy_data[player_id]["balance"] += amount_to_steal
        economy_data[target_id]["balance"] -= amount_to_steal
        await ctx.send(f"""You've successfully stolen 
        {amount_to_steal} breads from <@{target_id}>!""")
    else:
        # Failed theft
        await ctx.send("""Failed! The computer's attempt to 
        steal was detected and blocked!, You should probalby 
        just join the Bread Community, and participate in FREE 
        Giveaways!""")
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.command(name='buy')
async def buy(ctx, item_name: str, quantity: int = 1):
    owner_id = '440205899898814496'  # Replace with your Discord user ID
    special_items = ["""Shoutout", "Custom Channel", "Farewell 
    Toasty role", "Toasty Economy bot user role"""]
    str(ctx.author.id)
    player_username = str(ctx.author)  # The player's Discord username and discriminator

    # Check if the item exists in the shop and the player can afford it
    

   
    # After confirming the purchase
    item_purchased = item_name  # The actual name of the item purchased
    if item_purchased in special_items:
        owner = bot.get_user(int(owner_id))
        if owner is not None:
            try:
                await owner.send(f"{player_username} has purchased a {item_purchased}.")
            except discord.errors.Forbidden:
                print(f"Could not send a DM to {owner_id}")

    # ... (the rest of your existing code for handling the purchase)

@bot.command(name='work')
@commands.cooldown(1, 21600, commands.BucketType.user)
async def work(ctx):
    member_id = str(ctx.author.id)

    # Check if the user exists in economy_data, if not add them with 0 balance
    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0, "inventory": {}}

    # Define the range of earnings from work
    min_earnings = 100
    max_earnings = 1000

    # Calculate random earnings
    earnings = random.randint(min_earnings, max_earnings)

    # Update the user's balance
    economy_data[member_id]["balance"] += earnings

    # Create an embed to display the work results
    embed = discord.Embed(title='Work Results', 
                          description=f"""You worked hard and 
                          earned {earnings} breads!""", color=0x00ff00)

    # Include additional information if needed
    embed.add_field(name='Current Balance', 
                    value=economy_data[member_id]["balance"], inline=False)

    # Send the embed to the user
    await ctx.send(embed=embed)

    # Optionally, you might want to save the updated data to economy_data.json
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.command(name='purchase')
async def purchase(ctx, item_name: str, quantity: int = 1):
    member_id = str(ctx.author.id)
    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0, "inventory": {}}

    item_info = shop_instance.get_item_info(item_name)
    if item_info is None:
        await ctx.send(f"The item `{item_name}` is not available in the shop.")
        return

    total_cost = item_info['price'] * quantity
    member_balance = economy_data[member_id].get("balance", 0)

    if member_balance < total_cost:
        await ctx.send(f"""You do not have enough breads to purchase {quantity} 
        `{item_name}`.""")
        return

    if item_info['quantity'] < quantity:
        await ctx.send(f"""There are not enough `{item_name}` in 
        the shop to fulfill your purchase.""")
        return
        

    # Proceed with the transaction
    economy_data[member_id]["balance"] -= total_cost
    if item_name not in economy_data[member_id].get("inventory", {}):
        economy_data[member_id]["inventory"][item_name] = 0
    economy_data[member_id]["inventory"][item_name] += quantity

    # Decrease the quantity in the shop
    shop_instance.remove_item(item_name, quantity)

    await ctx.send(f"""You have purchased {quantity} `{item_name}`. Remaining balance: 
    {economy_data[member_id]['balance']} breads.""")
        # Save the updated data to economy_data.json
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.command(name='toasty')
async def Toasty(ctx):
    await ctx.send("Farewell Toasty! Your memory will forever live on in me.")

@bot.command(name='invite')
async def invite(ctx):
    embed = discord.Embed(
        title='Invite Link',
        description="""Invite me to your server with the 
        following link: https://discord.com/api/oauth2/authorize?client_id=1181057947774746644&permissions=8&scope=bot+applications.commands""",
        color=discord.Color.blue())
    
    await ctx.send(embed=embed)

@bot.command(name='pay')
async def pay(ctx, recipient: discord.Member, amount: int):
    # Check if the amount is at least 1
    if amount < 1:
        return await ctx.send('Payment amount must be at least 1.')

    # Check if the sender has enough balance
    sender_id = str(ctx.author.id)
    sender_balance = economy_data.get(sender_id, {"balance": 0})["balance"]

    if sender_balance < amount:
        return await ctx.send('Insufficient balance.')

    # Perform the transaction
    recipient_id = str(recipient.id)
    economy_data.get(recipient_id, {"balance": 0})["balance"]

    economy_data[sender_id]["balance"] -= amount
    economy_data[recipient_id]["balance"] += amount

    # Update the database (replace this with your actual database update logic)
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

    # Create an embed to display the transaction information
    embed = discord.Embed(title='Transaction Successful', 
                          description=f"""{ctx.author.name} paid 
                          {recipient.name} {amount} breads!""", color=0x00ff00)

    # Include additional information if needed
    embed.add_field(name='Sender Balance', 
                    value=economy_data[sender_id]["balance"], inline=False)
    embed.add_field(name='Recipient Balance', 
                    value=economy_data[recipient_id]["balance"], inline=False)

    # Send the embed to the user
    await ctx.send(embed=embed)


# ... [rest of your main.py file above]

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    # Sort users by their balance in descending order
    sorted_users = sorted(economy_data.items(), key=lambda x: 
                          x[1]["balance"], reverse=True)
    # Define variables for pagination
    page = 0
    items_per_page = 10
    pages = [sorted_users[i:i + items_per_page] for i in range(0, len(sorted_users), items_per_page)]
    
    def create_embed(users_for_page, page_index):
        embed = discord.Embed(title=f'Leaderboard - Page {page_index + 1}', color=0x00ff00)
        for i, (user_id, user_data) in enumerate(users_for_page, start=1):
            user = ctx.guild.get_member(int(user_id))
            name = user.name if user else 'User not found'
            embed.add_field(name=f'{i + items_per_page * page_index}. {name}', 
                            value=f'Balance: {user_data["balance"]} breads', 
                            inline=False)
        return embed

    # Send the first page to the channel
    current_embed = create_embed(pages[page], page)
    message = await ctx.send(embed=current_embed)

    # Add reaction emoji for navigation
    await message.add_reaction('⬅️')
    await message.add_reaction('➡️')

    # Check to make sure it's the user who called the command and that it's the correct emoji
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ('⬅️', '➡️') and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == '➡️' and page < len(pages) - 1:
                page += 1
                current_embed = create_embed(pages[page], page)
                await message.edit(embed=current_embed)
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == '⬅️' and page > 0:
                page -= 1
                current_embed = create_embed(pages[page], page)
                await message.edit(embed=current_embed)
                await message.remove_reaction(reaction, user)
            else:
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break

    # Remove reaction emoji when finished
    await message.clear_reactions()

# ... [rest of your main.py file below]

@bot.command(name='rolldice')
async def rolldice(ctx):
    result = random.randint(1, 6)

    embed_result = discord.Embed(title='Dice Roll Result', color=0x00ff00)
    embed_result.add_field(name='Result', value=str(result), inline=False)

    sender_id = str(ctx.author.id)

    if result == 6:
        # User wins
        winnings = 1000  # You can adjust the multiplier
        economy_data[sender_id]["balance"] += winnings

        embed_outcome = discord.Embed(title='Dice Roll Outcome - Win', color=0x00ff00)
        embed_outcome.add_field(name='Outcome', value=f"Congratulations! You rolled a 6 and win {winnings} breads!", inline=False)
    else:
        # User loses
        economy_data[sender_id]["balance"] -= 1  # Adjust as needed

        embed_outcome = discord.Embed(title='Dice Roll Outcome - Lose', color=0xff0000)
        embed_outcome.add_field(name='Outcome', value="Sorry! You didn't roll a 6. You lose.", inline=False)

    await ctx.send(embed=embed_result)
    await ctx.send(embed=embed_outcome)
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)
    
@bot.command(name='slots')
async def slots(ctx, bet: int):
    symbols = ['🍒', '🍊', '🍋', '🍇', '🍉', '🍓']
    reels = [random.choice(symbols) for _ in range(3)]
    
    embed = discord.Embed(title='Slot Machine', color=0x00ff00)
    embed.add_field(name='Result', value=' '.join(reels), inline=False)

    sender_id = str(ctx.author.id)
    if reels.count(reels[0]) == 3:
        # User wins
        winnings = 10  # You can adjust the multiplier
        economy_data[sender_id]["balance"] += bet * winnings
        embed.add_field(name='Outcome', 
                        value=f"""Congratulations! You win 
                        {winnings} times your bet!""", inline=False)
    else:
        # User loses
        economy_data[sender_id]["balance"] -= bet
        embed.add_field(name='Outcome', value="""Sorry! No 
        winning combination. You lose your bet.""", inline=False)

    await ctx.send(embed=embed)
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

bot.remove_command('help')  # This line disables the default help command

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="Help",
        description="All commands",
        color=discord.Color.blue()
    )

    # Add fields for each command with name and description
    embed.add_field(name="TE work", value="Description of the command", inline=False)
    embed.add_field(name="TE balance", value="Shows your current balance", inline=False)
    embed.add_field(name="TE rolldice", value="Rolls a dice and wins if you roll a 6", inline=False)
    embed.add_field(name="TE slots", value="Play slots and win x10 if all three reels match", inline=False)
    embed.add_field(name="TE leaderboard", value="Shows the top 10 users with the most breads", inline=False)
    embed.add_field(name="TE shop", value="Shows the items available for purchase", inline=False)
    embed.add_field(name="TE buy [item]", value="Buys an item from the shop ROLES ONLY", inline=False)
    embed.add_field(name="TE inventory", value="Shows your current inventory", inline=False)
    embed.add_field(name="TE help", value="Shows this help message", inline=False)
    embed.add_field(name="TE pay [user] [amount]", value="Pays a user a specified amount of breads", inline=False)
    embed.add_field(name="TE purchase [item]", value="Purchases an item from the shop. NOT FOR ROLES ITEMS ONLY", inline=False)
    embed.add_field(name="TE steal [user]", value="Attempt to steal a user's breads.", inline=False)
    embed.add_field(name="TE daily", value="Claim your daily breads.", inline=False)
    embed.add_field(name="TE monthly", value="Claim your monthly breads.", inline=False)

    await ctx.send(embed=embed)

DAILY_REWARD = 100
MONTHLY_REWARD = 10000

@bot.command(name='daily')
async def daily(ctx):
    member_id = str(ctx.author.id)
    
    # Check if the member is in the economy_data
    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0, "last_daily": None}
    
    # Check if the user has already claimed their daily today
    last_claimed = economy_data[member_id].get('last_daily')
    if last_claimed is not None:
        last_claimed_date = datetime.fromisoformat(last_claimed)
        # Check if 24 hours have passed
        if (datetime.now() - last_claimed_date) < timedelta(days=1):  # Correct indentation
            time_left = timedelta(days=1) - (datetime.now() - last_claimed_date)  # Correct usage of timedelta and datetime
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You have already claimed your daily reward. You can claim again in {hours}h {minutes}m.")
            return  # Correct indentation
            
    # Give daily reward
    economy_data[member_id]['balance'] += DAILY_REWARD
    economy_data[member_id]['last_daily'] =                    datetime.now().isoformat()

    await ctx.send(f"You have claimed your daily reward of {DAILY_REWARD} coins!")
    # Save the updated data to economy_data.json
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.command(name='monthly')
async def monthly(ctx):
    member_id = str(ctx.author.id)
    
    # Check if the member is in the economy_data
    if member_id not in economy_data:
        economy_data[member_id] = {"balance": 0, "last_monthly": None}
    
    # Check if the user has already claimed their monthly reward
    last_claimed = economy_data[member_id].get('last_monthly')
    if last_claimed is not None:
        last_claimed_date = datetime.fromisoformat(last_claimed)
        # Check if 30 days have passed
        if (datetime.now() - last_claimed_date) < timedelta(days=30):
            time_left = timedelta(days=30) - (datetime.now() - last_claimed_date)
            days, remainder = divmod(int(time_left.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You have already claimed your monthly reward. You can claim again in {days}d {hours}h {minutes}m.")
            return
    
    # Give monthly reward
    economy_data[member_id]['balance'] += MONTHLY_REWARD
    economy_data[member_id]['last_monthly'] = datetime.now().isoformat()
    await ctx.send(f"You have claimed your monthly reward of {MONTHLY_REWARD} coins!")
    # Save the updated data to economy_data.json
    with open('economy_data.json', 'w') as file:
        json.dump(economy_data, file, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

status = cycle(['With The Bread Community','With Python'])

@tasks.loop(seconds=5)
async def change_status():
  await bot.change_presence(activity=discord.Game(next(status)))


app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask app serving as the home for the Discord bot."

if __name__ == '__main__':
    if TOKEN:
        bot_thread = Thread(target=lambda: bot.run(TOKEN))
        bot_thread.start()
    app.run(host='0.0.0.0', port=8080)
else:
    print("The DISCORD_BOT_TOKEN environment variable is not set.")

