import arcade
from consts import *


def load_texture_pair(filename):

    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PlayerCharacter(arcade.Sprite):
    """Sprite персонажа"""

    def __init__(self):

        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        main_path = ":resources:images/alien/alienBlue"

        # Загрузка текстур
        self.front_texture_pair = load_texture_pair(f"{main_path}_front.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_walk2.png")

        # Загрузка текстур для ходьбы
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Загрузка текстур для лазанья
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        self.texture = self.front_texture_pair[0]

    def update_animation(self, delta_time: float = 1 / 60):

        # Разворот
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Лазанье
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Прыжки
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Лицом к экрану (front)
        if self.change_x == 0:
            self.texture = self.front_texture_pair[self.character_face_direction]
            return

        # Ходьба
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]
