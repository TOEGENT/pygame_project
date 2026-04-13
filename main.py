import math
import random
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 960, 640
FPS = 120
BACKGROUND = (18, 22, 28)
WALL_RESTITUTION = 0.98
MIN_RADIUS = 6.0
RICOCHET_RESTITUTION = 0.94

MIN_SENSITIVITY_K = 6.5
ASSIMILATION_K = 0.12
RUPTURE_K = 0.2

ASSIMILATION_TRANSFER_RATE = 0.09
ASSIMILATION_DRAG = 0.5

ATTACKER_RUPTURE_COST = 0.22
MAX_RUPTURE_EXTRA_FRAGMENTS = 5
FRAGMENT_MIN_RADIUS = 9.0
FRAGMENT_PROTECTION_TIME = 0.45


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    color: tuple[int, int, int]
    coherence: float
    alive: bool = True
    spawn_protection: float = 0.0

    @property
    def mass(self) -> float:
        return math.pi * self.radius * self.radius

    def add_mass(self, delta: float) -> None:
        new_mass = self.mass + delta
        min_mass = math.pi * MIN_RADIUS * MIN_RADIUS
        if new_mass < min_mass:
            self.alive = False
            return
        self.radius = math.sqrt(new_mass / math.pi)

    def update(self, dt: float) -> None:
        if self.spawn_protection > 0.0:
            self.spawn_protection = max(0.0, self.spawn_protection - dt)

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
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def target_thresholds(defender: Ball) -> tuple[float, float, float]:
    t_min = MIN_SENSITIVITY_K * math.sqrt(defender.mass) * defender.coherence
    t_assim = ASSIMILATION_K * defender.mass * defender.coherence
    t_rupture = t_assim + RUPTURE_K * defender.mass * (2.0 - defender.coherence)
    return t_min, t_assim, t_rupture


def apply_impulse(a: Ball, b: Ball, nx: float, ny: float, vel_along_normal: float, restitution: float) -> None:
    if vel_along_normal > 0:
        return

    impulse = -(1 + restitution) * vel_along_normal
    impulse /= (1 / a.mass) + (1 / b.mass)

    impulse_x = impulse * nx
    impulse_y = impulse * ny

    a.vx -= impulse_x / a.mass
    a.vy -= impulse_y / a.mass
    b.vx += impulse_x / b.mass
    b.vy += impulse_y / b.mass


def shatter_ball(defender: Ball, count: int, closing_speed: float) -> list[Ball]:
    fragments: list[Ball] = []
    count = max(2, count)
    total_mass = defender.mass
    min_fragment_mass = math.pi * FRAGMENT_MIN_RADIUS * FRAGMENT_MIN_RADIUS
    max_by_mass = max(2, int(total_mass / min_fragment_mass))
    count = min(count, max_by_mass)

    weights = [random.uniform(0.75, 1.25) for _ in range(count)]
    weight_sum = sum(weights)

    for weight in weights:
        part_mass = total_mass * (weight / weight_sum)
        part_radius = max(FRAGMENT_MIN_RADIUS, math.sqrt(part_mass / math.pi))
        angle = random.uniform(0, math.tau)
        speed = random.uniform(90, 180) + closing_speed * random.uniform(0.2, 0.5)
        color = (
            max(0, min(255, defender.color[0] + random.randint(-18, 18))),
            max(0, min(255, defender.color[1] + random.randint(-18, 18))),
            max(0, min(255, defender.color[2] + random.randint(-18, 18))),
        )
        fragments.append(
            Ball(
                x=max(part_radius, min(WIDTH - part_radius, defender.x + math.cos(angle) * (defender.radius * 0.45))),
                y=max(part_radius, min(HEIGHT - part_radius, defender.y + math.sin(angle) * (defender.radius * 0.45))),
                vx=defender.vx + math.cos(angle) * speed,
                vy=defender.vy + math.sin(angle) * speed,
                radius=part_radius,
                color=color,
                coherence=max(0.5, min(1.5, defender.coherence * random.uniform(0.9, 1.05))),
                spawn_protection=FRAGMENT_PROTECTION_TIME,
            )
        )

    return fragments


