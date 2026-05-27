import pygame
import numpy as np
import random
import os
import sys

# 運行路徑鎖死到py檔同層 By AI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
print(f'目前遊戲的絕對路徑已鎖定在：{os.getcwd()}')

# 系統縮放取得 By AI
def getsysscaling():
    if sys.platform == "darwin": 
        try:
            from AppKit import NSScreen
            return NSScreen.mainScreen().backingScaleFactor()
        except ImportError:
            import subprocess
            cmd = "system_profiler SPDisplaysDataType | grep 'Retina'"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            if "Retina" in result.stdout:
                return 2.0
    if sys.platform == "win32":
        import ctypes
        try:
            scale_percent = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            return scale_percent / 100.0  
        except Exception:
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) 
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
    return 1.0

# 變數初始化
SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,810),(4,1920,1440),(0,2880,2160)]
SS = 3
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]/getsysscaling()), int(SCREEN_SIZE[SS][2]/getsysscaling())
FPS = 60
Pr, Pc = 11, 11
PlayerV = 5.0
Background = "StartWeapon" # 一開始進入選初始武器畫面
Global_Time = 0 
Anim_Time = {} 
BackHistory = [] 
MAPListName = ["無","出生點","小寶箱","闖關區","大寶箱","交易所","零和遊戲","菁英怪","整備區","Boss"]

# 全域字體與資源字典宣告
FHeadPath = os.path.join("assets", "font", "NotoSansTC-Bold.ttf")
FTextPath = os.path.join("assets", "font", "NotoSansTC-Light.ttf")
font_big = None
font_mid = None
font_small = None
Asset_dict = {}
CardImage = {}
EventCardImage = {}
MAPList = []
CARD_W, CARD_H, EVENT_CARD_W, EVENT_CARD_H = 0, 0, 0, 0

# 卡牌池
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

# 戰鬥數值
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
has_nana_shield = False # 免死金牌效果判定標記

# 地圖生成
MAP = np.zeros((23,23),dtype=int)
MAP[11,11] = 1
MAP[10,11] = 2
MAP[12,11] = 2
MAP[11,12] = 2
MAP[11,10] = 2
BackHistory.append("Map")
mapused = True

# 主程式初始化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('骰子迷因大亂鬥')
clock = pygame.time.Clock()

