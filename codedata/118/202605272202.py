# Auto-generated from Untitled1.ipynb

# --- Code Cell ---
import pygame
import numpy as np
import random

# 變數初始化
SCREEN_SIZE = [(1, 480, 360),(2, 720, 540),(3, 1080, 720),(4, 1920, 1440),(5, 2880, 2160)]
SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60
Pr, Pc = 11, 11
PlayerV = 5
Background = "StartWeapon"   # StartWeapon / Map / Battle / Event / GameOver
Global_Time = 0
Anim_Time = {}

# 卡牌系統變數
PlayerDeck = []
UsedRooms = set()
ItemCardPool = [{"name": "腦袋尖尖的", "type": "brain"},{"name": "小草", "type": "grass"},{"name": "戰術翻滾", "type": "roll"},{"name": "菜菜撈撈", "type": "nana"},{"name": "心靈課程名單", "type": "mind"},{"name": "老千的技術", "type": "cheat"},{"name": "你從桃園到新竹", "type": "taoyuan"}]
WeaponChoices = [{"name": "傑里科941半自動手槍", "type": "gun"},{"name": "鞭子", "type": "whip"},{"name": "巨槌瑞斯", "type": "darius"}]
EventCardPool = [{"name": "橙汁汙中山羨恭喜", "type": "monster_double_attack"},{"name": "3cm 感謝祭", "type": "seal_monster_once"},{"name": "我一步都沒有退ㄟ", "type": "boss_no_immunity"},{"name": "我中了兩槍", "type": "dice_becomes_three"},{"name": "寵物溝通師", "type": "enemy_hp_double_player_attack_half"},{"name": "芒果醬", "type": "mango_bonus"},{"name": "武術大師晨晨", "type": "next_battle_chengchen"},{"name": "幹你敢不敢啦", "type": "player_hp_one"}]
SelectedWeapon = None
CurrentEventCard = None

card_positions = []
weapon_positions = []
battle_weapon_position = None

# =========================
# 戰鬥系統變數
# =========================

player_hp = 30
enemy_hp = 40
enemy_max_hp = 40

dice_value = 1
dice_rolling = False
dice_roll_timer = 0
roll_times = 8

battle_message = "按 R 或空白鍵重新擲骰"

player_attack_bonus = 0
gun_double_turns = 0
cheat_mode = False
roll_immunity = False
hit_count = 0

stored_damage_turns = 0
stored_damage = 0

enemy_color = (0, 0, 0)

enemy_double_attack_times = 0
seal_monster_once = False
boss_no_immunity = False
next_dice_fixed_three = False
enemy_hp_multiplier = 1
player_attack_half = False
mango_bonus = False
next_battle_chengchen = False

# =========================
# 地圖生成
# =========================

MAP = np.zeros((23, 23), dtype=int)
MAP[11, 11] = 1
MAP[10, 11] = 2
MAP[12, 11] = 2
MAP[11, 12] = 2
MAP[11, 10] = 2

# =========================
# Pygame 初始化
# =========================

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("骰子戰鬥遊戲")
clock = pygame.time.Clock()

# =========================
# 地圖檔載入
# =========================

MAPList = []

for i in range(1, 10):
    img = pygame.image.load("assets/map" + str(i) + ".png").convert()
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    MAPList.append(img)

MAPListName = ["無","出生點","小寶箱","事件區","大寶箱","交易區","陷阱區","菁英怪",
    "整備區",
    "魔王關"]

# =========================
# 戰鬥背景載入
# =========================

battle_bg = pygame.image.load(r"final\battleback2nog.jpeg").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

# =========================
# 卡牌圖片載入
# =========================

CARD_W = int(WIDTH * 0.15)
CARD_H = int(HEIGHT * 0.33)

EVENT_CARD_W = int(WIDTH * 0.25)
EVENT_CARD_H = int(HEIGHT * 0.55)


def load_card_image(path):
    return pygame.image.load(path).convert_alpha()


