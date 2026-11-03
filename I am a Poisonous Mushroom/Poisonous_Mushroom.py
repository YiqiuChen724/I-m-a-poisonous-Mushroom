import os
import sys
import random
import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("I'm a poisonous Mushroom")
clock = pygame.time.Clock()

SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_GREEN = (70, 160, 70)
BUTTON_RED = (160, 70, 70)
STATUS_BG = (50, 100, 50, 180)
ENDING_BG = (30, 10, 10)
CAVE_BG = (45, 45, 60)
CAVE_GROUND = (75, 60, 45)
RELIC_BG = (200, 180, 150)
RELIC_GROUND = (140, 110, 80)
SHOP_BG = (210, 190, 150)
SHOP_GROUND = (150, 120, 80)

try:
    font = pygame.font.SysFont("simhei", 24)
    font_small = pygame.font.SysFont("simhei", 20)
    font_status = pygame.font.SysFont("simhei", 18)
    font_title = pygame.font.SysFont("simhei", 38)
except:
    font = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 24)
    font_status = pygame.font.Font(None, 22)
    font_title = pygame.font.Font(None, 44)

# ---------------- 背景图加载 ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE_DIR, "assets")

def load_img(filename, size=None):
    path = os.path.join(BG_DIR, filename)
    try:
        img = pygame.image.load(path).convert()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        print(f"[Image failed to load] {path}: {e}")
        return None

def load_bg(filename):
    return load_img(filename, (WIDTH, HEIGHT))

BG_INTRO      = load_bg("bg_intro.png")
BG_MENU       = load_bg("bg_menu.png")
BG_GAME       = load_bg("bg_game.png")
BG_STONE      = load_bg("bg_stone.png")
BG_CAVE       = load_bg("bg_cave.jpg")
BG_RELIC      = load_bg("bg_relic.png")
BG_SHOP       = load_bg("bg_shop.png")
BG_PLOT1      = load_bg("bg_plot1.png")
BG_PLOT2      = load_bg("bg_plot2.png")
BG_TRAINING   = load_bg("bg_training.png")
BG_TELEPORT   = load_bg("bg_relic.png")
BG_ENDING = None
BG_ACHIEVE = None
IMG_SHOP_ITEM = None

IMG_BAR        = load_img("img_bar.png")          # （Click "Go to the bar"）

def draw_bg(bg, fallback_color):
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(fallback_color)

STATE_INTRO = "intro"
STATE_MENU = "menu"
STATE_GAME = "game"
STATE_STONE_TOWN = "stone_town"
STATE_CAVE = "cave"
STATE_RELICS = "relics"
STATE_ENDING = "ending"
STATE_PLOT1 = "plot1"
STATE_PLOT2 = "plot2"
STATE_TRAINING = "training"
STATE_TELEPORT = "teleport"
STATE_ACHIEVEMENT = "achievement"
STATE_SHOP = "shop"
STATE_SHOP_REWARD = "shop_reward"
STATE_BAR = "bar"                  # 新增：酒吧图片展示状态

current_state = STATE_MENU
ending_to_achievement = False

teleport_text = ""
ending_title = ""
ending_text = ""
popup_text = ""
popup_timer = 0

# 酒吧展示状态的数据
bar_data = {
    "text": "",
}

def reset_game():
    global current_state, teleport_text, ending_title, ending_text
    global popup_text, popup_timer, ending_to_achievement
    global player, dialog_data, stone_town_data, cave_data, relic_data, shop_data
    global plot1_data, plot2_data, training_data, bar_data

    player = {
        "day": 1, "money": 0, "friendship": 0, "ap": 1,
        "first_town": False, "bath_done": False, "bar_count": 0,
        "socialite": False, "met_bruce": False, "secret_done": False,
        "ivan_done": False, "ivan_asked": False, "ivan_f": 0,
        "dandelion_done": False, "richest": False, "dormouse_done": False,
        "stone_picked": False, "ending3_done": False,
        "potion_bought_today": False, "discount_coupon": False,
        "bruce_explore_count": 0, "bruce_explore_today": False,
        "explorer": False, "house_built": False, "relic_first_visit": False,
    }

    dialog_data = {
        "text": "It is Day 1. Where should we go?",
        "options": ["Stone Town", "Underground Cave", "Ruins of the Wind"]
    }

    stone_town_data = {
        "text": "You have arrived in Stone Town. What shall we do today?",
        "options": ["Work", "Go to the bar with Alan", "Bathe in human soup"],
        "stage": "choose", "story_index": 0,
        "story_lines": [
            "-This is the busiest town around. So many humans wandering about! What should we do?",
            "(A friendly-looking human man approaches.)",
            "-Alan: Hey, a walking mushroom! What is your name? I am Alan.",
            "-I am Toxie Mushi, a poisonous mushroom. Nice to meet you!",
            "-Alan: Cool name! Let us be friends. I work at the bar next door."
        ]
    }

    cave_data = {
        "text": "You enter the Underground Cave. It is dark and damp.",
        "options": ["Search for gold", "Pick up a pretty stone", "Sleep"],
        "stage": "choose", "story_lines": [], "story_index": 0, "after_story": None,
    }

    relic_data = {
        "text": "You reach the Ruins of the Wind. Ancient pillars whisper in the breeze.",
        "options": ["Fight the invader with Ivan", "Pick a dandelion"],
        "stage": "choose", "story_lines": [], "story_index": 0, "after_story": None,
    }

    shop_data = {
        "text": "Shopkeeper: Welcome! What can I get for you?",
        "stage": "shop", "options": ["Buy strength potion", "Leave"]
    }

    plot1_data = {
        "stage": "story", "story_index": 0,
        "story_lines": [
            "A deep, muffled voice answers you and Toxie.",
            "?: Hero chosen by the Earth God, a terrible dragon has tormented us. Please help us...",
            "A mole with long front teeth has somehow appeared before Toxie.",
            "Make your choice:"
        ],
        "text": "", "options": ["Stay", "Run away"], "after_text": "", "choice": None,
    }

    plot2_data = {
        "text": "Prepare yourself before facing the dragon:",
        "options": ["Train: Swordsmanship", "Train: Mushroom Magic", "Explore the dragon's lair"],
        "stage": "choose"
    }

    training_data = {
        "stage": "choose", "story_index": 0, "story_lines": [], "text": "",
        "options": ["Train: Swordsmanship", "Train: Mushroom Magic", "Explore the dragon's lair"],
        "pending_ending": None,
    }

    bar_data = {"text": ""}

    teleport_text = ""
    ending_title = ""
    ending_text = ""
    popup_text = ""
    popup_timer = 0
    ending_to_achievement = False
    current_state = STATE_MENU

