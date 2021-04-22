import typing
import enum
import random
import operator
import itertools


class Card(object):
    """
    A card object that holds the suit and value for a given card.

    Attributes:
        suit (str): One of ""
        values (list[int]): Description
    """

    VALID_SUITS = ["HEART", "DIAMOND", "SPADE", "CLUB",]
    EMOJI_CARDS = {
        (1, "CLUB",): "<:ace_of_clubs:613975944490778626>",
        (1, "DIAMOND",): "<:ace_of_diamonds:614064395420565504>",
        (1, "HEART",): "<:ace_of_hearts:613989868271304706>",
        (1, "SPADE",): "<:ace_of_spades:614064879992832000>",
        (2, "CLUB",): "<:two_of_clubs:613975947162550282>",
        (2, "DIAMOND",): "<:two_of_diamonds:614064395114381314>",
        (2, "HEART",): "<:two_of_hearts:613989868380487690>",
        (2, "SPADE",): "<:two_of_spades:614065256574091285>",
        (3, "CLUB",): "<:three_of_clubs:613975945015197697>",
        (3, "DIAMOND",): "<:three_of_diamonds:614064395491868703>",
        (3, "HEART",): "<:three_of_hearts:613989868267241475>",
        (3, "SPADE",): "<:three_of_spades:614065256687337483>",
        (4, "CLUB",): "<:four_of_clubs:613975944545304590>",
        (4, "DIAMOND",): "<:four_of_diamonds:614064395156455454>",
        (4, "HEART",): "<:four_of_hearts:613989868317573120>",
        (4, "SPADE",): "<:four_of_spades:614064880068067338>",
        (5, "CLUB",): "<:five_of_clubs:613975944952152084>",
        (5, "DIAMOND",): "<:five_of_diamonds:614064395131289640>",
        (5, "HEART",): "<:five_of_hearts:613989868023971861>",
        (5, "SPADE",): "<:five_of_spades:614064879996764170>",
        (6, "CLUB",): "<:six_of_clubs:613975946634067978>",
        (6, "DIAMOND",): "<:six_of_diamonds:614064395328159803>",
        (6, "HEART",): "<:six_of_hearts:613989868334481428>",
        (6, "SPADE",): "<:six_of_spades:614064880001089566>",
        (7, "CLUB",): "<:seven_of_clubs:613975944948088862>",
        (7, "DIAMOND",): "<:seven_of_diamonds:614064395332616213>",
        (7, "HEART",): "<:seven_of_hearts:613989868304859136>",
        (7, "SPADE",): "<:seven_of_spades:614064880017997854>",
        (8, "CLUB",): "<:eight_of_clubs:613975944788574208>",
        (8, "DIAMOND",): "<:eight_of_diamonds:614064395152130058>",
        (8, "HEART",): "<:eight_of_hearts:613989868774621200>",
        (8, "SPADE",): "<:eight_of_spades:614064880042901504>",
        (9, "CLUB",): "<:nine_of_clubs:613975944776122375>",
        (9, "DIAMOND",): "<:nine_of_diamonds:614064395160387604>",
        (9, "HEART",): "<:nine_of_hearts:613989868179161101>",
        (9, "SPADE",): "<:nine_of_spades:614064879636054018>",
        (10, "CLUB",): "<:ten_of_clubs:613975944981643281>",
        (10, "DIAMOND",): "<:ten_of_diamonds:614064395328159754>",
        (10, "HEART",): "<:ten_of_hearts:613989868359647233>",
        (10, "SPADE",): "<:ten_of_spades:614064880072392726>",
        (11, "CLUB",): "<:jack_of_clubs:613975944885043200>",
        (11, "DIAMOND",): "<:jack_of_diamonds:614064395038752779>",
        (11, "HEART",): "<:jack_of_hearts:613989868208521226>",
        (11, "SPADE",): "<:jack_of_spades:614064880017735700>",
        (12, "CLUB",): "<:queen_of_clubs:613975945027780618>",
        (12, "DIAMOND",): "<:queen_of_diamonds:614064395332616193>",
        (12, "HEART",): "<:queen_of_hearts:613989868393201684>",
        (12, "SPADE",): "<:queen_of_spades:614064879988506654>",
        (13, "CLUB",): "<:king_of_clubs:613975944855552031>",
        (13, "DIAMOND",): "<:king_of_diamonds:614064395328159763>",
        (13, "HEART",): "<:king_of_hearts:613989868380487710>",
        (13, "SPADE",): "<:king_of_spades:614064880076718091>",
        None: "<:card_back:834578062514585652>",
    }
    CARD_BACK = EMOJI_CARDS[None]
    __slots__ = ("_value", "suit",)

    def __init__(self, value: int, suit: str):
        """
        Args:
            value (int): The value that the card has.
            suit (str): The suit of the card.
        """

        self._value = value
        self.suit: str = suit.upper()
        if self.suit not in self.VALID_SUITS:
            raise ValueError("Given value %s for suit was not valid - %s", self.suit, self.VALID_SUITS)

    def get_values(self) -> typing.List[int]:
        if self._value == 1:
            return [1, 11,]
        elif self._value == 11:
            return [10,]  # Jack
        elif self._value == 12:
            return [10,]  # Queen
        elif self._value == 13:
            return [10,]  # King
        return [self._value,]

    @property
    def emoji(self) -> str:
        return self.EMOJI_CARDS[(self._value, self.suit,)]

    @property
    def name(self) -> str:
        card_name = {
            1: "Ace",
            11: "Jack",
            12: "Queen",
            13: "King",
        }.get(self._value, str(self._value))
        return f"{card_name} of {self.suit.title()}s"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r}, {self.suit!r})"

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can't compare types: %s and %s", self.__class__.name, other.__class__.__name__)
        return max(self.get_values()) >= max(other.get_values())

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can't compare types: %s and %s", self.__class__.name, other.__class__.__name__)
        return max(self.get_values()) > max(other.get_values())

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can't compare types: %s and %s", self.__class__.name, other.__class__.__name__)
        return max(self.get_values()) <= max(other.get_values())

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can't compare types: %s and %s", self.__class__.name, other.__class__.__name__)
        return max(self.get_values()) < max(other.get_values())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can't compare types: %s and %s", self.__class__.name, other.__class__.__name__)
        return max(self.get_values()) == max(other.get_values())

    def __hash__(self):
        return hash((self._value, self.suit,))


