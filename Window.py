"""Importing key libraries"""
import arcade
import math
from pyglet.gl import GL_NEAREST


"""Defining Constants"""
# Screen Setup Constants
SCREEN_TITLE = "Naval Warfare Game"

# Scaling Constants
SCALING = 1
WEAPON_SCALING = 2
EXPLOSION_SCALING = 4
SIGN_SCALING = 8

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
TORPEDO_SPEED = 4


class Projectile(arcade.Sprite):
    """Child Class Of The Sprite Class"""
    # This is a base Class for projectiles and this Class inherits attributes from arcade.Sprite

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self, image, scaling, angle):
        # Init the parent Class, arcade.Sprite, with the image and scaling
        super().__init__(image, scaling)
        # Setting up attributes
        # It's start location is important for several calculations so we define it
        self.start_x = None
        self.start_y = None
        self.distance_to_travel = None
        # A projectile is an object in motion where the only external force is gravity
        # So ignoring friction, it's velocity is constant so it only has to be calculated once
        self.change_x = self.speed * math.cos(math.radians(angle))
        self.change_y = self.speed * math.sin(math.radians(angle))
        self.angle = angle


class Torpedo(Projectile):
    """Child Class of the Projectile Class"""
    # This class inherits attributes from the Projectile class
    # Objects of this class are fired from ships

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self, scaling, angle):
        self.speed = TORPEDO_SPEED
        # Init the parent Class, Projectile, with the image, scaling and angle
        super().__init__("Images/Torpedo.png", scaling, angle)
        # Setting up attributes
        self.distance_traveled = 0
        # It's origin is needed so it doesn't collide with the ship it is fired from
        self.origin = None
        # Alpha changes opacity, higher number means higher opacity
        # Alpha unless overridden is 255
        self.alpha = 63
        self.color = [0, 0, 127]

    def update(self):
        # This is an update function called a maximum of 60 times a second

        # Move the torpedo based on it's velocity
        self.center_x += self.change_x
        self.center_y += self.change_y

        # If it is off the window then remove it
        if self.right < 0 \
                or self.left > arcade.get_window().width - 1 \
                or self.top < 0 \
                or self.bottom > arcade.get_window().height - 1:
            self.remove_from_sprite_lists()


def create_torpedo(angle, x, y, distance_to_travel, identifier):
    # This function creates a object of the Torpedo Class
    # and sets up it's attributes using the given parameters
    torpedo = Torpedo(WEAPON_SCALING, angle)

    torpedo.center_x = x
    torpedo.center_y = y
    torpedo.start_x = x
    torpedo.start_y = y
    torpedo.distance_to_travel = distance_to_travel
    torpedo.origin = identifier
    # Return a handle on the object so it can be easily appended to SpriteLists
    return torpedo


