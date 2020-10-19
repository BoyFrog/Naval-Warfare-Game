"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
# Import key libraries
import arcade
import math

# Defining Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Naval Warfare Game"
# Sprite Size Scaling
SCALING = 0.75
# Speed limit
MAX_SPEED = 1
MIN_SPEED = 0
# How fast the ships speed changes
ACCELERATION_RATE = 0.005
# How fast the ships rotation changes
ANGLE_SPEED = 0.5


class Player(arcade.Sprite):
    # Call the parent init
    def __init__(self):
        """ Set up the player """
        self.speed = 0

        super().__init__("Images/Ship1-x2.png", SCALING)

    # 'angle' is created by the parent

    def update(self):
        # Update ship's position
        self.center_x += self.speed * math.cos(math.radians(self.angle) + math.pi/2)
        self.center_y += self.speed * math.sin(math.radians(self.angle) + math.pi/2)

        # Wall Collision
        # Check to see if we hit the screen edge
        if self.left < 0:
            self.left = 0
            self.change_x = -self.change_x
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1
            self.change_x = -self.change_x

        if self.bottom < 0:
            self.bottom = 0
            self.change_y = -self.change_y
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1
            self.change_y = -self.change_y

        # Speed Limits
        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED
        elif self.speed < MIN_SPEED:
            self.speed = MIN_SPEED

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.ship_list = None
        self.all_sprites = None

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player_sprite = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background colour/color
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.center_y = SCREEN_HEIGHT/2
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Call draw() on all your sprite lists below
        # Draw all the sprites.
        self.player_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        # Apply acceleration based on the keys pressed
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.speed += ACCELERATION_RATE
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.speed -= ACCELERATION_RATE

        # Change angle based on the keys pressed
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.angle += ANGLE_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.angle -= ANGLE_SPEED

        # Call update to move the sprite
        # If using a physics engine, call update on it instead of the sprite
        # list.
        self.player_list.update()

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


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()