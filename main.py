import random
from typing import Final, Dict, Any
import os
import time
import json

import discord
from discord import Member
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.ui import Button, View
from keep_alive import keep_alive
from discord.ext import commands

STARTING_COINS = 5000.0
GAMBLE_MINIMUM = 1.0
GAMBLE_MAXIMUM = 50000.0
BALANCES_FILE = 'user_balances.json'

COMMAND_PREFIX: Final[str] = "pls "


def load_balances() -> Dict[str, list]:
    if not os.path.exists(BALANCES_FILE):
        return {}
    with open(BALANCES_FILE, 'r') as file:
        return json.load(file)


def save_balances(balances: Dict[str, list]) -> None:
    with open(BALANCES_FILE, 'w') as file:
        json.dump(balances, file, indent=4)


user_balances = load_balances()

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)


# Function to start the user's journey and give them coins
async def start_journey(message: Message) -> None:
    user_id = str(message.author.id)
    if user_id not in user_balances:
        user_balances[user_id] = [STARTING_COINS, 0, 0, 0]
        # current balance, total coins earned, total coins lost, total times hit beg
        save_balances(user_balances)
        await message.channel.send(f"Your journey begins! You've received {STARTING_COINS} coins.")
    else:
        await message.channel.send("Your journey has already begun!")


# Function to give the responses of ball command
def get_8ball_response() -> str:
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes – definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    return random.choice(responses)


# Function to play the gambling game
async def gamble(message: Message, bet: int, choice: str) -> None:
    user_id = str(message.author.id)
    if user_id not in user_balances:
        await message.channel.send("Haven't joined the casino journey yet? Get in on the action now!")
        return

    if user_balances[user_id][0] < bet:
        await message.channel.send("Oops! Bet exceeds balance. Keep it within limits next time!")
        return

    if bet < GAMBLE_MINIMUM:
        await message.channel.send("Down on your luck? Go on, beg the bot for some spare change.")
        return

    if bet > GAMBLE_MAXIMUM:
        await message.channel.send("Feeling lucky, eh? Keep it within the maximum bet amount of 50000.")
        return

    choices = ['red', 'black']
    if choice.lower() not in choices:
        await message.channel.send("Please choose either 'red' or 'black'.")
        return

    result = random.choice(choices)
    if result == choice.lower():
        user_balances[user_id][0] += bet
        user_balances[user_id][1] += bet
        await message.channel.send(
            f"Congratulations <@{user_id}>! You chose {choice} and won {bet} coins.")
    else:
        user_balances[user_id][0] -= bet
        user_balances[user_id][2] += bet
        await message.channel.send(
            f"Sorry <@{user_id}>! You chose {choice} but the result was {result} and lost {bet} coins.")
    save_balances(user_balances)


# Function to play roulette game
async def roulette(message: Message, bet_type: str, bet_value: str, bet: int):
    user_id = str(message.author.id)
    if user_id not in user_balances:
        await message.channel.send("Haven't joined the casino journey yet? Get in on the action now!")
        return

    if user_balances[user_id][0] < bet:
        await message.channel.send("Oops! Bet exceeds balance. Keep it within limits next time!")
        return

    if bet < GAMBLE_MINIMUM:
        await message.channel.send("Down on your luck? Go on, beg the bot for some spare change.")
        return

    if bet > GAMBLE_MAXIMUM:
        await message.channel.send("Feeling lucky, eh? Keep it within the maximum bet amount of 50000.")
        return

    # Check if the bet is valid
    if bet_type not in ['color', 'number'] or bet <= GAMBLE_MINIMUM:
        await message.channel.send('Invalid bet type or amount.')
        return

    if bet_type == 'color' and bet_value not in ['red', 'black']:
        await message.channel.send('Invalid color. Choose red or black.')
        return

    if bet_type == 'number' and (int(bet_value) < 0 or int(bet_value) > 36):
        await message.channel.send('Invalid number. Choose a number between 0 and 36.')
        return

    # Spin the roulette wheel
    result_color = random.choice(['red', 'black'])
    result_number = random.randint(0, 36)

    # Check if the user won or lost
    if bet_type == 'color':
        if bet_value == result_color:
            user_balances[user_id][0] += bet
            user_balances[user_id][1] += bet
            await message.channel.send(
                f"The roulette landed on {result_color} {result_number}. <@{user_id}> won {bet * 2} coins.")
        else:
            user_balances[user_id][0] -= bet
            user_balances[user_id][2] += bet
            await message.channel.send(f"The roulette landed on {result_color} {result_number}. <@{user_id}> lost {bet} coins.")
        save_balances(user_balances)

    else:  # bet_type == 'number'
        if int(bet_value) == result_number:
            user_balances[user_id][0] += bet
            user_balances[user_id][1] += bet
            print("hello")
            await message.channel.send(
                f"The roulette landed on {result_color} {result_number}. <@{user_id}> won {bet * 36} coins.")
        else:
            user_balances[user_id][0] -= bet
            user_balances[user_id][2] += bet
            await message.channel.send(f"The roulette landed on {result_color} {result_number}. <@{user_id}> lost {bet} coins.")
        save_balances(user_balances)


