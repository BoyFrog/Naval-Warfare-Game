# Import key libraries
import arcade
import math
from pyglet.gl import GL_NEAREST
import random

# ~~~Defining Constants~~~

# Screen Setup Constants
SCREEN_TITLE = "Naval Warfare Game"

# Scaling Constants
SCALING = 1
WEAPON_SCALING = 2
EXPLOSION_SCALING = 4

# Ship Constants
MAX_SPEED = 1.5
MIN_SPEED = 0
ACCELERATION_RATE = 0.01
ANGLE_SPEED = 1
WEAPON_COOLDOWN_TIME = 5
HP_BAR_WIDTH = 100
HP_BAR_HEIGHT = 10

# Aiming Constants
AIM_DISTANCE_SPEED = 5
AIM_ANGLE_SPEED = 2
MAX_AIM_DISTANCE = 350
MIN_AIM_DISTANCE = 75

# Other Constants
ENEMY_SHIP_NUMBER = 3
AI_OUTER_DISTANCE = 100
AI_INNER_DISTANCE = 125
TORPEDO_SPEED = 5


class Projectile(arcade.Sprite):
    # Init the class
    def __init__(self, image, scaling, angle):
        # Creating New Attributes
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
        # Creating New Attributes
        self.speed = TORPEDO_SPEED
        self.distance_traveled = 0
        self.origin = None
        # Init the parent
        super().__init__("Images/Torpedo.png", scaling, angle)
        self.alpha = 63
        self.color = [0, 0, 127]

    def update_torpedo(self, explosion_list, all_collidable_sprites):
        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # If torpedo has reached it's endpoint then make an explosion
        self.distance_traveled = ((self.center_x - self.start_x) ** 2 + (self.center_y - self.start_y) ** 2) ** 0.5

        if self.distance_traveled >= self.distance_to_travel:
            self.remove_from_sprite_lists()

            explosion = arcade.Sprite("Images/Explosion.png", EXPLOSION_SCALING)
            explosion.center_x = self.center_x
            explosion.center_y = self.center_y

            explosion_list.append(explosion)
            all_collidable_sprites.append(explosion)

        # If it is off the window then remove it
        elif self.right < 0 \
                or self.left > arcade.get_window().width - 1 \
                or self.top < 0 \
                or self.bottom > arcade.get_window().height - 1:
            self.remove_from_sprite_lists()