CardOriginalImage = {
    "腦袋尖尖的": load_card_image("final/S__76242953.png"),
    "小草": load_card_image("final/S__76242954.png"),
    "戰術翻滾": load_card_image("final/S__76242955.png"),
    "菜菜撈撈": load_card_image("final/S__76242956.png"),
    "心靈課程名單": load_card_image("final/S__76242957.png"),
    "老千的技術": load_card_image("final/S__76242958.png"),
    "你從桃園到新竹": load_card_image("final/S__76242959.png"),

    "橙汁汙中山羨恭喜": load_card_image("final/S__76242960.png"),
    "3cm 感謝祭": load_card_image("final/S__76242961.png"),
    "我一步都沒有退ㄟ": load_card_image("final/S__76242962.png"),
    "我中了兩槍": load_card_image("final/S__76242964.png"),
    "寵物溝通師": load_card_image("final/S__76242965.png"),
    "芒果醬": load_card_image("final/S__76242966.png"),
    "武術大師晨晨": load_card_image("final/S__76242967.png"),
    "幹你敢不敢啦": load_card_image("final/S__76242968.png"),

    "傑里科941半自動手槍": load_card_image("final/S__76242970.png"),
    "鞭子": load_card_image("final/S__76242971.png"),
    "巨槌瑞斯": load_card_image("final/S__76242972.png")
}

CardImage = {}

for card_name in CardOriginalImage:
    CardImage[card_name] = pygame.transform.smoothscale(
        CardOriginalImage[card_name],
        (CARD_W, CARD_H)
    )

EventCardImage = {}

for card_name in CardOriginalImage:
    EventCardImage[card_name] = pygame.transform.smoothscale(
        CardOriginalImage[card_name],
        (EVENT_CARD_W, EVENT_CARD_H)
    )

# =========================
# 素材庫
# =========================

Asset_dict = {
    "b049anim_room1": pygame.transform.smoothscale(
        pygame.image.load("assets/animdict/b049anim_room1.png").convert_alpha(),
        (int(WIDTH / 5 * 2), int(WIDTH / 25 * 2))
    )
}

# =========================
# 字體載入
# =========================

FHeadPath = "assets/font/NotoSansTC-Bold.ttf"
FTextPath = "assets/font/NotoSansTC-Light.ttf"

font_big = pygame.font.SysFont("Microsoft JhengHei", 52)
font_mid = pygame.font.SysFont("Microsoft JhengHei", 34)
font_small = pygame.font.SysFont("Microsoft JhengHei", 24)

# =========================
# Class 區域
# =========================

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1.0):
        super().__init__()
        self.original_image = pygame.image.load("assets/player.png").convert_alpha()
        self.rect = pygame.Rect(x, y, 0, 0)
        self.set_scale(scale_factor)
        self.speed = PlayerV

    def set_scale(self, new_scale):
        if new_scale > 0:
            self.image_right = pygame.transform.smoothscale(
                self.original_image,
                (
                    int(WIDTH / 12 * new_scale),
                    int(HEIGHT / 8 * new_scale)
                )
            )
            self.image_left = pygame.transform.flip(self.image_right, True, False)
            self.image = self.image_right

            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PlayerV * HEIGHT / 1080 * 60 / FPS
            self.image = self.image_left
            self.mask = pygame.mask.from_surface(self.image)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PlayerV * HEIGHT / 1080 * 60 / FPS
            self.image = self.image_right
            self.mask = pygame.mask.from_surface(self.image)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= PlayerV * HEIGHT / 1080 * 60 / FPS

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += PlayerV * HEIGHT / 1080 * 60 / FPS

        if self.rect.left < WIDTH * 0.15:
            self.rect.left = int(WIDTH * 0.15)

        if self.rect.right > WIDTH * 0.85:
            self.rect.right = int(WIDTH * 0.85)

        if self.rect.top < HEIGHT * 0.1:
            self.rect.top = int(HEIGHT * 0.1)

        if self.rect.bottom > HEIGHT * 0.95:
            self.rect.bottom = int(HEIGHT * 0.95)


class Gate(pygame.sprite.Sprite):
    def __init__(self, GateType):
        super().__init__()

        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/gate.png").convert_alpha(),
            (int(WIDTH / 12), int(HEIGHT / 8))
        )

        self.rect = self.image.get_rect()
        self.GateType = GateType

        if GateType == "N":
            self.rect.center = (WIDTH / 2, HEIGHT * 0.1)

        elif GateType == "S":
            self.rect.center = (WIDTH / 2, HEIGHT * 0.95)

        elif GateType == "W":
            self.rect.center = (WIDTH * 0.15, HEIGHT / 2)

        elif GateType == "E":
            self.rect.center = (WIDTH * 0.85, HEIGHT / 2)

        self.mask = pygame.mask.from_surface(self.image)


