# Auto-generated from Untitled.ipynb

# --- Code Cell ---
import pygame

pygame.init()

SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,720),(4,1920,1440),(5,2880,2160)]
SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("骰子戰鬥遊戲")

battle_bg = pygame.image.load(r"final\battleback2nog.jpeg").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(battle_bg, (0, 0))

    pygame.display.update()

pygame.quit()

# --- Code Cell ---
import pygame
import numpy as np
import random

#變數初始化
SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,720),(4,1920,1440),(5,2880,2160)]
SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60
Pr,Pc = 11,11
PlayerV = 5
Background = "Map" #這個是到時候切背景可以改的東東
Global_Time = 0 #系統級時間碼，暫停的時候會暫停
Anim_Time = {} #各動畫時間碼專用辭典
# ================= 新增：卡牌系統變數 =================
PlayerDeck = [] # 玩家目前擁有的卡牌清單（一開始為空）
CardPool = ["腦袋尖尖的", "小草", "戰術翻滾", "菜菜撈撈", "心靈課程名單", "老千的技術", "你從桃園到新竹"] # 寶箱可以開出的卡牌種類
# ====================================================

#地圖生成
MAP = np.zeros((23,23),dtype=int)
MAP[11,11] = 1
MAP[10,11] = 2
MAP[12,11] = 2
MAP[11,12] = 2
MAP[11,10] = 2

#主程式
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#地圖檔載入
MAPList = [] #地圖類型背景庫
for i in range(1,10): #共1~9種房間的底圖
    MAPList.append(pygame.transform.scale(pygame.image.load("assets/map"+str(i)+".png").convert(), (WIDTH, HEIGHT)))
MAPListName = ["無","出生點","小寶箱","事件區","大寶箱","交易區","陷阱區","菁英怪","整備區","魔王關"]

#素材庫
Asset_dict = {
    "b049anim_room1":pygame.transform.smoothscale(pygame.image.load("assets/animdict/b049anim_room1.png").convert_alpha(), (int(WIDTH / 5 * 2), int(WIDTH / 25 * 2)))
}

#字體載入
FHeadPath = "assets/font/NotoSansTC-Bold.ttf" #粗字
FTextPath = "assets/font/NotoSansTC-Light.ttf" #細字

#Class區域
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1.0):
        super().__init__()
        self.original_image = pygame.image.load("assets/player.png").convert_alpha()
        self.rect = pygame.Rect(x, y, 0, 0)        
        self.set_scale(scale_factor)
        self.speed = PlayerV

    def set_scale(self, new_scale):
        """縮放倍率調整"""
        if new_scale > 0:
            self.image_right = pygame.transform.smoothscale(self.original_image, (int(WIDTH / 12 * new_scale), int(HEIGHT / 8 * new_scale)))
            self.image_left = pygame.transform.flip(self.image_right, True, False)
            self.image = self.image_right if self.image_right else self.image_left
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        """移動與判定邊界"""
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
        self.image = pygame.transform.smoothscale(pygame.image.load("assets/gate.png").convert_alpha(), (int(WIDTH / 12), int(HEIGHT / 8)))
        self.rect = self.image.get_rect()
        self.GateType = GateType
        if GateType == "N":
            self.rect.center = (WIDTH/2, HEIGHT*0.1)
        elif GateType == "S":
            self.rect.center = (WIDTH/2, HEIGHT*0.95)
        elif GateType == "W":
            self.rect.center = (WIDTH*0.15, HEIGHT/2)
        elif GateType == "E":
            self.rect.center = (WIDTH*0.85, HEIGHT/2)
        self.mask = pygame.mask.from_surface(self.image)

