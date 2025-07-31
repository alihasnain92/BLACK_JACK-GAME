import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import pygame
from tkinter import messagebox

# Initialize mixer for sounds
pygame.mixer.init()


# Play sound from sounds folder
def play_sound(filename):
    try:
        pygame.mixer.Sound(os.path.join("sounds", filename)).play()
    except Exception as e:
        print(f"Could not play sound {filename}: {e}")


# Load card image from cards folder
def load_card_image(rank, suit):
    # Map our internal names to the actual filenames from the GitHub repo
    rank_map = {
        'ace': 'A',
        'jack': 'J',
        'queen': 'Q',
        'king': 'K',
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
        '7': '7', '8': '8', '9': '9', '10': '10'
    }

    suit_map = {
        'hearts': 'H',
        'diamonds': 'D',
        'clubs': 'C',
        'spades': 'S'
    }

    # Try multiple filename formats
    possible_filenames = [
        f"{rank_map.get(rank, rank)}{suit_map.get(suit, suit)}.png",  # AH.png format
        f"{rank}_{suit}.png",  # ace_hearts.png format
        f"{rank}_of_{suit}.png",  # ace_of_hearts.png format
        f"{rank_map.get(rank, rank)}_of_{suit}.png"  # A_of_hearts.png format
    ]

    for filename in possible_filenames:
        path = os.path.join("cards", filename)
        try:
            img = Image.open(path).resize((70, 100), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            continue

    # If no format worked, create placeholder
    print(f"Could not load card image for {rank} of {suit}. Tried: {possible_filenames}")
    placeholder = Image.new("RGB", (70, 100), "darkred")
    return ImageTk.PhotoImage(placeholder)


# Load card back image
def load_card_back():
    # Try different possible names for card back
    possible_backs = ["back.png", "card_back.png", "blue_back.png", "red_back.png"]

    for back_name in possible_backs:
        try:
            img = Image.open(os.path.join("cards", back_name)).resize((70, 100), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            continue

    # Gray placeholder for hidden card if no back image found
    hidden = Image.new("RGB", (70, 100), "gray")
    return ImageTk.PhotoImage(hidden)


# Generate random card
def deal_card():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    rank = random.choice(ranks)
    suit = random.choice(suits)

    # Handle value assignment
    if rank == 'ace':
        value = 11
    elif rank in ['jack', 'queen', 'king']:
        value = 10
    else:
        value = int(rank)

    return {'rank': rank, 'suit': suit, 'value': value}


# Calculate score with ace logic
def calculate_score(cards):
    values = [card['value'] for card in cards]
    total = sum(values)

    # Check for blackjack (21 with exactly 2 cards)
    if total == 21 and len(cards) == 2:
        return 0  # Special value for blackjack

    # Convert aces from 11 to 1 if needed
    aces = values.count(11)
    while total > 21 and aces > 0:
        total -= 10  # Convert an ace from 11 to 1
        aces -= 1

    return total


# Compare game result
def compare(player_score, dealer_score):
    if player_score == dealer_score:
        return "It's a Draw! 🤝", "draw"
    elif dealer_score == 0:
        return "Dealer has Blackjack! 😱", "lose"
    elif player_score == 0:
        return "Blackjack! You Win! 🎉", "win"
    elif player_score > 21:
        return "You Bust! Dealer Wins 😭", "lose"
    elif dealer_score > 21:
        return "Dealer Busts! You Win! 😄", "win"
    elif player_score > dealer_score:
        return "You Win! 😃", "win"
    else:
        return "Dealer Wins 😤", "lose"


# GUI Game Class
class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎴 Blackjack Casino 🎴")
        self.root.geometry("800x600")
        self.root.config(bg="#0f5132")  # Casino green

        # Game state
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.player_cards = []
        self.dealer_cards = []
        self.game_over = False

        # Load card back image once
        self.card_back = load_card_back()

        self.create_widgets()
        self.start_game()

    def create_widgets(self):
        # Title
        self.title_label = tk.Label(
            self.root,
            text="🎴 BLACKJACK CASINO 🎴",
            font=("Helvetica", 24, "bold"),
            bg="#0f5132",
            fg="gold"
        )
        self.title_label.pack(pady=15)

        # Score tracking
        self.score_label = tk.Label(
            self.root,
            text="Wins: 0 | Losses: 0 | Draws: 0",
            font=("Helvetica", 14, "bold"),
            bg="#0f5132",
            fg="white"
        )
        self.score_label.pack(pady=5)

        # Game info
        self.info_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 14),
            bg="#0f5132",
            fg="yellow"
        )
        self.info_label.pack(pady=10)

        # Dealer section
        dealer_title = tk.Label(
            self.root,
            text="🎩 DEALER",
            font=("Helvetica", 16, "bold"),
            bg="#0f5132",
            fg="lightcyan"
        )
        dealer_title.pack()

        self.dealer_score_label = tk.Label(
            self.root,
            text="Score: ?",
            font=("Helvetica", 12),
            bg="#0f5132",
            fg="lightcyan"
        )
        self.dealer_score_label.pack()

        self.dealer_frame = tk.Frame(self.root, bg="#0f5132")
        self.dealer_frame.pack(pady=10)

        # Player section
        player_title = tk.Label(
            self.root,
            text="🎲 PLAYER",
            font=("Helvetica", 16, "bold"),
            bg="#0f5132",
            fg="lightgreen"
        )
        player_title.pack()

        self.player_score_label = tk.Label(
            self.root,
            text="Score: 0",
            font=("Helvetica", 12),
            bg="#0f5132",
            fg="lightgreen"
        )
        self.player_score_label.pack()

        self.player_frame = tk.Frame(self.root, bg="#0f5132")
        self.player_frame.pack(pady=10)

        # Action buttons
        self.button_frame = tk.Frame(self.root, bg="#0f5132")
        self.button_frame.pack(pady=20)

        self.hit_button = tk.Button(
            self.button_frame,
            text="🃏 HIT",
            command=self.hit,
            width=15,
            height=2,
            bg="#d4a574",
            fg="black",
            font=("Helvetica", 12, "bold")
        )
        self.hit_button.grid(row=0, column=0, padx=15)

        self.stand_button = tk.Button(
            self.button_frame,
            text="✋ STAND",
            command=self.stand,
            width=15,
            height=2,
            bg="#8b0000",
            fg="white",
            font=("Helvetica", 12, "bold")
        )
        self.stand_button.grid(row=0, column=1, padx=15)

        # New game button
        self.new_button = tk.Button(
            self.root,
            text="🎮 NEW GAME",
            command=self.start_game,
            width=25,
            height=2,
            bg="#4682b4",
            fg="white",
            font=("Helvetica", 12, "bold")
        )
        self.new_button.pack(pady=15)

    def start_game(self):
        """Start a new game"""
        play_sound("shuffle.mp3")

        self.player_cards = [deal_card(), deal_card()]
        self.dealer_cards = [deal_card(), deal_card()]
        self.game_over = False

        self.display_cards()
        self.update_scores()
        self.info_label.config(text="Choose HIT to take another card or STAND to hold")

        # Enable buttons
        self.hit_button.config(state="normal")
        self.stand_button.config(state="normal")

        # Check for immediate blackjack
        if calculate_score(self.player_cards) == 0:
            self.root.after(1000, self.stand)

    def display_cards(self):
        """Display all cards on screen"""
        # Clear existing cards
        for widget in self.dealer_frame.winfo_children():
            widget.destroy()
        for widget in self.player_frame.winfo_children():
            widget.destroy()

        # Display dealer cards
        for i, card in enumerate(self.dealer_cards):
            if i == 0 and not self.game_over:
                # Show card back for hidden card
                img = self.card_back
            else:
                img = load_card_image(card['rank'], card['suit'])

            label = tk.Label(self.dealer_frame, image=img, bg="#0f5132")
            label.image = img  # Keep reference
            label.pack(side="left", padx=5)

        # Display player cards
        for card in self.player_cards:
            img = load_card_image(card['rank'], card['suit'])
            label = tk.Label(self.player_frame, image=img, bg="#0f5132")
            label.image = img  # Keep reference
            label.pack(side="left", padx=5)

    def update_scores(self):
        """Update score displays"""
        player_score = calculate_score(self.player_cards)
        dealer_score = calculate_score(self.dealer_cards)

        # Player score (always visible)
        if player_score == 0:
            self.player_score_label.config(text="Score: BLACKJACK!")
        else:
            self.player_score_label.config(text=f"Score: {player_score}")

        # Dealer score (hidden until game over)
        if self.game_over:
            if dealer_score == 0:
                self.dealer_score_label.config(text="Score: BLACKJACK!")
            else:
                self.dealer_score_label.config(text=f"Score: {dealer_score}")
        else:
            visible_score = self.dealer_cards[1]['value']  # Only second card visible
            self.dealer_score_label.config(text=f"Score: {visible_score}+?")

    def hit(self):
        """Player chooses to hit"""
        play_sound("card_flip.mp3")

        self.player_cards.append(deal_card())
        self.display_cards()
        self.update_scores()

        # Check for bust
        if calculate_score(self.player_cards) > 21:
            self.root.after(500, self.stand)

    def stand(self):
        """Player chooses to stand"""
        self.game_over = True
        self.hit_button.config(state="disabled")
        self.stand_button.config(state="disabled")

        # Dealer draws cards
        while calculate_score(self.dealer_cards) < 17 and calculate_score(self.dealer_cards) != 0:
            self.dealer_cards.append(deal_card())
            play_sound("card_flip.mp3")

        self.display_cards()
        self.update_scores()

        # Show result after delay
        self.root.after(1000, self.show_result)

    def show_result(self):
        """Show final result and update statistics"""
        player_score = calculate_score(self.player_cards)
        dealer_score = calculate_score(self.dealer_cards)
        result_text, outcome = compare(player_score, dealer_score)

        self.info_label.config(text=result_text)

        # Update statistics and play sound
        if outcome == "win":
            self.wins += 1
            play_sound("win.mp3")
        elif outcome == "lose":
            self.losses += 1
            play_sound("lose.mp3")
        else:  # draw
            self.draws += 1
            play_sound("draw.mp3")

        self.score_label.config(text=f"Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}")


# Launch the game
if __name__ == "__main__":
    root = tk.Tk()
    try:
        game = BlackjackGame(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Game could not start: {e}")
        print(f"Error: {e}")