class Ship(arcade.Sprite):
    """Child Class Of The Sprite Class"""
    # This is a base class for the AI ships and player ship to derive the same attributes and updates from

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self, image):
        # Init the parent
        super().__init__(image, SCALING)

        # Creating New Attributes
        self.speed = 0
        self.hp = 1000
        self.max_hp = self.hp
        # Identifier is useful for making torpedoes fired from a ship not collide with the ship upon firing
        self.identifier = None
        # Cooldown_time allows for a cooldown after a projectile is fired
        self.cooldown_time = 0

    def on_update(self, delta_time: float = 1/60):
        # This is an update function which takes the parameter of the time since the last frame / last update

        # Update ship's position based on ship's direction and speed
        self.center_x += self.speed * math.cos(math.radians(self.angle))
        self.center_y += self.speed * math.sin(math.radians(self.angle))

        # Increase the cooldown_time by the time since the last update
        # When it reaches a certain value then they can fire
        self.cooldown_time += delta_time

        # Wall Collision
        # Check to see if the ship hit the screen edge and if so prevent the ship from going off the window
        if self.left < 0:
            self.left = 0
        elif self.right > arcade.get_window().width - 1:
            self.right = arcade.get_window().width - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > arcade.get_window().height - 1:
            self.top = arcade.get_window().height - 1

        # Prevent the ship from exceeding speed limits
        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED
        elif self.speed < MIN_SPEED:
            self.speed = MIN_SPEED

    def draw_health(self):
        # This function allows for a ship to have its health displayed in a bar above it
        # It draws a green bar and a red bar based on the percentage of hp remaining
        # Green bar is hp left and red bar is hp gone

        # Determine what percentage of hp is left
        percent = self.hp / self.max_hp

        # If hp is temporarily negative then fill would be negative which causes issues
        # So we make fill = 0 if that is the case
        # Fill determines how long the bars are based off the hp remaining
        if self.hp < 0:
            fill = 0
        else:
            fill = HP_BAR_WIDTH * percent

        # Determine the left side the green bar
        left = int(self.center_x - HP_BAR_WIDTH // 2)
        # Determine where the right side of the green bar the left side of the red bar meet
        # Depending on the hp remaining
        middle = int(left + fill)
        # Determine the right side of the red bar
        right = left + HP_BAR_WIDTH

        # Determine the bottom and top of the bars
        bottom = self.center_y + self.width / 2
        top = bottom + HP_BAR_HEIGHT

        # Draw the bars
        arcade.draw_lrtb_rectangle_filled(middle, right, top, bottom, (255, 0, 0))  # Red bar
        arcade.draw_lrtb_rectangle_filled(left, middle, top, bottom, (0, 128, 0))  # Green bar


class AI(Ship):
    """Child Class Of The Ship Class"""
    # This class inherits attributes and updates from the ship class
    # This class gives the AI ships more attributes

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self, image):
        # Init the parent
        super().__init__(image)
        # These attributes are required to turn it away from the window edge if the AI gets too close
        self.left_turn = False
        self.right_turn = False


class Player(Ship):
    """Child Class Of The Ship Class"""
    # This class inherits attributes and updates from the ship class
    # This class is for the player's ship which gives them more attributes

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self):
        # Init the parent
        super().__init__("Images/PlayerShip.png")

        # Creating New Attributes
        # These attributes will be changed by the player to show and determine where the player is aiming
        self.aim_angle = 0
        self.aim_distance = MIN_AIM_DISTANCE

    def update(self):
        # Limit the aim_distance of the player so they cannot go outside of the determined range
        if self.aim_distance > MAX_AIM_DISTANCE:
            self.aim_distance = MAX_AIM_DISTANCE
        elif self.aim_distance < MIN_AIM_DISTANCE:
            self.aim_distance = MIN_AIM_DISTANCE


class BufferView(arcade.View):
    """Child Class Of The View Class"""
    # Views hold information to be shown on the window and are used to transition between different content
    # This View lasts a very short time in order to allow for the proper resizing of the window

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self):
        super().__init__()
        self.time = 0

    def on_show(self):
        # The on_show function is called when the view is shown
        # The background is set to a specific shade of blue
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_update(self, delta_time: float):
        # Switch to the MenuView after some time has passed
        # A little bit of time is required as going to a view and instantly going to the next view may cause issues
        self.time += delta_time
        if self.time > 0.5:
            # MenuView is created then shown
            menu_view = MenuView()
            self.window.show_view(menu_view)


