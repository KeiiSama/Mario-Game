import pygame as pg
from . import powerups
from .. import setup
from .. import constants as c


class Enemy(pg.sprite.Sprite):
    """Base class for all enemies (Goombas, Koopas, etc.)"""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)

    def setup_enemy(self, x, y, direction, name, setup_frames):
        """Sets up various values for enemy"""
        self.sprite_sheet = setup.GFX["smb_enemies_sheet"]
        self.frames = []
        self.frame_index = 0
        self.animate_timer = 0
        self.death_timer = 0
        self.gravity = 1.5
        self.state = c.WALK

        self.name = name
        self.direction = direction
        setup_frames()

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.set_velocity()

    def set_velocity(self):
        """Sets velocity vector based on direction"""
        if self.direction == c.LEFT:
            self.x_vel = -2
        else:
            self.x_vel = 2

        self.y_vel = 0

    def get_image(self, x, y, width, height):
        """Get the image frames from the sprite sheet"""
        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)

        image = pg.transform.scale(
            image,
            (int(rect.width * c.SIZE_MULTIPLIER), int(rect.height * c.SIZE_MULTIPLIER)),
        )
        return image

    def handle_state(self, fire_group):
        """Enemy behavior based on state"""
        if self.state == c.WALK:
            self.walking()
        elif self.state == c.FALL:
            self.falling()
        elif self.state == c.JUMPED_ON:
            self.jumped_on()
        elif self.state == c.SHELL_SLIDE:
            self.shell_sliding()
        elif self.state == c.DEATH_JUMP:
            self.death_jumping()
        elif self.state == c.STAND:
            self.standing()
        elif self.state == c.SHOOT:
            self.shoot(fire_group)

    def walking(self):
        if not self.x_vel:
            self.set_velocity()
        """Default state of moving sideways"""
        if (self.current_time - self.animate_timer) > 125:
            if self.frame_index == 0:
                self.frame_index += 1
            elif self.frame_index == 1:
                self.frame_index = 0

            self.animate_timer = self.current_time

    def standing(self):
        self.x_vel = 0
        self.y_vel = 0

    def shoot():
        pass

    def falling(self):
        """For when it falls off a ledge"""
        if self.y_vel < 10:
            self.y_vel += self.gravity

    def jumped_on(self):
        """Placeholder for when the enemy is stomped on"""
        pass

    def death_jumping(self):
        """Death animation"""
        self.rect.y += self.y_vel
        self.rect.x += self.x_vel
        self.y_vel += self.gravity

        if self.rect.y > 600:
            self.kill()

    def start_death_jump(self, direction):
        """Transitions enemy into a DEATH JUMP state"""
        self.y_vel = -8
        if direction == c.RIGHT:
            self.x_vel = 2
        else:
            self.x_vel = -2
        self.gravity = 0.5
        self.frame_index = 3
        self.image = self.frames[self.frame_index]
        self.state = c.DEATH_JUMP

    def animation(self):
        """Basic animation, switching between two frames"""
        self.image = self.frames[self.frame_index]

    def update(self, game_info, fire_group=None, viewport=None):
        """Updates enemy behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state(fire_group)
        self.animation()


class Goomba(Enemy):
    def __init__(self, y=c.GROUND_HEIGHT, x=0, direction=c.LEFT, name="goomba"):
        Enemy.__init__(self)
        self.setup_enemy(x, y, direction, name, self.setup_frames)

    def setup_frames(self):
        """Put the image frames in a list to be animated"""

        self.frames.append(self.get_image(0, 4, 16, 16))
        self.frames.append(self.get_image(30, 4, 16, 16))
        self.frames.append(self.get_image(61, 0, 16, 16))
        self.frames.append(pg.transform.flip(self.frames[1], False, True))

    def jumped_on(self):
        """When Mario squishes him"""
        self.frame_index = 2

        if (self.current_time - self.death_timer) > 500:
            self.kill()


class Koopa(Enemy):
    def __init__(self, y=c.GROUND_HEIGHT, x=0, direction=c.LEFT, name="koopa"):
        Enemy.__init__(self)
        self.setup_enemy(x, y, direction, name, self.setup_frames)

    def setup_frames(self):
        """Sets frame list"""
        self.frames.append(self.get_image(150, 0, 16, 24))
        self.frames.append(self.get_image(180, 0, 16, 24))
        self.frames.append(self.get_image(360, 5, 16, 15))
        self.frames.append(pg.transform.flip(self.frames[2], False, True))

    def jumped_on(self):
        """When Mario jumps on the Koopa and puts him in his shell"""
        self.x_vel = 0
        self.frame_index = 2
        shell_y = self.rect.bottom
        shell_x = self.rect.x
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.x = shell_x
        self.rect.bottom = shell_y

    def shell_sliding(self):
        """When the koopa is sliding along the ground in his shell"""
        if self.direction == c.RIGHT:
            self.x_vel = 10
        elif self.direction == c.LEFT:
            self.x_vel = -10


class Bowser(Enemy):
    def __init__(self, y=c.GROUND_HEIGHT, x=0, direction=c.LEFT, name=c.BOWSER):
        Enemy.__init__(self)
        self.setup_enemy(x, y, direction, name, self.setup_frames)
        self.time = 0
        self.last_fireball_time = 0
        self.facing_right = False
        self.x_vel = 0
        self.state = c.SHOOT
        self.hp = 30

    def setup_frames(self):
        """Sets frame list"""
        self.frames.append(self.get_image(122, 212, 31, 30))
        self.frames.append(self.get_image(82, 212, 31, 30))
        self.frames.append(self.get_image(42, 212, 31, 30))
        self.frames.append(self.get_image(2, 212, 31, 30))
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.frames.append(pg.transform.flip(self.frames[2], True, False))
        self.frames.append(pg.transform.flip(self.frames[3], True, False))

    def shoot(self, fire_group):
        """Shoots fireball"""
        if (self.current_time - self.last_fireball_time) > 1000:
            setup.SFX["fireball"].play()
            fire_group.add(
                powerups.FireShoot(self.rect.right, self.rect.y + 15, self.facing_right)
            )
            self.last_fireball_time = self.current_time
            if self.facing_right:
                self.frame_index = 6
            else:
                self.frame_index = 2

    def walking(self):
        if not self.x_vel:
            self.set_velocity()
        """Default state of moving sideways"""
        if (self.current_time - self.animate_timer) > 125:
            if not self.facing_right:
                if self.frame_index == 0:
                    self.frame_index = 1
                else:
                    self.frame_index = 0
            else:
                if self.frame_index == 4:
                    self.frame_index = 5
                else:
                    self.frame_index = 4

            self.animate_timer = self.current_time

    def update(self, game_info, fire_group, viewport=None):
        """Updates enemy behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        if viewport:
            if (self.current_time - self.time) > 10000:
                self.x_vel = 2 if self.facing_right else -2
                self.state = c.WALK
                self.time = self.current_time
            if self.rect.x > viewport.x + viewport.width - 100:
                self.rect.x = viewport.x + viewport.width - 100
                self.turning()
            if self.rect.x < viewport.x + 10:
                self.rect.x = viewport.x + 10
                self.turning()
        self.handle_state(fire_group)
        self.animation()

    def turning(self):
        self.facing_right = not self.facing_right
        self.x_vel = 0
        self.state = c.SHOOT

    def jumped_on(self):
        pass
