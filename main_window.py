import arcade
from consts import *
from character import PlayerCharacter


class MainMenu(arcade.View):
    """Главное меню игры"""

    def on_show_view(self):
        arcade.set_background_color((21, 11, 59))

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Other planet - Click to play",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = MyGame()
        self.window.show_view(game_view)


class MyGame(arcade.View):
    """
    Основной геймплей.
    """

    def __init__(self):
        super().__init__()
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.tile_map = None
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.reset_score = True
        self.end_of_map = 0
        self.level = 1
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin3.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump3.wav")
        self.game_over = arcade.load_sound(":resources:sounds/lose5.wav")

    def setup(self):
        """Метод настраивает основной функционал игры"""

        # Установка камеры, откуда мы будем начинать игру
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        map_name = f"C:/Users/Admin/PycharmProjects/my_game/lvl_{self.level}.tmx"

        # для взаимодействия со слоями карты
        layer_options = {
            LAYER_NAME_PLATFORMS: {"use_spatial_hash": True},
            LAYER_NAME_COINS: {"use_spatial_hash": True},
            LAYER_NAME_DONT_TOUCH: {"use_spatial_hash": True},
            LAYER_NAME_LADDERS: {"use_spatial_hash": True},
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # выгружаем карту. Все слои автоматически будут сохранены как SpriteLists
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        if self.reset_score:
            self.score = 0
        self.reset_score = True

        # Добавить список спрайтов игрока перед слоем «Foreground». Так передний план будет рисоваться после персонажа,
        # оставляя последнего на заднем плане.
        self.scene.add_sprite_list_after(LAYER_NAME_PLAYER, LAYER_NAME_FOREGROUND)

        # Задание начальных координат игрока
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Высчитываем правый край карты в пикселях
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Вызываем игровой движок 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            platforms=self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()

        score_text = f"coins: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

    def process_keychange(self):
        # вверх/вниз
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # вверх/вниз по лестнице
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # влево/вправо
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def update(self, delta_time):
        """Реализация движения и игровой логики"""

        # задаем движение персонажа с помощью движка
        self.physics_engine.update()

        # обновление анимации
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.scene.update_animation(delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND, LAYER_NAME_PLAYER])

        # сбор монет
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )

        # убираем монету с карты и добавляем в кошелёк
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # проверяем чтобы игрок не вышел за пределы карты
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)

        # проверяем не коснулся ли персонаж смертельной зоны
        if arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)
            game_over = GameOverView()
            self.window.show_view(game_over)
            return

        # проверяем дошел ли игрок до конца карты уровня
        if self.player_sprite.center_x >= self.end_of_map:
            if self.level == 2:
                game_passed = GamePassed()
                self.window.show_view(game_passed)
                return
            else:
                self.level += 1
            self.reset_score = False
            # загрузка нового уровня
            self.setup()
        self.center_camera_to_player()


class GameOverView(arcade.View):

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Game Over - Click to restart",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = MyGame()
        self.window.show_view(game_view)


class GamePassed(arcade.View):

    def on_show_view(self):
        arcade.set_background_color((37, 49, 71))

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Game Passed - Click to restart or you can exit",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = MyGame()
        self.window.show_view(game_view)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenu()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
