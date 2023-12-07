import pygame
import sys
import random
import time

pygame.init()

width, height = 400, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("낚시 게임")

img_bg = pygame.image.load("sea.png")
img_start_bg = pygame.image.load("sea.png")
img_start_bg = pygame.transform.scale(img_start_bg, (width, height))

fish_image = pygame.image.load("myfish.png")
fish_image = pygame.transform.scale(fish_image, (70, 70))
trash_image = pygame.image.load("trash.png")
trash_image = pygame.transform.scale(trash_image, (70, 70))
plastic_image = pygame.image.load("plastic.png")
plastic_image = pygame.transform.scale(plastic_image, (70, 70))
paper_image = pygame.image.load("paper.png")
paper_image = pygame.transform.scale(paper_image, (70, 70))
net_image = pygame.image.load("net.png")
net_image = pygame.transform.scale(net_image, (150, 150))
heart_image = pygame.image.load("heart.png")
heart_image = pygame.transform.scale(heart_image, (50, 50))
hook_image = pygame.image.load("hook.png")
hook_image = pygame.transform.scale(hook_image, (50, 150))

font = pygame.font.Font(None, 36)

game_started = False

start_button_rect = pygame.Rect(150, height // 2 - 25, 100, 50)

clock = pygame.time.Clock()

fish_health = 5
invincible_time = 2
invincible_start_time = 0

white = (255, 255, 255)
red = (255, 0, 0)

fish_x = width // 2 - 35
fish_y = height - 50
fish_speed = 10

falling_objects = []
falling_speed = 2
falling_frequency = 0.5
last_falling_time = pygame.time.get_ticks()

hook_x = random.randint(0, width - 20)
hook_y = 0
hook_speed = 5
hook_falling = True  # 낚시바늘이 내려가는 중인지 여부
falling_start_time = time.time()

start_time = pygame.time.get_ticks()

net_active = False
net_x = 0
net_y = 0
net_speed = 5
net_direction = 1
net_caught = False
escape_countdown = 0

heart_active = False
heart_x = 0
heart_y = 0
heart_spawn_time = 30
last_heart_time = pygame.time.get_ticks()

bg_music_file = "실행bgm.wav"
pygame.mixer.music.load(bg_music_file)
pygame.mixer.music.set_volume(0.5)

button_sound = pygame.mixer.Sound("button.wav")

collide_sound = pygame.mixer.Sound("하트.wav")

item_scores = {
    trash_image: -1,
    plastic_image: -1,
    paper_image: -1,
    fish_image: 1
}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                screen = pygame.display.set_mode((600, 400), pygame.FULLSCREEN)
            if event.key == pygame.K_F2 or event.key == pygame.K_ESCAPE:
                screen = pygame.display.set_mode((600, 400))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if start_button_rect.collidepoint(event.pos) and not game_started:
                    game_started = True
                    button_sound.play()

    if not game_started:
        screen.blit(img_start_bg, (0, 0))
        pygame.draw.rect(screen, white, start_button_rect)
        start_text = font.render("game start", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=(width // 2, height // 2))
        screen.blit(start_text, start_text_rect)
        pygame.display.flip()
        clock.tick(30)
        continue

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and fish_x > 0:
        fish_x -= fish_speed
    if keys[pygame.K_RIGHT] and fish_x < width - 70:
        fish_x += fish_speed
    if keys[pygame.K_UP] and fish_y > 0:
        fish_y -= fish_speed
    if keys[pygame.K_DOWN] and fish_y < height - 70:
        fish_y += fish_speed

    current_time = pygame.time.get_ticks()

    if hook_falling:
        hook_y += hook_speed
        if hook_y > random.randint(200, height - 50):
            hook_falling = False
            falling_start_time = time.time()  # 낚시바늘이 멈춘 시간 저장
    else:
        if time.time() - falling_start_time > 1:
            hook_y -= hook_speed
        if hook_y < 0:
            hook_falling = True
            hook_y = 0
            hook_x = random.randint(50, height - 50)

    if current_time - invincible_start_time > invincible_time:
        fish_rect = pygame.Rect(fish_x, fish_y, 50, 50)
        hook_rect = pygame.Rect(hook_x, hook_y, 50, 50)
        if fish_rect.colliderect(hook_rect):
            fish_health -= 1
            invincible_start_time = time.time()

    if (current_time - last_falling_time) / 1000 > 1 / falling_frequency:
        last_falling_time = current_time
        random_object = random.choice(
            [trash_image, plastic_image, paper_image, net_image])
        if current_time - last_heart_time > heart_spawn_time * 1000:
            random_object = heart_image
            last_heart_time = current_time

        object_probabilities = [0.24, 0.24, 0.24, 0.24, 0.04]
        random_number = random.random()

        if random_number < object_probabilities[0]:
            random_object = trash_image
        elif random_number < object_probabilities[0] + object_probabilities[1]:
            random_object = plastic_image
        elif random_number < object_probabilities[0] + object_probabilities[1] + object_probabilities[2]:
            random_object = paper_image
        elif random_number < object_probabilities[0] + object_probabilities[1] + object_probabilities[2]:
            random_object = net_image
        else:
            random_object = heart_image

        if random_object in [trash_image, plastic_image, paper_image]:
            falling_speed += 0.1

        falling_objects.append(
            [random.randint(0, width - 30), 0, random_object])

    screen.blit(img_bg, (0, 0))

    for falling_object in falling_objects:
        falling_object[1] += falling_speed

        if (
            fish_x - 35 < falling_object[0] < fish_x + 35
            and fish_y - 35 < falling_object[1] < fish_y + 35
        ):
            if falling_object[2] == net_image and not net_caught:
                fish_speed = 3
                net_caught = True
                net_effect_start_time = time.time()

            elif falling_object[2] == heart_image and not heart_active:
                fish_health += 1
                heart_active = True

                collide_sound.play()

            falling_objects.remove(falling_object)
            invincible_start_time = time.time()

        if falling_object[1] > height:
            falling_objects.remove(falling_object)

        if falling_object[2] in [trash_image, paper_image, plastic_image] and falling_object[1] > height:
            fish_health -= 1

        screen.blit(falling_object[2], (falling_object[0], falling_object[1]))

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()

    if net_active:
        screen.blit(net_image, (net_x, net_y))
        net_x += net_speed * net_direction
        net_y += net_speed * net_direction
        if net_x < 0 or net_x > width - 150:
            net_direction *= -1
            escape_countdown = 0

        if net_caught:
            escape_countdown += 1
            if escape_countdown == 5:
                fish_speed = 10
                net_active = False
                net_caught = False
                falling_speed = 2
                escape_countdown = 0

    if heart_active:
        screen.blit(heart_image, (heart_x, heart_y))
        heart_y += falling_speed
        if heart_y > height:
            heart_active = False

    screen.blit(fish_image, (fish_x, fish_y))

    screen.blit(hook_image, (hook_x, hook_y))
    health_text = font.render(f"Life: {fish_health}", True, white)
    screen.blit(health_text, (10, 10))

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    time_text = font.render(f"Time: {elapsed_time} seconds", True, white)
    screen.blit(time_text, (width - 200, 10))

    if fish_health <= 0:
        pygame.mixer.music.stop()
        game_over_text = font.render("Game Over", True, red)
        game_over_text_rect = game_over_text.get_rect(
            center=(width // 2, height // 3))
        screen.blit(game_over_text, game_over_text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    pygame.display.flip()

    clock.tick(30)