# =========================
# Def 區域
# =========================

def refresh_gates(i, j, gates_group):
    gates_group.empty()

    if MAP[Pr, Pc - 1] == 0 or RoomStep == 0:
        gates_group.add(Gate("W"))

    if MAP[Pr, Pc + 1] == 0 or RoomStep == 0:
        gates_group.add(Gate("E"))

    if MAP[Pr - 1, Pc] == 0 or RoomStep == 0:
        gates_group.add(Gate("N"))

    if MAP[Pr + 1, Pc] == 0 or RoomStep == 0:
        gates_group.add(Gate("S"))

    if RoomStep == 8 + GameRound:
        gates_group.empty()


def miniMap():
    if Background == "Map":
        for i in range(23):
            for j in range(23):
                ColorLS = [
                    (0, 0, 0),
                    (210, 210, 210),
                    (218, 165, 32),
                    (0, 0, 255),
                    (255, 215, 0),
                    (255, 105, 180),
                    (139, 69, 19),
                    (255, 99, 71),
                    (0, 255, 0),
                    (255, 0, 0)
                ]

                Color = ColorLS[MAP[i, j]]

                x = (WIDTH / 160) + (j * WIDTH / 120)
                y = (HEIGHT / 120) + (i * HEIGHT / 90)
                w = WIDTH / 120
                h = HEIGHT / 90

                if (i, j) == (Pr, Pc):
                    pygame.draw.rect(screen, Color, (x, y, w, h))
                    pygame.draw.rect(
                        screen,
                        (0, 0, 0),
                        (x, y, w, h),
                        int(max(HEIGHT / 300, 1))
                    )

                elif MAP[i, j] != 0:
                    pygame.draw.rect(screen, Color, (x, y, w, h))


def Animation():
    if "Anim_Room" in Anim_Time and Anim_Time.get("Anim_Room") > 0:
        Anim_Room()


def Anim_Room():
    recimg = Asset_dict["b049anim_room1"]
    rec = recimg.get_rect()

    adx = WIDTH / 2
    ady = min(
        (
            -0.00003
            * (int(Anim_Time["Anim_Room"]) - 60)
            * (int(Anim_Time["Anim_Room"]) - 120)
            + 0.1
        ),
        0.1
    ) * HEIGHT

    rec.centerx = adx
    rec.centery = ady

    screen.blit(recimg, rec)

    FHead = pygame.font.Font(FHeadPath, int(HEIGHT / 15))
    Head = FHead.render(MAPListName[MAP[Pr, Pc]], True, (255, 255, 255))

    trec = Head.get_rect()
    trec.center = rec.center

    screen.blit(Head, trec)


