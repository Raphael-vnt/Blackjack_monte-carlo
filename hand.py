# hand.py

from card import Card

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    @property
    def value(self):
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def value_ace(self):
        values = [0]
        for card in self.cards:
            if card.rank == 'A':
                values = [v + x for v in values for x in [1, 11]]
            else:
                values = [v + card.value for v in values]
        unique_values = sorted(set(values))
        valid_values = [v for v in unique_values if v <= 21]
        if not valid_values:
            valid_values = [min(unique_values)]
        return valid_values

    def __repr__(self):
        return f"Hand({self.cards})"

    def is_pair(self):
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def has_ace(self):
        return any(card.rank == 'A' for card in self.cards)

    def is_blackjack(self):
        return len(self.cards) == 2 and self.value == 21