# 素材載入函式（具備防打錯檔名、編碼亂碼、檔案遺失不閃退功能）
def assetsload(WIDTH, HEIGHT):
    '''圖檔尺寸、載入刷新'''
    global MAPList, Asset_dict, CardImage, EventCardImage
    global CARD_H, CARD_W, EVENT_CARD_H, EVENT_CARD_W
    global font_big, font_mid, font_small, FHeadPath

    # 1. 地圖底圖安全載入
    MAPList = [] 
    for i in range(1, 11): 
        path = os.path.join("assets", f'map{i}.png')
        try:
            MAPList.append(pygame.transform.scale(pygame.image.load(path).convert(), (WIDTH, HEIGHT)))
        except Exception:
            surf = pygame.Surface((WIDTH, HEIGHT))
            surf.fill((40, 40, i * 20))
            MAPList.append(surf)

    # 2. UI素材與遊戲背景安全載入
    Asset_dict = {}
    ui_assets = {
        "b049anim_room1": (int(WIDTH / 5 * 2), int(WIDTH / 25 * 2), "animdict", (100, 100, 100)),
        "b049setting": (int(WIDTH / 20), int(WIDTH / 20), "animdict", (150, 150, 150)),
        "xesc": (int(WIDTH / 20), int(WIDTH / 20), "", (250, 50, 50)),
        "b049settingback": (WIDTH, HEIGHT, "Background", (30, 30, 30)),
        "b049settingb": (int(WIDTH / 5 * 1.5), int(WIDTH / 25 * 1.5), "animdict", (70, 70, 70)),
        "b049roomcenter8": (int(WIDTH / 8), int(WIDTH / 8), "animdict", (50, 200, 50)),
        "b049roomcenter7": (int(WIDTH / 3), int(HEIGHT / 4), "Enemy", (220, 40, 40)), 
        "b049roomcload3-1": (int(WIDTH / 3), int(HEIGHT / 3), "animdict", (150, 150, 50)),
        "b049roomcload3-2": (WIDTH, HEIGHT, "animdict", (10, 10, 10)),
        "b049gaming0-1": (WIDTH, HEIGHT, "animdict", (0, 0, 0)),
        "b049gaming0-21": (int(WIDTH/6), int(WIDTH/6), "animdict", (80, 80, 80)),
        "b049gaming0-22": (int(WIDTH/8), int(WIDTH/8), "animdict", (100, 100, 100)),
        "b049gaming0-23": (int(WIDTH/10), int(WIDTH/10), "animdict", (120, 120, 120)),
        "b118battle_bg": (WIDTH, HEIGHT, "Background", (20, 20, 40))
    }

    for name, info in ui_assets.items():
        w, h, subfolder, fallback_color = info
        success = False
        exts = [".jpeg", ".jpg", ".png"] if "battle" in name else [".png"]
        for ext in exts:
            filename = "battleback2nog.jpeg" if (name == "b118battle_bg" and ext == ".jpeg") else f"{name}{ext}"
            path = os.path.join("assets", subfolder, filename) if subfolder else os.path.join("assets", filename)
            if os.path.exists(path):
                try:
                    Asset_dict[name] = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), (w, h))
                    success = True
                    break
                except Exception:
                    pass
        if not success:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.fill(fallback_color)
            Asset_dict[name] = surf

    for i in range(1, 7):
        path = os.path.join("assets", "animdict", f'b049roomcenter{i}.png')
        try:
            Asset_dict[f'b049roomcenter{i}'] = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), (int(WIDTH / 8), int(WIDTH / 8)))
        except Exception:
            surf = pygame.Surface((int(WIDTH / 8), int(WIDTH / 8)), pygame.SRCALPHA)
            surf.fill((100, i * 25, 200))
            Asset_dict[f'b049roomcenter{i}'] = surf

    for j in range(0, 1):
        path = os.path.join("assets", "Background", f'b049gaming{j}.png')
        try:
            Asset_dict[f'b049gaming{j}'] = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), (WIDTH, HEIGHT))
        except Exception:
            surf = pygame.Surface((WIDTH, HEIGHT))
            surf.fill((40, 20, 20))
            Asset_dict[f'b049gaming{j}'] = surf

    # 3. 卡牌與事件卡安全配對
    CARD_W = int(WIDTH * 0.15)
    CARD_H = int(HEIGHT * 0.33)
    EVENT_CARD_W = int(WIDTH * 0.25)
    EVENT_CARD_H = int(HEIGHT * 0.55)

    CardImage = {}
    EventCardImage = {}
    card_keys = [
        "腦袋尖尖的", "小草", "戰術翻滾", "菜菜撈撈", "心靈課程名單", "老千的技術", "你從桃園到新竹",
        "橙汁汙中山羨恭喜", "3cm 感謝祭", "我一步都沒有退ㄟ", "我中了兩槍", "寵物溝通師", "芒果醬",
        "武術大師晨晨", "幹你敢不敢啦", "雷霆測資", "傑里科941半自動手槍", "鞭子", "巨槌瑞斯"
    ]
    img_files = [
        "S__76242953.png", "S__76242954.png", "S__76242955.png", "S__76242956.png", "S__76242957.png", "S__76242958.png", "S__76242959.png",
        "S__76242960.png", "S__76242961.png", "S__76242962.png", "S__76242964.png", "S__76242965.png", "S__76242966.png", "S__76242967.png",
        "S__76242968.png", "S__76242973.png", "S__76242970.png", "S__76242971.png", "S__76242972.png"
    ]

    for key, filename in zip(card_keys, img_files):
        path = os.path.join("assets", "card", filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            CardImage[key] = pygame.transform.smoothscale(img, (CARD_W, CARD_H))
            EventCardImage[key] = pygame.transform.smoothscale(img, (EVENT_CARD_W, EVENT_CARD_H))
        except Exception:
            surf = pygame.Surface((EVENT_CARD_W, EVENT_CARD_H))
            surf.fill((60, 60, 80))
            pygame.draw.rect(surf, (255, 255, 255), (0, 0, EVENT_CARD_W, EVENT_CARD_H), 3)
            try:
                temp_font = pygame.font.SysFont("microsoftjhenghei", 20)
                text_surf = temp_font.render(key, True, (255, 255, 255))
                surf.blit(text_surf, (15, 15))
            except Exception: pass
            CardImage[key] = pygame.transform.smoothscale(surf, (CARD_W, CARD_H))
            EventCardImage[key] = surf

    # 4. 字體安全初始化
    try:
        font_big = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), 52)
        font_mid = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), 34)
        font_small = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), 24)
    except Exception:
        font_big = pygame.font.SysFont("microsoftjhenghei", 48)
        font_mid = pygame.font.SysFont("microsoftjhenghei", 32)
        font_small = pygame.font.SysFont("microsoftjhenghei", 22)

    return MAPList, Asset_dict, CardImage, EventCardImage

