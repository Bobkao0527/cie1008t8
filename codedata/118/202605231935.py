# Auto-generated from 118-202605201818.ipynb

# --- Code Cell ---
import pygame

pygame.init()

SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,720),(4,1920,1440),(5,2880,2160)]
SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("骰子戰鬥遊戲")

battle_bg = pygame.image.load(r"C:\Users\Eason\Desktop\python\final\battleback2nog.png").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(battle_bg, (0, 0))

    pygame.display.update()

pygame.quit()

