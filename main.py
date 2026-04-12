import math
import random
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 960, 640
FPS = 120
BACKGROUND = (18, 22, 28)
WALL_RESTITUTION = 0.98


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    color: tuple[int, int, int]

    @property
    def mass(self) -> float:
        # Use area as mass to make larger balls feel heavier.
        return math.pi * self.radius * self.radius

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx * WALL_RESTITUTION
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -self.vx * WALL_RESTITUTION

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy * WALL_RESTITUTION
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy = -self.vy * WALL_RESTITUTION

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


def resolve_ball_collision(a: Ball, b: Ball) -> None:
    dx = b.x - a.x
    dy = b.y - a.y
    distance_sq = dx * dx + dy * dy
    min_dist = a.radius + b.radius

    if distance_sq == 0:
        # Rare overlap case: nudge to avoid division by zero.
        dx = random.uniform(-1.0, 1.0)
        dy = random.uniform(-1.0, 1.0)
        distance_sq = dx * dx + dy * dy

    if distance_sq >= min_dist * min_dist:
        return

    distance = math.sqrt(distance_sq)
    nx = dx / distance
    ny = dy / distance

    overlap = min_dist - distance
    total_mass = a.mass + b.mass

    # Positional correction to separate balls proportionally to mass.
    a.x -= nx * overlap * (b.mass / total_mass)
    a.y -= ny * overlap * (b.mass / total_mass)
    b.x += nx * overlap * (a.mass / total_mass)
    b.y += ny * overlap * (a.mass / total_mass)

    rvx = b.vx - a.vx
    rvy = b.vy - a.vy
    vel_along_normal = rvx * nx + rvy * ny

    if vel_along_normal > 0:
        return

    restitution = 1.0  # nearly perfect elastic collision
    impulse = -(1 + restitution) * vel_along_normal
    impulse /= (1 / a.mass) + (1 / b.mass)

    impulse_x = impulse * nx
    impulse_y = impulse * ny

    a.vx -= impulse_x / a.mass
    a.vy -= impulse_y / a.mass
    b.vx += impulse_x / b.mass
    b.vy += impulse_y / b.mass


def generate_balls(count: int) -> list[Ball]:
    balls: list[Ball] = []
    attempts = 0

    while len(balls) < count and attempts < 5000:
        attempts += 1
        radius = random.randint(12, 26)
        x = random.uniform(radius, WIDTH - radius)
        y = random.uniform(radius, HEIGHT - radius)
        vx = random.uniform(-260, 260)
        vy = random.uniform(-260, 260)
        color = (
            random.randint(70, 255),
            random.randint(70, 255),
            random.randint(70, 255),
        )
        candidate = Ball(x, y, vx, vy, radius, color)

        if all((candidate.x - b.x) ** 2 + (candidate.y - b.y) ** 2 >= (candidate.radius + b.radius) ** 2 for b in balls):
            balls.append(candidate)

    return balls


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Ball Inertia Demo")
    clock = pygame.time.Clock()

    balls = generate_balls(14)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                balls = generate_balls(14)

        for ball in balls:
            ball.update(dt)

        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                resolve_ball_collision(balls[i], balls[j])

        screen.fill(BACKGROUND)
        for ball in balls:
            ball.draw(screen)

        pygame.display.set_caption(
            f"2D Ball Inertia Demo | balls={len(balls)} | FPS={clock.get_fps():.1f} | R - reset"
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