class Deck(object):

    def __init__(self, cards: typing.List[Card] = None):
        self._cards: typing.List[Card] = cards or list()

    @classmethod
    def create_deck(cls, shuffle: typing.Union[bool, random.Random] = True) -> "Deck":
        """
        Make a deck of cards, unshuffled, containing all 52 cards in a deck.
        """

        cards = list()
        for v in range(1, 14):
            for s in Card.VALID_SUITS:
                cards.append(Card(v, s))
        v = cls(cards)
        if shuffle:
            if isinstance(shuffle, random.Random):
                v.shuffle(shuffle)
            else:
                v.shuffle()
        return v

    def shuffle(self, *, cls: random.Random = None):
        """
        Shuffles the internal deck of cards.
        """

        if cls is None:
            cls = random
        cls.shuffle(self._cards)

    def draw(self, amount: int = 1) -> typing.List[Card]:
        """
        Draw a card from the deck, removing it.

        Returns:
            Card: The card that was drawn.
        """

        if amount < 1:
            raise ValueError("Numbers lower than 1 are not supported for drawing from the deck")
        return [self._cards.pop(0) for i in range(amount)]


class Hand(Deck):

    def __init__(self, deck: Deck):
        self.deck = deck
        super().__init__()

    @classmethod
    def create_deck(cls):
        return cls()

    def draw(self, amount: int = 1) -> typing.List[Card]:
        """
        Draws a card from the deck and adds it to the current hand.
        """

        cards = self.deck.draw(amount)
        for c in cards:
            self.add(c)
        return cards

    def add(self, card: Card) -> None:
        """
        Adds a single card to your hand.
        """

        self._cards.append(card)

    def sort(self) -> None:
        """
        Sorts your hand.
        """

        self._cards.sort(key=operator.attrgetter("_value", "suit",))

    def remove(self, card: Card) -> None:
        """
        Removes a card from your hand.
        """

        self._cards.remove(card)

    def __str__(self):
        return self._cards

    def get_values(self, *, cast: typing.Callable[[int], typing.Any] = None, max_value: int = None):
        """
        Get the possible values of your current hand.
        """

        max_value = max_value or float("inf")
        hand_values = [i.get_values() for i in self._cards]
        hand_value_permutations = list(itertools.product(*hand_values))
        v = sorted(list(set([sum(i) for i in hand_value_permutations])), reverse=True)
        cast = cast or (lambda x: x)
        return [cast(i) for i in sorted(v, reverse=True) if i <= max_value]

    def display(self, show_cards: typing.Union[bool, int] = True):
        """
        Shows the emojis for each of the cards in your hand.
        """

        if show_cards is True:
            return "".join([i.emoji for i in self._cards])
        elif show_cards is False:
            return "".join([Card.CARD_BACK for i in self._cards])
        else:
            shown_cards = "".join([self._cards[i].emoji for i in range(show_cards)])
            non_shown_cards = "".join([Card.CARD_BACK for i in range(len(self._cards) - show_cards)])
            return shown_cards + non_shown_cards