# Function to play the dice roll game
async def dice_roll(message: Message, bet: int) -> None:
    user_id = str(message.author.id)
    if user_id not in user_balances:
        await message.channel.send("Haven't joined the casino journey yet? Get in on the action now!")
        return

    if user_balances[user_id][0] < bet:
        await message.channel.send("Oops! Bet exceeds balance. Keep it within limits next time!")
        return

    if bet < GAMBLE_MINIMUM:
        await message.channel.send("Down on your luck? Go on, beg the bot for some spare change.")
        return

    if bet > GAMBLE_MAXIMUM:
        await message.channel.send("Feeling lucky, eh? Keep it within the maximum bet amount of 50000.")
        return

    chance = random.randint(1, 10000)
    if chance <= 9998:
        dice_result = random.randint(1, 6)
    else:
        dice_result = 7
    if dice_result == 1:
        user_balances[user_id][0] -= bet
        user_balances[user_id][2] += bet
        await message.channel.send(
            f"Unlucky <@{user_id}>! You rolled a 1 and lost {bet} coins.")
    if dice_result == 2:
        loss = int(0.5 * bet)
        user_balances[user_id][0] -= loss
        user_balances[user_id][2] += loss
        await message.channel.send(
            f"Unlucky <@{user_id}>! You rolled a 2 and lost {loss} coins.")
    if dice_result == 3:
        loss = int(0.25 * bet)
        user_balances[user_id][0] -= loss
        user_balances[user_id][2] += loss
        await message.channel.send(
            f"Unlucky <@{user_id}>! You rolled a 3 and lost {loss} coins.")
    if dice_result == 4:
        win = int(0.25 * bet)
        user_balances[user_id][0] += win
        user_balances[user_id][1] += win
        await message.channel.send(
            f"Congratulations <@{user_id}>! You rolled a 4 and won {win} coins.")
    if dice_result == 5:
        win = int(0.5 * bet)
        user_balances[user_id][0] += win
        user_balances[user_id][1] += win
        await message.channel.send(
            f"Congratulations <@{user_id}>! You rolled a 5 and won {win} coins.")
    if dice_result == 6:
        user_balances[user_id][0] += bet
        user_balances[user_id][1] += bet
        await message.channel.send(
            f"Congratulations <@{user_id}>! You rolled a 6 and won {bet} coins.")
    if dice_result == 7:
        user_balances[user_id][0] += 100 * bet
        user_balances[user_id][1] += 100 * bet
        await message.channel.send(
            f"JACKPOT <@{user_id}>!!! You rolled a 7 and won {100 * bet} coins.")

    save_balances(user_balances)


