# Import key libraries
import arcade
import math

# ~~~Defining Constants~~~
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Naval Warfare Game"
# Sprite Size Scaling
SCALING = 1
# Ship Speed limit
MAX_SPEED = 1.5
MIN_SPEED = 0
# Rate of change of ship speed
ACCELERATION_RATE = 0.01
# Rate of change of ship angle
ANGLE_SPEED = 1  # Maybe make angle speed based on ship speed
AIM_DISTANCE_SPEED = 5
AIM_ANGLE_SPEED = 2


class Projectile(arcade.Sprite):
    # Init the class
    def __init__(self, image, angle):
        self.end_x = None
        self.end_y = None
        # Init the parent
        super().__init__(image)
        self.change_x = self.speed * math.cos(math.radians(angle))
        self.change_y = self.speed * math.sin(math.radians(angle))
        print(self.change_x, " , ", self.change_y)


class Torpedo(Projectile):
    # Init the class
    def __init__(self, angle):
        # Init the parent
        self.speed = 5
        super().__init__("Images/NuclearMissle.png", angle)

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

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


class Ship(arcade.Sprite):
    # Init the class
    def __init__(self, image):
        self.speed = 0
        # Init the parent
        super().__init__(image, SCALING)

    def update(self):
        # Update ship's position based on ship's direction and speed
        self.center_x += self.speed * math.cos(math.radians(self.angle))
        self.center_y += self.speed * math.sin(math.radians(self.angle))

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
        self.aim_distance = 0
        # Init the parent
        super().__init__("Images/Ship1-x2.png")
        self.angle = 90

    def update2(self):
        # aim_distance limits
        if self.aim_distance > 250:
            self.aim_distance = 250
        elif self.aim_distance < 0:
            self.aim_distance = 0


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
        self.projectile_list = None
        self.player_list = None

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

        # Set the background colour/color
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.center_y = SCREEN_HEIGHT/2
        self.player_list.append(self.player_sprite)

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
                                   self.player_sprite.aim_distance, arcade.color.BLACK, 3, -1)

        end_x = self.player_sprite.aim_distance * math.cos(math.radians(self.player_sprite.aim_angle))
        end_y = self.player_sprite.aim_distance * math.sin(math.radians(self.player_sprite.aim_angle))
        arcade.draw_line(self.player_sprite.center_x, self.player_sprite.center_y, end_x + self.player_sprite.center_x,
                         end_y + self.player_sprite.center_y, arcade.color.BLACK, 3)

        # Call draw() on all your sprite lists below
        # Draw all the sprites.
        self.player_list.draw()
        self.projectile_list.draw()

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

        if self.space_pressed:
            torpedo = Torpedo(self.player_sprite.aim_angle)

            #torpedo.angle = self.player_sprite.aim_angle
            torpedo.center_x = self.player_sprite.center_x
            torpedo.center_y = self.player_sprite.center_y

            self.projectile_list.append(torpedo)

        # Call update to move the sprites
        self.player_list.update()
        self.player_sprite.update2()
        self.projectile_list.update()

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