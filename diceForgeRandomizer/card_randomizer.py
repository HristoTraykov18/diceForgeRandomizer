import os
import random
from glob import glob
from re import search
from sys import platform

from PIL import Image


class DiceForgeRandomizer():
    '''Dice Forge Randomizer class'''
    CARDS_PER_BOARD_SIDE = 7
    GAME_MODULES = ('base', 'goddess', 'titans')

    def __init__(self):
        self.active_module = random.choice(self.GAME_MODULES)
        self.boss_card = ''
        self.board_path = ''
        self.delimiter = '/'

        if 'win' in platform:
            self.delimiter = '\\'

    def run(self):
        parent_folder = os.path.dirname(__file__)
        self.board_path = f'{parent_folder}/img/board.png'
        boss_cards_folder = parent_folder + \
            f'{self.delimiter}img{self.delimiter}boss'
        moon_cards_folder = parent_folder + \
            f'{self.delimiter}img{self.delimiter}moon'
        sun_cards_folder = parent_folder + \
            f'{self.delimiter}img{self.delimiter}sun'

        boss_cards_paths = glob(f'{boss_cards_folder}/*')
        moon_cards_paths, sun_cards_paths = self._get_cards_lists(
            moon_cards_folder, sun_cards_folder)

        self.boss_card = random.choice(boss_cards_paths)
        moon_cards = self._get_filenames_from_list(
            moon_cards_folder, moon_cards_paths)
        sun_cards = self._get_filenames_from_list(
            sun_cards_folder, sun_cards_paths)

        random_moon_cards = []
        random_sun_cards = []

        for i in range(self.CARDS_PER_BOARD_SIDE):
            random_moon_cards.append(
                moon_cards_folder + self.delimiter + random.choice(self._get_cards_per_row(i, moon_cards)))
            random_sun_cards.append(
                sun_cards_folder + self.delimiter + random.choice(self._get_cards_per_row(i, sun_cards)))

        with Image.open(self.board_path) as board:
            self._add_cards_to_board_sides(
                board, random_moon_cards, random_sun_cards)
            boss = Image.open(self.boss_card)
            boss = boss.convert('RGBA')
            boss_pos = (int((board.size[0] - boss.size[0]) / 2), 0)
            board.paste(boss, boss_pos, boss)
            board.save(f'{parent_folder}/Dice Forge.png')

    def _add_cards_to_board_sides(self, board, moon_cards, sun_cards):
        '''Add the card images to the main board image'''
        INITIAL_MARGIN = 448
        SMALL_MARGIN = 80
        LARGE_MARGIN = 170

        for i in range(self.CARDS_PER_BOARD_SIDE):
            moon_card = Image.open(moon_cards[i])
            sun_card = Image.open(sun_cards[i])

            y_pos = INITIAL_MARGIN + \
                (i * moon_card.size[0]) + (int((i + 1) / 2) * SMALL_MARGIN)

            if i > 1:
                y_pos += (int(i / 2) * LARGE_MARGIN)

            if i < 6:
                moon_card = moon_card.convert('RGBA').rotate(90, expand=True)
                sun_card = sun_card.convert('RGBA').rotate(-90, expand=True)
            else:
                moon_card = moon_card.convert('RGBA').rotate(60, expand=True)
                sun_card = sun_card.convert('RGBA').rotate(-60, expand=True)
                y_pos += SMALL_MARGIN + LARGE_MARGIN

            pos_moon = (0, board.size[1] - y_pos)
            pos_sun = (board.size[0] - sun_card.size[0],
                       board.size[1] - y_pos)

            if i == 6:
                # Some pretty, unknown to anyone, numbers used to position the images precisely
                pos_moon = (pos_moon[0] + 65, pos_moon[1] + 40)
                pos_sun = (pos_sun[0] - 65, pos_sun[1] + 55)

            board.paste(moon_card, pos_moon, moon_card)
            board.paste(sun_card, pos_sun, sun_card)

    def _get_cards_lists(self, *cards):
        '''Get separate lists for moon and sun cards'''
        moon_cards_paths = glob(f'{cards[0]}{self.delimiter}?_?.png')
        sun_cards_paths = glob(f'{cards[1]}{self.delimiter}?_?.png')

        if self.active_module != self.GAME_MODULES[0]:
            module_moon_cards = glob(
                f'{cards[0]}{self.delimiter}?_{self.active_module}.png')
            module_sun_cards = glob(
                f'{cards[1]}{self.delimiter}?_{self.active_module}.png')
            module_moon_cards_pattern = ''.join(
                map(str, self._get_filenames_from_list(cards[0], module_moon_cards)))
            module_sun_cards_pattern = ''.join(
                map(str, self._get_filenames_from_list(cards[1], module_sun_cards)))
            module_moon_cards_pattern = f'[{module_moon_cards_pattern}]_[0-9].png$'
            module_sun_cards_pattern = f'[{module_sun_cards_pattern}]_[0-9].png$'

            moon_cards_paths = list(filter(lambda card: search(
                module_moon_cards_pattern, card) is None, moon_cards_paths))
            sun_cards_paths = list(filter(lambda card: search(
                module_sun_cards_pattern, card) is None, sun_cards_paths))

            moon_cards_paths += module_moon_cards
            sun_cards_paths += module_sun_cards

        return (moon_cards_paths, sun_cards_paths)

    def _get_cards_per_row(self, row_num, cards_list):
        '''Get cards for each row on the board'''
        i = row_num
        cards_per_row = []
        cards_list_len = len(cards_list)

        if self.active_module == self.GAME_MODULES[0]:
            while int(cards_list[i][0]) < row_num:
                i += 1
        else:
            while i < cards_list_len - 1 and int(cards_list[i][0]) != row_num:
                i += 1

        while cards_list[i].startswith(str(row_num)):
            cards_per_row.append(cards_list[i])

            if i < cards_list_len - 1:
                i += 1
            else:
                break

        return cards_per_row

    def _get_filenames_from_list(self, directory, paths):
        '''Get only the names of the files'''
        return [path.removeprefix(directory).strip(self.delimiter)
                for path in paths]


if __name__ == "__main__":
    dfr = DiceForgeRandomizer()
    dfr.run()