# Function to play the slots game
async def slots(message: Message, bet: int) -> None:
    user_id = str(message.author.id)
    if user_id not in user_balances:
        await message.channel.send("Haven't joined the casino journey yet? Get in on the action now!")
        return

    if user_balances[user_id][0] < bet:
        await message.channel.send("Oops! Bet exceeds balance. Keep it within limits next time!")
        return

    if bet < GAMBLE_MINIMUM:
        await message.channel.send("Down on your luck? Go on, beg the bot for some spare change.")
        return

    if bet > GAMBLE_MAXIMUM:
        await message.channel.send("Feeling lucky, eh? Keep it within the maximum bet amount of 50000.")
        return

    slots = ['🍒', '🍋', '🍊', '🍇', '🍉', '🍓', '🍍', '🍎', '🍌', '🍐']
    slot1 = random.choice(slots)
    slot2 = random.choice(slots)
    slot3 = random.choice(slots)
    await message.channel.send(f"{slot1} {slot2} {slot3}")
    if slot1 == slot2 == slot3:
        user_balances[user_id][0] += 3 * bet
        user_balances[user_id][1] += 3 * bet
        await message.channel.send(
            f"Congratulations <@{user_id}>! You won {3 * bet} coins.")
    elif slot1 == slot2 or slot2 == slot3:
        user_balances[user_id][0] += bet
        user_balances[user_id][1] += bet
        await message.channel.send(
            f"Congratulations <@{user_id}>! You won {bet} coins.")
    elif slot1 == slot3:
        user_balances[user_id][0] += bet
        user_balances[user_id][1] += bet
        await message.channel.send(
            f"Congratulations <@{user_id}>! <@{user_id}> won {bet} coins.")
    else:
        user_balances[user_id][0] -= bet
        user_balances[user_id][2] += bet
        await message.channel.send(
            f"Unlucky <@{user_id}>! You lost {bet} coins.")
    save_balances(user_balances)


# Define the get_card_value function here
def get_card_value(card):
    if card[:-2] in ["J", "Q", "K"]:
        return 10
    elif card[:-2] == "A":
        return 1
    else:
        return int(card[:-2])


