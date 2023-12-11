import json
import random
from datetime import datetime

from main import bot, economy_data, shop_instance


@bot.command(name='usekeycard')
async def use_keycard(ctx):
    if datetime.today().weekday() != 6:  
        await ctx.send("You can only use a keycard on Sundays!")
        return

    member_id = str(ctx.author.id)
    if member_id not in economy_data or 'keycard' not in economy_data[member_id].get(
        "inventory", {}):
        await ctx.send("You do not have a keycard to use.")
        return

    # If the user has a keycard, decrease the keycard count by one
    economy_data[member_id]["inventory"]["keycard"] -= 1
    if economy_data[member_id]["inventory"]["keycard"] <= 0:
        del economy_data[member_id]["inventory"]["keycard"]

    # Get a random item from the shop
    shop_items = shop_instance.list_items()
    if not shop_items:
        await ctx.send("The shop is currently empty.")
        return

    random_item = random.choice(list(shop_items.keys()))
    item_quantity = shop_items[random_item]["quantity"]
    if item_quantity <= 0:
        await ctx.send(f"Sorry, {random_item} is out of stock.")
        return

    # Add the random item to the user's inventory
    if random_item not in economy_data[member_id].get("inventory", {}):
        economy_data[member_id]["inventory"][random_item] = 0
    economy_data[member_id]["inventory"][random_item] += 1

    # Check if the random item is a "Potion" before the return statement.
    if random_item == "Potion":
        economy_data[member_id]["balance"] *= 2
    try:
        user = await bot.fetch_user(ctx.author.id)
        if user.dm_channel is None:
            await user.create_dm()
        user = user.dm_channel.recipient

        await user.send(f"""You used a potion and gained 
        {economy_data[member_id]['balance']} coins!""")

    
    # Decrease the quantity of the item in the shop
    shop_instance.remove_item(random_item, 1)

    await ctx.send(f"You used a keycard and received a {random_item}!")

        # Save the updated economy data
    with open('economy_data.json', 'w') as file:
         json.dump(economy_data, file, indent=4)
