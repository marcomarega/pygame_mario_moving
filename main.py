import pygame

import sys
import os


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Tile, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y


class TileDesc:
    def __init__(self, image):
        self.image = image

    def get_tile(self, x, y):
        return Tile(self.image, x, y)


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Character, self).__init__(character_group)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y


class Toroid:
    def __init__(self, level, level_x, level_y):
        self.level = level
        self.level_x = level_x
        self.level_y = level_y

        self.tile_descs = list()
        for row in self.level:
            self.tile_descs.append(list())
            for el in row:
                if el != '@':
                    self.tile_descs[-1].append(TileDesc(tiles_image[el]))
                else:
                    self.tile_descs[-1].append(TileDesc(tiles_image['.']))

        self.shift_x = 0
        self.shift_y = 0

    def set_d_shift(self, dx, dy):
        self.shift_x += dx
        self.shift_y += dy

    def get_tile_desc(self, x, y):
        return self.tile_descs[(y - self.shift_y) % self.level_y][(x - self.shift_x) % self.level_x]

    def get_view(self, count_x, count_y):
        view_group = pygame.sprite.Group()
        for i in range(count_x):
            for j in range(count_y):
                tile = self.tile_descs[(j - self.shift_y) % self.level_y][(i - self.shift_x) % self.level_x].\
                    get_tile(i * TILE_SIZE, j * TILE_SIZE)
                tile.add(view_group)
        return view_group


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for x in range(len(level)):
        for y in range(len(level[x])):
            if level[x][y] == '@':
                new_player = Character(y * TILE_SIZE, x * TILE_SIZE)
    # вернем игрока, а также размер поля в клетках
    return new_player, y + 1, x + 1


SIZE = WIDTH, HEIGHT = 450, 450
TILE_SIZE = 50

pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Перемещение героя. Новый уровень")

clock = pygame.time.Clock()
FPS = 50


tiles_image = {
    '.': load_image("grass.png"),
    '#': load_image("box.png"),
}
player_image = load_image("mario.png")

character_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["MARIO: La gioca italiana", "",
                  "Правила игры",
                  "Перемещать Mario можно",
                  "только по траве,",
                  "на коробки залезать",
                  "нельзя"]

    screen.fill(pygame.Color("white"))
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 25)
    text_coord = 250
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 220
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def level(map_filename):
    level = load_level(map_filename)
    character, level_x, level_y = generate_level(level)
    toroid = Toroid(level, level_x, level_y)
    shift_x = -(character.rect.x + TILE_SIZE // 2 - WIDTH // 2) // TILE_SIZE
    shift_y = -(character.rect.y + TILE_SIZE // 2 - HEIGHT // 2) // TILE_SIZE
    # shift_x, shift_y = 0, 0
    character.set_pos(character.rect.x + shift_x * TILE_SIZE + 15, character.rect.y + shift_y * TILE_SIZE + 5)
    toroid.set_d_shift(shift_x, shift_y)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                if event.key == pygame.K_RIGHT:
                    dx = 1
                if event.key == pygame.K_UP:
                    dy = -1
                if event.key == pygame.K_DOWN:
                    dy = 1
                x = (character.rect.x - 15) // TILE_SIZE + dx
                y = (character.rect.y - 5) // TILE_SIZE + dy
                if toroid.get_tile_desc(x, y).image != tiles_image['#']:
                    toroid.set_d_shift(-dx, -dy)

        screen.fill((0, 0, 0))
        view_group = toroid.get_view(WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE)
        view_group.draw(screen)
        character_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    start_screen()
    level("minimap.txt")