#Def區域
def refresh_gates(i, j, gates_group):
    gates_group.empty()
    if MAP[Pr,Pc-1] == 0 or RoomStep == 0:
        gates_group.add(Gate("W"))
    if MAP[Pr,Pc+1] == 0 or RoomStep == 0:
        gates_group.add(Gate("E"))
    if MAP[Pr-1,Pc] == 0 or RoomStep == 0:
        gates_group.add(Gate("N"))
    if MAP[Pr+1,Pc] == 0 or RoomStep == 0:
        gates_group.add(Gate("S"))
    if RoomStep == 8+GameRound:
        gates_group.empty()

def miniMap():
    if Background == "Map":
        for i in range(23):
            for j in range(23):
                ColorLS = [(0,0,0),(210,210,210),(218,165,32),(0,0,255),(255,215,0),(255,105,180),(139,69,19),(255,99,71),(0,255,0),(255,0,0)]
                Color = ColorLS[MAP[i,j]]
                if (i,j) == (Pr,Pc):
                    pygame.draw.rect(screen, Color, ((WIDTH / 160) + (j * WIDTH / 120), (HEIGHT / 120) + (i * HEIGHT / 90), WIDTH / 120, HEIGHT / 90))
                    pygame.draw.rect(screen, (0,0,0), ((WIDTH / 160) + (j * WIDTH / 120), (HEIGHT / 120) + (i * HEIGHT / 90), WIDTH / 120, HEIGHT / 90), int(max(HEIGHT / 300,1)))
                elif MAP[i,j] != 0:
                    pygame.draw.rect(screen, Color, ((WIDTH / 160) + (j * WIDTH / 120), (HEIGHT / 120) + (i * HEIGHT / 90), WIDTH / 120, HEIGHT / 90))

def event(head,color,text):
    return True

def Animation():
    if 'Anim_Room' in Anim_Time and Anim_Time.get('Anim_Room') > 0:
        Anim_Room()

#個別動畫專用區

def Anim_Room():
    recimg = Asset_dict["b049anim_room1"]
    rec = recimg.get_rect()
    adx = WIDTH / 2
    ady = min(( -0.00003 * (int(Anim_Time['Anim_Room']) - 60 ) * (int(Anim_Time['Anim_Room']) - 120) + 0.1 ), 0.1) * HEIGHT
    rec.centerx = adx
    rec.centery = ady
    screen.blit(recimg, rec)
    FHead = pygame.font.Font(FHeadPath, int(HEIGHT/15))
    Head = FHead.render(MAPListName[MAP[Pr,Pc]], True, (255, 255, 255))
    trec = Head.get_rect()
    trec.center = rec.center
    screen.blit(Head, trec)

#開始運作
player = Player(WIDTH/2,HEIGHT/2) #玩家生成
GameRound = 1
RoomStep = 0
gates_group = pygame.sprite.Group() #門元件生成
refresh_gates(Pr, Pc, gates_group)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if Background == "Map":
        player.update(keys)
        hit_gate = pygame.sprite.spritecollideany(player, gates_group)
        if hit_gate:
            if hit_gate.GateType == "N":
                Pr -= 1
                player.rect.center = (WIDTH/2, HEIGHT*0.9)
            elif hit_gate.GateType == "S":
                Pr += 1
                player.rect.center = (WIDTH/2, HEIGHT*0.15)
            elif hit_gate.GateType == "W":
                Pc -= 1
                player.rect.center = (WIDTH*0.75, HEIGHT/2)
            elif hit_gate.GateType == "E":
                Pc += 1
                player.rect.center = (WIDTH*0.25, HEIGHT/2)
            RoomStep += 1
            if MAP[Pr,Pc] == 0 and RoomStep not in [4,7+GameRound,8+GameRound]:
                MAP[Pr,Pc] = random.randint(2,6) #傳送瞬間去改 Numpy 陣列，隨機判定房間類型，這裡不處理精英怪、整備、Boss，這幾個交給RoomStep處理
            elif RoomStep == 4:
                MAP[Pr,Pc] = 7
            elif RoomStep == 7+GameRound:
                MAP[Pr,Pc] = 8
            elif RoomStep == 8+GameRound:
                MAP[Pr,Pc] = 9
            refresh_gates(Pr, Pc, gates_group)
            Anim_Time["Anim_Room"] = 3 * FPS
    
    #顯示區
    if Background == "Map":
        screen.blit(MAPList[int(MAP[Pr,Pc])-1], (0, 0))
        gates_group.draw(screen)
        screen.blit(player.image, player.rect)
        #小地圖
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH * 0.41 / 4 , HEIGHT * 0.41 / 3),WIDTH * 18 / 240)
        miniMap()
        Animation()
                    
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1
    for Akey in Anim_Time:
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()