def draw_text(text, x, y, font, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_dice(x, y, size, value):
    pygame.draw.rect(
        screen,
        (245, 245, 245),
        (x, y, size, size),
        border_radius=20
    )

    pygame.draw.rect(
        screen,
        (0, 0, 0),
        (x, y, size, size),
        5,
        border_radius=20
    )

    text = font_big.render(str(value), True, (0, 0, 0))
    rect = text.get_rect(center=(x + size // 2, y + size // 2))
    screen.blit(text, rect)


def draw_card(card, x, y):
    card_name = card["name"]
    screen.blit(CardImage[card_name], (x, y))


def draw_event_card(card, x, y):
    card_name = card["name"]
    screen.blit(EventCardImage[card_name], (x, y))


def draw_card_row(card_list, y):
    positions = []

    if len(card_list) == 0:
        return positions

    gap = int(WIDTH * 0.025)
    total_width = len(card_list) * CARD_W + (len(card_list) - 1) * gap
    start_x = int((WIDTH - total_width) / 2)

    for i, card in enumerate(card_list):
        card_x = start_x + i * (CARD_W + gap)
        draw_card(card, card_x, y)
        positions.append((card_x, y, CARD_W, CARD_H, card))

    return positions


def get_random_item_card():
    global battle_message

    new_card = random.choice(ItemCardPool)
    PlayerDeck.append(new_card)

    battle_message = f"獲得道具卡：{new_card['name']}"
    print("獲得道具卡：", new_card["name"])


def get_random_event_card():
    global CurrentEventCard
    global battle_message

    CurrentEventCard = random.choice(EventCardPool)
    battle_message = f"事件發生：{CurrentEventCard['name']}"
    print("事件發生：", CurrentEventCard["name"])


def apply_event_card(event_card):
    global player_hp, battle_message
    global enemy_double_attack_times, seal_monster_once
    global boss_no_immunity, next_dice_fixed_three
    global enemy_hp_multiplier, player_attack_half
    global mango_bonus, next_battle_chengchen

    if event_card is None:
        return

    event_type = event_card["type"]

    if event_type == "monster_double_attack":
        enemy_double_attack_times = 3
        battle_message = "事件：接下來三次怪物攻擊點數兩倍"

    elif event_type == "seal_monster_once":
        seal_monster_once = True
        battle_message = "事件：怪物不可攻擊一次"

    elif event_type == "boss_no_immunity":
        boss_no_immunity = True
        battle_message = "事件：此戰 Boss 攻擊不可被免疫"

    elif event_type == "dice_becomes_three":
        next_dice_fixed_three = True
        battle_message = "事件：下一場戰鬥骰子先變成 3"

    elif event_type == "enemy_hp_double_player_attack_half":
        enemy_hp_multiplier = 2
        player_attack_half = True
        battle_message = "事件：下場戰鬥敵方血量 x2，玩家攻擊減半"

    elif event_type == "mango_bonus":
        mango_bonus = True
        battle_message = "事件：芒果醬啟動，攻擊獲得額外加成"

    elif event_type == "next_battle_chengchen":
        next_battle_chengchen = True
        battle_message = "事件：下一場戰鬥生成武術大師晨晨"

    elif event_type == "player_hp_one":
        player_hp = 1
        battle_message = "事件：生命值變成 1 點"


def basic_damage():
    damage = dice_value + player_attack_bonus

    if mango_bonus:
        damage += int(damage * 0.3)

    if player_attack_half:
        damage = max(damage // 2, 1)

    return damage


def weapon_attack(card_type):
    global enemy_hp, battle_message, gun_double_turns

    if enemy_hp <= 0 or player_hp <= 0:
        return

    damage = basic_damage()

    if card_type == "gun":
        if gun_double_turns > 0:
            damage *= 2
            gun_double_turns -= 1
            enemy_hp -= damage
            battle_message = f"手槍攻擊！前三次雙倍，造成 {damage} 點，剩 {gun_double_turns} 次雙倍"
        else:
            enemy_hp -= damage
            battle_message = f"手槍攻擊！造成 {damage} 點傷害"

    elif card_type == "whip":
        if enemy_color == (0, 0, 0):
            damage *= 2
            enemy_hp -= damage
            battle_message = f"鞭子攻擊！黑色敵人雙倍傷害，造成 {damage}"
        else:
            enemy_hp -= damage
            battle_message = f"鞭子攻擊！造成 {damage} 傷害"

    elif card_type == "darius":
        if dice_value == 3:
            if MAP[Pr, Pc] == 9:
                hook_damage = max(int(enemy_hp * 0.2), 1)
                enemy_hp -= hook_damage
                battle_message = f"巨槌瑞斯鉤中 Boss！造成 {hook_damage} 傷害"
            else:
                hook_damage = max(enemy_hp // 2, 1)
                enemy_hp -= hook_damage
                battle_message = f"巨槌瑞斯鉤中！造成敵人一半血量 {hook_damage}"
        else:
            enemy_hp -= damage
            battle_message = f"巨槌瑞斯普通攻擊，造成 {damage} 傷害"


def use_item_card(card_type):
    global player_hp, enemy_hp
    global battle_message, dice_value
    global player_attack_bonus
    global cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage

    if enemy_hp <= 0 or player_hp <= 0:
        return

    damage = basic_damage()

    if card_type == "brain":
        player_attack_bonus += 5
        player_hp += 10
        battle_message = "腦袋尖尖的：力量 +5，血量 +10"

    elif card_type == "grass":
        enemy_hp -= damage

        if random.random() < 0.5:
            extra_damage = max(damage // 2, 1)
            enemy_hp -= extra_damage
            battle_message = f"小草：造成 {damage} 傷害，額外攻擊 {extra_damage}"
        else:
            battle_message = f"小草：造成 {damage} 傷害，沒有觸發額外攻擊"

    elif card_type == "roll":
        hit_count = 0
        roll_immunity = True
        battle_message = "戰術翻滾：受到三次傷害後，免疫下一次傷害"

    elif card_type == "nana":
        battle_message = "菜菜撈撈：免死效果已準備，血量歸零時會剩 1"

    elif card_type == "mind":
        player_hp += 25
        battle_message = "心靈課程名單：血量 +25"

    elif card_type == "cheat":
        cheat_mode = True
        battle_message = "老千的技術：請按 1～6 選擇骰子點數"

    elif card_type == "taoyuan":
        stored_damage = damage
        stored_damage_turns = 3
        battle_message = f"你從桃園到新竹：儲存本回合傷害 {damage}"

    if stored_damage_turns > 0 and card_type != "taoyuan":
        enemy_hp -= stored_damage
        stored_damage_turns -= 1
        battle_message += f"，桃園新竹追加 {stored_damage}"


def check_enemy_dead():
    global enemy_hp, battle_message

    if enemy_hp <= 0:
        enemy_hp = 0
        battle_message = "敵人被擊敗了！按 M 回地圖"


def monster_attack():
    global player_hp, battle_message, roll_times, Background
    global enemy_double_attack_times, seal_monster_once
    global roll_immunity, hit_count, boss_no_immunity

    if enemy_hp <= 0 or player_hp <= 0:
        return

    if seal_monster_once:
        seal_monster_once = False
        roll_times = 8
        battle_message = "怪物攻擊被封鎖！輪到你重新擲骰"
        return

    monster_damage = random.randint(1, 20)

    if enemy_double_attack_times > 0:
        monster_damage *= 2
        enemy_double_attack_times -= 1

    if roll_immunity and not boss_no_immunity:
        hit_count += 1

        if hit_count >= 3:
            roll_immunity = False
            hit_count = 0
            roll_times = 8
            battle_message = "戰術翻滾觸發！免疫這次怪物攻擊，輪到你重新擲骰"
            return

    player_hp -= monster_damage

    if player_hp <= 0:
        player_hp = 0
        battle_message = f"怪物攻擊造成 {monster_damage} 點傷害，你被擊敗了！"
        Background = "GameOver"
    else:
        roll_times = 8
        battle_message = f"怪物攻擊！造成 {monster_damage} 點傷害，輪到你重新擲骰"


def reset_battle():
    global enemy_hp, enemy_max_hp
    global dice_value, dice_rolling, dice_roll_timer, battle_message
    global roll_times, player_attack_bonus, gun_double_turns
    global cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage
    global enemy_hp_multiplier, player_attack_half
    global next_dice_fixed_three

    if MAP[Pr, Pc] == 9:
        enemy_max_hp = 80
    else:
        enemy_max_hp = 40

    enemy_max_hp *= enemy_hp_multiplier
    enemy_hp = enemy_max_hp

    dice_value = 1
    dice_rolling = False
    dice_roll_timer = 0
    roll_times = 8

    player_attack_bonus = 0
    cheat_mode = False
    roll_immunity = False
    hit_count = 0
    stored_damage_turns = 0
    stored_damage = 0

    if SelectedWeapon is not None and SelectedWeapon["type"] == "gun":
        gun_double_turns = 3
    else:
        gun_double_turns = 0

    enemy_hp_multiplier = 1

    if next_dice_fixed_three:
        dice_value = 3
        next_dice_fixed_three = False
        battle_message = "事件效果：這場戰鬥骰子先變成 3"
    else:
        battle_message = "先按 R / 空白鍵擲骰，再點左邊武器卡攻擊怪物"


def reset_game():
    global Pr, Pc, Background, Global_Time, Anim_Time
    global PlayerDeck, UsedRooms, SelectedWeapon, CurrentEventCard
    global card_positions, weapon_positions, battle_weapon_position
    global player_hp, enemy_hp, enemy_max_hp
    global dice_value, dice_rolling, dice_roll_timer, roll_times, battle_message
    global player_attack_bonus, gun_double_turns, cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage
    global enemy_double_attack_times, seal_monster_once, boss_no_immunity
    global next_dice_fixed_three, enemy_hp_multiplier, player_attack_half
    global mango_bonus, next_battle_chengchen
    global MAP, player, GameRound, RoomStep, gates_group

    Pr, Pc = 11, 11
    Background = "StartWeapon"

    Global_Time = 0
    Anim_Time = {}

    PlayerDeck = []
    UsedRooms = set()
    SelectedWeapon = None
    CurrentEventCard = None

    card_positions = []
    weapon_positions = []
    battle_weapon_position = None

    player_hp = 30
    enemy_hp = 40
    enemy_max_hp = 40

    dice_value = 1
    dice_rolling = False
    dice_roll_timer = 0
    roll_times = 8

    battle_message = "按 R 或空白鍵重新擲骰"

    player_attack_bonus = 0
    gun_double_turns = 0
    cheat_mode = False
    roll_immunity = False
    hit_count = 0

    stored_damage_turns = 0
    stored_damage = 0

    enemy_double_attack_times = 0
    seal_monster_once = False
    boss_no_immunity = False
    next_dice_fixed_three = False
    enemy_hp_multiplier = 1
    player_attack_half = False
    mango_bonus = False
    next_battle_chengchen = False

    MAP = np.zeros((23, 23), dtype=int)
    MAP[11, 11] = 1
    MAP[10, 11] = 2
    MAP[12, 11] = 2
    MAP[11, 12] = 2
    MAP[11, 10] = 2

    GameRound = 1
    RoomStep = 0

    player = Player(WIDTH / 2, HEIGHT / 2)

    gates_group = pygame.sprite.Group()
    refresh_gates(Pr, Pc, gates_group)


# =========================
# 開始運作
# =========================

player = Player(WIDTH / 2, HEIGHT / 2)

GameRound = 1
RoomStep = 0

gates_group = pygame.sprite.Group()
refresh_gates(Pr, Pc, gates_group)

running = True

while running:
    clock.tick(FPS)

    # =========================
    # 事件處理
    # =========================

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 滑鼠點擊
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if Background == "StartWeapon":
                    for rect in weapon_positions:
                        x, y, w, h, weapon = rect

                        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                            SelectedWeapon = weapon
                            Background = "Map"
                            print("選擇武器：", SelectedWeapon["name"])

                elif Background == "Battle":

                    if battle_weapon_position is not None:
                        x, y, w, h, weapon = battle_weapon_position

                        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                            weapon_attack(weapon["type"])
                            check_enemy_dead()

                    for rect in card_positions:
                        x, y, w, h, card = rect

                        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                            use_item_card(card["type"])
                            check_enemy_dead()

                            if card in PlayerDeck:
                                PlayerDeck.remove(card)

                            break

        # 鍵盤事件
        if event.type == pygame.KEYDOWN:

            # Game Over 畫面按 P 重新開始
            if Background == "GameOver":
                if event.key == pygame.K_p:
                    reset_game()

            # 測試用：按 B 直接進戰鬥
            if event.key == pygame.K_b and Background != "GameOver":
                reset_battle()
                Background = "Battle"

            # 按 M 回地圖
            if event.key == pygame.K_m and Background != "GameOver":
                Background = "Map"

            # 事件一定要接受，只能按 Y
            if Background == "Event":
                if event.key == pygame.K_y:
                    apply_event_card(CurrentEventCard)
                    CurrentEventCard = None
                    Background = "Map"

            if Background == "Battle" and cheat_mode:
                if event.key == pygame.K_1:
                    dice_value = 1
                    cheat_mode = False
                    battle_message = "老千成功：骰子變成 1"
                elif event.key == pygame.K_2:
                    dice_value = 2
                    cheat_mode = False
                    battle_message = "老千成功：骰子變成 2"
                elif event.key == pygame.K_3:
                    dice_value = 3
                    cheat_mode = False
                    battle_message = "老千成功：骰子變成 3"
                elif event.key == pygame.K_4:
                    dice_value = 4
                    cheat_mode = False
                    battle_message = "老千成功：骰子變成 4"
                elif event.key == pygame.K_5:
                    dice_value = 5
                    cheat_mode = False
                    battle_message = "老千成功：骰子變成 5"
                elif event.key == pygame.K_6:
                    dice_value = 6
                    cheat_mode = False
                    battle_message = "老千成功：骰子變成 6"

            if Background == "Battle":
                if (event.key == pygame.K_r or event.key == pygame.K_SPACE) and roll_times > 0:
                    if enemy_hp > 0 and player_hp > 0:
                        dice_rolling = True
                        dice_roll_timer = 15

    keys = pygame.key.get_pressed()

    # =========================
    # 地圖邏輯
    # =========================

    if Background == "Map":
        player.update(keys)

        hit_gate = pygame.sprite.spritecollideany(player, gates_group)

        if hit_gate:
            if hit_gate.GateType == "N":
                Pr -= 1
                player.rect.center = (WIDTH / 2, HEIGHT * 0.9)

            elif hit_gate.GateType == "S":
                Pr += 1
                player.rect.center = (WIDTH / 2, HEIGHT * 0.15)

            elif hit_gate.GateType == "W":
                Pc -= 1
                player.rect.center = (WIDTH * 0.75, HEIGHT / 2)

            elif hit_gate.GateType == "E":
                Pc += 1
                player.rect.center = (WIDTH * 0.25, HEIGHT / 2)

            RoomStep += 1

            if MAP[Pr, Pc] == 0 and RoomStep not in [4, 7 + GameRound, 8 + GameRound]:
                MAP[Pr, Pc] = random.randint(2, 6)

            elif RoomStep == 4:
                MAP[Pr, Pc] = 7

            elif RoomStep == 7 + GameRound:
                MAP[Pr, Pc] = 8

            elif RoomStep == 8 + GameRound:
                MAP[Pr, Pc] = 9

            refresh_gates(Pr, Pc, gates_group)
            Anim_Time["Anim_Room"] = 3 * FPS

            current_room = (Pr, Pc)

            if MAP[Pr, Pc] in [2, 4]:
                if current_room not in UsedRooms:
                    get_random_item_card()
                    UsedRooms.add(current_room)

            elif MAP[Pr, Pc] == 3:
                if current_room not in UsedRooms:
                    get_random_event_card()
                    UsedRooms.add(current_room)
                    Background = "Event"

            elif MAP[Pr, Pc] in [7, 9]:
                reset_battle()
                Background = "Battle"

    # =========================
    # 戰鬥骰子邏輯
    # =========================

    if Background == "Battle":
        if dice_rolling:
            dice_value = random.randint(1, 6)
            dice_roll_timer -= 1

            if dice_roll_timer <= 0:
                dice_rolling = False
                roll_times -= 1

                if roll_times > 0:
                    battle_message = f"你骰出了 {dice_value} 點，還剩 {roll_times} 次擲骰"
                else:
                    battle_message = f"你骰出了 {dice_value} 點，擲骰次數歸 0，換怪物攻擊"
                    monster_attack()

    # =========================
    # 顯示區
    # =========================

    if Background == "StartWeapon":
        screen.fill((20, 20, 30))

        draw_text(
            "選擇你的初始武器",
            int(WIDTH * 0.34),
            int(HEIGHT * 0.08),
            font_big,
            (255, 255, 255)
        )

        weapon_positions = draw_card_row(WeaponChoices, int(HEIGHT * 0.30))

        draw_text(
            "點擊一張武器卡開始遊戲",
            int(WIDTH * 0.34),
            int(HEIGHT * 0.82),
            font_mid,
            (255, 255, 255)
        )

    elif Background == "Map":
        screen.blit(MAPList[int(MAP[Pr, Pc]) - 1], (0, 0))

        gates_group.draw(screen)
        screen.blit(player.image, player.rect)

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (WIDTH * 0.41 / 4, HEIGHT * 0.41 / 3),
            WIDTH * 18 / 240
        )

        miniMap()
        Animation()

        draw_text(
            f"道具卡數量：{len(PlayerDeck)}",
            int(WIDTH * 0.72),
            int(HEIGHT * 0.03),
            font_small,
            (255, 255, 255)
        )

        if SelectedWeapon is not None:
            draw_text(
                f"武器：{SelectedWeapon['name']}",
                int(WIDTH * 0.58),
                int(HEIGHT * 0.08),
                font_small,
                (255, 255, 255))

        draw_text(
            battle_message,
            int(WIDTH * 0.05),
            int(HEIGHT * 0.92),
            font_small,
            (255, 255, 255))

    elif Background == "Event":
        screen.fill((45, 20, 65))

        draw_text(
            "事件發生",
            int(WIDTH * 0.40),
            int(HEIGHT * 0.04),
            font_big,
            (255, 255, 255))

        if CurrentEventCard is not None:
            event_x = int(WIDTH * 0.5 - EVENT_CARD_W / 2)
            event_y = int(HEIGHT * 0.18)

            draw_event_card(CurrentEventCard, event_x, event_y)

        draw_text(
            "按 Y 確認事件效果",
            int(WIDTH * 0.38),
            int(HEIGHT * 0.82),
            font_mid,
            (255, 255, 255))

        draw_text(
            battle_message,
            int(WIDTH * 0.25),
            int(HEIGHT * 0.90),
            font_small,
            (255, 255, 255))

    elif Background == "Battle":
        screen.blit(battle_bg, (0, 0))

        draw_text(
            f"玩家 HP：{player_hp}",
            int(WIDTH * 0.06),
            int(HEIGHT * 0.04),
            font_mid,
            (70, 190, 90))

        draw_text(
            f"敵人 HP：{enemy_hp}/{enemy_max_hp}",
            int(WIDTH * 0.72),
            int(HEIGHT * 0.04),
            font_mid,
            (220, 60, 60))

        draw_text(
            "攻擊方式：先按 R / 空白鍵擲骰，再點左邊武器卡攻擊怪物",
            int(WIDTH * 0.20),
            int(HEIGHT * 0.09),
            font_small,
            (255, 255, 255))

        draw_text(
            "擲骰次數歸 0 後，怪物會攻擊 1~20 點；下方道具卡只能使用一次",
            int(WIDTH * 0.20),
            int(HEIGHT * 0.13),
            font_small,
            (255, 255, 255))

        battle_weapon_position = None

        if SelectedWeapon is not None:
            weapon_x = int(WIDTH * 0.03)
            weapon_y = int(HEIGHT * 0.30)

            draw_text(
                "武器卡",
                weapon_x,
                int(weapon_y - HEIGHT * 0.06),
                font_small,
                (255, 255, 255))

            draw_card(SelectedWeapon, weapon_x, weapon_y)

            battle_weapon_position = (
                weapon_x,
                weapon_y,
                CARD_W,
                CARD_H,
                SelectedWeapon)

        dice_size = int(HEIGHT * 0.16)
        dice_x = int(WIDTH * 0.5 - dice_size / 2)
        dice_y = int(HEIGHT * 0.25)

        draw_dice(dice_x, dice_y, dice_size, dice_value)

        info_text = f"剩餘擲骰：{roll_times}　攻擊加成：+{player_attack_bonus}　手槍雙倍：{gun_double_turns}"
        draw_text(
            info_text,
            int(WIDTH * 0.24),
            int(HEIGHT * 0.44),
            font_small,
            (255, 255, 255))

        msg_img = font_mid.render(battle_message, True, (255, 255, 255))
        msg_rect = msg_img.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.53)))
        screen.blit(msg_img, msg_rect)

        BattleItems = PlayerDeck.copy()
        BattleItems = BattleItems[:6]

        if len(BattleItems) == 0:
            card_positions = []

            draw_text(
                "目前沒有道具卡",
                int(WIDTH * 0.40),
                int(HEIGHT * 0.70),
                font_mid,
                (255, 255, 255))

        else:
            draw_text(
                "道具卡：使用後會消失",
                int(WIDTH * 0.40),
                int(HEIGHT * 0.58),
                font_small,
                (255, 255, 255))

            card_positions = draw_card_row(BattleItems, int(HEIGHT * 0.63))

    elif Background == "GameOver":
        screen.fill((20, 0, 0))

        draw_text(
            "你被擊敗了！",
            int(WIDTH * 0.36),
            int(HEIGHT * 0.32),
            font_big,
            (255, 80, 80) )

        draw_text(
            "重新遊戲請按 P 鍵",
            int(WIDTH * 0.32),
            int(HEIGHT * 0.48),
            font_mid,
            (255, 255, 255))

        draw_text(
            "按 P 後會回到遊戲一開始，重新選擇武器",
            int(WIDTH * 0.27),
            int(HEIGHT * 0.58),
            font_small,
            (255, 255, 255))
    # 時間更新
    pygame.display.flip()

    Global_Time += 1

    for Akey in Anim_Time:
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1
pygame.quit()

