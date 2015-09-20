from aot import get_cards_list


def test_bishop():
    cards = get_cards_list(None)
    for card in cards:
        if card.name == 'Bishop':
            assert len(card.colors) == 2
