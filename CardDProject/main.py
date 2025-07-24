import random
from enum import Enum
from abc import ABC, abstractmethod
import functools
from typing import List, Iterator, Union, Dict, Any, Tuple


class CardSuit(Enum):
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4

class CardRank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class DeckCheatingError(Exception):
    def __init__(self, message: str = "חשד למניפולציה בחפיסת קלפים: פעולה לא חוקית בוצעה."):
        super().__init__(message)

class AbstractCard(ABC):
    @property
    @abstractmethod
    def suit(self) -> CardSuit:
        pass

    @property
    @abstractmethod
    def rank(self) -> CardRank:
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __lt__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __gt__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class AbstractDeck(ABC):
    @property
    @abstractmethod
    def cards(self) -> List['Card']:
        pass

    @abstractmethod
    def shuffle(self):
        pass

    @abstractmethod
    def draw(self) -> Union['Card', None]:
        pass

    @abstractmethod
    def add_card(self, card: 'Card'):
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> 'Card':
        pass

    @abstractmethod
    def __iter__(self) -> Iterator['Card']:
        pass

    @abstractmethod
    def max(self) -> 'Card':
        pass

    @abstractmethod
    def min(self) -> 'Card':
        pass

def fair_deck(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        cards_to_check = []
        if isinstance(self, Deck) and hasattr(self, '_cards'):
            cards_to_check = self._cards
        elif isinstance(result, list) and all(isinstance(c, Card) for c in result):
            cards_to_check = result

        if cards_to_check:
            seen_cards = set()
            for card in cards_to_check:
                if card in seen_cards:
                    raise DeckCheatingError(f"Illegal deck: duplicate card found in deck: {card}")
                seen_cards.add(card)
        return result

    return wrapper

class Card(AbstractCard):
    def __init__(self, rank: CardRank, suit: CardSuit):
        if not isinstance(rank, CardRank) or not isinstance(suit, CardSuit):
            raise ValueError("Rank and Suit must be valid Enum members.")
        self._rank = rank
        self._suit = suit

    @property
    def rank(self) -> CardRank:
        return self._rank

    @property
    def suit(self) -> CardSuit:
        return self._suit

    def get_display_name(self) -> str:
        rank_name = self.rank.name.replace('_', ' ').title()
        suit_name = self.suit.name.replace('_', ' ').title()
        return f"{rank_name} of {suit_name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            raise TypeError(f"Can only compare Card with an object of type Card, not with {type(other).__name__}.")
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            raise TypeError(f"Can only compare Card with an object of type Card, not with {type(other).__name__}.")

        if self.rank.value < other.rank.value:
            return True
        elif self.rank.value > other.rank.value:
            return False
        else:
            return self.suit.value < other.suit.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            raise TypeError(f"Can only compare Card with an object of type Card, not with {type(other).__name__}.")

        if self.rank.value > other.rank.value:
            return True
        elif self.rank.value < other.rank.value:
            return False
        else:
            return self.suit.value > other.suit.value

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    def __str__(self) -> str:
        return self.get_display_name()

    def __repr__(self) -> str:
        return f"Card(rank=CardRank.{self.rank.name}, suit=CardSuit.{self.suit.name})"

class Deck(AbstractDeck):
    def __init__(self, shuffle: bool = True):
        self._cards: List[Card] = []
        for suit in CardSuit:
            for rank in CardRank:
                self._cards.append(Card(rank, suit))

        if shuffle:
            self.shuffle()

        self._draw_index = 0

    @property
    @fair_deck
    def cards(self) -> List[Card]:
        return list(self._cards[self._draw_index:])

    def shuffle(self):
        random.shuffle(self._cards)
        self._draw_index = 0

    def draw(self) -> Union[Card, None]:
        if self._draw_index >= len(self._cards):
            return None

        card = self._cards[self._draw_index]
        self._draw_index += 1
        return card

    @fair_deck
    def add_card(self, card: Card):
        if not isinstance(card, Card):
            raise TypeError("Only objects of type Card can be added to the deck.")

        if card in self._cards[self._draw_index:]:
            raise DeckCheatingError(f"Card '{card}' already exists in the deck. Cheating suspected!")

        self._cards.append(card)

    def __len__(self) -> int:
        return len(self._cards) - self._draw_index

    def __getitem__(self, index: int) -> Card:
        if not isinstance(index, int):
            raise TypeError("Index must be an integer.")

        actual_index = self._draw_index + index
        if 0 <= index < len(self):
            return self._cards[actual_index]
        else:
            raise IndexError(f"Index {index} out of bounds for the remaining deck (size: {len(self)}).")

    def __iter__(self) -> Iterator[Card]:
        return iter(self._cards[self._draw_index:])

    def max(self) -> Card:
        if not self._cards[self._draw_index:]:
            raise ValueError("No cards in the deck to find the maximum.")
        return max(self._cards[self._draw_index:])

    def min(self) -> Card:
        if not self._cards[self._draw_index:]:
            raise ValueError("No cards in the deck to find the minimum.")
        return min(self._cards[self._draw_index:])


def max_card(*cards: Card) -> Card:
    if not cards:
        raise ValueError("At least one card must be provided to find the maximum.")

    for card in cards:
        if not isinstance(card, Card):
            raise TypeError(f"All arguments must be of type Card, found {type(card).__name__}.")

    return max(cards)


def cards_stats(*cards: Card, **kwargs: int) -> Dict[str, Union[Card, int, List[Card]]]:
    if not cards:
        raise ValueError("Cards must be provided to get statistics.")

    results = {}
    sorted_cards = sorted(cards)

    for key, value in kwargs.items():
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"Invalid value for '{key}': must be a positive integer.")

        if key == 'max':
            if value > len(sorted_cards):
                value = len(sorted_cards)
            results['max'] = sorted_cards[-value:]
        elif key == 'min':
            if value > len(sorted_cards):
                value = len(sorted_cards)
            results['min'] = sorted_cards[:value]
        elif key == 'len':
            results['len'] = len(cards)
        else:
            print(f"Warning: Unknown request in kwargs: '{key}'. Ignoring.")

    return results