# --- Code Cell ---
import pygame
import numpy as np
import random

# =========================
# 變數初始化
# =========================

SCREEN_SIZE = [
    (1, 480, 360),
    (2, 720, 540),
    (3, 1080, 720),
    (4, 1920, 1440),
    (5, 2880, 2160)
]

SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60

Pr, Pc = 11, 11
PlayerV = 5

Background = "Map"   # Map / Battle
Global_Time = 0
Anim_Time = {}

# =========================
# 卡牌系統變數
# =========================

PlayerDeck = []
CardPool = [
    "腦袋尖尖的",
    "小草",
    "戰術翻滾",
    "菜菜撈撈",
    "心靈課程名單",
    "老千的技術",
    "你從桃園到新竹"
]

# =========================
# 戰鬥系統變數
# =========================

player_hp = 30
enemy_hp = 40

dice_value = 1
dice_rolling = False
dice_roll_timer = 0

battle_message = "按 R 或空白鍵重新擲骰"

cards = [
    {
        "name": "普通攻擊",
        "desc": "造成骰子點數傷害",
        "type": "attack"
    },
    {
        "name": "重擊",
        "desc": "造成骰子點數 + 3 傷害",
        "type": "heavy"
    },
    {
        "name": "治療",
        "desc": "回復骰子點數 HP",
        "type": "heal"
    }
]

card_positions = []

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

MAPListName = [
    "無",
    "出生點",
    "小寶箱",
    "事件區",
    "大寶箱",
    "交易區",
    "陷阱區",
    "菁英怪",
    "整備區",
    "魔王關"]

# =========================
# 戰鬥背景載入
# =========================

battle_bg = pygame.image.load(r"final\battleback2nog.jpeg").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

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

# 備用系統字體
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


def event(head, color, text):
    return True


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