class MenuView(arcade.View):
    """Child Class Of The View Class"""
    # This View allows the user to start the game when they want after the program has been started

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self):
        super().__init__()
        # This sets up an image called sign to be displayed on this view
        # Every sprite must be in a SpriteList() to be drawn
        self.sign_list = arcade.SpriteList()
        self.sign = arcade.Sprite("Images/Sign.png", SIGN_SCALING)
        self.sign_list.append(self.sign)

    def on_show(self):
        # When shown set the background to this blue
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_draw(self):
        # on_draw is called every frame to draw each frame
        # arcade.start_render() is required to start drawing on the window
        # It clears the window to the background colour
        arcade.start_render()

        # The sign is set up in a position dependant on the window size so it moves when the window is resized
        self.sign.center_x = self.window.width / 2
        self.sign.center_y = (self.window.height / 2) + 50
        # This draws all the sprites in this SpriteList and the parameter determines how they are drawn
        # GL_NEAREST prevents anti-aliasing
        self.sign_list.draw(filter=GL_NEAREST)

        # Some supporting text is drawn to tell the user how to progress to the next view
        arcade.draw_text("Click to start", self.window.width / 2, self.window.height / 2 - 300, arcade.color.WHITE,
                         font_size=35, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # This function is called when the mouse is pressed
        # This creates the GameView, shows it and causes the on_resize function of the GameView
        game_view = GameView()
        self.window.show_view(game_view)
        game_view.on_resize(self.window.width, self.window.height)


class GameView(arcade.View):
    """Child Class Of The View Class"""
    # This View has the gameplay on it

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self):
        super().__init__()

        # These attributes track the current state of what key is pressed
        # Initially they are set to False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False
        self.space_pressed = False

        # These attributes will be rectangles
        # They are used for determining whether the AI Ships are too close to the window edge
        self.ai_outer_rect = None
        self.ai_inner_rect = None

        # Create Sprite lists to hold the sprites
        self.player_list = arcade.SpriteList()
        self.ship_list = arcade.SpriteList()
        self.torpedo_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.all_collidable_sprites = arcade.SpriteList()
        self.enemy_ship_list = arcade.SpriteList()

        # Create and setup the player ship
        self.player_sprite = Player()
        self.player_sprite.identifier = 0
        # Append the player sprite to the appropriate lists
        self.player_list.append(self.player_sprite)
        self.ship_list.append(self.player_sprite)
        self.all_collidable_sprites.append(self.player_sprite)

        # Create and setup the enemy ships
        # This for loop allows for any number of enemy ships to be created
        for i in range(ENEMY_SHIP_NUMBER):
            # Create ship with an image based on the iterated value
            # There are 3 different colours of enemy ships
            # So every 3 enemy ships the colours will repeat
            ship = AI("Images/EnemyShip" + str((i % 3) + 1) + ".png")
            # Assign their identifier based on the iterated value
            ship.identifier = i + 1

            # Append the AI ships to the appropriate lists
            self.all_collidable_sprites.append(ship)
            self.ship_list.append(ship)
            self.enemy_ship_list.append(ship)

        # This sets up the starting position of all the ships depending on how many ships there are
        i = 0
        for ship in self.ship_list:
            # The ships are arranged equally on points of a circle originating at the middle of the window
            # The angle different between them is determined on the number of ships
            angle = i * 360 / len(self.ship_list)
            # Their direction is determined by the angle they were placed at
            ship.angle = angle

            # Their position from the center of the window is determined by the angle and window size
            # It's cartesian coordinates are determined by polar coordinates
            ship.center_x = self.window.height / 4 * math.cos(math.radians(angle)) + self.window.width / 2
            ship.center_y = self.window.height / 4 * math.sin(math.radians(angle)) + self.window.height / 2
            # Increment the i value for the next ship so it's angle is the next value
            i += 1

    def on_show(self):
        # Code to run when the view is shown

        # Set the background colour/color
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_resize(self, width, height):
        # When the window is resized, this function is called
        # So the sizes of the rectangles for the AI Ship wall avoidance code need to be resized

        # Create rectangles which have a midpoint at the window's midpoint
        # The outer rect is to determine when the AI Ships start turning away from the wall
        p1 = (AI_OUTER_DISTANCE, AI_OUTER_DISTANCE)
        p2 = (width - AI_OUTER_DISTANCE, AI_OUTER_DISTANCE)
        p3 = (width - AI_OUTER_DISTANCE, height - AI_OUTER_DISTANCE)
        p4 = (AI_OUTER_DISTANCE, height - AI_OUTER_DISTANCE)
        self.ai_outer_rect = [p1, p2, p3, p4]

        # The inner rect is to determine when the AI Ships stop turning away from the wall
        p1 = (AI_INNER_DISTANCE, AI_INNER_DISTANCE)
        p2 = (width - AI_INNER_DISTANCE, AI_INNER_DISTANCE)
        p3 = (width - AI_INNER_DISTANCE, height - AI_INNER_DISTANCE)
        p4 = (AI_INNER_DISTANCE, height - AI_INNER_DISTANCE)
        self.ai_inner_rect = [p1, p2, p3, p4]

    def on_draw(self):
        # Render the screen and draw shapes and sprites on it

        # arcade.start_render() is needed to start drawing and it clears the window
        arcade.start_render()

        # This creates a circle originating at the player where it's radius is the player's aim_distance
        # This is used to show how far the player is aiming
        arcade.draw_circle_outline(self.player_sprite.center_x, self.player_sprite.center_y,
                                   self.player_sprite.aim_distance, [0, 75, 120], 3, -1)

        # This code draws a line dependant on the player's aim_angle and aim_distance
        # Create shorter named handles of the player's attributes to be used in equations
        aim_angle = self.player_sprite.aim_angle
        aim_distance = self.player_sprite.aim_distance

        # The lines's cartesian endpoints are determined by polar coordinates
        # The length of the line is the player's aim_distance and it's angle, the player's aim_angle
        # The player's current coordinates need to be added
        # Otherwise the line's endpoints will be based on the window's origin rather than the player
        end_x = aim_distance * math.cos(math.radians(aim_angle)) + self.player_sprite.center_x
        end_y = aim_distance * math.sin(math.radians(aim_angle)) + self.player_sprite.center_y

        # Draw the line using the start point and end point
        # This shows what direction the player is aiming
        arcade.draw_line(self.player_sprite.center_x, self.player_sprite.center_y, end_x, end_y, [0, 75, 120], 3)

        # The sprites are drawn by calling the draw() function on the sprite lists
        # The GL_NEAREST determines the quality
        self.torpedo_list.draw(filter=GL_NEAREST)
        self.explosion_list.draw(filter=GL_NEAREST)

        # This draws the health bars for each ship
        for ship in self.ship_list:
            ship.draw_health()

        self.ship_list.draw(filter=GL_NEAREST)

    def on_update(self, delta_time):
        # This function is called a maximum of 60 times a second
        # It is used to update the game information

        # The player is updated first based on the keys pressed
        # If only the w key is pressed then the player is accelerating
        # If both are pressed then the player's speed is not changed
        # If only the s key is pressed then the player is decelerating
        if self.w_pressed and not self.s_pressed:
            self.player_sprite.speed += ACCELERATION_RATE
        elif self.s_pressed and not self.w_pressed:
            self.player_sprite.speed -= ACCELERATION_RATE

        # Changes angle of the player ship
        # Like comments above but a key turns player ship left and d key right
        # The angle turning is based on the speed of the player so they can't turn if they have a speed of 0
        if self.a_pressed and not self.d_pressed:
            self.player_sprite.angle += ANGLE_SPEED * self.player_sprite.speed
        elif self.d_pressed and not self.a_pressed:
            self.player_sprite.angle -= ANGLE_SPEED * self.player_sprite.speed

        # Change aim_distance
        # Like comments above but up arrow key increases aim_distance
        # Down arrow decreases aim_distance
        # This changes how far the player is aiming
        # These change the radius and length of the circle and line that show the player's aiming
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.aim_distance += AIM_DISTANCE_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.aim_distance -= AIM_DISTANCE_SPEED

        # Change aim_angle
        # Like comments above, left arrow key increases aim_angle (left)
        # Right arrow key decreases aim_angle (right)
        # This changes the direction the player is aiming
        # This changes the direction of the line that shows the player's aiming
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.aim_angle += AIM_ANGLE_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.aim_angle -= AIM_ANGLE_SPEED

        # The space key is the player's shoot key
        # If it's pressed, it checks if the player can shoot a torpedo
        # cooldown_time is increased every update in the Ship Class update function
        # If cooldown_time is greater than the WEAPON_COOLDOWN_TIME
        # Then a torpedo is created
        if self.space_pressed:
            if self.player_sprite.cooldown_time >= WEAPON_COOLDOWN_TIME:
                # Since the player fired a torpedo, reset the cooldown_time
                self.player_sprite.cooldown_time = 0

                # Create shorter named handles of the player's attributes to use to setup the torpedo
                angle = self.player_sprite.aim_angle
                x = self.player_sprite.center_x
                y = self.player_sprite.center_y
                distance_to_travel = self.player_sprite.aim_distance
                identifier = self.player_sprite.identifier

                # Creates the torpedo
                # Gets a handle of the torpedo in order to append it to the SpriteLists below
                torpedo = create_torpedo(angle, x, y, distance_to_travel, identifier)

                self.torpedo_list.append(torpedo)
                self.all_collidable_sprites.append(torpedo)

        # Updates Explosions
        # When a torpedo explodes, an explosion is made
        for explosion in self.explosion_list:
            # Determine if any ships are in an explosion
            # If so, decrease their hp
            # Every frame that the ship is in the explosion, it's hp decreases by 5
            hit_list = arcade.check_for_collision_with_list(explosion, self.ship_list)
            for ship in hit_list:
                ship.hp -= 5

            # Explosions go away over time
            # So reduce explosion size and if small enough then remove it
            explosion.scale -= 0.05
            if explosion.scale <= 0:
                # This removes it from all sprite lists so it is no longer updated, displayed or used
                explosion.remove_from_sprite_lists()

        # Updates torpedoes
        for torpedo in self.torpedo_list:
            # Find all the collidable sprites the torpedo can collide with
            hit_list = arcade.check_for_collision_with_list(torpedo, self.all_collidable_sprites)

            # Determine how far the torpedo has traveled from it's start position
            distance_traveled = ((torpedo.center_x - torpedo.start_x) ** 2 +
                                 (torpedo.center_y - torpedo.start_y) ** 2) ** 0.5

            # If the ship that fired the torpedo is in the hit_list then remove it
            # This prevents the torpedo from exploding as soon as it was fired
            # Because it hit the ship it was fired from
            for ship in self.ship_list:
                # If the torpedo's origin equals the identifier of the ship in the hit_list then remove that ship
                if ship in hit_list and ship.identifier == torpedo.origin:
                    hit_list.remove(ship)
                    # Since the torpedo's origin has been found, no other ships have to be checked
                    # as there is only one ship the torpedo can originate from
                    break

            # After removing any ships, if the hit_list is greater than 0
            # Then the torpedo hit at least one sprite that was not it's origin so it shall explode
            # Also if the torpedo reached it's endpoint then it shall explode
            if len(hit_list) > 0 or distance_traveled >= torpedo.distance_to_travel:
                torpedo.remove_from_sprite_lists()

                # Create an explosion at the torpedoes midpoint
                explosion = arcade.Sprite("Images/Explosion.png", EXPLOSION_SCALING)
                explosion.center_x = torpedo.center_x
                explosion.center_y = torpedo.center_y

                # Add the explosion to the appropriate SpriteLists
                self.explosion_list.append(explosion)
                self.all_collidable_sprites.append(explosion)

                # If a ship was hit, decrease it's hp
                for sprite in hit_list:
                    if sprite in self.ship_list:
                        sprite.hp -= 150

        # Updates AI Ships
        for ship in self.enemy_ship_list:
            # Check for the closest ship
            # Have to remove this ship from the sprite list being checked
            # Otherwise it will return itself as the closest ship
            self.ship_list.remove(ship)
            # arcade.get_closest_sprite returns a tuple with the closest sprite and the distance to the sprite
            closest_sprite = arcade.get_closest_sprite(ship, self.ship_list)
            # Add the ship back
            self.ship_list.append(ship)

            # If the distance to the closest sprite is within the MAX_AIM_DISTANCE
            # Then check if the AI Ship can shoot
            if closest_sprite[1] <= MAX_AIM_DISTANCE:
                # If the ship can shoot then do the next code
                if ship.cooldown_time >= WEAPON_COOLDOWN_TIME:
                    # Creates a shorter named handle for the closest sprite
                    target = closest_sprite[0]

                    # Determines the cartesian coordinate difference between the ship and the target
                    x_diff = target.center_x - ship.center_x
                    y_diff = target.center_y - ship.center_y

                    # t = d / v
                    # Determine the time taken for a torpedo to reach the target's current position
                    time_taken = closest_sprite[1] / TORPEDO_SPEED

                    # Determine the target's change in x and y by the time_taken
                    dx = target.speed * math.cos(math.radians(target.angle)) * time_taken
                    dy = target.speed * math.sin(math.radians(target.angle)) * time_taken

                    # Determine the destination of the target
                    dest_x = x_diff + dx
                    dest_y = y_diff + dy

                    # Determine the distance the torpedo would have to travel
                    # To get to the destination of the target
                    distance_to_travel = ((dest_x ** 2) + (dest_y ** 2)) ** 0.5

                    # If the distance to travel is greater than the MAX_AIM_DISTANCE
                    # Then there is no point in firing as the torpedo will explode
                    # Before it reaches the target's destination
                    if distance_to_travel <= MAX_AIM_DISTANCE:
                        # If the distance to travel is smaller than the MIN_AIM_DISTANCE
                        # Then set it to the MIN_AIM_DISTANCE
                        # This helps prevent a ship from destroying itself
                        if distance_to_travel < MIN_AIM_DISTANCE:
                            distance_to_travel = MIN_AIM_DISTANCE

                        # The AI Ship fires a torpedo so reset it's cooldown_time
                        ship.cooldown_time = 0

                        # Calculate the direction of the torpedo
                        # Create shorter named handles of the AI Ships attributes to be used for the torpedo
                        angle = math.degrees(math.atan2(dest_y, dest_x))
                        x = ship.center_x
                        y = ship.center_y
                        identifier = ship.identifier

                        # Creates the torpedo
                        # Gets a handle of the torpedo in order to append it to the SpriteLists below
                        torpedo = create_torpedo(angle, x, y, distance_to_travel, identifier)

                        self.torpedo_list.append(torpedo)
                        self.all_collidable_sprites.append(torpedo)

            # If the ai ship is below it's max speed then accelerate it
            if ship.speed < MAX_SPEED:
                ship.speed += ACCELERATION_RATE

            # This code below determines how the AI Ships should turn
            # If one of these variables is true then the ai ship is close to the window edge
            # Window edge avoidance takes priority over other turning so it is checked first
            if ship.left_turn or ship.right_turn:
                # Depending on which variable is true, make it turn that way
                if ship.left_turn:
                    ship.angle += ANGLE_SPEED * ship.speed
                elif ship.right_turn:
                    ship.angle -= ANGLE_SPEED * ship.speed

                # arcade.is_point_in_polygon checks if a given point is in a given polygon
                # If the ai ship is inside this rect, then it is not by the window edge anymore
                # So stop making it turn away from the edge
                if arcade.is_point_in_polygon(ship.center_x, ship.center_y, self.ai_inner_rect):
                    ship.left_turn = False
                    ship.right_turn = False

            # If the ai ship is not turning away from the edge then check the other turning code
            else:
                # Check if the ai ship is too close to the edge
                in_rect = arcade.is_point_in_polygon(ship.center_x, ship.center_y, self.ai_outer_rect)

                # If the ship is not in the rect, it means it is too close to the window edge
                # Then depending on angle it is approaching the window edge
                # Make it turn left or right
                if not in_rect:
                    if (ship.angle // 45) % 2 == 0:
                        ship.left_turn = True
                    else:
                        ship.right_turn = True

                # If it is in the rect then do the other turning code
                elif in_rect:
                    # Determine x and y difference between this ship and closest ship
                    x_diff = closest_sprite[0].center_x - ship.center_x
                    y_diff = closest_sprite[0].center_y - ship.center_y

                    # Determine the atan2 angle of the closest ship relative to this ship
                    # Create modified value of this ship's angle to be used later
                    arctan_angle = math.degrees(math.atan2(y_diff, x_diff))
                    ship_angle = abs(ship.angle % 360)

                    # If the closest sprite is within a certain distance to this ship
                    # Then depending on the arctan_angle the closest ship is to this ship
                    # Make this ship turn left or right
                    # Explaining how this code works without diagrams and more space is difficult
                    # So I won't explain
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

                    # If the closest ship is not close enough to shoot at
                    # Then depending on the arctan_angle the closest ship is to this ship
                    # Make this ship turn left or right
                    # So this ship can get closer and then attack the nearest ship
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

                # If everyone but the player is dead
                # Then setup the GameOverView to say "You Won!"
                if len(self.enemy_ship_list) == 0:
                    game_over_view = GameOverView()
                    game_over_view.text = "You Won!"
                    self.window.show_view(game_over_view)

                # If the player is dead
                # Then setup the GameOverView to say "You Lost!"
                elif len(self.player_list) == 0:
                    game_over_view = GameOverView()
                    game_over_view.text = "You Lost!"
                    self.window.show_view(game_over_view)

        # Update the sprites in these SpriteLists using the update function in their class
        self.ship_list.on_update(delta_time)
        self.player_sprite.update()
        self.torpedo_list.update()

    def on_key_press(self, key, key_modifiers):
        # on_key_press is called whenever a key is pressed
        # Depending on the key pressed
        # It sets the GameView's state of the key to True

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
        # on_key_release is called whenever a key is pressed
        # Depending on the key released
        # It sets the GameView's state of the key to False

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
    """Child Class Of The View Class"""
    # This View is shown when the game is lost or won
    # This View allows the player to replay the game whenever they want after the game ends

    # The __init__ functions are called when an object of that class are made
    # It sets up several attributes
    def __init__(self):
        super().__init__()
        # This is used to store what text to say depending if the player won or lost
        self.text = None

    def on_show(self):
        # When shown, set the background to this colour
        arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)

    def on_draw(self):
        # Start the render and draw some text
        arcade.start_render()

        # Draws text saying whether the player won or lost
        arcade.draw_text(self.text, self.window.width / 2, self.window.height / 2, arcade.color.WHITE,
                         font_size=100, anchor_x="center")

        # Draw text that tells the player they can replay by clicking
        arcade.draw_text("Click to replay", self.window.width / 2, self.window.height / 2 - 100, arcade.color.WHITE,
                         font_size=50, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # When the player clicks, create and show the GameView
        # So the player can replay the game
        game_view = GameView()
        self.window.show_view(game_view)
        game_view.on_resize(self.window.width, self.window.height)


def main():
    """ Main method """
    # Set initial size of window
    # This is not a perfect fitting of the display due to any task bars and window heading
    size = arcade.get_display_size(0)
    window = arcade.Window(size[0], size[1], SCREEN_TITLE, resizable=True)
    # Put the window into focus
    window.maximize()
    # Set a minimum size of window as very small sizes diminish quality of gameplay
    window.set_min_size(1200, 800)

    # Create the BufferView then show it
    # This view is created to allow for correct resize of window
    buffer_view = BufferView()
    window.show_view(buffer_view)
    arcade.run()


# Runs main()
if __name__ == "__main__":
    main()