def main():
    print("--- Demonstrating Card and Deck Classes ---")

    card1 = Card(CardRank.ACE, CardSuit.SPADES)
    card2 = Card(CardRank.KING, CardSuit.HEARTS)
    card3 = Card(CardRank.TWO, CardSuit.CLUBS)
    card4 = Card(CardRank.ACE, CardSuit.DIAMONDS)
    card5 = Card(CardRank.TEN, CardSuit.CLUBS)

    print(f"\nCard 1: {card1} (debugging representation: {repr(card1)})")
    print(f"Card 2: {card2}")
    print(f"Card 3: {card3}")
    print(f"Card 4: {card4}")
    print(f"Card 5: {card5}")

    print("\n--- Demonstrating Card Comparisons (dunder methods) ---")
    print(f"{card1} == {card4}? {card1 == card4}")
    print(f"{card1} > {card2}? {card1 > card2}")
    print(f"{card2} < {card3}? {card2 < card3}")
    print(f"{card1} > {card4}? {card1 > card4}")
    print(f"{card3} < {card5}? {card3 < card5}")

    try:
        _ = card1 == "string"
    except TypeError as e:
        print(f"Expected error when comparing card with string: {e}")

    print("\n--- Creating a Deck and Basic Operations ---")
    deck = Deck()
    print(f"New deck created with {len(deck)} cards.")

    print("\nCards in deck (first few, via fair_deck decorated cards property):")
    try:
        first_5_cards = deck.cards[:5]
        for card in first_5_cards:
            print(f"  {card}")
        print("...")
    except DeckCheatingError as e:
        print(f"Cheating error caught when accessing cards property: {e}")

    drawn_card = deck.draw()
    if drawn_card:
        print(f"\nCard drawn: {drawn_card}. Remaining cards: {len(deck)}.")
    else:
        print("\nDeck is empty, cannot draw a card.")

    print(f"\n--- Demonstrating adding a card and fair_deck on add_card ---")
    card_to_add = Card(CardRank.SEVEN, CardSuit.CLUBS)
    try:
        deck.add_card(card_to_add)
        print(f"Card {card_to_add} added to deck. Remaining cards: {len(deck)}.")
    except DeckCheatingError as e:
        print(f"Expected cheating error when adding card: {e} (deck size remains: {len(deck)})")
    except Exception as e:
        print(f"Other error when adding card: {e}")

    print("\n--- Attempting to add an existing card (DeckCheatingError demo) ---")
    if len(deck) > 0:
        existing_card_in_deck = deck[0]
        try:
            print(f"Attempting to add an already existing card to the deck: {existing_card_in_deck}")
            deck.add_card(existing_card_in_deck)
        except DeckCheatingError as e:
            print(f"Cheating error caught when adding existing card: {e}")
        except Exception as e:
            print(f"Other error: {e}")
    else:
        print("Deck is empty, cannot demonstrate adding an existing card.")

    print("\n--- Direct access to cards by index (dunder __getitem__) ---")
    try:
        print(f"Card at index 0 (among remaining cards): {deck[0]}")
        if len(deck) > 10:
            print(f"Card at index 10 (among remaining cards): {deck[10]}")
        print(f"Last card in deck (among remaining cards): {deck[len(deck) - 1]}")
        _ = deck[len(deck)]
    except IndexError as e:
        print(f"Expected IndexError: {e}")
    except TypeError as e:
        print(f"Expected TypeError: {e}")

    print("\n--- Iterating through all cards in the deck (using for loop) ---")
    count = 0
    for card in deck:
        print(card)
        count += 1
        if count >= 10:
            print("...")
            break
    print(f"Number of cards iterated: {count}. Deck size still: {len(deck)}")

    print("\n--- Minimum and Maximum card in the deck (max/min methods) ---")
    try:
        if len(deck) > 0:
            print(f"Lowest card in the deck: {deck.min()}")
            print(f"Highest card in the deck: {deck.max()}")
        else:
            print("Deck is empty, cannot find minimum and maximum.")
    except ValueError as e:
        print(f"Error (expected if deck is empty): {e}")

    print("\n--- Demonstrating global max_card function ---")
    test_cards_for_max = [
        Card(CardRank.QUEEN, CardSuit.DIAMONDS),
        Card(CardRank.SEVEN, CardSuit.SPADES),
        Card(CardRank.KING, CardSuit.CLUBS),
        Card(CardRank.ACE, CardSuit.HEARTS),
        Card(CardRank.ACE, CardSuit.CLUBS)
    ]
    print(f"Cards for testing: {[str(c) for c in test_cards_for_max]}")
    print(f"Highest card among them: {max_card(*test_cards_for_max)}")

    try:
        max_card(card1, "not a card")
    except TypeError as e:
        print(f"Expected error in max_card (invalid argument): {e}")
    try:
        max_card()
    except ValueError as e:
        print(f"Expected error in max_card (no cards): {e}")

    print("\n--- Demonstrating global cards_stats function ---")
    stats_cards = [
        Card(CardRank.ACE, CardSuit.SPADES),
        Card(CardRank.TWO, CardSuit.HEARTS),
        Card(CardRank.ACE, CardSuit.DIAMONDS),
        Card(CardRank.KING, CardSuit.CLUBS),
        Card(CardRank.THREE, CardSuit.SPADES),
        Card(CardRank.NINE, CardSuit.HEARTS)
    ]
    print(f"Cards for stats testing: {[str(c) for c in stats_cards]}")

    results = cards_stats(*stats_cards, max=2, min=1, len=1, average=1)
    print("Statistics results:")
    for key, value in results.items():
        if isinstance(value, list):
            print(f"  {key}: {[str(c) for c in value]}")
        else:
            print(f"  {key}: {value}")

    try:
        cards_stats(*stats_cards, max="two")
    except ValueError as e:
        print(f"Expected error in cards_stats (invalid value): {e}")
    try:
        cards_stats()
    except ValueError as e:
        print(f"Expected error in cards_stats (no cards): {e}")

    print("\n--- End of Demonstrations ---")


if __name__ == "__main__":
    main()