def resolve_ball_collision(a: Ball, b: Ball) -> list[Ball]:
    if not a.alive or not b.alive:
        return []

    dx = b.x - a.x
    dy = b.y - a.y
    distance_sq = dx * dx + dy * dy
    min_dist = a.radius + b.radius

    if distance_sq == 0:
        dx = random.uniform(-1.0, 1.0)
        dy = random.uniform(-1.0, 1.0)
        distance_sq = dx * dx + dy * dy

    if distance_sq >= min_dist * min_dist:
        return []

    distance = math.sqrt(distance_sq)
    nx = dx / distance
    ny = dy / distance

    overlap = min_dist - distance
    total_mass = a.mass + b.mass

    a.x -= nx * overlap * (b.mass / total_mass)
    a.y -= ny * overlap * (b.mass / total_mass)
    b.x += nx * overlap * (a.mass / total_mass)
    b.y += ny * overlap * (a.mass / total_mass)

    rvx = b.vx - a.vx
    rvy = b.vy - a.vy
    vel_along_normal = rvx * nx + rvy * ny
    closing_speed = max(0.0, -vel_along_normal)

    if closing_speed <= 0:
        return []

    impact_a_to_b = (a.mass * closing_speed * closing_speed) / max(1.0, b.radius)
    impact_b_to_a = (b.mass * closing_speed * closing_speed) / max(1.0, a.radius)

    if impact_a_to_b >= impact_b_to_a:
        attacker = a
        defender = b
        impact = impact_a_to_b
    else:
        attacker = b
        defender = a
        impact = impact_b_to_a

    t_min, t_assim, t_rupture = target_thresholds(defender)

    if impact < t_min:
        apply_impulse(a, b, nx, ny, vel_along_normal, RICOCHET_RESTITUTION)
        return []

    if impact < t_assim:
        apply_impulse(a, b, nx, ny, vel_along_normal, 0.22)
        progress = 1.0 - (impact / max(t_assim, 1e-6))
        transfer_mass = attacker.mass * ASSIMILATION_TRANSFER_RATE * progress
        transfer_mass = min(transfer_mass, attacker.mass * 0.35)

        if transfer_mass > 0:
            attacker.add_mass(-transfer_mass)
            if attacker.alive:
                defender.add_mass(transfer_mass)

        drag = max(0.0, 1.0 - ASSIMILATION_DRAG * progress)
        attacker.vx *= drag
        attacker.vy *= drag
        attacker.color = lerp_color(attacker.color, defender.color, 0.16 + 0.34 * progress)
        return []

    can_shatter = defender.spawn_protection <= 0.0 and defender.radius >= FRAGMENT_MIN_RADIUS * 1.45

    if impact < t_rupture or not can_shatter:
        apply_impulse(a, b, nx, ny, vel_along_normal, 0.08)
        if not can_shatter:
            return []
        overload = (impact - t_assim) / max(t_rupture - t_assim, 1e-6)
        fragment_count = 2 + int(overload * MAX_RUPTURE_EXTRA_FRAGMENTS)
        fragments = shatter_ball(defender, fragment_count, closing_speed)
        defender.alive = False

        resistance_loss = ATTACKER_RUPTURE_COST * (0.5 + 0.5 * overload) * defender.mass
        attacker.add_mass(-min(resistance_loss, attacker.mass * 0.55))
        attacker.vx *= 0.86
        attacker.vy *= 0.86
        return fragments

    if not can_shatter:
        apply_impulse(a, b, nx, ny, vel_along_normal, 0.12)
        return []

    apply_impulse(a, b, nx, ny, vel_along_normal, 0.03)
    fragments = shatter_ball(defender, 2 + MAX_RUPTURE_EXTRA_FRAGMENTS + 2, closing_speed)
    defender.alive = False
    resistance_loss = ATTACKER_RUPTURE_COST * 1.35 * defender.mass
    attacker.add_mass(-min(resistance_loss, attacker.mass * 0.7))
    attacker.vx *= 0.8
    attacker.vy *= 0.8
    return fragments


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
        coherence = random.uniform(0.7, 1.35)
        candidate = Ball(x, y, vx, vy, radius, color, coherence)

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

        spawned_balls: list[Ball] = []
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                if balls[i].alive and balls[j].alive:
                    spawned_balls.extend(resolve_ball_collision(balls[i], balls[j]))

        if spawned_balls:
            balls.extend(spawned_balls)
        balls = [ball for ball in balls if ball.alive]

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
