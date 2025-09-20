import os
import pygame
import random
import sys
import cv2
import mediapipe as mp

# Optional: set Pygame window position
os.environ['SDL_VIDEO_WINDOW_POS'] = '700,100'

# Initialize Pygame
pygame.init()

# Initial game window size
INITIAL_WIDTH, INITIAL_HEIGHT = 600, 800
win = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hand-Controlled Car Game")

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
DARK_GRAY = (30, 30, 30)
GREEN = (0, 200, 0)
BLUE = (0, 122, 255)

# Fonts
title_font = pygame.font.SysFont("Arial", 60)
button_font = pygame.font.SysFont("Arial", 35)
score_font = pygame.font.SysFont("Arial", 30)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Initial car size (will adjust dynamically)
car_width, car_height = 60, 100

# Obstacles
obstacles = []
obstacle_width, obstacle_height = 60, 100
obstacle_speed = 15


def spawn_obstacle(WIDTH):
    x = random.randint(50, WIDTH - obstacle_width - 50)
    return pygame.Rect(x, -obstacle_height, obstacle_width, obstacle_height)


def draw_window(state, score, WIDTH, HEIGHT, car, obstacles):
    win.fill(GRAY)

    # Road borders
    pygame.draw.rect(win, (80, 80, 80), (40, 0, WIDTH - 80, HEIGHT))

    # Lane lines
    lane_line_height = 40
    lane_line_gap = 60
    for i in range(0, HEIGHT, lane_line_gap):
        pygame.draw.rect(win, WHITE, (WIDTH // 2 - 5, i, 10, lane_line_height))

    # Obstacles
    for obs in obstacles:
        pygame.draw.rect(win, WHITE, obs)

    # Car
    pygame.draw.rect(win, RED, car)

    # Score (only show if game is playing)
    if state == "playing":
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        win.blit(score_text, (40, 30))

    pygame.display.update()


def draw_menu(WIDTH, HEIGHT):
    win.fill(DARK_GRAY)

    title = title_font.render("Car Game", True, WHITE)
    start_btn_text = button_font.render("Start Game", True, WHITE)
    start_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

    pygame.draw.rect(win, BLUE, start_btn_rect)
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
    win.blit(start_btn_text, (
        start_btn_rect.centerx - start_btn_text.get_width() // 2,
        start_btn_rect.centery - start_btn_text.get_height() // 2)
    )

    pygame.display.update()


def draw_game_over(WIDTH, HEIGHT):
    win.fill(DARK_GRAY)

    over_text = title_font.render("Game Over!", True, RED)

    restart_text = button_font.render("Restart", True, WHITE)
    quit_text = button_font.render("Quit", True, WHITE)

    restart_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2, 100, 60)
    quit_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2, 100, 60)

    pygame.draw.rect(win, GREEN, restart_rect)
    pygame.draw.rect(win, RED, quit_rect)

    win.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 120))

    win.blit(restart_text, (
        restart_rect.centerx - restart_text.get_width() // 2,
        restart_rect.centery - restart_text.get_height() // 2)
    )
    win.blit(quit_text, (
        quit_rect.centerx - quit_text.get_width() // 2,
        quit_rect.centery - quit_text.get_height() // 2)
    )

    pygame.display.update()


def main():
    global obstacles
    score = 0

    # Hand tracking setup
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1,
                           min_detection_confidence=0.7,
                           min_tracking_confidence=0.7)

    # Webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cv2.namedWindow('Hand Camera')
    cv2.moveWindow('Hand Camera', 100, 100)

    game_state = "menu"
    spawn_timer = 0
    frame_counter = 0

    # Set initial window size variables
    WIDTH, HEIGHT = pygame.display.get_surface().get_size()

    # Initialize car rect dynamically
    car_width_dynamic = max(40, WIDTH // 10)
    car_height_dynamic = max(60, HEIGHT // 8)
    car = pygame.Rect(WIDTH // 2 - car_width_dynamic // 2, HEIGHT - 150, car_width_dynamic, car_height_dynamic)

    # Adjust obstacle size dynamically (optional)
    global obstacle_width, obstacle_height
    obstacle_width = max(40, WIDTH // 10)
    obstacle_height = max(60, HEIGHT // 8)

    while True:
        clock.tick(FPS)
        frame_counter += 1

        # Update current window size on each frame
        WIDTH, HEIGHT = pygame.display.get_surface().get_size()

        # Update car and obstacle sizes relative to window size if you want (optional)
        car_width_dynamic = max(40, WIDTH // 10)
        car_height_dynamic = max(60, HEIGHT // 8)
        obstacle_width = max(40, WIDTH // 10)
        obstacle_height = max(60, HEIGHT // 8)

        # Update car size but keep position centered horizontally
        car.width = car_width_dynamic
        car.height = car_height_dynamic
        # Keep car near bottom
        if car.bottom != HEIGHT - 50:
            car.bottom = HEIGHT - 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()

            if game_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if WIDTH // 2 - 100 <= event.pos[0] <= WIDTH // 2 + 100 and HEIGHT // 2 <= event.pos[1] <= HEIGHT // 2 + 60:
                        game_state = "playing"
                        car.x = WIDTH // 2 - car.width // 2
                        obstacles = []
                        score = 0

            elif game_state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if WIDTH // 2 - 110 <= event.pos[0] <= WIDTH // 2 - 10:
                        game_state = "playing"
                        car.x = WIDTH // 2 - car.width // 2
                        obstacles = []
                        score = 0
                    elif WIDTH // 2 + 10 <= event.pos[0] <= WIDTH // 2 + 110:
                        cap.release()
                        cv2.destroyAllWindows()
                        pygame.quit()
                        sys.exit()

        # Webcam processing
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)


        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2))

                index_finger = hand_landmarks.landmark[8]
                finger_x = int(index_finger.x * WIDTH)
                car.centerx += (finger_x - car.centerx) // 3

                # Clamp inside road borders dynamically
                if car.left < 40:
                    car.left = 40
                if car.right > WIDTH - 40:
                    car.right = WIDTH - 40

        cv2.imshow('Hand Camera', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

        if game_state == "menu":
            draw_menu(WIDTH, HEIGHT)

        elif game_state == "playing":
            spawn_timer += 1
            if spawn_timer > 30:
                obstacles.append(spawn_obstacle(WIDTH))
                spawn_timer = 0

            new_obstacles = []
            for obs in obstacles:
                obs.y += obstacle_speed
                if obs.y > HEIGHT:
                    score += 1
                else:
                    new_obstacles.append(obs)
            obstacles = new_obstacles

            for obs in obstacles:
                if car.colliderect(obs):
                    game_state = "game_over"

            draw_window(game_state, score, WIDTH, HEIGHT, car, obstacles)

        elif game_state == "game_over":
            draw_game_over(WIDTH, HEIGHT)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()