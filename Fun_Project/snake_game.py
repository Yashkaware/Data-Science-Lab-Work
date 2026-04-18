import turtle
import time
import random
import json
import os

# ── Constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 600
CELL = 20
DELAY = 0.12
LB_FILE = "leaderboard.json"

# ── Leaderboard helpers ────────────────────────────────────────────────────────
def load_leaderboard():
    if os.path.exists(LB_FILE):
        with open(LB_FILE) as f:
            return json.load(f)
    return []

def save_leaderboard(lb):
    with open(LB_FILE, "w") as f:
        json.dump(lb, f)

def add_score(name, score):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score})
    lb = sorted(lb, key=lambda x: x["score"], reverse=True)[:10]
    save_leaderboard(lb)
    return lb

def show_leaderboard(lb):
    print("\n🏆 Leaderboard")
    print("─" * 25)
    for i, entry in enumerate(lb[:10], 1):
        print(f"  {i:2}. {entry['name']:<12} {entry['score']}")
    print("─" * 25)

# ── Setup ──────────────────────────────────────────────────────────────────────
screen = turtle.Screen()
screen.title("🐍 Snake Game")
screen.bgcolor("black")
screen.setup(WIDTH + 20, HEIGHT + 60)
screen.tracer(0)

# Score display
score_pen = turtle.Turtle()
score_pen.hideturtle()
score_pen.penup()
score_pen.color("white")
score_pen.goto(0, HEIGHT // 2 - 30)

def update_score(score, best):
    score_pen.clear()
    score_pen.write(
        f"Score: {score}   Best: {best}",
        align="center",
        font=("Courier", 14, "bold")
    )

# Snake head
head = turtle.Turtle()
head.shape("square")
head.color("#378ADD")
head.penup()
head.goto(0, 0)
head.direction = "Right"

# Food
food = turtle.Turtle()
food.shape("circle")
food.color("#D85A30")
food.penup()
food.goto(
    random.randrange(-WIDTH // 2 // CELL, WIDTH // 2 // CELL) * CELL,
    random.randrange(-HEIGHT // 2 // CELL, HEIGHT // 2 // CELL) * CELL
)

# ── Game state ─────────────────────────────────────────────────────────────────
segments = []
score = 0
best_score = 0
game_running = False

# ── Direction controls ─────────────────────────────────────────────────────────
def go_up():
    if head.direction != "Down":
        head.direction = "Up"

def go_down():
    if head.direction != "Up":
        head.direction = "Down"

def go_left():
    if head.direction != "Right":
        head.direction = "Left"

def go_right():
    if head.direction != "Left":
        head.direction = "Right"

screen.listen()
screen.onkeypress(go_up, "Up")
screen.onkeypress(go_down, "Down")
screen.onkeypress(go_left, "Left")
screen.onkeypress(go_right, "Right")
screen.onkeypress(go_up, "w")
screen.onkeypress(go_down, "s")
screen.onkeypress(go_left, "a")
screen.onkeypress(go_right, "d")

# ── Movement ───────────────────────────────────────────────────────────────────
def move():
    if head.direction == "Up":
        head.sety(head.ycor() + CELL)
    elif head.direction == "Down":
        head.sety(head.ycor() - CELL)
    elif head.direction == "Left":
        head.setx(head.xcor() - CELL)
    elif head.direction == "Right":
        head.setx(head.xcor() + CELL)

def reset_game():
    global score, segments, game_running
    time.sleep(0.5)
    head.goto(0, 0)
    head.direction = "Right"
    for seg in segments:
        seg.goto(1000, 1000)
    segments.clear()
    score = 0
    update_score(score, best_score)

# ── Main loop ──────────────────────────────────────────────────────────────────
def game_loop():
    global score, best_score, game_running

    # Move body segments
    for i in range(len(segments) - 1, 0, -1):
        segments[i].setx(segments[i - 1].xcor())
        segments[i].sety(segments[i - 1].ycor())
    if segments:
        segments[0].setx(head.xcor())
        segments[0].sety(head.ycor())

    move()
    screen.update()

    # Wall collision
    if (abs(head.xcor()) > WIDTH // 2 - CELL // 2 or
            abs(head.ycor()) > HEIGHT // 2 - CELL // 2):
        game_over()
        return

    # Self collision
    for seg in segments:
        if seg.distance(head) < CELL - 2:
            game_over()
            return

    # Food collision
    if head.distance(food) < CELL:
        food.goto(
            random.randrange(-WIDTH // 2 // CELL, WIDTH // 2 // CELL) * CELL,
            random.randrange(-HEIGHT // 2 // CELL, HEIGHT // 2 // CELL) * CELL
        )
        # Add segment
        new_seg = turtle.Turtle()
        new_seg.shape("square")
        new_seg.color("#5DCAA5")
        new_seg.penup()
        segments.append(new_seg)

        score += 1
        if score > best_score:
            best_score = score
        update_score(score, best_score)

    screen.ontimer(game_loop, int(DELAY * 1000))

def game_over():
    global game_running
    game_running = False

    # Save to leaderboard
    player_name = screen.textinput("Game Over!", f"Score: {score}\nEnter your name:")
    if player_name:
        lb = add_score(player_name.strip() or "Player", score)
        show_leaderboard(lb)

    # Ask to play again
    play_again = screen.textinput("Play again?", "Enter 'yes' to restart or 'no' to quit:")
    if play_again and play_again.strip().lower() in ("yes", "y"):
        reset_game()
        start_game()
    else:
        print("\nThanks for playing! 🐍")
        screen.bye()

def start_game():
    global game_running
    game_running = True
    update_score(score, best_score)
    screen.ontimer(game_loop, int(DELAY * 1000))

# ── Draw border ────────────────────────────────────────────────────────────────
border = turtle.Turtle()
border.hideturtle()
border.penup()
border.goto(-WIDTH // 2, -HEIGHT // 2)
border.pendown()
border.pensize(3)
border.pencolor("#444444")
for _ in range(4):
    border.forward(WIDTH if border.heading() in (0, 180) else HEIGHT)
    border.left(90)

# ── Start ──────────────────────────────────────────────────────────────────────
print("🐍 Snake Game")
print("Controls: Arrow keys or WASD")
print("Close the window or enter 'no' after game over to quit.\n")

update_score(0, 0)
start_game()
turtle.done()