def draw_card(card, x, y, w, h):
    pygame.draw.rect(
        screen,
        (235, 218, 180),
        (x, y, w, h),
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (90, 60, 30),
        (x, y, w, h),
        4,
        border_radius=18
    )

    title = font_mid.render(card["name"], True, (0, 0, 0))
    title_rect = title.get_rect(center=(x + w // 2, y + h * 0.28))
    screen.blit(title, title_rect)

    desc = font_small.render(card["desc"], True, (0, 0, 0))
    desc_rect = desc.get_rect(center=(x + w // 2, y + h * 0.62))
    screen.blit(desc, desc_rect)


def use_card(card_type):
    global player_hp, enemy_hp, battle_message, dice_value, Background

    if card_type == "attack":
        damage = dice_value
        enemy_hp -= damage
        battle_message = f"普通攻擊！造成 {damage} 點傷害"

    elif card_type == "heavy":
        damage = dice_value + 3
        enemy_hp -= damage
        battle_message = f"重擊！造成 {damage} 點傷害"

    elif card_type == "heal":
        heal = dice_value
        player_hp += heal
        battle_message = f"治療！回復 {heal} 點 HP"

    if enemy_hp <= 0:
        enemy_hp = 0
        battle_message = "敵人被擊敗了！按 M 回地圖"


def reset_battle():
    global enemy_hp, dice_value, dice_rolling, dice_roll_timer, battle_message

    enemy_hp = 40
    dice_value = 1
    dice_rolling = False
    dice_roll_timer = 0
    battle_message = "按 R 或空白鍵重新擲骰"


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

        if event.type == pygame.KEYDOWN:

            # 測試用：按 B 直接進戰鬥
            if event.key == pygame.K_b:
                reset_battle()
                Background = "Battle"


            # 戰鬥中：按 R 或空白鍵重新擲骰
            if Background == "Battle":
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    rolling

# --- Code Cell ---
                    dice_rolling = True
                    dice_roll_timer = 15

        # 戰鬥中：滑鼠點卡牌
        if event.type == pygame.MOUSEBUTTONDOWN:
            if Background == "Battle" and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for i, rect in enumerate(card_positions):
                    x, y, w, h = rect

                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        use_card(cards[i]["type"])

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

            # =========================
            # 重點：進入菁英怪或魔王房，切到戰鬥
            # =========================
            if MAP[Pr, Pc] in [7, 9]:
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
                battle_message = f"你骰出了 {dice_value} 點"
                

    # =========================
    # 顯示區
    # =========================

    if Background == "Map":
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

    elif Background == "Battle":
        screen.blit(battle_bg, (0, 0))

        # 血量
        draw_text(
            f"玩家 HP：{player_hp}",
            int(WIDTH * 0.08),
            int(HEIGHT * 0.08),
            font_mid,
            (70, 190, 90)
        )

        draw_text(
            f"敵人 HP：{enemy_hp}",
            int(WIDTH * 0.72),
            int(HEIGHT * 0.08),
            font_mid,
            (220, 60, 60)
        )

        # 操作提示
        draw_text(
            "R / 空白鍵：重新擲骰    M：回地圖",
            int(WIDTH * 0.30),
            int(HEIGHT * 0.08),
            font_small,
            (255, 255, 255)
        )

        # 骰子
        dice_size = int(HEIGHT * 0.18)
        dice_x = int(WIDTH * 0.5 - dice_size / 2)
        dice_y = int(HEIGHT * 0.30)

        draw_dice(dice_x, dice_y, dice_size, dice_value)

        # 戰鬥訊息
        msg_img = font_mid.render(battle_message, True, (255, 255, 255))
        msg_rect = msg_img.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.58)))
        screen.blit(msg_img, msg_rect)

        # 卡牌
        card_positions = []

        card_w = int(WIDTH * 0.22)
        card_h = int(HEIGHT * 0.22)
        card_y = int(HEIGHT * 0.70)

        for i, card in enumerate(cards):
            card_x = int(WIDTH * 0.13 + i * WIDTH * 0.28)
            card_positions.append((card_x, card_y, card_w, card_h))
            draw_card(card, card_x, card_y, card_w, card_h)

    # =========================
    # 時間更新
    # =========================

    pygame.display.flip()

    Global_Time += 1

    for Akey in Anim_Time:
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()

# --- Code Cell ---
import pygame
import numpy as np
import random

# =========================
# 變數初始化
# =========================

SCREEN_SIZE = [
    (1, 480, 360),
    (2, 720, 540),
    (3, 1080, 720),
    (4, 1920, 1440),
    (5, 2880, 2160)
]

SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60

Pr, Pc = 11, 11
PlayerV = 5

Background = "Map"   # Map / Battle
Global_Time = 0
Anim_Time = {}

# =========================
# 卡牌系統變數
# =========================

PlayerDeck = []
CardPool = [
    "腦袋尖尖的",
    "小草",
    "戰術翻滾",
    "菜菜撈撈",
    "心靈課程名單",
    "老千的技術",
    "你從桃園到新竹"
]

# =========================
# 戰鬥系統變數
# =========================

player_hp = 30
enemy_hp = 40

dice_value = 1
dice_rolling = False
dice_roll_timer = 0

battle_message = "按 R 或空白鍵重新擲骰"

cards = [
    {
        "name": "普通攻擊",
        "desc": "造成骰子點數傷害",
        "type": "attack"
    },
    {
        "name": "重擊",
        "desc": "造成骰子點數 + 3 傷害",
        "type": "heavy"
    },
    {
        "name": "治療",
        "desc": "回復骰子點數 HP",
        "type": "heal"
    }
]

card_positions = []

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

MAPListName = [
    "無",
    "出生點",
    "小寶箱",
    "事件區",
    "大寶箱",
    "交易區",
    "陷阱區",
    "菁英怪",
    "整備區",
    "魔王關"
]

# =========================
# 戰鬥背景載入
# =========================

battle_bg = pygame.image.load(r"final\battleback2nog.jpeg").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

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

# 備用系統字體
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


def event(head, color, text):
    return True


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


def draw_card(card, x, y, w, h):
    pygame.draw.rect(
        screen,
        (235, 218, 180),
        (x, y, w, h),
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (90, 60, 30),
        (x, y, w, h),
        4,
        border_radius=18
    )

    title = font_mid.render(card["name"], True, (0, 0, 0))
    title_rect = title.get_rect(center=(x + w // 2, y + h * 0.28))
    screen.blit(title, title_rect)

    desc = font_small.render(card["desc"], True, (0, 0, 0))
    desc_rect = desc.get_rect(center=(x + w // 2, y + h * 0.62))
    screen.blit(desc, desc_rect)


def use_card(card_type):
    global player_hp, enemy_hp, battle_message, dice_value, Background

    if card_type == "attack":
        damage = dice_value
        enemy_hp -= damage
        battle_message = f"普通攻擊！造成 {damage} 點傷害"

    elif card_type == "heavy":
        damage = dice_value + 3
        enemy_hp -= damage
        battle_message = f"重擊！造成 {damage} 點傷害"

    elif card_type == "heal":
        heal = dice_value
        player_hp += heal
        battle_message = f"治療！回復 {heal} 點 HP"

    if enemy_hp <= 0:
        enemy_hp = 0
        battle_message = "敵人被擊敗了！按 M 回地圖"


def reset_battle():
    global enemy_hp, dice_value, dice_rolling, dice_roll_timer, battle_message

    enemy_hp = 40
    dice_value = 1
    dice_rolling = False
    dice_roll_timer = 0
    battle_message = "按 R 或空白鍵重新擲骰"


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

        if event.type == pygame.KEYDOWN:

            # 測試用：按 B 直接進戰鬥
            if event.key == pygame.K_b:
                reset_battle()
                Background = "Battle"

            # 按 M 回地圖
            if event.key == pygame.K_m:
                Background = "Map"

            # 戰鬥中：按 R 或空白鍵重新擲骰
            if Background == "Battle":
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    dice_rolling = True
                    dice_roll_timer = 15
                    rolling_times = 8

        # 戰鬥中：滑鼠點卡牌
        if event.type == pygame.MOUSEBUTTONDOWN:
            if Background == "Battle" and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for i, rect in enumerate(card_positions):
                    x, y, w, h = rect

                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        use_card(cards[i]["type"])

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

            # =========================
            # 重點：進入菁英怪或魔王房，切到戰鬥
            # =========================
            if MAP[Pr, Pc] in [7, 9]:
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
                rolling_times -= 1
                battle_message = f"你骰出了 {dice_value} 點，還剩｛

# --- Code Cell ---
"

    # =========================
    # 顯示區
    # =========================

    if Background == "Map":
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

    elif Background == "Battle":
        screen.blit(battle_bg, (0, 0))

        # 血量
        draw_text(
            f"玩家 HP：{player_hp}",
            int(WIDTH * 0.08),
            int(HEIGHT * 0.08),
            font_mid,
            (70, 190, 90)
        )

        draw_text(
            f"敵人 HP：{enemy_hp}",
            int(WIDTH * 0.72),
            int(HEIGHT * 0.08),
            font_mid,
            (220, 60, 60)
        )

        # 操作提示
        draw_text(
            "R / 空白鍵：重新擲骰    M：回地圖",
            int(WIDTH * 0.30),
            int(HEIGHT * 0.08),
            font_small,
            (255, 255, 255)
        )

        # 骰子
        dice_size = int(HEIGHT * 0.18)
        dice_x = int(WIDTH * 0.5 - dice_size / 2)
        dice_y = int(HEIGHT * 0.30)

        draw_dice(dice_x, dice_y, dice_size, dice_value)

        # 戰鬥訊息
        msg_img = font_mid.render(battle_message, True, (255, 255, 255))
        msg_rect = msg_img.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.58)))
        screen.blit(msg_img, msg_rect)

        # 卡牌
        card_positions = []

        card_w = int(WIDTH * 0.22)
        card_h = int(HEIGHT * 0.22)
        card_y = int(HEIGHT * 0.70)

        for i, card in enumerate(cards):
            card_x = int(WIDTH * 0.13 + i * WIDTH * 0.28)
            card_positions.append((card_x, card_y, card_w, card_h))
            draw_card(card, card_x, card_y, card_w, card_h)

    # =========================
    # 時間更新
    # =========================

    pygame.display.flip()

    Global_Time += 1

    for Akey in Anim_Time:
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()

# --- Code Cell ---
import pygame
import numpy as np
import random

# =========================
# 變數初始化
# =========================

SCREEN_SIZE = [
    (1, 480, 360),
    (2, 720, 540),
    (3, 1080, 720),
    (4, 1920, 1440),
    (5, 2880, 2160)
]

SS = 2
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])
FPS = 60

