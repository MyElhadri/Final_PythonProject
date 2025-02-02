import pygame
import random
import sys

WIDTH, HEIGHT = 800, 600
FPS = 60

def start_animation():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Animation Pygame")
    clock = pygame.time.Clock()

    shapes = [
        {"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "dx": 2, "dy": 3}
        for _ in range(10)
    ]

    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for shape in shapes:
            shape["x"] += shape["dx"]
            shape["y"] += shape["dy"]
            if shape["x"] <= 0 or shape["x"] >= WIDTH:
                shape["dx"] *= -1
            if shape["y"] <= 0 or shape["y"] >= HEIGHT:
                shape["dy"] *= -1
            pygame.draw.circle(screen, (0, 0, 255), (shape["x"], shape["y"]), 20)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