# 執行首次全域資源加載
MAPList, Asset_dict, CardImage, EventCardImage = assetsload(WIDTH, HEIGHT)

# Sprite 類別定義
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1.0):
        super().__init__()
        try:
            self.original_image = pygame.image.load(os.path.join("assets","player.png")).convert_alpha()
        except Exception:
            self.original_image = pygame.Surface((50, 70), pygame.SRCALPHA)
            self.original_image.fill((0, 200, 100))
        self.rect = pygame.Rect(x, y, 0, 0)        
        self.set_scale(scale_factor)
        self.speed = PlayerV

    def set_scale(self, new_scale):
        if new_scale > 0:
            self.image_right = pygame.transform.smoothscale(self.original_image, (int(WIDTH / 12 * new_scale), int(HEIGHT / 8 * new_scale)))
            self.image_left = pygame.transform.flip(self.image_right, True, False)
            self.image = self.image_right
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        move_offset = PlayerV * HEIGHT / 1080 * 60 / FPS
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= move_offset
            self.image = self.image_left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += move_offset
            self.image = self.image_right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= move_offset
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += move_offset
            
        if self.rect.left < WIDTH * 0.15: self.rect.left = int(WIDTH * 0.15)
        if self.rect.right > WIDTH * 0.85: self.rect.right = int(WIDTH * 0.85)
        if self.rect.top < HEIGHT * 0.1: self.rect.top = int(HEIGHT * 0.1)
        if self.rect.bottom > HEIGHT * 0.95: self.rect.bottom = int(HEIGHT * 0.95)
    
    def check_trigger(self, target):
        return pygame.sprite.collide_rect(self, target)

class Gate(pygame.sprite.Sprite):
    def __init__(self, GateType):
        super().__init__()
        try:
            self.image = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","gate.png")).convert_alpha(), (int(WIDTH / 12), int(HEIGHT / 9)))
        except Exception:
            self.image = pygame.Surface((int(WIDTH / 12), int(HEIGHT / 9)), pygame.SRCALPHA)
            self.image.fill((200, 200, 255, 120))
        self.rect = self.image.get_rect()
        self.GateType = GateType
        if GateType == "N": self.rect.center = (WIDTH/2, HEIGHT*0.1)
        elif GateType == "S": self.rect.center = (WIDTH/2, HEIGHT*0.95)
        elif GateType == "W": self.rect.center = (WIDTH*0.15, HEIGHT/2)
        elif GateType == "E": self.rect.center = (WIDTH*0.85, HEIGHT/2)
        self.mask = pygame.mask.from_surface(self.image)

class ingameSetting(pygame.sprite.Sprite): 
    def __init__(self, x, y, asset_dict):
        super().__init__()
        self.image = asset_dict['b049setting']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)

class Xesc(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_dict):
        super().__init__()
        self.image = asset_dict['xesc']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)

class ingameSettingSSB(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_dict):
        super().__init__()
        self.image = asset_dict['b049settingb']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)
    def update(self, W, H):
        try:
            FHead = pygame.font.Font(FHeadPath, int(H/25))
        except Exception:
            FHead = pygame.font.SysFont("microsoftjhenghei", int(H/25))
        Head = FHead.render(f'{int(W*getsysscaling())} x {int(H*getsysscaling())}', True, (255, 255, 255))
        trec = Head.get_rect(center=(self.rect.centerx, self.rect.centery - int(0.006 * HEIGHT)))
        screen.blit(Head, trec)

class roomcenterthing(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = Asset_dict['b049roomcenter1']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)
    def update(self):
        rec = self.rect.center
        idx = MAP[Pr, Pc] if MAP[Pr, Pc] in Asset_dict else 1
        self.image = Asset_dict.get(f'b049roomcenter{idx}', Asset_dict['b049roomcenter1'])
        self.rect = self.image.get_rect()
        self.rect.center = rec
    def touch(self):
        global mapused, Anim_Time, Background
        if MAP[Pr,Pc] in [2, 4]:
            mapused = True
            Anim_Time['AnimRoomCenter2'] = 1 * FPS
        if MAP[Pr,Pc] == 3:
            mapused = True
            Anim_Time['AnimRoomCenter3'] = 4 * FPS
        if MAP[Pr,Pc] == 6:
            mapused = True
            Anim_Time['AnimRoomCenter6'] = 4 * FPS
        if MAP[Pr,Pc] in [7, 9]:
            reset_battle()
            Background = "Battle"
        if MAP[Pr,Pc] == 8:
            mapused = True
            Anim_Time['AnimRoomCenter8'] = 1 * FPS