Pr, Pc = 11, 11
PlayerV = 5

Background = "Map"   # Map / Battle
Global_Time = 0
Anim_Time = {}

# =========================
# 卡牌系統變數
# =========================

PlayerDeck = []
CardPool = [
    "腦袋尖尖的",
    "小草",
    "戰術翻滾",
    "菜菜撈撈",
    "心靈課程名單",
    "老千的技術",
    "你從桃園到新竹"
]

# =========================
# 戰鬥系統變數
# =========================

player_hp = 30
enemy_hp = 40

dice_value = 1
dice_rolling = False
dice_roll_timer = 0

battle_message = "按 R 或空白鍵重新擲骰"

cards = [
    {
        "name": "普通攻擊",
        "desc": "造成骰子點數傷害",
        "type": "attack"
    },
    {
        "name": "重擊",
        "desc": "造成骰子點數 + 3 傷害",
        "type": "heavy"
    },
    {
        "name": "治療",
        "desc": "回復骰子點數 HP",
        "type": "heal"
    }
]

card_positions = []

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

MAPListName = [
    "無",
    "出生點",
    "小寶箱",
    "事件區",
    "大寶箱",
    "交易區",
    "陷阱區",
    "菁英怪",
    "整備區",
    "魔王關"
]

# =========================
# 戰鬥背景載入
# =========================