class Ship(arcade.Sprite):
    # Init the class
    def __init__(self, image):
        # Creating New Attributes
        self.speed = 0
        self.hp = 500
        self.max_hp = self.hp
        self.identifier = None
        self.cooldown_time = 0
        # Init the parent
        super().__init__(image, SCALING)

    def on_update(self, delta_time: float = 1/60):
        # Update ship's position based on ship's direction and speed
        self.center_x += self.speed * math.cos(math.radians(self.angle))
        self.center_y += self.speed * math.sin(math.radians(self.angle))

        # Increase the cooldown_time
        # When it reaches a certain value then they can fire
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

    def draw_health(self):
        percent = self.hp / self.max_hp

        if self.hp < 0:
            fill = 0
        else:
            fill = HP_BAR_WIDTH * percent

        left = int(self.center_x - HP_BAR_WIDTH // 2)
        middle = int(left + fill)
        right = left + HP_BAR_WIDTH

        bottom = self.center_y + self.width / 2
        top = bottom + HP_BAR_HEIGHT

        arcade.draw_lrtb_rectangle_filled(middle, right, top, bottom, (255, 0, 0))  # Red
        arcade.draw_lrtb_rectangle_filled(left, middle, top, bottom, (0, 128, 0))  # Green


class AI(Ship):
    def __init__(self, image):
        self.left_turn = False
        self.right_turn = False
        # Init the parent
        super().__init__(image)


class Player(Ship):
    # Init the class
    def __init__(self):
        # Creating New Attributes
        self.aim_angle = 0
        self.aim_distance = MIN_AIM_DISTANCE
        # Init the parent
        super().__init__("Images/PlayerShip.png")

    def update2(self):
        # aim_distance limits
        if self.aim_distance > MAX_AIM_DISTANCE:
            self.aim_distance = MAX_AIM_DISTANCE
        elif self.aim_distance < MIN_AIM_DISTANCE:
            self.aim_distance = MIN_AIM_DISTANCE


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

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

        # Create Sprite lists
        self.player_list = arcade.SpriteList()
        self.ship_list = arcade.SpriteList()
        self.torpedo_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.all_collidable_sprites = arcade.SpriteList()
        self.enemy_ship_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.identifier = 0
        self.player_list.append(self.player_sprite)
        self.ship_list.append(self.player_sprite)
        self.all_collidable_sprites.append(self.player_sprite)

        # Set up the enemy ships
        for i in range(ENEMY_SHIP_NUMBER):
            # Create ship with an image based on the iterated value
            ship = AI("Images/EnemyShip" + str((i % 3) + 1) + ".png")
            # Assign their identifier based on the iterated value
            ship.identifier = i + 1

            # Assign them to the appropriate lists
            self.all_collidable_sprites.append(ship)
            self.ship_list.append(ship)
            self.enemy_ship_list.append(ship)

        # setup the starting position of the ships
        i = 0
        for ship in self.ship_list:
            # Arrange the ships evenly on points of a circle originating at the window's midpoint
            angle = i * 360 / len(self.ship_list)
            ship.angle = angle
            ship.center_x = self.window.height / 4 * math.cos(math.radians(angle)) + self.window.width / 2
            ship.center_y = self.window.height / 4 * math.sin(math.radians(angle)) + self.window.height / 2
            i += 1

    def on_show(self):
        # Code to run when the view is shown

        # Set the background colour/color
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_resize(self, width, height):
        # When the window is resized,
        # change the size of the rectangles required for AI Ships wall avoidance code

        # Create the rectangles
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
        # Render the screen and draw shapes and sprites on it

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
        self.torpedo_list.draw(filter=GL_NEAREST)
        self.explosion_list.draw(filter=GL_NEAREST)

        for ship in self.ship_list:
            ship.draw_health()

        self.ship_list.draw(filter=GL_NEAREST)

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
                self.all_collidable_sprites.append(torpedo)

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
            hit_list = arcade.check_for_collision_with_list(torpedo, self.all_collidable_sprites)

            for ship in self.ship_list:
                if ship in hit_list and ship.identifier == torpedo.origin:
                    hit_list.remove(ship)
                    break

            # If the torpedo did hit something, explode it
            if len(hit_list) > 0:
                torpedo.remove_from_sprite_lists()

                explosion = arcade.Sprite("Images/Explosion.png", EXPLOSION_SCALING)
                explosion.center_x = torpedo.center_x
                explosion.center_y = torpedo.center_y

                self.explosion_list.append(explosion)
                self.all_collidable_sprites.append(explosion)

            # If a ship was hit, decrease it's hp
            for sprite in hit_list:
                if sprite in self.ship_list:
                    sprite.hp -= 100

        for ship in self.enemy_ship_list:
            # Check for the closest ship
            # Have to remove this ship from the sprite list being checked
            # Otherwise it will return itself as the closest ship
            self.ship_list.remove(ship)
            closest_sprite = arcade.get_closest_sprite(ship, self.ship_list)
            self.ship_list.append(ship)

            # Determining if the ship can and should shoot
            if closest_sprite[1] <= MAX_AIM_DISTANCE:
                if ship.cooldown_time >= WEAPON_COOLDOWN_TIME:
                    # Determining where the ship should shoot
                    target = closest_sprite[0]
                    x_diff = target.center_x - ship.center_x
                    y_diff = target.center_y - ship.center_y
                    
                    time_taken = closest_sprite[1] / (TORPEDO_SPEED * 60)

                    dx = target.speed * math.cos(math.radians(target.angle)) * time_taken
                    dy = target.speed * math.sin(math.radians(target.angle)) * time_taken

                    distance_to_travel = ((x_diff + dx) ** 2 + (y_diff + dy) ** 2) ** 0.5

                    new_time_taken = distance_to_travel / (TORPEDO_SPEED * 60)

                    ratio = new_time_taken / time_taken

                    dx = dx * ratio
                    dy = dy * ratio
                    x = x_diff + dx
                    y = y_diff + dy

                    distance_to_travel = ((x ** 2) + (y ** 2)) ** 0.5

                    if distance_to_travel <= MAX_AIM_DISTANCE:
                        if distance_to_travel < MIN_AIM_DISTANCE:
                            distance_to_travel = MIN_AIM_DISTANCE

                        ship.cooldown_time = 0
                        angle = math.degrees(math.atan2(y, x))

                        torpedo = Torpedo(WEAPON_SCALING, angle)

                        torpedo.center_x = ship.center_x
                        torpedo.center_y = ship.center_y
                        torpedo.start_x = ship.center_x
                        torpedo.start_y = ship.center_y
                        torpedo.distance_to_travel = distance_to_travel
                        torpedo.origin = ship.identifier

                        self.torpedo_list.append(torpedo)
                        self.all_collidable_sprites.append(torpedo)

            # If the ai ship is below it's max speed then accelerate it
            if ship.speed < MAX_SPEED:
                ship.speed += ACCELERATION_RATE

            # If one of these variables is true then the ai ship is close to the edge
            # Edge avoidance takes priority over other turning so it is done first
            if ship.left_turn or ship.right_turn:
                # Depending on which variable is true, make it turn that way
                if ship.left_turn:
                    ship.angle += ANGLE_SPEED * ship.speed
                elif ship.right_turn:
                    ship.angle -= ANGLE_SPEED * ship.speed

                # If the ai ship is inside this rect, then it is not by the edge anymore
                # So stop making it turn away from the edge
                if arcade.is_point_in_polygon(ship.center_x, ship.center_y, self.ai_inner_rect):
                    ship.left_turn = False
                    ship.right_turn = False

            # If the ai ship is not turning away from the edge then check this code
            else:
                # Check if the ai ship is too close to the edge
                in_rect = arcade.is_point_in_polygon(ship.center_x, ship.center_y, self.ai_outer_rect)

                # If the ship is not in the rect / too close to the edge
                # Then depending on the section it is in
                # Make it turn left or right
                if not in_rect:
                    if (ship.angle // 45) % 2 == 0:
                        ship.left_turn = True
                    else:
                        ship.right_turn = True

                # If it is in the rect then do this code
                elif in_rect:
                    # Determine x and y difference between this ship and closest ship
                    x = closest_sprite[0].center_x - ship.center_x
                    y = closest_sprite[0].center_y - ship.center_y

                    # Determine the atan2 angle of the closest ship relative to this ship
                    # Create modified value of this ship's angle to be used
                    arctan_angle = math.degrees(math.atan2(y, x))
                    ship_angle = abs(ship.angle % 360)

                    # If there is another ship nearby
                    # Then turn away from it
                    if closest_sprite[1] < MAX_AIM_DISTANCE / 2:
                        if arctan_angle >= 0:
                            if arctan_angle < ship_angle < arctan_angle + 180:
                                ship.angle += ANGLE_SPEED * ship.speed
                            else:
                                ship.angle -= ANGLE_SPEED * ship.speed

                        else:
                            if arctan_angle + 180 < ship_angle < arctan_angle + 360:
                                ship.angle -= ANGLE_SPEED * ship.speed
                            else:
                                ship.angle += ANGLE_SPEED * ship.speed

                    # If no ships are in it's aim distance
                    # Then turn towards the nearest ship
                    elif closest_sprite[1] > MAX_AIM_DISTANCE:
                        if arctan_angle >= 0:
                            if arctan_angle < ship_angle < arctan_angle + 180:
                                ship.angle -= ANGLE_SPEED * ship.speed
                            else:
                                ship.angle += ANGLE_SPEED * ship.speed

                        else:
                            if arctan_angle + 180 < ship_angle < arctan_angle + 360:
                                ship.angle += ANGLE_SPEED * ship.speed
                            else:
                                ship.angle -= ANGLE_SPEED * ship.speed

        # Check if a ship is dead and if so remove it
        for ship in self.ship_list:
            if ship.hp <= 0:
                ship.remove_from_sprite_lists()

                # If the player is dead or all the enemy ships are dead
                # Then go to the GameOverView
                if len(self.enemy_ship_list) == 0 or len(self.player_list) == 0:
                    game_over_view = GameOverView()
                    self.window.show_view(game_over_view)

        # Update these sprites using the update function in their class
        self.ship_list.on_update(delta_time)
        self.player_sprite.update2()
        for torpedo in self.torpedo_list:
            torpedo.update_torpedo(self.explosion_list, self.all_collidable_sprites)

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


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_draw(self):
        arcade.start_render()
        """
        Draw "Game over" across the screen.
        """
        arcade.draw_text("Game Over", self.window.width / 2, self.window.height / 2, arcade.color.WHITE,
                         font_size=100, anchor_x="center")
        arcade.draw_text("Click to restart", self.window.width / 2, self.window.height / 2 - 100, arcade.color.WHITE,
                         font_size=50, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)
        game_view.on_resize(self.window.width, self.window.height)
        arcade.run()


def main():
    """ Main method """
    # Set size of window
    # This is not a perfect fitting of the display due to any task bars and window heading
    # Have to do this to get a somewhat accurate window size to set up the ships more towards the middle of the window
    size = arcade.get_display_size(0)
    window = arcade.Window(size[0], size[1], SCREEN_TITLE, resizable=True)
    # Put the window into focus
    window.maximize()

    # Create the GameView then show it
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()