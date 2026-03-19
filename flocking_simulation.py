import math
import random
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 960, 640
BACKGROUND = (18, 22, 35)
BOID_COLOR = (235, 238, 245)

NUM_BOIDS = 60
NEIGHBOR_RADIUS = 70
SEPARATION_RADIUS = 24

SEPARATION_WEIGHT = 1.7
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0

MAX_SPEED = 4.0
MAX_FORCE = 0.09


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0

    def add(self, other: "Vector2") -> "Vector2":
        self.x += other.x
        self.y += other.y
        return self

    def sub(self, other: "Vector2") -> "Vector2":
        self.x -= other.x
        self.y -= other.y
        return self

    def mult(self, scalar: float) -> "Vector2":
        self.x *= scalar
        self.y *= scalar
        return self

    def div(self, scalar: float) -> "Vector2":
        if scalar != 0:
            self.x /= scalar
            self.y /= scalar
        return self

    def mag(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> "Vector2":
        magnitude = self.mag()
        if magnitude > 0:
            self.div(magnitude)
        return self

    def limit(self, maximum: float) -> "Vector2":
        if self.mag() > maximum:
            self.normalize().mult(maximum)
        return self

    def heading(self) -> float:
        return math.atan2(self.y, self.x)

    def copy(self) -> "Vector2":
        return Vector2(self.x, self.y)


class Boid:
    def __init__(self) -> None:
        self.position = Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        if self.velocity.mag() == 0:
            self.velocity = Vector2(1, 0)
        self.acceleration = Vector2()
        self.max_speed = MAX_SPEED
        self.max_force = MAX_FORCE

    def apply_force(self, force: Vector2) -> None:
        self.acceleration.add(force)

    def flock(self, boids: list["Boid"]) -> None:
        separation_force = self.separation(boids).mult(SEPARATION_WEIGHT)
        alignment_force = self.alignment(boids).mult(ALIGNMENT_WEIGHT)
        cohesion_force = self.cohesion(boids).mult(COHESION_WEIGHT)

        self.apply_force(separation_force)
        self.apply_force(alignment_force)
        self.apply_force(cohesion_force)

    def separation(self, boids: list["Boid"]) -> Vector2:
        steer = Vector2()
        count = 0

        for other in boids:
            if other is self:
                continue
            distance = dist(self.position, other.position)
            if 0 < distance < SEPARATION_RADIUS:
                diff = self.position.copy().sub(other.position)
                diff.normalize().div(distance)
                steer.add(diff)
                count += 1

        if count == 0:
            return steer

        steer.div(count)
        if steer.mag() > 0:
            steer.normalize().mult(self.max_speed)
            steer.sub(self.velocity).limit(self.max_force)
        return steer

    def alignment(self, boids: list["Boid"]) -> Vector2:
        average_velocity = Vector2()
        count = 0

        for other in boids:
            if other is self:
                continue
            if dist(self.position, other.position) < NEIGHBOR_RADIUS:
                average_velocity.add(other.velocity)
                count += 1

        if count == 0:
            return Vector2()

        average_velocity.div(count).normalize().mult(self.max_speed)
        steer = average_velocity.sub(self.velocity)
        return steer.limit(self.max_force)

    def cohesion(self, boids: list["Boid"]) -> Vector2:
        center = Vector2()
        count = 0

        for other in boids:
            if other is self:
                continue
            if dist(self.position, other.position) < NEIGHBOR_RADIUS:
                center.add(other.position)
                count += 1

        if count == 0:
            return Vector2()

        center.div(count)
        return self.seek(center)

    def seek(self, target: Vector2) -> Vector2:
        desired = target.copy().sub(self.position).normalize().mult(self.max_speed)
        steer = desired.sub(self.velocity)
        return steer.limit(self.max_force)

    def update(self) -> None:
        self.velocity.add(self.acceleration).limit(self.max_speed)
        self.position.add(self.velocity)
        self.acceleration = Vector2()

        # Screen wrapping
        if self.position.x < 0:
            self.position.x = WIDTH
        elif self.position.x > WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = HEIGHT
        elif self.position.y > HEIGHT:
            self.position.y = 0

    def draw(self, surface: pygame.Surface) -> None:
        heading = self.velocity.heading()
        size = 8

        front = (
            self.position.x + math.cos(heading) * size,
            self.position.y + math.sin(heading) * size,
        )
        left = (
            self.position.x + math.cos(heading + 2.6) * (size * 0.7),
            self.position.y + math.sin(heading + 2.6) * (size * 0.7),
        )
        right = (
            self.position.x + math.cos(heading - 2.6) * (size * 0.7),
            self.position.y + math.sin(heading - 2.6) * (size * 0.7),
        )

        pygame.draw.polygon(surface, BOID_COLOR, (front, left, right))


def dist(a: Vector2, b: Vector2) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boids Flocking Simulation")
    clock = pygame.time.Clock()

    boids = [Boid() for _ in range(NUM_BOIDS)]
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND)

        for boid in boids:
            boid.flock(boids)
            boid.update()
            boid.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