battle_bg = pygame.image.load(r"final\battleback2nog.jpeg").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

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

# 備用系統字體
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


def event(head, color, text):
    return True


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


def draw_card(card, x, y, w, h):
    pygame.draw.rect(
        screen,
        (235, 218, 180),
        (x, y, w, h),
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (90, 60, 30),
        (x, y, w, h),
        4,
        border_radius=18
    )

    title = font_mid.render(card["name"], True, (0, 0, 0))
    title_rect = title.get_rect(center=(x + w // 2, y + h * 0.28))
    screen.blit(title, title_rect)

    desc = font_small.render(card["desc"], True, (0, 0, 0))
    desc_rect = desc.get_rect(center=(x + w // 2, y + h * 0.62))
    screen.blit(desc, desc_rect)


def use_card(card_type):
    global player_hp, enemy_hp, battle_message, dice_value, Background

    if card_type == "attack":
        damage = dice_value
        enemy_hp -= damage
        battle_message = f"普通攻擊！造成 {damage} 點傷害"

    elif card_type == "heavy":
        damage = dice_value + 3
        enemy_hp -= damage
        battle_message = f"重擊！造成 {damage} 點傷害"

    elif card_type == "heal":
        heal = dice_value
        player_hp += heal
        battle_message = f"治療！回復 {heal} 點 HP"

    if enemy_hp <= 0:
        enemy_hp = 0
        battle_message = "敵人被擊敗了！按 M 回地圖"


def reset_battle():
    global enemy_hp, dice_value, dice_rolling, dice_roll_timer, battle_message

    enemy_hp = 40
    dice_value = 1
    dice_rolling = False
    dice_roll_timer = 0
    battle_message = "按 R 或空白鍵重新擲骰"


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

        if event.type == pygame.KEYDOWN:

            # 測試用：按 B 直接進戰鬥
            if event.key == pygame.K_b:
                reset_battle()
                Background = "Battle"
                roll_times = 8

            # 按 M 回地圖
            if event.key == pygame.K_m:
                Background = "Map"

            # 戰鬥中：按 R 或空白鍵重新擲骰
            if Background == "Battle":
                if (event.key == pygame.K_r or event.key == pygame.K_SPACE) and roll_times>0:
                    dice_rolling = True
                    dice_roll_timer = 15
                    

        # 戰鬥中：滑鼠點卡牌
        if event.type == pygame.MOUSEBUTTONDOWN:
            if Background == "Battle" and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for i, rect in enumerate(card_positions):
                    x, y, w, h = rect

                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        use_card(cards[i]["type"])

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

            # =========================
            # 重點：進入菁英怪或魔王房，切到戰鬥
            # =========================
            if MAP[Pr, Pc] in [7, 9]:
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
                battle_message = f"你骰出了 {dice_value} 點，還剩{roll_times}次擲骰次數"

    # =========================
    # 顯示區
    # =========================

    if Background == "Map":
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

    elif Background == "Battle":
        screen.blit(battle_bg, (0, 0))

        # 血量
        draw_text(
            f"玩家 HP：{player_hp}",
            int(WIDTH * 0.08),
            int(HEIGHT * 0.08),
            font_mid,
            (70, 190, 90)
        )

        draw_text(
            f"敵人 HP：{enemy_hp}",
            int(WIDTH * 0.72),
            int(HEIGHT * 0.08),
            font_mid,
            (220, 60, 60)
        )

        # 操作提示
        draw_text(
            "R / 空白鍵：重新擲骰    M：回地圖",
            int(WIDTH * 0.30),
            int(HEIGHT * 0.08),
            font_small,
            (255, 255, 255)
        )

        # 骰子
        dice_size = int(HEIGHT * 0.18)
        dice_x = int(WIDTH * 0.5 - dice_size / 2)
        dice_y = int(HEIGHT * 0.30)

        draw_dice(dice_x, dice_y, dice_size, dice_value)

        # 戰鬥訊息
        msg_img = font_mid.render(battle_message, True, (255, 255, 255))
        msg_rect = msg_img.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.58)))
        screen.blit(msg_img, msg_rect)

        # 卡牌
        card_positions = []

        card_w = int(WIDTH * 0.22)
        card_h = int(HEIGHT * 0.22)
        card_y = int(HEIGHT * 0.70)

        for i, card in enumerate(cards):
            card_x = int(WIDTH * 0.13 + i * WIDTH * 0.28)
            card_positions.append((card_x, card_y, card_w, card_h))
            draw_card(card, card_x, card_y, card_w, card_h)

    # =========================
    # 時間更新
    # =========================

    pygame.display.flip()

    Global_Time += 1

    for Akey in Anim_Time:
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()

