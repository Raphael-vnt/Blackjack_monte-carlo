# blackjack_game.py

from deck import Deck
from hand import Hand

class BlackjackGame:
    def __init__(self, min_bet, initial_bet, num_decks, reshuffle_pct):
        self.min_bet = min_bet
        self.initial_bet = initial_bet
        self.num_decks = num_decks
        self.reshuffle_pct = reshuffle_pct
        self.deck = Deck(num_decks)
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.bet = initial_bet

    def reshuffle_needed(self):
        return (self.deck.cards_left() / (52 * self.num_decks)) < (self.reshuffle_pct / 100)

    def initial_deal(self):
        for hand in self.player_hands:
            hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        for hand in self.player_hands:
            hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

    def dealer_action(self):
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal())

    def play_round(self, player_strategy):
        info_round = ""
        if self.reshuffle_needed():
            self.deck = Deck(self.num_decks)
            info_round += "Reshuffling the deck...\n"

        self.bet = self.initial_bet
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.initial_deal()

        nb_hands = 1
        index_hands = 0
        list_bets = [self.bet]
        while nb_hands > 0:
            hand = self.player_hands[index_hands]
            list_bets[index_hands] = list_bets[index_hands]

            info_round += f"Player's hand: {hand}\n"
            info_round += f"Dealer's hand: {self.dealer_hand.cards[0]} and [Hidden]\n"

            while hand.value < 21 and player_strategy(hand, self.dealer_hand.cards[0]) == 'H':
                hand.add_card(self.deck.deal())
                info_round += f"Player hits: {hand}\n"

            if hand.value < 21 and len(hand.cards) == 2 and player_strategy(hand, self.dealer_hand.cards[0]) == 'D':
                list_bets[index_hands] = list_bets[index_hands] * 2
                hand.add_card(self.deck.deal())
                info_round += f"Player doubles: {hand}\n"

            if hand.is_pair() and player_strategy(hand, self.dealer_hand.cards[0]) == 'SP':
                nb_hands += 2
                list_bets.append(self.bet)

                new_hand = Hand()
                new_hand.add_card(hand.cards.pop())
                hand.add_card(self.deck.deal())
                new_hand.add_card(self.deck.deal())

                self.player_hands.pop(index_hands)
                index_hands -= 1
                self.player_hands.append(hand)
                self.player_hands.append(new_hand)

                info_round += f"Player splits: {hand} and {new_hand}\n"

            info_round += '\n'

            nb_hands -= 1
            index_hands += 1

        self.dealer_action()
        info_round += f"Dealer's hand: {self.dealer_hand}\n\n"
        final_bet = 0

        for i, hand in enumerate(self.player_hands):
            if hand.value > 21:
                info_round += f"Player busts with {hand.value}\n"
                final_bet -= list_bets[i]

            elif hand.is_blackjack() and not self.dealer_hand.is_blackjack():
                final_bet += 1.5 * list_bets[i]
                info_round += f"BLACKJACK! Player wins with {hand.value} against dealer's {self.dealer_hand.value}\n"

            elif self.dealer_hand.value > 21 or hand.value > self.dealer_hand.value:
                final_bet += list_bets[i]
                info_round += f"Player wins with {hand.value} against dealer's {self.dealer_hand.value}\n"

            elif hand.value == self.dealer_hand.value:
                info_round += f"Push with {hand.value}\n"

            else:
                info_round += f"Dealer wins with {self.dealer_hand.value} against player's {hand.value}\n"
                final_bet -= list_bets[i]

        return final_bet, info_round