reset_game()

# ---------------- 工具函数 ----------------

def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        current_line = ""
        for char in paragraph:
            if font.size(current_line + char)[0] <= max_width:
                current_line += char
            else:
                lines.append(current_line)
                current_line = char
        lines.append(current_line)
    return lines

def get_button_rects(options, start_y=HEIGHT-50, btn_width=180, gap=20):
    total = btn_width * len(options) + gap * (len(options) - 1)
    start_x = (WIDTH - total) // 2
    return [pygame.Rect(start_x + i*(btn_width+gap), start_y, btn_width, 40)
            for i in range(len(options))]

def draw_buttons(options, start_y=HEIGHT-50, btn_width=180, gap=20):
    rects = get_button_rects(options, start_y, btn_width, gap)
    mouse = pygame.mouse.get_pos()
    for i, opt in enumerate(options):
        color = (200, 200, 100) if rects[i].collidepoint(mouse) else (180, 180, 80)
        pygame.draw.rect(screen, color, rects[i], border_radius=10)
        pygame.draw.rect(screen, BLACK, rects[i], width=1, border_radius=10)
        surf = font_small.render(opt, True, BLACK)
        screen.blit(surf, surf.get_rect(center=rects[i].center))
    return rects

def draw_mushroom(x, y):
    pygame.draw.ellipse(screen, (220, 20, 20), (x, y, 80, 50))
    pygame.draw.circle(screen, WHITE, (x+20, y+15), 8)
    pygame.draw.circle(screen, WHITE, (x+50, y+30), 6)
    pygame.draw.rect(screen, (240, 240, 240), (x+30, y+40, 20, 40))

    def draw_toxie(happy=False, x=80, y=160, width=180):
        img = TOXIE_HAPPY if happy else TOXIE_NORMAL

        if img is None:
            return

        ratio = width / img.get_width()
        height = int(img.get_height() * ratio)

        scaled = pygame.transform.smoothscale(img, (width, height))
        screen.blit(scaled, (x, y))

def draw_status_bar():
    bar = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
    bar.fill(STATUS_BG)
    screen.blit(bar, (0, 0))
    info = f"Day: {player['day']}  Money: ${player['money']}  F: {player['friendship']}  AP: {player['ap']}"
    surf = font_status.render(info, True, WHITE)
    screen.blit(surf, (10, 10))

