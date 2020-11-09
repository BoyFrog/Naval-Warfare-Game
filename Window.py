# Import key libraries
import arcade
import math
import random

# ~~~Defining Constants~~~
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 801
SCREEN_TITLE = "Naval Warfare Game"
# Sprite Size Scaling
SCALING = 1
WEAPON_SCALING = 2
EXPLOSION_SCALING = 4
# Ship Speed limit
MAX_SPEED = 1.5
MIN_SPEED = 0
# Rate of change of ship speed
ACCELERATION_RATE = 0.01
# Rate of change of ship angle
ANGLE_SPEED = 1
AIM_DISTANCE_SPEED = 5
AIM_ANGLE_SPEED = 2
WEAPON_COOLDOWN_TIME = 1
MAX_AIM_DISTANCE = 350
MIN_AIM_DISTANCE = 75
# Setup Variables
ENEMY_SHIP_NUMBER = 3
DISTANCE_FROM_START = SCREEN_HEIGHT / 4
AI_OUTER_DISTANCE = 100
AI_INNER_DISTANCE = 125


class Projectile(arcade.Sprite):
    # Init the class
    def __init__(self, image, scaling, angle):
        self.start_x = None
        self.start_y = None
        self.distance_to_travel = None
        # Init the parent
        super().__init__(image, scaling)
        self.change_x = self.speed * math.cos(math.radians(angle))
        self.change_y = self.speed * math.sin(math.radians(angle))
        self.angle = angle


class Torpedo(Projectile):
    # Init the class
    def __init__(self, scaling, angle):
        # Init the parent
        self.speed = 5
        self.distance = 0
        self.origin = None
        super().__init__("Images/Torpedo.png", scaling, angle)
        self.alpha = 63
        self.color = [0, 0, 127]

    def update3(self, explosion_list, all_sprites):
        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # If torpedo has reached it's endpoint then make an explosion
        self.distance = ((self.center_x - self.start_x) ** 2 + (self.center_y - self.start_y) ** 2) ** 0.5

        if self.distance >= self.distance_to_travel:
            self.remove_from_sprite_lists()

            explosion = arcade.Sprite("Images/Explosion.png", EXPLOSION_SCALING)
            explosion.center_x = self.center_x
            explosion.center_y = self.center_y

            explosion_list.append(explosion)
            all_sprites.append(explosion)

        # If it is off the window then remove it
        elif self.right < 0 \
                or self.left > arcade.get_window().width - 1 \
                or self.top < 0 \
                or self.bottom > arcade.get_window().height - 1:
            self.remove_from_sprite_lists()


class Ship(arcade.Sprite):
    # Init the class
    def __init__(self, image):
        self.speed = 0
        self.hp = 1000
        self.identifier = None
        # Init the parent
        super().__init__(image, SCALING)

        self.cooldown_time = WEAPON_COOLDOWN_TIME

    def on_update(self, delta_time):
        # Update ship's position based on ship's direction and speed
        self.center_x += self.speed * math.cos(math.radians(self.angle))
        self.center_y += self.speed * math.sin(math.radians(self.angle))

        self.cooldown_time += delta_time

        # Wall Collision
        # Check to see if we hit the screen edge
        if self.left < 0:
            self.left = 0
        elif self.right > arcade.get_window().width - 1:
            self.right = arcade.get_window().width - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > arcade.get_window().height - 1:
            self.top = arcade.get_window().height - 1

        # Speed Limits
        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED
        elif self.speed < MIN_SPEED:
            self.speed = MIN_SPEED


class AI(Ship):
    def __init__(self, image):
        super().__init__(image)
        self.left_turn = False
        self.right_turn = False


class Player(Ship):
    # Init the class
    def __init__(self):
        """ Set up the player """
        self.aim_angle = 0
        self.aim_distance = 50
        # Init the parent
        super().__init__("Images/PlayerShip.png")
        self.angle = 90

    def update2(self):
        # aim_distance limits
        if self.aim_distance > MAX_AIM_DISTANCE:
            self.aim_distance = MAX_AIM_DISTANCE
        elif self.aim_distance < MIN_AIM_DISTANCE:
            self.aim_distance = MIN_AIM_DISTANCE