# 邏輯與功能函式區域
def refresh_gates(i, j, gates_group):
    gates_group.empty()
    if RoomStep == 8+GameRound: return
    if MAP[Pr,Pc-1] == 0 or RoomStep == 0: gates_group.add(Gate("W"))
    if MAP[Pr,Pc+1] == 0 or RoomStep == 0: gates_group.add(Gate("E"))
    if MAP[Pr-1,Pc] == 0 or RoomStep == 0: gates_group.add(Gate("N"))
    if MAP[Pr+1,Pc] == 0 or RoomStep == 0: gates_group.add(Gate("S"))

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

def draw_text(text, x, y, font, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_dice(x, y, size, value):
    pygame.draw.rect(screen, (245, 245, 245), (x, y, size, size), border_radius=20)
    pygame.draw.rect(screen, (0, 0, 0), (x, y, size, size), 5, border_radius=20)
    text = font_big.render(str(value), True, (0, 0, 0))
    rect = text.get_rect(center=(x + size // 2, y + size // 2))
    screen.blit(text, rect)

def draw_card(card, x, y):
    screen.blit(CardImage[card["name"]], (x, y))

def draw_event_card(card, x, y):
    if card is not None and card["name"] in EventCardImage:
        screen.blit(EventCardImage[card["name"]], (x, y))

def draw_card_row(card_list, y):
    positions = []
    if len(card_list) == 0: return positions
    gap = int(WIDTH * 0.025)
    total_width = len(card_list) * CARD_W + (len(card_list) - 1) * gap
    start_x = int((WIDTH - total_width) / 2)
    for i, card in enumerate(card_list):
        card_x = start_x + i * (CARD_W + gap)
        draw_card(card, card_x, y)
        card_rect = pygame.Rect(card_x, y, CARD_W, CARD_H)
        positions.append((card_rect, card))
    return positions

def get_random_item_card():
    global battle_message
    new_card = random.choice(ItemCardPool)
    PlayerDeck.append(new_card)
    battle_message = f"獲得道具卡：{new_card['name']}"
    print(f"【系統】卡片正確載入背包！目前持有數: {len(PlayerDeck)}，卡片: {new_card['name']}")

def get_random_event_card():
    global CurrentEventCard, battle_message
    CurrentEventCard = random.choice(EventCardPool)
    battle_message = f"事件發生：{CurrentEventCard['name']}"

def apply_event_card(event_card):
    global player_hp, battle_message, enemy_double_attack_times, seal_monster_once
    global boss_no_immunity, next_dice_fixed_three, enemy_hp_multiplier, player_attack_half, mango_bonus, next_battle_chengchen

    if event_card is None: return
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
    if mango_bonus: damage += int(damage * 0.3)
    if player_attack_half: damage = max(damage // 2, 1)
    return damage

def weapon_attack(card_type):
    global enemy_hp, battle_message, gun_double_turns
    if enemy_hp <= 0 or player_hp <= 0: return
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
    global player_hp, enemy_hp, battle_message, player_attack_bonus
    global cheat_mode, roll_immunity, hit_count, stored_damage_turns, stored_damage, has_nana_shield

    if enemy_hp <= 0 or player_hp <= 0: return
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
        has_nana_shield = True
        battle_message = "菜菜撈撈：免死效果已準備，血量歸零時會剩 1"
    elif card_type == "mind":
        player_hp += 25
        battle_message = "心靈課程名單：血量 +25"
    elif card_type == "cheat":
        cheat_mode = True
        battle_message = "老千的技術：請按主鍵盤數字鍵 1～6 選擇骰子點數"
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
    global enemy_double_attack_times, seal_monster_once, roll_immunity, hit_count, boss_no_immunity

    if enemy_hp <= 0 or player_hp <= 0: return
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
            battle_message = "戰術翻滾觸發！完美閃避怪物猛擊，輪到你重新擲骰"
            return

    player_hp -= monster_damage
    if player_hp <= 0:
        if has_nana_shield:
            player_hp = 1
            has_nana_shield = False
            battle_message = "免死發動！菜菜撈撈幫你擋下致命傷，剩餘 1 HP！"
        else:
            player_hp = 0
            battle_message = f"怪物攻擊造成 {monster_damage} 點傷害，你被擊敗了！"
            Background = "GameOver"
    else:
        roll_times = 8
        battle_message = f"怪物攻擊！造成 {monster_damage} 點傷害，輪到你重新擲骰"

def reset_battle():
    global enemy_hp, enemy_max_hp, dice_value, dice_rolling, dice_roll_timer, battle_message
    global roll_times, player_attack_bonus, gun_double_turns, cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage, enemy_hp_multiplier, next_dice_fixed_three

    if MAP[Pr, Pc] == 9: enemy_max_hp = 80
    else: enemy_max_hp = 40

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

    if SelectedWeapon is not None and SelectedWeapon["type"] == "gun": gun_double_turns = 3
    else: gun_double_turns = 0

    enemy_hp_multiplier = 1

    if next_dice_fixed_three:
        dice_value = 3
        next_dice_fixed_three = False
        battle_message = "事件效果：這場戰鬥骰子先變成 3"
    else:
        battle_message = "先按 R / 空白鍵擲骰，再點左邊武器卡攻擊怪物"

def reset_game():
    global Pr, Pc, Background, Global_Time, Anim_Time, PlayerDeck, UsedRooms, SelectedWeapon, CurrentEventCard
    global card_positions, weapon_positions, battle_weapon_position, player_hp, enemy_hp, enemy_max_hp
    global dice_value, dice_rolling, dice_roll_timer, roll_times, battle_message, player_attack_bonus, gun_double_turns
    global cheat_mode, roll_immunity, hit_count, stored_damage_turns, stored_damage, enemy_double_attack_times
    global seal_monster_once, boss_no_immunity, next_dice_fixed_three, enemy_hp_multiplier, player_attack_half
    global mango_bonus, next_battle_chengchen, has_nana_shield, MAP, player, GameRound, RoomStep, gates_group

    Pr, Pc = 11, 11
    Background = "StartWeapon"
    Global_Time = 0
    Anim_Time = {}
    PlayerDeck = []
    UsedRooms = set()
    SelectedWeapon = None
    CurrentEventCard = None
    card_positions, weapon_positions, battle_weapon_position = [], [], None

    player_hp, enemy_hp, enemy_max_hp = 30, 40, 40
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
    has_nana_shield = False

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

def Animation():
    if 'Anim_Room' in Anim_Time and Anim_Time.get('Anim_Room') > 0: Anim_Room()
    if 'AnimRoomCenter2' in Anim_Time and Anim_Time.get('AnimRoomCenter2') > 0: Anim_RoomCenter2()
    if 'AnimRoomCenter3' in Anim_Time and Anim_Time.get('AnimRoomCenter3') > 0: Anim_RoomCenter3()
    if 'AnimRoomCenter6' in Anim_Time and Anim_Time.get('AnimRoomCenter6') > 0: Anim_RoomCenter6()
    if 'AnimRoomCenter8' in Anim_Time and Anim_Time.get('AnimRoomCenter8') > 0: Anim_RoomCenter8()

# 各別渲染動畫模組
def Anim_Room():
    recimg = Asset_dict["b049anim_room1"]
    rec = recimg.get_rect()
    adx = WIDTH / 2
    ady = min(( -0.00003 * (int(Anim_Time['Anim_Room']) - 60 ) * (int(Anim_Time['Anim_Room']) - 120) + 0.1 ), 0.1) * HEIGHT
    rec.centerx, rec.centery = adx, ady
    screen.blit(recimg, rec)
    try:
        FHead = pygame.font.Font(FHeadPath, int(HEIGHT/15))
    except Exception:
        FHead = pygame.font.SysFont("microsoftjhenghei", int(HEIGHT/15))
    Head = FHead.render(MAPListName[MAP[Pr,Pc]], True, (255, 255, 255))
    trec = Head.get_rect(centerx=rec.centerx, centery=rec.centery - int(0.006 * HEIGHT))
    screen.blit(Head, trec)

def Anim_RoomCenter2():
    rec= pygame.Rect(WIDTH / 2, HEIGHT / 2, WIDTH / 160 * (60-Anim_Time['AnimRoomCenter2']), HEIGHT / 120 * (60-Anim_Time['AnimRoomCenter2']))
    rec.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (255, 215, 0), rec, int(max(HEIGHT / 60, 1)))

def Anim_RoomCenter3():
    global Background, Gamekind
    tick = 240 - Anim_Time['AnimRoomCenter3']
    adx = WIDTH * 0.3
    bdx = WIDTH * 0.7
    cdy = -0.00001 * HEIGHT * (tick - 120) * (tick - 120) * (tick - 120) + HEIGHT / 2
    recimg = Asset_dict["b049roomcload3-2"]
    gun = Asset_dict["b049roomcload3-1"]
    cube = Asset_dict["b049roomcenter3"]
    recg = gun.get_rect(centerx=adx, centery=cdy)
    recc = cube.get_rect(centerx=bdx, centery=cdy)
    if tick <= 30:
        Allblack.set_alpha(int(tick*8.5))
        screen.blit(Allblack, (0, 0))
        if tick == 30: Background = "Loading"
    elif tick <= 60:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha(int((60-tick)*8.5))
        screen.blit(Allblack, (0, 0))
    elif tick <= 180:
        screen.blit(recimg, (0,0))
        screen.blit(gun, recg)
        screen.blit(cube, recc)
    elif tick <= 210:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha(int((tick-180)*8.5))
        screen.blit(Allblack, (0, 0))
        if tick == 210:
            Gamekind = random.randint(0,0)
            Background = "Gaming"
    elif tick <= 240:
        Allblack.set_alpha(int((240-tick)*8.5))
        screen.blit(Allblack, (0, 0))

def Anim_RoomCenter6(): 
    global Background, Gamekind
    tick = 240 - Anim_Time['AnimRoomCenter6'] 
    adx = WIDTH * 0.3
    bdx = WIDTH * 0.7
    cdy = -0.00001 * HEIGHT * (tick - 120) * (tick - 120) * (tick - 120) + HEIGHT / 2
    recimg = Asset_dict["b049roomcload3-2"]
    gun = Asset_dict["b049roomcload3-1"]
    cube = Asset_dict["b049roomcenter3"]
    recg = gun.get_rect(centerx=adx, centery=cdy)
    recc = cube.get_rect(centerx=bdx, centery=cdy)
    if tick <= 30:
        Allblack.set_alpha(int(tick*8.5))
        screen.blit(Allblack, (0, 0))
        if tick == 30: Background = "Loading"
    elif tick <= 60:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha(int((60-tick)*8.5))
        screen.blit(Allblack, (0, 0))
    elif tick <= 180:
        screen.blit(recimg, (0,0))
        screen.blit(gun, recg)
        screen.blit(cube, recc)
    elif tick <= 210:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha(int((tick-180)*8.5))
        screen.blit(Allblack, (0, 0))
        if tick == 210:
            Gamekind = random.randint(0,0)
            Background = "Betting"
    elif tick <= 240:
        Allblack.set_alpha(int((240-tick)*8.5))
        screen.blit(Allblack, (0, 0))

def Anim_RoomCenter8():
    rec= pygame.Rect(WIDTH / 2, HEIGHT / 2, WIDTH / 160 * (60-Anim_Time['AnimRoomCenter8']), HEIGHT / 120 * (60-Anim_Time['AnimRoomCenter8']))
    rec.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (0, 255, 0), rec, int(max(HEIGHT / 60, 1)))

# 按鈕與基礎實體初次配對生成
player = Player(WIDTH/2, HEIGHT/2) 
b049setting = ingameSetting(WIDTH*0.970, HEIGHT*0.04, Asset_dict)
xesc = Xesc(WIDTH*0.970, HEIGHT*0.04, Asset_dict)
b049settingb = ingameSettingSSB(WIDTH*0.2, HEIGHT*0.1, Asset_dict)
roomcenter = roomcenterthing(WIDTH/2, HEIGHT/2)
Allblack = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
Allblack.fill((0, 0, 0))

GameRound = 1
RoomStep = 0
Gamekind = 0
gates_group = pygame.sprite.Group() 
refresh_gates(Pr, Pc, gates_group)

# 遊戲運作主迴圈
running = True
while running:
    
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            mouse_pos = event.pos # 點擊瞬間精準視窗物理像素座標
            
            if Background == "X_Ingame_Settings":
                if xesc.rect.collidepoint(mouse_pos):
                    if len(BackHistory) > 0: del BackHistory[-1]
                    Background = BackHistory[-1] if len(BackHistory) > 0 else "Map"
                if b049settingb.rect.collidepoint(mouse_pos):
                    SS = (SS + 1) % len(SCREEN_SIZE)
                    WIDTH = int(SCREEN_SIZE[SS][1]/getsysscaling())
                    HEIGHT = int(SCREEN_SIZE[SS][2]/getsysscaling())
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    MAPList, Asset_dict, CardImage, EventCardImage = assetsload(WIDTH, HEIGHT) 
                    player = Player(WIDTH/2, HEIGHT/2)
                    b049setting = ingameSetting(WIDTH*0.970, HEIGHT*0.04, Asset_dict)
                    xesc = Xesc(WIDTH*0.970, HEIGHT*0.04, Asset_dict)
                    b049settingb = ingameSettingSSB(WIDTH*0.2, HEIGHT*0.1, Asset_dict)
                    refresh_gates(Pr, Pc, gates_group)
                    
            elif Background == "Map":
                if b049setting.rect.collidepoint(mouse_pos):
                    Background = "X_Ingame_Settings"
                    BackHistory.append("X_Ingame_Settings")
                    
            elif Background == "StartWeapon":
                for rect_obj, weapon in weapon_positions:
                    if rect_obj.collidepoint(mouse_pos):
                        SelectedWeapon = weapon
                        Background = "Map"
                        print("【選單】初始武器已成功解鎖：", SelectedWeapon["name"])
                        break
                        
            elif Background == "Battle":
                if battle_weapon_position is not None:
                    weapon_rect, weapon = battle_weapon_position
                    if weapon_rect.collidepoint(mouse_pos):
                        weapon_attack(weapon["type"])
                        check_enemy_dead()
                for rect_obj, card in card_positions:
                    if rect_obj.collidepoint(mouse_pos):
                        use_item_card(card["type"])
                        check_enemy_dead()
                        if card in PlayerDeck: PlayerDeck.remove(card)
                        break

        # 鍵盤事件監聽
        if event.type == pygame.KEYDOWN:
            if Background == "GameOver" and event.key == pygame.K_p:
                reset_game()
            if event.key == pygame.K_b and Background != "GameOver":
                reset_battle()
                Background = "Battle"
            if event.key == pygame.K_m and Background != "GameOver":
                Background = "Map"
            if Background == "Event" and event.key == pygame.K_y:
                apply_event_card(CurrentEventCard)
                CurrentEventCard = None
                Background = "Map"

            if Background == "Battle" and cheat_mode:
                cheat_keys = {pygame.K_1:1, pygame.K_2:2, pygame.K_3:3, pygame.K_4:4, pygame.K_5:5, pygame.K_6:6}
                if event.key in cheat_keys:
                    dice_value = cheat_keys[event.key]
                    cheat_mode = False
                    battle_message = f"老千成功：骰子變成 {dice_value}"

            if Background == "Battle":
                if (event.key == pygame.K_r or event.key == pygame.K_SPACE) and roll_times > 0 and not dice_rolling:
                    if enemy_hp > 0 and player_hp > 0:
                        dice_rolling = True
                        dice_roll_timer = 15
                        
    keys = pygame.key.get_pressed() 
    if Background == "Map":
        player.update(keys)
        hit_gate = pygame.sprite.spritecollideany(player, gates_group)
        
        if hit_gate and mapused:
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
                MAP[Pr,Pc] = random.randint(2,6) 
            elif RoomStep == 4:
                MAP[Pr,Pc] = 7
            elif RoomStep == 7+GameRound:
                MAP[Pr,Pc] = 8
            elif RoomStep == 8+GameRound:
                MAP[Pr,Pc] = 9
                
            refresh_gates(Pr, Pc, gates_group)
            Anim_Time["Anim_Room"] = 3 * FPS
            
            # 【關鍵修復點】: 先處理房間道具包發放邏輯，再更新 mapused 狀態
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
            
            if MAP[Pr,Pc] != 5:
                mapused = False
                
            roomcenter.update()

    if player.check_trigger(roomcenter) and not mapused: 
        print("玩家碰到交互物品roomcenter")
        roomcenter.touch()

    # 骰子戰鬥運算處理
    if Background == "Battle" and dice_rolling:
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
    
    # 畫布圖層渲染輸出
    if Background == "StartWeapon":
        screen.fill((20, 20, 30))
        draw_text("選擇你的初始武器", int(WIDTH * 0.34), int(HEIGHT * 0.08), font_big)
        weapon_positions = draw_card_row(WeaponChoices, int(HEIGHT * 0.30))
        draw_text("點擊一張武器卡開始遊戲", int(WIDTH * 0.34), int(HEIGHT * 0.82), font_mid)
        
    elif Background == "Map":
        screen.blit(MAPList[int(MAP[Pr,Pc])-1], (0, 0))
        gates_group.draw(screen)
        screen.blit(player.image, player.rect)
        screen.blit(b049setting.image, b049setting.rect)
        if MAP[Pr,Pc] != 1 and not mapused:
            screen.blit(roomcenter.image, roomcenter.rect)
        pygame.draw.circle(screen, (255, 255, 255), (int(WIDTH * 0.41 / 4) , int(HEIGHT * 0.41 / 3)), int(WIDTH * 18 / 240))
        miniMap()
        draw_text(f"道具卡數量：{len(PlayerDeck)}", int(WIDTH * 0.72), int(HEIGHT * 0.03), font_small)
        if SelectedWeapon is not None:
            draw_text(f"武器：{SelectedWeapon['name']}", int(WIDTH * 0.58), int(HEIGHT * 0.08), font_small)
        draw_text(battle_message, int(WIDTH * 0.05), int(HEIGHT * 0.92), font_small)
        
    elif Background == "X_Ingame_Settings":
        screen.blit(Asset_dict["b049settingback"], (0, 0))
        screen.blit(b049settingb.image, b049settingb.rect)
        b049settingb.update(WIDTH,HEIGHT)
        screen.blit(xesc.image, xesc.rect)
        
    elif Background == "Gaming": 
        screen.blit(Asset_dict[f'b049gaming{Gamekind}'], (0, 0))
        if Gamekind == 0:
            screen.blit(Asset_dict[f'b049gaming0-1'], (pygame.mouse.get_pos()[0]-WIDTH/2,max(pygame.mouse.get_pos()[1]-HEIGHT/2,0)))
            
    elif Background == "Betting": 
        screen.blit(Asset_dict[f'b049gaming{Gamekind}'], (0, 0))
        
    elif Background == "Event":
        screen.fill((45, 20, 65))
        draw_text("事件發生", int(WIDTH * 0.40), int(HEIGHT * 0.04), font_big)
        if CurrentEventCard is not None:
            draw_event_card(CurrentEventCard, int(WIDTH * 0.5 - EVENT_CARD_W / 2), int(HEIGHT * 0.18))
        draw_text("按 Y 確認事件效果", int(WIDTH * 0.38), int(HEIGHT * 0.82), font_mid)
        draw_text(battle_message, int(WIDTH * 0.25), int(HEIGHT * 0.90), font_small)
        
    elif Background == "Battle":
        screen.blit(Asset_dict["b118battle_bg"], (0, 0))
        draw_text(f"玩家 HP：{player_hp}", int(WIDTH * 0.06), int(HEIGHT * 0.04), font_mid, (70, 190, 90))
        draw_text(f"敵人 HP：{enemy_hp}/{enemy_max_hp}", int(WIDTH * 0.72), int(HEIGHT * 0.04), font_mid, (220, 60, 60))
        draw_text("攻擊方式：先按 R / 空白鍵擲骰，再點左邊武器卡攻擊怪物", int(WIDTH * 0.20), int(HEIGHT * 0.09), font_small)
        draw_text("擲骰次數歸 0 後，怪物會攻擊 1~20 點；下方道具卡只能使用一次", int(WIDTH * 0.20), int(HEIGHT * 0.13), font_small)
        
        battle_weapon_position = None
        if SelectedWeapon is not None:
            weapon_x, weapon_y = int(WIDTH * 0.03), int(HEIGHT * 0.30)
            draw_text("武器卡", weapon_x, int(weapon_y - HEIGHT * 0.06), font_small)
            draw_card(SelectedWeapon, weapon_x, weapon_y)
            w_rect = pygame.Rect(weapon_x, weapon_y, CARD_W, CARD_H)
            battle_weapon_position = (w_rect, SelectedWeapon)
            
        draw_dice(int(WIDTH * 0.5 - int(HEIGHT * 0.16) / 2), int(HEIGHT * 0.25), int(HEIGHT * 0.16), dice_value)
        draw_text(f"剩餘擲骰：{roll_times}　攻擊加成：+{player_attack_bonus}　手槍雙倍：{gun_double_turns}", int(WIDTH * 0.24), int(HEIGHT * 0.44), font_small)
        
        msg_img = font_mid.render(battle_message, True, (255, 255, 255))
        screen.blit(msg_img, msg_img.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.53))))
        
        BattleItems = PlayerDeck[:6]
        if len(BattleItems) == 0:
            card_positions = []
            draw_text("目前沒有道具卡", int(WIDTH * 0.40), int(HEIGHT * 0.70), font_mid)
        else:
            draw_text("道具卡：使用後會消失", int(WIDTH * 0.40), int(HEIGHT * 0.58), font_small)
            card_positions = draw_card_row(BattleItems, int(HEIGHT * 0.63))
            
    elif Background == "GameOver":
        screen.fill((20, 0, 0))
        draw_text("你被擊敗了！", int(WIDTH * 0.36), int(HEIGHT * 0.32), font_big, (255, 80, 80))
        draw_text("重新遊戲請按 P 鍵", int(WIDTH * 0.32), int(HEIGHT * 0.48), font_mid)
        draw_text("按 P 後會回到遊戲一開始，重新選擇武器", int(WIDTH * 0.27), int(HEIGHT * 0.58), font_small)

    Animation()
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1
    
    for Akey in list(Anim_Time.keys()): 
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()