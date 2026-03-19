import argparse
import math
import random
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 960, 640
BACKGROUND = (18, 22, 35)
BOID_COLOR = (235, 238, 245)
PREDATOR_COLOR = (235, 80, 80)
GOAL_COLOR = (105, 230, 145)

NUM_BOIDS = 60
NEIGHBOR_RADIUS = 70
SEPARATION_RADIUS = 24

SEPARATION_WEIGHT = 1.7
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0

MAX_SPEED = 4.0
MAX_FORCE = 0.09

# Alternate challenge mode weights
PREDATOR_AVOID_RADIUS = 130
PREDATOR_AVOID_WEIGHT = 2.2
GOAL_SEEK_WEIGHT = 0.85
WALL_MARGIN = 55
WALL_FORCE = 0.13


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


class Predator:
    def __init__(self) -> None:
        self.position = Vector2(WIDTH * 0.65, HEIGHT * 0.5)
        self.velocity = Vector2(2.2, 1.7)
        self.radius = 12

    def update(self) -> None:
        self.position.add(self.velocity)

        if self.position.x < self.radius or self.position.x > WIDTH - self.radius:
            self.velocity.x *= -1
        if self.position.y < self.radius or self.position.y > HEIGHT - self.radius:
            self.velocity.y *= -1

        self.position.x = min(max(self.position.x, self.radius), WIDTH - self.radius)
        self.position.y = min(max(self.position.y, self.radius), HEIGHT - self.radius)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(
            surface,
            PREDATOR_COLOR,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )
        pygame.draw.circle(
            surface,
            (255, 180, 180),
            (int(self.position.x), int(self.position.y)),
            self.radius + 2,
            2,
        )


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

    def flock(
        self,
        boids: list["Boid"],
        challenge_mode: bool,
        predator_position: Vector2 | None,
        goal_position: Vector2 | None,
    ) -> None:
        separation_force = self.separation(boids).mult(SEPARATION_WEIGHT)
        alignment_force = self.alignment(boids).mult(ALIGNMENT_WEIGHT)
        cohesion_force = self.cohesion(boids).mult(COHESION_WEIGHT)

        self.apply_force(separation_force)
        self.apply_force(alignment_force)
        self.apply_force(cohesion_force)

        if challenge_mode and predator_position is not None and goal_position is not None:
            flee_force = self.avoid_predator(predator_position).mult(PREDATOR_AVOID_WEIGHT)
            goal_force = self.seek(goal_position).mult(GOAL_SEEK_WEIGHT)
            wall_force = self.contain().mult(1.0)
            self.apply_force(flee_force)
            self.apply_force(goal_force)
            self.apply_force(wall_force)

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

    def avoid_predator(self, predator_pos: Vector2) -> Vector2:
        distance = dist(self.position, predator_pos)
        if distance >= PREDATOR_AVOID_RADIUS or distance == 0:
            return Vector2()

        desired = self.position.copy().sub(predator_pos)
        desired.normalize().mult(self.max_speed)
        steer = desired.sub(self.velocity)
        return steer.limit(self.max_force)

    def contain(self) -> Vector2:
        desired = Vector2()

        if self.position.x < WALL_MARGIN:
            desired.x = self.max_speed
        elif self.position.x > WIDTH - WALL_MARGIN:
            desired.x = -self.max_speed

        if self.position.y < WALL_MARGIN:
            desired.y = self.max_speed
        elif self.position.y > HEIGHT - WALL_MARGIN:
            desired.y = -self.max_speed

        if desired.mag() == 0:
            return Vector2()

        desired.normalize().mult(self.max_speed)
        steer = desired.sub(self.velocity)
        return steer.limit(WALL_FORCE)

    def seek(self, target: Vector2) -> Vector2:
        desired = target.copy().sub(self.position)
        if desired.mag() == 0:
            return Vector2()
        desired.normalize().mult(self.max_speed)
        steer = desired.sub(self.velocity)
        return steer.limit(self.max_force)

    def update(self, wrap: bool) -> None:
        self.velocity.add(self.acceleration).limit(self.max_speed)
        self.position.add(self.velocity)
        self.acceleration = Vector2()

        if wrap:
            if self.position.x < 0:
                self.position.x = WIDTH
            elif self.position.x > WIDTH:
                self.position.x = 0

            if self.position.y < 0:
                self.position.y = HEIGHT
            elif self.position.y > HEIGHT:
                self.position.y = 0
        else:
            self.position.x = min(max(self.position.x, 0), WIDTH)
            self.position.y = min(max(self.position.y, 0), HEIGHT)

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Boids flocking simulation")
    parser.add_argument(
        "--mode",
        choices=("classic", "challenge"),
        default="classic",
        help="classic flocking or challenge mode (predator + goal + containment)",
    )
    return parser.parse_args()


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, mode: str) -> None:
    label = (
        f"Mode: {mode.upper()} | Press M to toggle | Click to place goal (challenge)"
    )
    text = font.render(label, True, (210, 220, 240))
    surface.blit(text, (12, 10))


def main() -> None:
    args = parse_args()
    challenge_mode = args.mode == "challenge"

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boids Flocking Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    boids = [Boid() for _ in range(NUM_BOIDS)]
    predator = Predator()
    goal = Vector2(WIDTH * 0.2, HEIGHT * 0.5)
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                challenge_mode = not challenge_mode
            elif (
                challenge_mode
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                goal = Vector2(*event.pos)

        if challenge_mode:
            predator.update()

        screen.fill(BACKGROUND)

        for boid in boids:
            boid.flock(
                boids,
                challenge_mode=challenge_mode,
                predator_position=predator.position if challenge_mode else None,
                goal_position=goal if challenge_mode else None,
            )
            boid.update(wrap=not challenge_mode)
            boid.draw(screen)

        if challenge_mode:
            predator.draw(screen)
            pygame.draw.circle(screen, GOAL_COLOR, (int(goal.x), int(goal.y)), 8)
            pygame.draw.circle(screen, (170, 255, 198), (int(goal.x), int(goal.y)), 16, 1)

        draw_hud(screen, font, "challenge" if challenge_mode else "classic")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