def draw_dialog_box(text, options=None, stage="choose"):
    box = pygame.Rect(WIDTH//2 - 300, HEIGHT-210, 600, 170)
    pygame.draw.rect(screen, WHITE, box, border_radius=15)
    pygame.draw.rect(screen, BLACK, box, width=3, border_radius=15)

    lines = wrap_text(text, font, 560)
    for i, line in enumerate(lines[:5]):
        surf = font.render(line, True, BLACK)
        screen.blit(surf, (WIDTH//2 - 280, HEIGHT-190 + i*32))

    if stage == "choose" and options:
        draw_buttons(options)
    else:
        tip_text = "Click anywhere to end the day" if stage == "done" else "Click anywhere to continue"
        tip = font_small.render(tip_text, True, (100, 100, 100))
        screen.blit(tip, tip.get_rect(center=(WIDTH//2, HEIGHT-50)))

def check_achievements():
    global popup_text, popup_timer
    if player["money"] > 8 and not player["richest"]:
        player["richest"] = True
        popup_text = "Achievement unlocked: Richest Mushroom!"
        popup_timer = 180

def check_explorer_achievement():
    global popup_text, popup_timer
    if player["bruce_explore_count"] >= 3 and not player["explorer"]:
        player["explorer"] = True
        popup_text = "Achievement unlocked: Explorer!"
        popup_timer = 180

def check_friend_ending():
    return False

# ---------------- Stone Town ----------------

def prepare_stone_town_choose():
    stone_town_data["stage"] = "choose"
    stone_town_data["text"] = "You have arrived in Stone Town. What shall we do today?"
    if player["bar_count"] >= 1:
        base = ["Work", "Go to the bar", "Bathe in human soup"]
    else:
        base = ["Work", "Go to the bar with Alan", "Bathe in human soup"]
    if player["day"] >= 2:
        base.append("Shop")
    stone_town_data["options"] = base
    player["potion_bought_today"] = False

def get_shop_price():
    return 3 if player["discount_coupon"] else 5

def open_shop():
    global current_state
    shop_data["stage"] = "shop"
    price = get_shop_price()
    coupon_tip = "(You have a coupon! Today: 3 coins!)" if player["discount_coupon"] else ""
    if player["potion_bought_today"]:
        shop_data["text"] = "Shopkeeper: You already bought a strength potion today. Come back tomorrow!"
        shop_data["options"] = ["Leave"]
    else:
        shop_data["text"] = f"Shopkeeper: Strength potion, {price} coins. {coupon_tip}"
        shop_data["options"] = ["Buy strength potion", "Leave"]
    current_state = STATE_SHOP

def handle_stone_town(index):
    global popup_text, popup_timer, current_state
    opt = stone_town_data["options"][index]

    if opt == "Work":
        player["money"] += 3
        stone_town_data["text"] = "Alan helped Toxie find a part-time job. 'Good work!' says the boss, paying three gold coins."
        check_achievements()
        stone_town_data["stage"] = "done"
        player["ap"] = 0

    elif opt in ("Go to the bar with Alan", "Go to the bar"):
        player["bar_count"] += 1
        if opt == "Go to the bar with Alan":
            player["friendship"] += 2
            bar_text = "Going to the bar with Alan is a blast. He knows how everything works, so Toxie can just have fun! Toxie makes two new friends."
        else:
            if player["bar_count"] == 2:
                player["friendship"] += 1
                player["socialite"] = True
                popup_text = "Achievement unlocked: Social Butterfly! You are the star of the bar!"
                popup_timer = 180
                bar_text = "Alan is busy today, so Toxie has a drink alone at the bar and makes one new friend."
            else:
                bar_text = "You visit the bar for another drink, but make no new friends today."
        player["ap"] = 0
        # 进入酒吧图片展示状态
        bar_data["text"] = bar_text
        current_state = STATE_BAR

    elif opt == "Bathe in human soup":
        player["friendship"] += 1
        player["bath_done"] = True
        popup_text = "Achievement unlocked: Bad Mushroom!"
        popup_timer = 180
        stone_town_data["text"] = "-Are we really doing this?\nToxie Mushi hesitates, but the soup smells delicious. It is rich and warm..."
        stone_town_data["stage"] = "done"
        player["ap"] = 0

    elif opt == "Shop":
        open_shop()

# ---------------- Shop ----------------

def handle_shop(index):
    global current_state, shop_data
    opt = shop_data["options"][index]

    if opt == "Buy strength potion":
        price = get_shop_price()
        if player["money"] < price:
            shop_data["text"] = f"Shopkeeper: Not enough coins! You need {price}."
            shop_data["options"] = ["Leave"]
            return
        player["money"] -= price
        if player["discount_coupon"]:
            player["discount_coupon"] = False
        player["potion_bought_today"] = True
        shop_data["stage"] = "reward"
        shop_data["text"] = "You drink the strength potion and feel power surging through you! Choose a stat to boost:"
        shop_data["options"] = ["Ivan Friendship +1", "Friendship +1", "Money +10"]
        current_state = STATE_SHOP_REWARD

    elif opt == "Leave":
        if player["day"] == 2 and not player["discount_coupon"] and not player["potion_bought_today"]:
            player["discount_coupon"] = True
            shop_data["text"] = "Shopkeeper: Not buying? Take this coupon! You can save 2 coins tomorrow!"
            shop_data["options"] = ["Leave the shop"]
            shop_data["stage"] = "coupon_given"
        else:
            shop_data["text"] = "Shopkeeper: All right! Come again soon!"
            shop_data["options"] = ["Leave the shop"]
            shop_data["stage"] = "normal_leave"

def handle_shop_leave():
    global current_state
    prepare_stone_town_choose()
    current_state = STATE_STONE_TOWN

def handle_shop_reward(index):
    global current_state
    opt = shop_data["options"][index]

    if opt == "Ivan Friendship +1":
        player["ivan_f"] += 1
        shop_data["text"] = "You feel closer to Ivan! (Ivan Friendship +1)"
    elif opt == "Friendship +1":
        player["friendship"] += 1
        shop_data["text"] = "You feel more popular! (Friendship +1)"
    elif opt == "Money +10":
        player["money"] += 10
        shop_data["text"] = "You feel light as air, and find 10 extra coins in your pocket!"
        check_achievements()

    prepare_stone_town_choose()
    current_state = STATE_STONE_TOWN

# ---------------- Underground Cave ----------------

def refresh_cave():
    cave_data["text"] = "You enter the Underground Cave. It is dark and damp."
    cave_data["stage"] = "choose"
    opts = ["Search for gold"]
    if not player["stone_picked"]:
        opts.append("Pick up a pretty stone")
    if not player["dormouse_done"]:
        opts.append("Sleep")
    if player["met_bruce"] and not player["bruce_explore_today"]:
        opts.append("Explore with Bruce")
    if player["day"] >= 3:
        opts.append("Build a cave house")
    cave_data["options"] = opts

def start_cave_story(lines, after):
    cave_data["story_lines"] = lines
    cave_data["story_index"] = 0
    cave_data["text"] = lines[0]
    cave_data["stage"] = "story"
    cave_data["after_story"] = after

def handle_cave(index):
    global current_state, ending_title, ending_text
    opt = cave_data["options"][index]

    if opt == "Search for gold":
        gold = random.choice([3, 6, 8])
        player["money"] += gold
        stone_name = "tiny gold nugget" if gold == 3 else ("gold nugget" if gold == 6 else "large gold nugget")
        lines = [
            "The dark tunnel holds unexpected surprises. Toxie digs with all their might...",
            f"Found one! A {stone_name}. (+{gold} coins)",
            "Exhausting, but well worth it."
        ]
        check_achievements()
        start_cave_story(lines, "done")
        player["ap"] = 0

    elif opt == "Pick up a pretty stone":
        player["stone_picked"] = True
        player["met_bruce"] = True
        player["friendship"] += 1
        lines = [
            "A strangely patterned stone glows like fire in the darkness. Toxie picks it up.",
            "(A furry paw reaches out.)",
            "It is a mole.",
            "Bruce: Little mushroom, that belongs to me. Could I have it back?",
            "-Oh, it is yours? Here you go! By the way, do you know where I can find more pretty stones?",
            "Bruce: You really like minerals, huh? We should go mining together sometime. I am Bruce. And you?",
            "-I am Toxie Mushi.",
            "(+1 friend)"
        ]
        start_cave_story(lines, "done")
        player["ap"] = 0

    elif opt == "Sleep":
        player["dormouse_done"] = True
        lines = [
            "The dim, damp cave makes Toxie sleepy, as if they were back where they first grew.",
            "-Where am I?"
        ]
        start_cave_story(lines, "plot1")

    elif opt == "Explore with Bruce":
        player["bruce_explore_today"] = True
        player["bruce_explore_count"] += 1
        player["friendship"] += 2
        player["money"] += 3
        check_achievements()
        check_explorer_achievement()
        lines = [
            "Bruce and his mole friends make a reliable mining team.",
            "Toxie finds many beautiful minerals with them, and they have a wonderful time chatting.",
            "(+2 friends, +3 coins)"
        ]
        start_cave_story(lines, "done")
        player["ap"] = 0

    elif opt == "Build a cave house":
        if player["money"] < 8:
            cave_data["text"] = "Not enough coins. Building a house costs 8 coins."
            cave_data["stage"] = "choose"
            refresh_cave()
            return
        player["money"] -= 8
        check_achievements()
        player["house_built"] = True
        ending_title = "Ending 8: A Home Underground"
        ending_text = ("Who would not want an underground home full of winding passages, safety, and surprises? "
                       "Little Toxie Mushi is no exception. Now a wealthy mushroom, "
                       "Toxie decides, with your help, to make a home underground.")
        current_state = STATE_ENDING

def advance_cave_story():
    global current_state
    cave_data["story_index"] += 1
    if cave_data["story_index"] < len(cave_data["story_lines"]):
        cave_data["text"] = cave_data["story_lines"][cave_data["story_index"]]
    else:
        after = cave_data["after_story"]
        cave_data["after_story"] = None
        if after == "plot1":
            start_plot1()
        else:
            cave_data["stage"] = "done"

# ---------------- 强制剧情 ----------------

def start_plot1():
    global current_state
    plot1_data["stage"] = "story"
    plot1_data["story_index"] = 0
    plot1_data["text"] = plot1_data["story_lines"][0]
    plot1_data["after_text"] = ""
    plot1_data["choice"] = None
    current_state = STATE_PLOT1

def advance_plot1_story():
    plot1_data["story_index"] += 1
    if plot1_data["story_index"] < len(plot1_data["story_lines"]):
        plot1_data["text"] = plot1_data["story_lines"][plot1_data["story_index"]]
    else:
        plot1_data["stage"] = "choose"
        plot1_data["text"] = "Make your choice:"

def handle_plot1_choice(index):
    if index == 0:
        plot1_data["choice"] = "stay"
        plot1_data["after_text"] = "The grateful mole takes Toxie by the hand."
    else:
        plot1_data["choice"] = "flee"
        player["money"] += 5
        check_achievements()
        plot1_data["after_text"] = (
            "Toxie is terrified. Three days are far too short to spend facing a dragon. "
            "While the mole is distracted, Toxie releases spores and runs away. "
            "Luckily, Toxie finds a tiny diamond on the way. (+5 coins)"
        )
    plot1_data["stage"] = "after_leave"

def start_plot2():
    global current_state
    plot2_data["stage"] = "choose"
    plot2_data["text"] = "Prepare yourself before facing the dragon:"
    plot2_data["options"] = ["Train: Swordsmanship", "Train: Mushroom Magic", "Explore the dragon's lair"]
    current_state = STATE_PLOT2

def start_training(option_index):
    global current_state
    training_data["story_index"] = 0
    if option_index == 0:
        training_data["story_lines"] = ["Mushrooms have no hands, but the chosen hero Mushi learns to lift a sword with spores. After some practice, it feels natural. Time to fight!"]
        training_data["pending_ending"] = "sword"
    elif option_index == 1:
        training_data["story_lines"] = ["In this magical world, the hero Mushi gradually masters ancient mushroom magic. Time to fight!"]
        training_data["pending_ending"] = "magic"
    else:
        training_data["story_lines"] = ["Know your enemy and know yourself. Let us take a look!"]
        training_data["pending_ending"] = "cave"
    training_data["stage"] = "story"
    training_data["text"] = training_data["story_lines"][0]
    current_state = STATE_TRAINING

def advance_training_story():
    global current_state, ending_title, ending_text
    training_data["story_index"] += 1
    if training_data["story_index"] < len(training_data["story_lines"]):
        training_data["text"] = training_data["story_lines"][training_data["story_index"]]
    else:
        pe = training_data["pending_ending"]
        training_data["pending_ending"] = None
        if pe == "sword":
            ending_title = "Ending 5: Mushroom Hero"
            ending_text = "The mushroom hero defeats the dragon. Peace returns underground, and the moles live happily. They invite Toxie to stay, but Toxie promises only to visit often."
        elif pe == "magic":
            ending_title = "Ending: Mushroom Mage (To Be Continued)"
            ending_text = "Story to be added: You master mushroom magic and defeat the dragon with poisonous mushroom powers..."
        elif pe == "cave":
            ending_title = "Ending 6: Hot Spring Inn"
            ending_text = "The dragon's fiery breath heats a cold underground spring into a lovely hot spring. You send Toxie to investigate, only to discover the dragon runs a hot spring inn! Toxie spots a hiring poster and joins the staff. Naturally, employees can enjoy the hot springs whenever they like."
        current_state = STATE_ENDING

# ---------------- Ruins of the Wind ----------------

def get_relic_options():
    opts = []
    if not player["ivan_done"]:
        opts.append("Fight the invader with Ivan")
    elif player["day"] >= 3 and player["ivan_asked"]:
        opts.append("Meet Ivan at our promised spot")
    else:
        opts.append("Hang out with Ivan")
    opts.append("Pick a dandelion")
    if player["day"] >= 2:
        opts.append("Enjoy the view alone")
    return opts

def refresh_relics():
    relic_data["stage"] = "choose"
    relic_data["text"] = "You reach the Ruins of the Wind. Ancient pillars whisper in the breeze."
    relic_data["options"] = get_relic_options()
    relic_data["after_story"] = None

def start_relic_story(lines, after):
    relic_data["story_lines"] = lines
    relic_data["story_index"] = 0
    relic_data["text"] = lines[0]
    relic_data["stage"] = "story"
    relic_data["after_story"] = after

def start_relic_first_visit():
    global current_state
    player["relic_first_visit"] = True
    lines = [
        "(This place feels close to the sky. A cliff lies nearby. The wind echoes through the ruins, filling them with a sacred feeling.)",
        "-What should we do today?",
        "(A lonely figure stands by the cliff. It looks like a little kestrel.)",
        "(Toxie walks over.)",
        "(The sky is gloomy. The kestrel seems to sense Toxie Mushi and turns around.)",
        "-Hey, are you thinking deep thoughts on that cliff?",
        "Ivan: This place is dangerous for you, little mushroom... Careful, or you might fall and become mushroom pieces.",
        "-Oh, I will be fine. By the way, I am Toxie Mushi. What is your name?",
        "Ivan: I am Ivan, guardian of these ruins. But there is no time to chat. The 'invader' is coming.",
        "-'Invader'?"
    ]
    relic_data["story_lines"] = lines
    relic_data["story_index"] = 0
    relic_data["text"] = lines[0]
    relic_data["stage"] = "story"
    relic_data["after_story"] = "choose"
    current_state = STATE_RELICS

def advance_relic_story():
    global current_state, ending_title, ending_text, teleport_text
    relic_data["story_index"] += 1
    if relic_data["story_index"] < len(relic_data["story_lines"]):
        relic_data["text"] = relic_data["story_lines"][relic_data["story_index"]]
    else:
        after = relic_data["after_story"]
        relic_data["after_story"] = None
        if after == "ending2":
            ending_title = "Ending 2: Journey Around the World"
            ending_text = "Ivan takes my 'hand' - or maybe my mycelium? Together, we set off to see the world. Ivan's wings lift me so gently. Every day ahead will be another adventure together."
            current_state = STATE_ENDING
        elif after == "teleport":
            target = random.choice(["Stone Town", "Underground Cave"])
            teleport_text = f"You pick a dandelion, and the wind sweeps you to {target}!"
            current_state = STATE_TELEPORT
        elif after == "choose":
            refresh_relics()
        else:
            relic_data["stage"] = "done"

def handle_relics(index):
    global current_state
    opt = relic_data["options"][index]

    if opt == "Fight the invader with Ivan":
        player["ivan_done"] = True
        player["ivan_f"] += 1
        player["friendship"] += 1
        lines = [
            "(Toxie does not leave. He wants to try helping Ivan.)",
            "(Soon, an ink-black beast appears on the horizon. Its form is impossible to make out.)",
            "(Ivan charges at the beast, wings beating, while Toxie tries to scatter spores all over the enormous monster.",
            "With Ivan's brave fighting and Toxie's spores, the beast finally vanishes into the clouds, and the sky clears.)",
            "-Nice work, Ivan.",
            "Ivan: Thank you, Toxie. We protected this place together. (Ivan Friendship +1)"
        ]
        start_relic_story(lines, "done")
        player["ap"] = 0

    elif opt == "Pick a dandelion":
        player["dandelion_done"] = True
        lines = [
            "-Well, Ivan is busy, so I will explore on my own.",
            "(A tiny dandelion grows on the ground. Toxie picks it.)",
            "(Suddenly... the world twists and blurs. Where Toxie will go tomorrow is now a mystery.)"
        ]
        start_relic_story(lines, "teleport")
        player["ap"] = 0

    elif opt == "Hang out with Ivan":
        player["ivan_f"] += 1
        player["friendship"] += 1
        player["ivan_asked"] = True
        lines = [
            "-Ivan, I came to hang out!",
            "Ivan: Toxie, let me tell you the story of these ruins today.",
            "(A lovely day passes quickly. As Toxie is leaving, Ivan calls out.)",
            "Ivan: Do not forget, we are meeting again tomorrow! (Ivan Friendship +1)"
        ]
        start_relic_story(lines, "done")
        player["ap"] = 0

    elif opt == "Enjoy the view alone":
        lines = [
            "(Although this place is now in ruins, it is still beautiful.",
            "The marble buildings are broken fragments of history, but stone tablets carved with sacred symbols still stand. The lost civilization makes Toxie Mushi feel a little lonely.",
            "Yet the ruins have blended with the lush greenery that grew around them, making the place feel full of life.)",
            "(Toxie notices someone else admiring the view.)"
        ]
        start_relic_story(lines, "done")
        player["ap"] = 0

    elif opt == "Meet Ivan at our promised spot":
        player["ivan_f"] += 1
        player["friendship"] += 1
        lines = [
            "Plants have taken over the heart of the ruins, with vines climbing the walls and stone bricks.",
            "Tall grass and scattered bushes cover the ground.",
            "Ivan stands on the tallest ruined wall. When he sees Toxie, he flies down.",
            "Ivan: Toxie, you kept your promise.",
            "-I always keep my promises.",
            "Ivan: My people once lived here. That is why I have always guarded this place.",
            "But whenever I look up at the sky from the cliff, I know staying here forever is not what I truly want.",
            "-Then let us travel together, only to places we really want to see.",
            "(Ivan Friendship +1)"
        ]
        if player["ivan_f"] >= 3:
            start_relic_story(lines, "ending2")
        else:
            start_relic_story(lines, "done")

# ---------------- 结束一天 ----------------

def end_day():
    global current_state, ending_title, ending_text, ending_to_achievement
    player["day"] += 1
    player["ap"] = 1
    player["bruce_explore_today"] = False

    if player["day"] > 3:
        if player["friendship"] > 3 and not player["ending3_done"]:
            player["ending3_done"] = True
            ending_title = "Ending 3: The Mushroom with the Most Friends"
            ending_text = "You are amazing! You helped me make so many friends. I must be the mushroom with the most friends in the world... ^^"
            current_state = STATE_ENDING
            return
        ending_title = "Ending 1: An Ordinary Little Mushroom"
        ending_text = "As a little mushroom, I have lived a simple life. Still, I will always remember these three wonderful days."
        ending_to_achievement = True
        current_state = STATE_ENDING
        return

    prepare_stone_town_choose()
    refresh_cave()
    refresh_relics()
    dialog_data["text"] = f"It is Day {player['day']}. Where should we go?"
    current_state = STATE_GAME

# ---------------- 绘制 ----------------

def draw_intro():
    draw_bg(BG_INTRO, GRASS_GREEN)
    title = font_title.render("I'm a poisonous Mushroom", True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
    sub = font.render("-- Introduction --", True, (230, 255, 230))
    screen.blit(sub, sub.get_rect(center=(WIDTH//2, 110)))
    lines = [
        "Hi! I am Toxie Mushi, a poisonous mushroom.",
        "I have spent my whole life growing in the forest, but I have dreamed of many different lives.",
        "Human, can you make my dreams come true?",
        "We have only three days. Choose where I go and what I do each day!",
        "That is right, only one action per day.",
        "Mushrooms have no legs, >< so put away that human arrogance..."
    ]
    for i, line in enumerate(lines):
        surf = font.render(line, True, WHITE)
        screen.blit(surf, (70, 155 + i * 40))
    mouse = pygame.mouse.get_pos()
    start_btn = pygame.Rect(WIDTH//2 - 110, 495, 220, 50)
    color = (100, 200, 100) if start_btn.collidepoint(mouse) else BUTTON_GREEN
    pygame.draw.rect(screen, color, start_btn, border_radius=15)
    pygame.draw.rect(screen, BLACK, start_btn, width=2, border_radius=15)
    bt = font.render("Start Game", True, WHITE)
    screen.blit(bt, bt.get_rect(center=start_btn.center))


def draw_menu():
    draw_bg(BG_MENU, GRASS_GREEN)
    title = font.render("I'm a poisonous Mushroom", True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 130)))
    mouse = pygame.mouse.get_pos()
    play_btn = pygame.Rect(WIDTH // 2 - 100, 250, 200, 60)
    pc = (153, 183, 125) if play_btn.collidepoint(mouse) else (120, 155, 97)
    pygame.draw.rect(screen, pc, play_btn, border_radius=15)
    pt = font.render("Play", True, WHITE)
    screen.blit(pt, pt.get_rect(center=play_btn.center))
    quit_btn = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)
    qc = (199, 139, 128) if quit_btn.collidepoint(mouse) else (166, 107, 101)
    pygame.draw.rect(screen, qc, quit_btn, border_radius=15)
    qt = font.render("Quit", True, WHITE)
    screen.blit(qt, qt.get_rect(center=quit_btn.center))


def draw_game():
    draw_bg(BG_GAME, SKY_BLUE)
    if not BG_GAME:
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        draw_mushroom(100, HEIGHT-150)
    draw_status_bar()
    draw_dialog_box(dialog_data["text"], dialog_data["options"], "choose")

def draw_stone_town():
    draw_bg(BG_STONE, (100, 150, 200))
    if not BG_STONE:
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        pygame.draw.circle(screen, (150, 150, 150), (WIDTH//2, HEIGHT//2 - 50), 40)
        pygame.draw.circle(screen, (100, 100, 100), (WIDTH//2 - 20, HEIGHT//2 - 70), 15)
    draw_status_bar()
    draw_dialog_box(stone_town_data["text"], stone_town_data["options"], stone_town_data["stage"])

def draw_cave():
    draw_bg(BG_CAVE, CAVE_BG)
    if not BG_CAVE:
        pygame.draw.rect(screen, CAVE_GROUND, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        pygame.draw.circle(screen, (120, 110, 100), (WIDTH//2 - 60, HEIGHT//2 - 30), 25)
        pygame.draw.circle(screen, (90, 80, 70), (WIDTH//2 + 80, HEIGHT//2 - 60), 30)
        pygame.draw.circle(screen, (110, 100, 90), (WIDTH//2 - 120, HEIGHT//2 - 80), 18)
    draw_status_bar()
    if cave_data["stage"] == "story":
        draw_dialog_box(cave_data["text"], None, "story")
    else:
        draw_dialog_box(cave_data["text"], cave_data["options"], cave_data["stage"])

def draw_relics():
    draw_bg(BG_RELIC, RELIC_BG)
    if not BG_RELIC:
        pygame.draw.rect(screen, RELIC_GROUND, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        pygame.draw.rect(screen, (150, 120, 90), (WIDTH//2 - 180, HEIGHT//2 - 180, 30, 180))
        pygame.draw.rect(screen, (150, 120, 90), (WIDTH//2 + 150, HEIGHT//2 - 150, 30, 150))
        pygame.draw.circle(screen, (160, 130, 100), (WIDTH//2 - 165, HEIGHT//2 - 180), 20)
        pygame.draw.circle(screen, (160, 130, 100), (WIDTH//2 + 165, HEIGHT//2 - 150), 20)
    draw_status_bar()
    if relic_data["stage"] == "story":
        draw_dialog_box(relic_data["text"], None, "story")
    else:
        draw_dialog_box(relic_data["text"], relic_data["options"], relic_data["stage"])

# ---------- 酒吧（新增图片展示位） ----------
def draw_bar():
    screen.fill((40, 25, 35))  # 酒吧暗色底
    # 图片展示区：上半屏
    img_rect = pygame.Rect(WIDTH//2 - 260, 60, 520, 300)
    img_rect = pygame.Rect(WIDTH // 2 - 260, 60, 520, 300)
    # 框改成几乎占满上半屏
    img_rect = pygame.Rect(20, 50, WIDTH - 40, 340)
    if IMG_BAR:
        img = IMG_BAR
        scale = min(img_rect.w / img.get_width(), img_rect.h / img.get_height())
        new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
        img_scaled = pygame.transform.smoothscale(img, new_size)
        screen.blit(img_scaled, img_scaled.get_rect(center=img_rect.center))
    else:
        pygame.draw.rect(screen, (90, 60, 70), img_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, img_rect, width=2, border_radius=12)
        tip = font_small.render("(Bar image placeholder: assets/img_bar.png)", True, (230, 200, 200))
        screen.blit(tip, tip.get_rect(center=img_rect.center))

    draw_status_bar()
    draw_dialog_box(bar_data["text"], None, "done")

# ---------- Shop（新增图片展示位） ----------
def draw_shop():
    draw_bg(BG_SHOP, SHOP_BG)
    if not BG_SHOP:
        pygame.draw.rect(screen, SHOP_GROUND, (0, HEIGHT//2, WIDTH, HEIGHT//2))

    # 图片展示区：对话框上方，右侧
    img_rect = pygame.Rect(WIDTH//2 + 60, 70, 220, 220)
    if IMG_SHOP_ITEM:
        img = IMG_SHOP_ITEM
        scale = min(img_rect.w / img.get_width(), img_rect.h / img.get_height())
        new_size = (int(img.get_width()*scale), int(img.get_height()*scale))
        img_scaled = pygame.transform.smoothscale(img, new_size)
        screen.blit(img_scaled, img_scaled.get_rect(center=img_rect.center))


    draw_status_bar()
    draw_dialog_box(shop_data["text"], shop_data["options"], "choose")

def draw_shop_reward():
    draw_bg(BG_SHOP, SHOP_BG)
    if not BG_SHOP:
        pygame.draw.rect(screen, SHOP_GROUND, (0, HEIGHT//2, WIDTH, HEIGHT//2))
    draw_status_bar()
    draw_dialog_box(shop_data["text"], shop_data["options"], "choose")

def draw_teleport():
    draw_bg(BG_TELEPORT, RELIC_BG)
    if not BG_TELEPORT:
        pygame.draw.rect(screen, RELIC_GROUND, (0, HEIGHT//2, WIDTH, HEIGHT//2))
    draw_status_bar()
    lines = wrap_text(teleport_text, font, 560)
    for i, line in enumerate(lines[:3]):
        surf = font.render(line, True, BLACK)
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 30 + i*40)))
    tip = font_small.render("Click anywhere to end the day", True, (100, 100, 100))
    screen.blit(tip, tip.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))

def draw_plot1():
    draw_bg(BG_PLOT1, (20, 20, 30))
    if not BG_PLOT1:
        pygame.draw.ellipse(screen, (120, 90, 60), (WIDTH//2 - 60, HEIGHT//2 - 120, 120, 80))
        pygame.draw.circle(screen, (150, 110, 70), (WIDTH//2 - 20, HEIGHT//2 - 100), 25)
        pygame.draw.circle(screen, BLACK, (WIDTH//2 - 30, HEIGHT//2 - 105), 4)
        pygame.draw.circle(screen, BLACK, (WIDTH//2 + 5, HEIGHT//2 - 105), 4)
    if plot1_data["stage"] == "story":
        draw_dialog_box(plot1_data["text"], None, "story")
    elif plot1_data["stage"] == "choose":
        draw_dialog_box(plot1_data["text"], plot1_data["options"], "choose")
    else:
        draw_dialog_box(plot1_data["after_text"], None, "done")

def draw_plot2():
    draw_bg(BG_PLOT2, (40, 20, 20))
    if not BG_PLOT2:
        pygame.draw.ellipse(screen, (50, 150, 50), (WIDTH//2 - 100, HEIGHT//2 - 160, 200, 120))
    draw_dialog_box(plot2_data["text"], plot2_data["options"], "choose")

def draw_training():
    draw_bg(BG_TRAINING, (20, 40, 20))
    if not BG_TRAINING:
        pygame.draw.rect(screen, (100, 70, 40), (WIDTH//2 - 20, HEIGHT//2 - 80, 40, 100))
        pygame.draw.circle(screen, (200, 150, 50), (WIDTH//2, HEIGHT//2 - 80), 25)
    if training_data["stage"] == "story":
        draw_dialog_box(training_data["text"], None, "story")
    else:
        draw_dialog_box("You decide to face the dragon! Three training paths await. Which will you master?",
                        training_data["options"], "choose")

def draw_ending():
    draw_bg(BG_ENDING, ENDING_BG)
    title = font_title.render(ending_title, True, (200, 50, 50))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))
    lines = wrap_text(ending_text, font, 600)
    for i, line in enumerate(lines[:4]):
        surf = font.render(line, True, WHITE)
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT//2 + i*40 - 10)))
    tip_text = "Press any key to view achievements" if ending_to_achievement else "Press any key to return to the main menu"
    tip = font_small.render(tip_text, True, (200, 200, 200))
    screen.blit(tip, tip.get_rect(center=(WIDTH//2, HEIGHT//2 + 120)))

def draw_achievement():
    draw_bg(BG_ACHIEVE, (30, 30, 60))
    title = font_title.render("Three Days of Adventure Complete", True, (255, 215, 0))
    screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
    achievements = [
        ("🛁 Bad Mushroom", player["bath_done"]),
        ("💰 Richest Mushroom", player["richest"]),
        ("💃 Social Butterfly", player["socialite"]),
        ("🎭 Explorer", player["explorer"]),
    ]
    for i, (label, unlocked) in enumerate(achievements):
        color = (100, 200, 100) if unlocked else (120, 120, 120)
        prefix = "√ " if unlocked else "× "
        surf = font.render(prefix + label, True, color)
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, 160 + i*50)))
    stats = f"Day: {min(player['day'], 3)}  Money: ${player['money']}  F: {player['friendship']}"
    stat_surf = font.render(stats, True, WHITE)
    screen.blit(stat_surf, stat_surf.get_rect(center=(WIDTH//2, HEIGHT-100)))
    tip = font_small.render("Press any key to return to the main menu", True, (180, 180, 180))
    screen.blit(tip, tip.get_rect(center=(WIDTH//2, HEIGHT-50)))

# ---------------- 主循环 ----------------

running = True
while running:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_INTRO:
                start_btn = pygame.Rect(WIDTH//2 - 110, 495, 220, 50)
                if start_btn.collidepoint(mouse):
                    current_state = STATE_GAME

            elif current_state == STATE_MENU:
                play_btn = pygame.Rect(WIDTH//2 - 100, 250, 200, 60)
                quit_btn = pygame.Rect(WIDTH//2 - 100, 350, 200, 60)
                if play_btn.collidepoint(mouse):
                    current_state = STATE_INTRO
                if quit_btn.collidepoint(mouse):
                    running = False

            elif current_state == STATE_GAME:
                rects = get_button_rects(dialog_data["options"], btn_width=160)
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse):
                        if dialog_data["options"][i] == "Stone Town":
                            if player["bath_done"]:
                                ending_title = "Ending 4: Arrested"
                                ending_text = "\"Police have been searching for a little mushroom whose poison killed a human. After a day of investigation, we caught it...\""
                                current_state = STATE_ENDING
                            else:
                                current_state = STATE_STONE_TOWN
                                if not player["first_town"]:
                                    player["first_town"] = True
                                    stone_town_data["stage"] = "story"
                                    stone_town_data["story_index"] = 0
                                    stone_town_data["text"] = stone_town_data["story_lines"][0]
                                else:
                                    prepare_stone_town_choose()
                        elif dialog_data["options"][i] == "Underground Cave":
                            current_state = STATE_CAVE
                            refresh_cave()
                        elif dialog_data["options"][i] == "Ruins of the Wind":
                            if not player["relic_first_visit"]:
                                start_relic_first_visit()
                            else:
                                current_state = STATE_RELICS
                                refresh_relics()

            elif current_state == STATE_STONE_TOWN:
                if stone_town_data["stage"] == "story":
                    stone_town_data["story_index"] += 1
                    if stone_town_data["story_index"] < len(stone_town_data["story_lines"]):
                        stone_town_data["text"] = stone_town_data["story_lines"][stone_town_data["story_index"]]
                    else:
                        prepare_stone_town_choose()
                elif stone_town_data["stage"] == "choose":
                    rects = get_button_rects(stone_town_data["options"])
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            handle_stone_town(i)
                            break
                elif stone_town_data["stage"] == "done":
                    end_day()

            elif current_state == STATE_BAR:
                # 点击任意处结束当天
                player["ap"] = 0
                end_day()

            elif current_state == STATE_SHOP:
                if shop_data["stage"] in ("coupon_given", "normal_leave"):
                    rects = get_button_rects(shop_data["options"])
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            handle_shop_leave()
                            break
                else:
                    rects = get_button_rects(shop_data["options"])
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            handle_shop(i)
                            break

            elif current_state == STATE_SHOP_REWARD:
                rects = get_button_rects(shop_data["options"], btn_width=200)
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse):
                        handle_shop_reward(i)
                        break

            elif current_state == STATE_CAVE:
                if cave_data["stage"] == "story":
                    advance_cave_story()
                elif cave_data["stage"] == "choose":
                    rects = get_button_rects(cave_data["options"])
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            handle_cave(i)
                            break
                else:
                    end_day()

            elif current_state == STATE_RELICS:
                if relic_data["stage"] == "story":
                    advance_relic_story()
                elif relic_data["stage"] == "choose":
                    rects = get_button_rects(relic_data["options"])
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            handle_relics(i)
                            break
                else:
                    end_day()

            elif current_state == STATE_TELEPORT:
                end_day()

            elif current_state == STATE_PLOT1:
                if plot1_data["stage"] == "story":
                    advance_plot1_story()
                elif plot1_data["stage"] == "choose":
                    rects = get_button_rects(plot1_data["options"])
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            handle_plot1_choice(i)
                            break
                elif plot1_data["stage"] == "after_leave":
                    if plot1_data["choice"] == "stay":
                        start_plot2()
                    else:
                        player["ap"] = 0
                        end_day()

            elif current_state == STATE_PLOT2:
                rects = get_button_rects(plot2_data["options"], btn_width=200)
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse):
                        start_training(i)
                        break

            elif current_state == STATE_TRAINING:
                if training_data["stage"] == "story":
                    advance_training_story()
                else:
                    rects = get_button_rects(training_data["options"], btn_width=200)
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse):
                            start_training(i)
                            break

            elif current_state == STATE_ENDING:
                if ending_to_achievement:
                    current_state = STATE_ACHIEVEMENT
                    ending_to_achievement = False
                else:
                    reset_game()

            elif current_state == STATE_ACHIEVEMENT:
                reset_game()

        if current_state == STATE_ENDING and event.type == pygame.KEYDOWN:
            if ending_to_achievement:
                current_state = STATE_ACHIEVEMENT
                ending_to_achievement = False
            else:
                reset_game()
        elif current_state == STATE_ACHIEVEMENT and event.type == pygame.KEYDOWN:
            reset_game()

    # ---------------- 绘制 ----------------
    if current_state == STATE_INTRO:
        draw_intro()
    elif current_state == STATE_MENU:
        draw_menu()
    elif current_state == STATE_GAME:
        draw_game()
    elif current_state == STATE_STONE_TOWN:
        draw_stone_town()
    elif current_state == STATE_BAR:
        draw_bar()
    elif current_state == STATE_SHOP:
        draw_shop()
    elif current_state == STATE_SHOP_REWARD:
        draw_shop_reward()
    elif current_state == STATE_CAVE:
        draw_cave()
    elif current_state == STATE_RELICS:
        draw_relics()
    elif current_state == STATE_TELEPORT:
        draw_teleport()
    elif current_state == STATE_PLOT1:
        draw_plot1()
    elif current_state == STATE_PLOT2:
        draw_plot2()
    elif current_state == STATE_TRAINING:
        draw_training()
    elif current_state == STATE_ENDING:
        draw_ending()
    elif current_state == STATE_ACHIEVEMENT:
        draw_achievement()

    if popup_timer > 0:
        popup_timer -= 1
        if popup_timer <= 0:
            popup_text = ""
        else:
            popup_surf = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
            popup_surf.fill((0, 0, 0, 180))
            screen.blit(popup_surf, (0, 100))
            txt = font_small.render(popup_text, True, (255, 215, 0))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, 140)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