class GameView(arcade.View):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self):
        super().__init__()

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.ship_list = None
        self.all_sprites = None
        self.torpedo_list = None
        self.player_list = None
        self.explosion_list = None
        self.enemy_ship_list = None

        # Set up the player info
        self.player_sprite = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False
        self.space_pressed = False

        self.ai_outer_rect = None
        self.ai_inner_rect = None

        # Set the background colour/color
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_show(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        # Sprite lists
        self.ship_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.torpedo_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.enemy_ship_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.center_y = SCREEN_HEIGHT/2
        self.player_sprite.identifier = 0
        self.player_list.append(self.player_sprite)
        self.ship_list.append(self.player_sprite)
        self.all_sprites.append(self.player_sprite)

        for i in range(ENEMY_SHIP_NUMBER):
            ship = AI("Images/EnemyShip" + str((i % 3) + 1) + ".png")

            ship.identifier = i + 1

            self.all_sprites.append(ship)
            self.ship_list.append(ship)
            self.enemy_ship_list.append(ship)

        i = 0
        for ship in self.ship_list:
            angle = i * 360 / len(self.ship_list)
            ship.center_x = DISTANCE_FROM_START * math.cos(math.radians(angle)) + SCREEN_WIDTH / 2
            ship.center_y = DISTANCE_FROM_START * math.sin(math.radians(angle)) + SCREEN_HEIGHT / 2
            ship.angle = angle
            i += 1

    def on_resize(self, width, height):
        p1 = (AI_OUTER_DISTANCE, AI_OUTER_DISTANCE)
        p2 = (width - AI_OUTER_DISTANCE, AI_OUTER_DISTANCE)
        p3 = (width - AI_OUTER_DISTANCE, height - AI_OUTER_DISTANCE)
        p4 = (AI_OUTER_DISTANCE, height - AI_OUTER_DISTANCE)
        self.ai_outer_rect = [p1, p2, p3, p4]

        p1 = (AI_INNER_DISTANCE, AI_INNER_DISTANCE)
        p2 = (width - AI_INNER_DISTANCE, AI_INNER_DISTANCE)
        p3 = (width - AI_INNER_DISTANCE, height - AI_INNER_DISTANCE)
        p4 = (AI_INNER_DISTANCE, height - AI_INNER_DISTANCE)
        self.ai_inner_rect = [p1, p2, p3, p4]

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        arcade.draw_circle_outline(self.player_sprite.center_x, self.player_sprite.center_y,
                                   self.player_sprite.aim_distance, [0, 75, 120], 3, -1)

        aim_angle = self.player_sprite.aim_angle
        aim_distance = self.player_sprite.aim_distance
        end_x = aim_distance * math.cos(math.radians(aim_angle)) + self.player_sprite.center_x
        end_y = aim_distance * math.sin(math.radians(aim_angle)) + self.player_sprite.center_y
        arcade.draw_line(self.player_sprite.center_x, self.player_sprite.center_y, end_x, end_y, [0, 75, 120], 3)

        # Call draw() on all your sprite lists below
        # Draw all the sprites.
        self.torpedo_list.draw()
        self.explosion_list.draw()
        self.ship_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        """
        Update player ship
        """
        # Apply acceleration based on the keys pressed
        if self.w_pressed and not self.s_pressed:
            self.player_sprite.speed += ACCELERATION_RATE
        elif self.s_pressed and not self.w_pressed:
            self.player_sprite.speed -= ACCELERATION_RATE

        # Change angle based on the keys pressed
        if self.a_pressed and not self.d_pressed:
            self.player_sprite.angle += ANGLE_SPEED * self.player_sprite.speed
        elif self.d_pressed and not self.a_pressed:
            self.player_sprite.angle -= ANGLE_SPEED * self.player_sprite.speed

        # Change aim_distance
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.aim_distance += AIM_DISTANCE_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.aim_distance -= AIM_DISTANCE_SPEED

        # Change aim_angle
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.aim_angle += AIM_ANGLE_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.aim_angle -= AIM_ANGLE_SPEED

        # Player firing torpedo
        if self.space_pressed:
            if self.player_sprite.cooldown_time >= WEAPON_COOLDOWN_TIME:
                self.player_sprite.cooldown_time = 0

                torpedo = Torpedo(WEAPON_SCALING, self.player_sprite.aim_angle)

                torpedo.center_x = self.player_sprite.center_x
                torpedo.center_y = self.player_sprite.center_y
                torpedo.start_x = self.player_sprite.center_x
                torpedo.start_y = self.player_sprite.center_y
                torpedo.distance_to_travel = self.player_sprite.aim_distance
                torpedo.origin = self.player_sprite.identifier

                self.torpedo_list.append(torpedo)
                self.all_sprites.append(torpedo)

        # Explosions
        for explosion in self.explosion_list:
            # If a ship collides with explosion, decrease it's hp
            hit_list = arcade.check_for_collision_with_list(explosion, self.ship_list)
            for ship in hit_list:
                ship.hp -= 5

            # Reduce explosion size and if small enough then remove it
            explosion.scale -= 0.05
            if explosion.scale <= 0:
                explosion.remove_from_sprite_lists()

        # Torpedoes
        for torpedo in self.torpedo_list:
            hit_list = arcade.check_for_collision_with_list(torpedo, self.all_sprites)

            if self.ship_list[torpedo.origin] in hit_list:
                hit_list.remove(self.ship_list[torpedo.origin])

            # If the torpedo did hit something, explode it
            if len(hit_list) > 0:
                torpedo.remove_from_sprite_lists()

                explosion = arcade.Sprite("Images/Explosion.png", EXPLOSION_SCALING)
                explosion.center_x = torpedo.center_x
                explosion.center_y = torpedo.center_y

                self.explosion_list.append(explosion)
                self.all_sprites.append(explosion)

            # If a ship was hit, decrease it's hp
            for sprite in hit_list:
                if sprite in self.ship_list:
                    sprite.hp -= 100

        for ship in self.enemy_ship_list:
            if ship.speed < MAX_SPEED:
                ship.speed += ACCELERATION_RATE

            if not arcade.is_point_in_polygon(ship.center_x, ship.center_y, self.ai_outer_rect)\
                    and not ship.left_turn \
                    and not ship.right_turn:
                if (ship.angle // 45) % 2 == 0:
                    ship.left_turn = True
                else:
                    ship.right_turn = True

            if ship.left_turn:
                ship.angle += ANGLE_SPEED * ship.speed
            elif ship.right_turn:
                ship.angle -= ANGLE_SPEED * ship.speed

            if arcade.is_point_in_polygon(ship.center_x, ship.center_y, self.ai_inner_rect):
                ship.left_turn = False
                ship.right_turn = False

        for ship in self.ship_list:
            if ship.hp <= 0:
                self.ship_list.remove(ship)
                if ship in self.enemy_ship_list:
                    self.enemy_ship_list.remove(ship)
                    if len(self.enemy_ship_list) == 0:
                        print(1)
                else:
                    print(2)

        # Call update to move the sprites
        self.ship_list.on_update(delta_time)
        self.player_sprite.update2()
        for torpedo in self.torpedo_list:
            torpedo.update3(self.explosion_list, self.all_sprites)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.W:
            self.w_pressed = True
        elif key == arcade.key.A:
            self.a_pressed = True
        elif key == arcade.key.S:
            self.s_pressed = True
        elif key == arcade.key.D:
            self.d_pressed = True
        elif key == arcade.key.SPACE:
            self.space_pressed = True

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.W:
            self.w_pressed = False
        elif key == arcade.key.A:
            self.a_pressed = False
        elif key == arcade.key.S:
            self.s_pressed = False
        elif key == arcade.key.D:
            self.d_pressed = False
        elif key == arcade.key.SPACE:
            self.space_pressed = False


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    window.set_maximum_size(window.width, window.height)
    window.maximize()
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()