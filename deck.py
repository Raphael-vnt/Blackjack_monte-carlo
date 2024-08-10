# deck.py

import random
from card import Card

class Deck:
    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.cards = self.create_deck()
        self.shuffle()

    def create_deck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [Card(suit, rank) for suit in suits for rank in ranks] * self.num_decks

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def cards_left(self):
        return len(self.cards)
