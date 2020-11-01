# Import key libraries
import arcade
import math

# ~~~Defining Constants~~~
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
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
        super().__init__("Images/Torpedo.png", scaling, angle)
        self.alpha = 63
        self.color = [0, 0, 127]

    def update(self):
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

            arcade.get_window().explosion_list.append(explosion)
            arcade.get_window().all_sprites.append(explosion)

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
        self.hp = 100
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


class Player(Ship):
    # Init the class
    def __init__(self):
        """ Set up the player """
        self.aim_angle = 0
        self.aim_distance = 50
        # Init the parent
        super().__init__("Images/Ship1-x2.png")
        self.angle = 90

    def update2(self):
        # aim_distance limits
        if self.aim_distance > 350:
            self.aim_distance = 350
        elif self.aim_distance < 75:
            self.aim_distance = 75


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.ship_list = None
        self.all_sprites = None
        self.torpedo_list = None
        self.player_list = None
        self.explosion_list = None

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

        self.active_torpedo_distance = None

        # Set the background colour/color
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        # Sprite lists
        self.ship_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.torpedo_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.center_y = SCREEN_HEIGHT/2
        self.player_list.append(self.player_sprite)
        self.ship_list.append(self.player_sprite)
        self.all_sprites.append(self.player_sprite)

        # Set up the distance that determines if the torpedo explodes when it collides with another sprite
        # Creating objects to use their attributes
        ship = Player()
        torpedo = Torpedo(WEAPON_SCALING, 0)

        # The time that has to pass before the torpedo is ahead of the ship that fired it
        ticks = ((ship.width + torpedo.width) / 2) * ((torpedo.speed - MAX_SPEED) ** -1)

        # The distance the torpedo has to travel to be ahead of the ship that fired it
        self.active_torpedo_distance = ticks * torpedo.speed

    def on_resize(self, width, height):
        super().on_resize(width, height)

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
        self.player_list.draw()

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
            # If the torpedo has moved in front of the ship that fired it, then check for collisions
            # This prevents a ship from damaging itself from it's own torpedo
            if torpedo.distance > self.active_torpedo_distance:
                hit_list = arcade.check_for_collision_with_list(torpedo, self.all_sprites)

                # If the torpedo did hit something, explode it
                if len(hit_list) > 0:
                    torpedo.remove_from_sprite_lists()

                    explosion = arcade.Sprite("Images/Explosion.png", EXPLOSION_SCALING)
                    explosion.center_x = torpedo.center_x
                    explosion.center_y = torpedo.center_y

                    self.explosion_list.append(explosion)

                # If a ship was hit, decrease it's hp
                for sprite in hit_list:
                    if sprite in self.ship_list:
                        sprite.hp -= 20

        # Call update to move the sprites
        self.player_list.on_update(delta_time)
        self.player_sprite.update2()
        self.torpedo_list.update()

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
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()