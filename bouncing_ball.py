import pygame
import random
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
TEAL = (0, 255, 180)
FPS = 60

HIGH_SCORE_FILE = "highscore.txt"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

hit_sound = pygame.mixer.Sound("hitpaddle.wav")


def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))


class Ball:
    def __init__(self, radius):
        self.radius = radius
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.vx = random.choice([-5, 5])
        self.vy = random.choice([-4, 4])
        self.speed_multiplier = 0.5
        self.color = self.random_color()
        self.active = True

    def random_color(self):
        return (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

    def move(self):
        self.x += self.vx * self.speed_multiplier
        self.y += self.vy * self.speed_multiplier

        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.vx = -self.vx
            self.color = self.random_color()

        if self.y - self.radius <= 0:
            self.vy = -self.vy
            self.color = self.random_color()

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def hit_paddle(self, paddle_rect):
        if paddle_rect.collidepoint(self.x, self.y + self.radius) and self.vy > 0:
            self.vy = -self.vy
            self.color = self.random_color()
            self.speed_multiplier += 0.05
            hit_sound.play()
            return True
        return False

    def missed(self):
        return self.y - self.radius > HEIGHT


class Paddle:
    def __init__(self, width, height, y_offset):
        self.width = width
        self.height = height
        self.x = (WIDTH - width) // 2
        self.y = HEIGHT - y_offset
        self.speed = 10

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.get_rect())

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


def draw_text_center(surface, text, color, y):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(WIDTH // 2, y))
    surface.blit(label, rect)


def main():
    paddle = Paddle(width=120, height=20, y_offset=40)
    balls = [Ball(radius=30)]
    score = 0
    high_score = load_high_score()
    game_state = "menu"
    balls_spawned = 1

    running = True
    while running:
        screen.fill((0, 0, 0))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if (event.type == pygame.MOUSEBUTTONDOWN or
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
                if game_state in ["menu", "game_over"]:
                    balls = [Ball(radius=30)]
                    score = 0
                    balls_spawned = 1
                    game_state = "playing"

        if game_state == "menu":
            draw_text_center(screen, " Bouncing Ball Game ", WHITE, HEIGHT // 2 - 80)
            draw_text_center(screen, "Move the paddle with <-- and -->", TEAL, HEIGHT // 2 - 20)
            draw_text_center(screen, "Click or Press SPACE to Start", TEAL, HEIGHT // 2 + 40)

        elif game_state == "playing":
            paddle.move(keys)

            for ball in balls:
                if not ball.active:
                    continue

                ball.move()

                if ball.hit_paddle(paddle.get_rect()):
                    score += 1

                if ball.missed():
                    ball.active = False

                ball.draw(screen)

            balls = [b for b in balls if b.active]

            if score >= balls_spawned * 20:
                balls.append(Ball(radius=30))
                balls_spawned += 1

            if len(balls) == 0:
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = "game_over"

            paddle.draw(screen)

            score_text = font.render(f"Score: {score}", True, WHITE)
            high_text = font.render(f"High Score: {high_score}", True, TEAL)
            screen.blit(score_text, (20, 20))
            screen.blit(high_text, (20, 60))

        elif game_state == "game_over":
            draw_text_center(screen, " Game Over ", WHITE, HEIGHT // 2 - 80)
            draw_text_center(screen, f"Score: {score}", WHITE, HEIGHT // 2 - 20)
            draw_text_center(screen, f"High Score: {high_score}", TEAL, HEIGHT // 2 + 40)
            draw_text_center(screen, "Click or Press SPACE to Restart", TEAL, HEIGHT // 2 + 100)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()