import pygame as pg


class HealthBar(pg.sprite.Sprite):
    def __init__(
        self, y, x, width, height, screen, current_health, max_health, target_health
    ):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.screen = screen
        self.current_health = current_health
        self.target_health = target_health
        self.max_health = max_health
        self.health_bar_length = width
        self.height = height
        self.health_ratio = self.max_health / self.health_bar_length
        self.health_change_speed = 1

    def get_damage(self, amount):
        if self.target_health > 0:
            self.target_health -= amount
        if self.target_health < 0:
            self.target_health = 0

    def update(self):
        self.advanced_health()

    def advanced_health(self):
        transition_width = 0
        transition_color = (255, 0, 0)

        if self.current_health < self.target_health:
            self.current_health += self.health_change_speed
            transition_width = int(
                (self.target_health - self.current_health) / self.health_ratio
            )
            transition_color = (0, 255, 0)

        if self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            transition_width = int(
                (self.target_health - self.current_health) / self.health_ratio
            )
            transition_color = (255, 255, 0)

        health_bar_width = int(self.current_health / self.health_ratio)
        health_bar = pg.Rect(self.x, self.y, health_bar_width, self.height)
        transition_bar = pg.Rect(
            health_bar.right, self.y, transition_width, self.height
        )

        pg.draw.rect(self.screen, (255, 0, 0), health_bar)
        pg.draw.rect(self.screen, transition_color, transition_bar)
        pg.draw.rect(
            self.screen,
            (255, 255, 255),
            (self.x, self.y, self.health_bar_length, self.height),
            4,
        )