# Function to play the blackjack game
async def blackjack(message: Message, bet: int) -> None:
    user_id = str(message.author.id)

    if user_id not in user_balances:
        await message.channel.send("Haven't joined the casino journey yet? Get in on the action now!")
        return

    if user_balances[user_id][0] < bet:
        await message.channel.send("Oops! Bet exceeds balance. Keep it within limits next time!")
        return

    if bet < GAMBLE_MINIMUM:
        await message.channel.send("Down on your luck? Go on, beg the bot for some spare change.")
        return

    if bet > GAMBLE_MAXIMUM:
        await message.channel.send("Feeling lucky, eh? Keep it within the maximum bet amount of 50000.")
        return

    # Create and shuffle the deck
    suits = ["♠️", "♣️", "♥️", "♦️"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    deck = [f"{value}{suit}" for value in values for suit in suits]
    random.shuffle(deck)

    # Deal initial cards
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    player_sum = get_card_value(player_hand[0]) + get_card_value(player_hand[1])
    dealer_sum = get_card_value(dealer_hand[0]) + get_card_value(dealer_hand[1])

    # Display initial hands
    embed = discord.Embed(title=f"{message.author.name}'s Blackjack Game", color=discord.Color.dark_red())
    embed.add_field(name="Player's Hand", value=f"{player_hand[0]} {player_hand[1]} (Total: {player_sum})",
                    inline=False)
    embed.add_field(name="Dealer's Hand", value=f"{dealer_hand[0]} ?", inline=False)
    await message.channel.send(embed=embed)

    # Player's turn
    while player_sum <= 21:
        player_action = ""
        while player_action.lower() not in ["hit", "stand"]:
            await message.channel.send("Do you want to hit or stand?")
            response = await client.wait_for('message', check=lambda m: m.author == message.author)
            player_action = response.content

        if player_action.lower() == "hit":
            card = deck.pop()
            player_hand.append(card)
            player_sum += get_card_value(card)  # Use the new function to get the card value
            embed = discord.Embed(title=f"{message.author.name}'s Blackjack Game", color=discord.Color.dark_red())
            embed.add_field(name="Player's Hand", value=f"{' '.join(player_hand)} (Total: {player_sum})", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"{dealer_hand[0]} ?", inline=False)
            await message.channel.send(embed=embed)
            if player_sum > 21:
                await message.channel.send(f"<@{user_id}> busted and lost {bet} coins! Dealer wins.")
                user_balances[user_id][0] -= bet
                user_balances[user_id][2] += bet
                return
        elif player_action.lower() == "stand":
            break

    # Dealer's turn
    while dealer_sum < 17:
        card = deck.pop()
        dealer_hand.append(card)
        dealer_sum += get_card_value(card)  # Use the new function to get the card value

    # Display final hands
    embed = discord.Embed(title=f"{message.author.name}'s Blackjack Game", color=discord.Color.dark_red())
    embed.add_field(name="Player's Hand", value=f"{' '.join(player_hand)} (Total: {player_sum})", inline=False)
    embed.add_field(name="Dealer's Hand", value=f"{' '.join(dealer_hand)} (Total: {dealer_sum})", inline=False)
    await message.channel.send(embed=embed)

    # Final comparison
    if dealer_sum > 21:
        await message.channel.send(f"Dealer busted! <@{user_id}> won {bet} coins.")
        user_balances[user_id][0] += bet
        user_balances[user_id][1] += bet
    elif dealer_sum > player_sum:
        await message.channel.send(f"Dealer won! <@{user_id}> lost {bet} coins.")
        user_balances[user_id][0] -= bet
        user_balances[user_id][2] += bet
    elif dealer_sum < player_sum:
        await message.channel.send(f"Dealer lost! <@{user_id}> won {bet} coins.")
        user_balances[user_id][0] += bet
        user_balances[user_id][1] += bet
    else:
        await message.channel.send("It's a tie!")


# Function to display user profile
async def display_profile(message: Message) -> None:
    # Display in an embed
    user_id = str(message.author.id)
    if user_id in user_balances:
        user = message.author
        avatar_url = user.default_avatar.url if not user.avatar else user.avatar.url
        embed = discord.Embed(title=f"{user.name}'s Profile", color=discord.Color.dark_red())
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Balance", value=f"{user_balances[user_id][0]} coins", inline=False)
        embed.add_field(name="Total Coins Earned", value=f"{user_balances[user_id][1]} coins", inline=False)
        embed.add_field(name="Total Coins Lost", value=f"{user_balances[user_id][2]} coins", inline=False)
        embed.add_field(name="Total Times Begged", value=f"{user_balances[user_id][3]} times", inline=False)
        await message.channel.send(embed=embed)
    else:
        await message.channel.send("You haven't started your journey yet! Use the `pls start` command.")


# Function to show leaderboard for balance
async def display_leaderboard_balances(message: Message) -> None:
    # Sort the user_balances dictionary by balance in descending order
    sorted_balances = sorted(user_balances.items(), key=lambda item: item[1][0], reverse=True)

    # Create an embed for the leaderboard
    embed = discord.Embed(title="Top Balance Leaderboard", color=discord.Color.dark_red())

    # Add the top 10 users to the embed
    for i, (user_id, data) in enumerate(sorted_balances[:5]):
        user = await message.guild.fetch_member(int(user_id))
        if user is not None:
            embed.add_field(name=f"{i+1}. {user.name}", value=f"Balance: {data[0]} coins", inline=False)

    # Send the embed
    await message.channel.send(embed=embed)


# Function to show leaderboard for begs
async def display_leaderboard_begs(message: Message) -> None:
    # Sort the user_balances dictionary by begs in descending order
    sorted_begs = sorted(user_balances.items(), key=lambda item: item[1][3], reverse=True)

    # Create an embed for the leaderboard
    embed = discord.Embed(title="Most Begs Leaderboard", color=discord.Color.dark_red())

    # Add the top 10 users to the embed
    for i, (user_id, data) in enumerate(sorted_begs[:5]):
        user = await message.guild.fetch_member(int(user_id))
        if user is not None:
            embed.add_field(name=f"{i+1}. {user.name}", value=f"Total Times Begged: {data[3]} times", inline=False)

    # Send the embed
    await message.channel.send(embed=embed)


# Function to show leaderboard for losses
async def display_leaderboard_losses(message: Message) -> None:
    # Sort the user_balances dictionary by losses in descending order
    sorted_losses = sorted(user_balances.items(), key=lambda item: item[1][2], reverse=True)

    # Create an embed for the leaderboard
    embed = discord.Embed(title="Most Losses Leaderboard", color=discord.Color.dark_red())

    # Add the top 10 users to the embed
    for i, (user_id, data) in enumerate(sorted_losses[:5]):
        user = await message.guild.fetch_member(int(user_id))
        if user is not None:
            embed.add_field(name=f"{i+1}. {user.name}", value=f"Total Coins Lost: {data[2]} coins", inline=False)

    # Send the embed
    await message.channel.send(embed=embed)


# Function to show leaderboard for profit
async def display_leaderboard_earned(message: Message) -> None:
    # Sort the user_balances dictionary by total coins earned in descending order
    sorted_earned = sorted(user_balances.items(), key=lambda item: item[1][1], reverse=True)

    # Create an embed for the leaderboard
    embed = discord.Embed(title="Most Coins Earned Leaderboard", color=discord.Color.dark_red())

    # Add the top 10 users to the embed
    for i, (user_id, data) in enumerate(sorted_earned[:5]):
        user = await message.guild.fetch_member(int(user_id))
        if user is not None:
            embed.add_field(name=f"{i+1}. {user.name}", value=f"Total Coins Earned: {data[1]} coins", inline=False)

    # Send the embed
    await message.channel.send(embed=embed)


# Function to request money from the bot
async def request_money(message: Message) -> None:
    user_id = str(message.author.id)
    if user_id in user_balances:
        if user_balances[user_id][0] == 0:
            user_balances[user_id][0] += 2000
            user_balances[user_id][3] += 1
            save_balances(user_balances)
            await message.channel.send("Imagine asking bot for money, nvm here's your 2000")
        else:
            await message.channel.send("Dont beg unless you are a brookie")
    else:
        await message.channel.send("You haven't started your journey yet! Use the 'pls start' command.")


# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str, username: str) -> None:
    if not user_message or not user_message.startswith(COMMAND_PREFIX):
        return

    user_message = user_message[len(COMMAND_PREFIX):]

    if not user_message:
        print('(Message was empty because the command prefix was used without a message)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        if user_message.lower() == 'help':
            embed = discord.Embed(title="Available commands:", color=discord.Color.dark_red())
            embed.add_field(name="pls ping",
                            value="See how fast the bot is responding!",
                            inline=False)
            embed.add_field(name="pls help",
                            value="Discover all the commands and how to use them.",
                            inline=False)
            embed.add_field(name="pls ball",
                            value="Ask the magic 8-ball a question and get a mystical answer!",
                            inline=False)
            embed.add_field(name="pls start",
                            value="Kick off your casino adventure with 5,000 coins!",
                            inline=False)
            embed.add_field(name="pls balance",
                            value="Check how many coins you have right now.",
                            inline=False)
            embed.add_field(name="pls beg",
                            value="Ask the bot for coins when you're out of luck.",
                            inline=False)
            embed.add_field(name="pls profile",
                            value="View your personal user profile and stats.",
                            inline=False)
            embed.add_field(name="pls gamble",
                            value="Explore all the exciting gambling games in our casino!",
                            inline=False)
            embed.add_field(name="pls leaderboard <stat>",
                            value="Display the leaderboard of top users based on their stats",
                            inline=False)
            await message.channel.send(embed=embed)
            return

        if user_message.lower() == 'gamble':
            embed = discord.Embed(title="Casino:", color=discord.Color.dark_red())
            embed.add_field(name="pls bet <amount> <red/black>",
                            value="Feel the rush of high-stakes betting!",
                            inline=False)
            embed.add_field(name="pls dice <amount>",
                            value="Roll the dice and embrace chance!",
                            inline=False)
            embed.add_field(name="pls slots <amount>",
                            value="Spin for jackpot thrills!",
                            inline=False)
            embed.add_field(name="pls blackjack <amount>",
                            value="Challenge the dealer for 21!",
                            inline=False)
            embed.add_field(name="pls roulette <color/number> <red/black/0-36> <bet_amount>",
                            value="Bet and spin for thrilling wins!",
                            inline=False)
            await message.channel.send(embed=embed)
            return

        if user_message.lower() == 'profile':
            await display_profile(message)
            return

        if user_message.lower() == 'leaderboard balance':
            await display_leaderboard_balances(message)
            return

        if user_message.lower() == 'leaderboard profit':
            await display_leaderboard_earned(message)
            return

        if user_message.lower() == 'leaderboard loss':
            await display_leaderboard_losses(message)
            return

        if user_message.lower() == 'leaderboard beg':
            await display_leaderboard_begs(message)
            return

        if user_message.lower() == 'ping':
            start_time = time.time()
            await message.channel.send(f'Pong! :ping_pong: Latency: {round(client.latency * 1000)}ms')
            return

        if user_message.lower() == 'start':
            await start_journey(message)
            return

        if user_message.lower() == 'balance':
            user_id = str(message.author.id)
            if user_id in user_balances:
                await message.channel.send(f"Your current balance is: {user_balances[user_id][0]} coins.")
            else:
                await message.channel.send("You haven't started your journey yet! Use the 'pls start' command.")
            return

        if user_message.lower().startswith('bet'):
            # Split the user message to extract the bet amount and choice
            bet_args = user_message.split(' ')[1:]
            if len(bet_args) != 2:
                await message.channel.send("Please use the command in the format: !bet <amount> <red/black>")
                return

            try:
                bet_amount = int(bet_args[0])
            except ValueError:
                await message.channel.send("Please enter a valid bet amount.")
                return

            choice = bet_args[1].lower()
            await gamble(message, bet_amount, choice)
            return

        if user_message.lower().startswith('roulette'):
            bet_args = user_message.split(' ')[1:]
            if len(bet_args) != 3:
                await message.channel.send("Use the command in format: !roulette <bet_type> <bet_value> <bet_amount>")
                return

            try:
                bet = int(bet_args[2])
            except ValueError:
                await message.channel.send("Please enter a valid bet amount.")
                return

            bet_type = bet_args[0].lower()
            bet_value = bet_args[1].lower()
            await roulette(message, bet_type, bet_value, bet)
            return

        if user_message.lower().startswith('dice'):
            bet_args = user_message.split(' ')[1:]
            if len(bet_args) != 1:
                await message.channel.send("Please use the command in the format: !dice <amount>")
                return

            try:
                bet_amount = int(bet_args[0])
            except ValueError:
                await message.channel.send("Please enter a valid bet amount.")
                return

            await dice_roll(message, bet_amount)
            return

        if user_message.lower().startswith('slots'):
            bet_args = user_message.split(' ')[1:]
            if len(bet_args) != 1:
                await message.channel.send("Please use the command in the format: !slots <amount>")
                return

            try:
                bet_amount = int(bet_args[0])
            except ValueError:
                await message.channel.send("Please enter a valid bet amount.")
                return

            await slots(message, bet_amount)
            return

        if user_message.lower() == 'beg':
            await request_money(message)
            return

        if user_message.lower().startswith('blackjack') or user_message.lower().startswith('bj'):
            # Split the user message to extract the bet amount
            bet_args = user_message.split(' ')[1:]
            if len(bet_args) != 1:
                await message.channel.send("Please use the command in the format: !blackjack <amount>")
                return

            try:
                bet_amount = int(bet_args[0])
            except ValueError:
                await message.channel.send("Please enter a valid bet amount.")
                return

            await blackjack(message, bet_amount)
            return

        if user_message.lower().startswith('ball'):
            ball_text = user_message[len('ball '):].strip()
            if not ball_text:
                await message.channel.send("Please ask a question after the command.")
                return

            response = get_8ball_response()
            emoji = "🎱"
            embed = discord.Embed(color=discord.Color.random())
            embed.add_field(name=username, value="", inline=False)
            embed.add_field(name=f"**{ball_text}**", value="", inline=False)
            embed.add_field(name="", value=f"{emoji} {response}")
            await message.channel.send(embed=embed)
            return

    except Exception as e:
        print(e)


# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')
    global user_balances
    user_balances = load_balances()


# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message, username)


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(TOKEN)


keep_alive()
if __name__ == '__main__':
    main()
