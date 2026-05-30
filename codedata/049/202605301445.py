import pygame
import numpy as np
import random
import os
import sys
import math

#運行路徑鎖死到py檔同層 By AI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
print(f'目前遊戲的絕對路徑已鎖定在：{os.getcwd()}')

#系統縮放取得 By AI
def getsysscaling():
    if sys.platform == "darwin": # macOS 的系統代號
        try:
            from AppKit import NSScreen
            # 拿到主螢幕的縮放因子（Retina 螢幕通常會回傳 2.0）
            return NSScreen.mainScreen().backingScaleFactor()
        except ImportError:
            # 如果沒有安裝 PyObjC，可以用指令從系統 profile 撈（較慢但保險）
            import subprocess
            cmd = "system_profiler SPDisplaysDataType | grep 'Retina'"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            if "Retina" in result.stdout:
                return 2.0
    if sys.platform == "win32":
        import ctypes
        try:
            # 獲取主顯示器的縮放百分比（例如 125, 150, 200）
            scale_percent = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            return scale_percent / 100.0  # 轉成倍數，例如 1.5 或 2.0
        except Exception:
            # 防呆機制：如果舊版 Windows 不支援，改用 DPI 計算
            hdc = ctypes.windll.user32.GetDC(0)
            # LOGPIXELSX 在 Win32 中代表橫向每英吋像素，預設 96 DPI 是 100%
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) 
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0

#變數初始化
#系統
SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,810),(4,1920,1440),(0,2880,2160)]
SS = 3
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]/getsysscaling()), int(SCREEN_SIZE[SS][2]/getsysscaling())
FPS = 60
Pr,Pc = 11,11
PlayerV = 5.0
Background = "StartWeapon" #這個是到時候切背景可以改的東東
Global_Time = 0 #系統級時間碼，暫停的時候會暫停
Anim_Time = {} #各動畫時間碼專用辭典
BackHistory = [] #紀錄頁面類型跳轉歷史，方便esc返回
MAPListName = ["無","出生點","小寶箱","闖關區","大寶箱","交易所","零和遊戲","菁英怪","整備區","Boss"]
coin = 30
now_coin = coin
#卡牌
PlayerDeck = []
UsedRooms = set()
ItemCardPool = [{"name": "腦袋尖尖的", "type": "brain"},{"name": "小草", "type": "grass"},{"name": "戰術翻滾", "type": "roll"},{"name": "菜菜撈撈", "type": "nana"},{"name": "心靈課程名單", "type": "mind"},{"name": "老千的技術", "type": "cheat"},{"name": "你從桃園到新竹", "type": "taoyuan"}]
WeaponChoices = [{"name": "傑里科941半自動手槍", "type": "gun"},{"name": "鞭子", "type": "whip"},{"name": "巨槌瑞斯", "type": "darius"}]
EventCardPool = [{"name": "橙汁汙中山羨恭喜", "type": "monster_double_attack"},{"name": "3cm 感謝祭", "type": "seal_monster_once"},{"name": "我一步都沒有退ㄟ", "type": "boss_no_immunity"},{"name": "我中了兩槍", "type": "dice_becomes_three"},{"name": "寵物溝通師", "type": "enemyx2_player/2"},{"name": "芒果醬", "type": "mango_bonus"},{"name": "武術大師晨晨", "type": "next_battle_cc"},{"name": "幹你敢不敢啦", "type": "player_hp_one"},{"name": "雷霆測資", "type": "all_is_fibo"}]
SelectedWeapon = None
CurrentEventCard = None
card_positions = []
weapon_positions = []
battle_weapon_position = None
#戰鬥
player_hp = 30
enemy_hp = 40
enemy_max_hp = 40

dice_value = [1,1,1,1,1]
selected_die_index = 0
dice_rolling = False
dice_roll_timer = 0
roll_times = 8

battle_message = ""

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
next_battle_cc = False
#地圖生成
MAP = np.zeros((23,23),dtype=int)
MAP[11,11] = 1
MAP[10,11] = 2
MAP[12,11] = 2
MAP[11,12] = 2
MAP[11,10] = 2
BackHistory.append("Map")
mapused = True

#主程式
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('骰子迷因大亂鬥')
clock = pygame.time.Clock()

#圖檔載入
def assetsload(WIDTH,HEIGHT):
    '''圖檔尺寸、載入刷新'''
    global MAPList
    MAPList = [] #地圖類型背景庫
    for i in range(1,10): #共1~9種房間的底圖
        MAPList.append(pygame.transform.scale(pygame.image.load(os.path.join("assets", f'map{str(i)}.png')).convert(), (WIDTH, HEIGHT)))
    global Asset_dict
    global CardImage
    global EventCardImage
    Asset_dict = {
        "b049anim_room1":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049anim_room1.png")).convert_alpha(), (int(WIDTH / 5 * 2), int(WIDTH / 25 * 2))),
        "b049setting":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049setting.png")).convert_alpha(), (int(WIDTH / 20), int(WIDTH / 20))),
        "xesc":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","xesc.png")).convert_alpha(), (int(WIDTH / 20), int(WIDTH / 20))),
        "b049settingback":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","b049settingback.png")).convert_alpha(), (WIDTH, HEIGHT)),
        "b049settingb":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049settingb.png")).convert_alpha(), (int(WIDTH / 5 * 1.5), int(WIDTH / 25 * 1.5))),
        "b049roomcenter8":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049roomcenter8.png")).convert_alpha(), (int(WIDTH / 8), int(WIDTH / 8))),
        "b049roomcenter7":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Enemy","Golem.png")).convert_alpha(), (int(WIDTH / 3), int(HEIGHT / 4))),
        "b049roomcenter9":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Enemy","level1 boss.png")).convert_alpha(), (int(WIDTH / 3), int(WIDTH / 3))),
        "b049roomcload3-1":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049roomcload3-1.png")).convert_alpha(), (int(WIDTH / 3), int(HEIGHT / 3))),
        "b049roomcload3-2":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049roomcload3-2.png")).convert_alpha(), (int(WIDTH), int(HEIGHT))),
        "b049gaming0-1":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049gaming0-1.png")).convert_alpha(), (int(WIDTH), int(HEIGHT))),
        "b049gaming0-21":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049gaming0-2.png")).convert_alpha(), (int(WIDTH/5), int(WIDTH/5))),
        "b049gaming0-22":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049gaming0-2.png")).convert_alpha(), (int(WIDTH/20), int(WIDTH/20))),
        "b049gaming0-23":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049gaming0-2.png")).convert_alpha(), (int(WIDTH/50), int(WIDTH/50))),
        "b118battle_bg":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","battleback2nog.jpeg")).convert_alpha(),(WIDTH,HEIGHT)),
        "b049bettingb":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","b049bettingb.jpeg")).convert_alpha(), (int(WIDTH), int(HEIGHT))),
        "b049bettingr":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049bettingr.png")).convert_alpha(), (int(WIDTH/3), int(WIDTH/3))),
        "b049gamingmvp":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","b049gamingmvp.jpeg")).convert_alpha(), (WIDTH, HEIGHT)),
        "b049bettingbe":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","b049bettingbe.jpeg")).convert_alpha(), (WIDTH, HEIGHT)),
        "choose_weapon_back":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","choose_weapon_back.png")).convert_alpha(), (WIDTH, HEIGHT))
    }
    for i in range(1,7):
        Asset_dict[f'b049roomcenter{i}'] = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict",f'b049roomcenter{i}.png')).convert_alpha(), (int(WIDTH / 8), int(WIDTH / 8)))
    for j in range(0,2):
        Asset_dict[f'b049gaming{j}'] = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background",f'b049gaming{j}.png')).convert_alpha(), (WIDTH, HEIGHT))
    for k in range(0,6):
        Asset_dict[f'b049coin{k}'] = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict",f'b049coin{k}.png')).convert_alpha(), (int(WIDTH/6),int(WIDTH/6)))
    for l in range(1,4):
        Asset_dict[f'b049Q{l}'] = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict",f'b049Q{l}.png')).convert_alpha(), (int(WIDTH/3*0.8),int(WIDTH/4*0.8)))
    global CARD_H
    global CARD_W
    global EVENT_CARD_H
    global EVENT_CARD_W
    CARD_W = int(WIDTH * 0.15)
    CARD_H = int(HEIGHT * 0.33)
    EVENT_CARD_W = int(WIDTH * 0.25)
    EVENT_CARD_H = int(HEIGHT * 0.55)
    CardImage = {
        "腦袋尖尖的": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242953.png")).convert_alpha(), (CARD_W, CARD_H)),
        "小草": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242954.png")).convert_alpha(), (CARD_W, CARD_H)),
        "戰術翻滾": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242955.png")).convert_alpha(), (CARD_W, CARD_H)),
        "菜菜撈撈": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242956.png")).convert_alpha(), (CARD_W, CARD_H)),
        "心靈課程名單": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242957.png")).convert_alpha(), (CARD_W, CARD_H)),
        "老千的技術": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242958.png")).convert_alpha(), (CARD_W, CARD_H)),
        "你從桃園到新竹": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242959.png")).convert_alpha(), (CARD_W, CARD_H)),
        
        "橙汁汙中山羨恭喜": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242960.png")).convert_alpha(), (CARD_W, CARD_H)),
        "3cm 感謝祭": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242961.png")).convert_alpha(), (CARD_W, CARD_H)),
        "我一步都沒有退ㄟ": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242962.png")).convert_alpha(), (CARD_W, CARD_H)),
        "我中了兩槍": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242964.png")).convert_alpha(), (CARD_W, CARD_H)),
        "寵物溝通師": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242965.png")).convert_alpha(), (CARD_W, CARD_H)),
        "芒果醬": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242966.png")).convert_alpha(), (CARD_W, CARD_H)),
        "武術大師晨晨": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242967.png")).convert_alpha(), (CARD_W, CARD_H)),
        "幹你敢不敢啦": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242968.png")).convert_alpha(), (CARD_W, CARD_H)),
        "雷霆測資": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242973.png")).convert_alpha(), (CARD_W, CARD_H)),

        "傑里科941半自動手槍": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242970.png")).convert_alpha(), (CARD_W, CARD_H)),
        "鞭子": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242971.png")).convert_alpha(), (CARD_W, CARD_H)),
        "巨槌瑞斯": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242972.png")).convert_alpha(), (CARD_W, CARD_H))
    }
    EventCardImage = {
        "腦袋尖尖的": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242953.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "小草": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242954.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "戰術翻滾": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242955.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "菜菜撈撈": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242956.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "心靈課程名單": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242957.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "老千的技術": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242958.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "你從桃園到新竹": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242959.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        
        "橙汁汙中山羨恭喜": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242960.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "3cm 感謝祭": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242961.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "我一步都沒有退ㄟ": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242962.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "我中了兩槍": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242964.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "寵物溝通師": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242965.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "芒果醬": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242966.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "武術大師晨晨": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242967.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "幹你敢不敢啦": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242968.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "雷霆測資": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242973.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),

        "傑里科941半自動手槍": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242970.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "鞭子": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242971.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H)),
        "巨槌瑞斯": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242972.png")).convert_alpha(), (EVENT_CARD_W, EVENT_CARD_H))
    }
    return MAPList, Asset_dict, CardImage, EventCardImage

MAPList, Asset_dict, CardImage, EventCardImage = assetsload(WIDTH,HEIGHT)
choose_weapon_back = Asset_dict["choose_weapon_back"]

#字體載入
FHeadPath = os.path.join("assets","font","NotoSansTC-Bold.ttf") #粗字
FTextPath = os.path.join("assets","font","NotoSansTC-Light.ttf") #細字
font_big = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), 52)
font_mid = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), 34)
font_small = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), 24)

#Class區域
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1.0):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join("assets","player.png")).convert_alpha()
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
    
    def check_trigger(self, target):
        """檢查自己是否碰觸到目標物件（例如 roomcenter）"""
        # 使用 Pygame 內建的矩形碰撞偵測
        if pygame.sprite.collide_rect(self, target):
            return True
        else:
            return False

class Gate(pygame.sprite.Sprite):
    def __init__(self, GateType):
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","gate.png")).convert_alpha(), (int(WIDTH / 12), int(HEIGHT / 9)))
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

class ingameSetting(pygame.sprite.Sprite): #按鈕可以拿這個當模板用
    def __init__(self, x, y):
        super().__init__()
        self.image = Asset_dict['b049setting']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)

class Xesc(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = Asset_dict['xesc']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)

class ingameSettingSSB(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = Asset_dict['b049settingb']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (x, y)
    def update(self, W, H):
        FHead = pygame.font.Font(FHeadPath, int(H/25))
        Head = FHead.render(f'{int(W*getsysscaling())} x {int(H*getsysscaling())}', True, (255, 255, 255))
        trec = Head.get_rect()
        trec.centerx = self.rect.centerx
        trec.centery = self.rect.centery - 0.006 * HEIGHT
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
        self.image = Asset_dict[f'b049roomcenter{MAP[Pr,Pc]}']
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2,HEIGHT/2)
    def touch(self):
        global mapused
        global Anim_Time
        global Background
        global attackted
        if MAP[Pr,Pc] == 2 or MAP[Pr,Pc] == 4:
            mapused = True
            Anim_Time['AnimRoomCenter2'] = 1 * FPS
            get_random_item_card()
            if MAP[Pr,Pc] == 4:
                get_random_item_card()
        if MAP[Pr,Pc] == 3:
            mapused = True
            Anim_Time['AnimRoomCenter3'] = 4 * FPS
        if MAP[Pr,Pc] == 6:
            mapused = True
            Anim_Time['AnimRoomCenter6'] = 4 * FPS
        if MAP[Pr,Pc] == 7:
            mapused = True
            reset_battle()
            Background = "Battle"
            attackted = False
        if MAP[Pr,Pc] == 8:
            mapused = True
            Anim_Time['AnimRoomCenter8'] = 1 * FPS
        if MAP[Pr,Pc] == 9:
            mapused = True
            reset_battle()
            Background = "Battle"
            attackted = False

#Def區域
def refresh_gates(i, j, gates_group):
    """地下城四個方向傳送門刷新"""
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
    """小地圖刷新"""
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
    imgr = img.get_rect()
    imgr.center = (x,y)
    screen.blit(img, imgr)

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
    global mango_bonus, next_battle_cc

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

    elif event_type == "enemyx2_player/2":
        enemy_hp_multiplier = 2
        player_attack_half = True
        battle_message = "事件：下場戰鬥敵方血量 x2，玩家攻擊減半"

    elif event_type == "mango_bonus":
        mango_bonus = True
        battle_message = "事件：芒果醬啟動，攻擊獲得額外加成"

    elif event_type == "next_battle_cc":
        next_battle_cc = True
        battle_message = "事件：下一場戰鬥生成武術大師晨晨"

    elif event_type == "player_hp_one":
        player_hp = 1
        battle_message = "事件：生命值變成 1 點"

    elif event_type == "all_is_fibo":
        player_hp = 100 #這裡要改
        battle_message = "事件：下次擲骰必定全為費式數列"

def evaluate_dice_pattern(dice):
    #回傳骰型、倍率
    counts = [dice.count(i) for i in range(1, 7)]
    unique_vals = sorted(list(set(dice)))
    if 5 in counts:
        return "五條 (傷害 x3.0)", 3.0
    elif 4 in counts:
        return "鐵支 (傷害 x2.0)", 2.0
    elif 3 in counts and 2 in counts:
        return "葫蘆 (傷害 x1.5)", 1.5
    elif len(unique_vals) == 5 and (unique_vals[-1] - unique_vals[0] == 4):
        return "順子 (傷害 x2.5)", 2.5
    elif 3 in counts:
        return "三條 (傷害 x1.2)", 1.2
    elif counts.count(2) == 2:
        return "兩對 (傷害 x1.1)", 1.1
    elif 2 in counts:
        return "一對", 1.0
    else:
        return "高牌", 1.0

def basic_damage():
    kind, multiplier = evaluate_dice_pattern(dice_values)
    base_damage = sum(dice_values) + player_attack_bonus
    damage = int(base_damage * multiplier)

    if mango_bonus:
        damage += int(damage * 0.3)

    if player_attack_half:
        damage = max(damage // 2, 1)

    return damage


def weapon_attack(card_type):
    global enemy_hp, battle_message, gun_double_turns, attackted

    if enemy_hp <= 0 or player_hp <= 0:
        return

    # 如果已經攻擊過，直接攔截不執行傷害
    if attackted:
        battle_message = "本回合已使用過武器攻擊！請重新擲骰"
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
        attackted = True

    elif card_type == "whip":
        if enemy_color == (0, 0, 0):
            damage *= 2
            enemy_hp -= damage
            battle_message = f"鞭子攻擊！黑色敵人雙倍傷害，造成 {damage}"
        else:
            enemy_hp -= damage
            battle_message = f"鞭子攻擊！造成 {damage} 傷害"
        attackted = True

    elif card_type == "darius":
        if 3 in dice_values:
            if MAP[Pr, Pc] == 9:
                hook_damage = max(int(enemy_hp * 0.2), 1)
                enemy_hp -= (hook_damage + damage)
                battle_message = f"巨槌瑞斯鉤中 Boss！造成 {hook_damage} 傷害"
            else:
                hook_damage = max(enemy_hp // 2, 1)
                enemy_hp -= (hook_damage + damage)
                battle_message = f"巨槌瑞斯鉤中！造成敵人一半血量 {hook_damage}"
        else:
            enemy_hp -= damage
            battle_message = f"巨槌瑞斯普通攻擊，造成 {damage} 傷害"
        attackted = True

def use_item_card(card_type):
    global player_hp, enemy_hp
    global battle_message, dice_values
    global player_attack_bonus
    global cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage
    global dice_rolling, dice_roll_timer
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
    global dice_values, dice_rolling, dice_roll_timer, battle_message
    global roll_times, player_attack_bonus, gun_double_turns
    global cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage
    global enemy_hp_multiplier, player_attack_half
    global next_dice_fixed_three
    global attackted
    global selected_die_index

    if MAP[Pr, Pc] == 9:
        enemy_max_hp = 80
    else:
        enemy_max_hp = 40

    enemy_max_hp *= enemy_hp_multiplier
    enemy_hp = enemy_max_hp
    dice_values = [random.randint(1, 6) for _ in range(5)]
    selected_die_index = 0

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
        dice_values = [3, 3, 3, 3, 3]
        next_dice_fixed_three = False
        attackted = False  #  3 點，直接攻擊
        battle_message = "事件效果：這場戰鬥骰子先變成 3"
    else:
        attackted = False   # 進入戰鬥還沒擲骰，鎖定攻擊
        battle_message = "先按 R / 空白鍵擲骰，再點左邊武器卡攻擊怪物"


def reset_game():
    global Pr, Pc, Background, Global_Time, Anim_Time
    global PlayerDeck, UsedRooms, SelectedWeapon, CurrentEventCard
    global card_positions, weapon_positions, battle_weapon_position
    global player_hp, enemy_hp, enemy_max_hp
    global dice_values, dice_rolling, dice_roll_timer, roll_times, battle_message
    global player_attack_bonus, gun_double_turns, cheat_mode, roll_immunity, hit_count
    global stored_damage_turns, stored_damage
    global enemy_double_attack_times, seal_monster_once, boss_no_immunity
    global next_dice_fixed_three, enemy_hp_multiplier, player_attack_half
    global mango_bonus, next_battle_cc
    global MAP, player, GameRound, RoomStep, gates_group, attackted
    global selected_die_index

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

    dice_values = [random.randint(1, 6) for _ in range(5)]
    selected_die_index = 0
    dice_rolling = False
    dice_roll_timer = 0
    roll_times = 8

    battle_message = "按空白鍵重新擲骰"

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
    next_battle_cc = False
    attackted = True

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

def distance(x1,y1,x2,y2):
    cal = ((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))*0.5
    return cal

def Animation():
    """動畫執行與呼叫"""
    if 'Anim_Room' in Anim_Time and Anim_Time.get('Anim_Room') > 0:
        Anim_Room()
    if 'AnimRoomCenter2' in Anim_Time and Anim_Time.get('AnimRoomCenter2') > 0:
        Anim_RoomCenter2()
    if 'AnimRoomCenter3' in Anim_Time and Anim_Time.get('AnimRoomCenter3') > 0:
        Anim_RoomCenter3()
    if 'AnimRoomCenter6' in Anim_Time and Anim_Time.get('AnimRoomCenter6') > 0:
        Anim_RoomCenter6()
    if 'AnimRoomCenter8' in Anim_Time and Anim_Time.get('AnimRoomCenter8') > 0:
        Anim_RoomCenter8()
    if 'AnimGameMVP' in Anim_Time and Anim_Time.get('AnimGameMVP') > 0:
        Anim_GameMVP()
    if 'AnimGameFire' in Anim_Time and Anim_Time.get('AnimGameFire') > 0:
        Anim_GameFire()

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
    trec.centerx = rec.centerx
    trec.centery = rec.centery - 0.006 * HEIGHT
    screen.blit(Head, trec)

def Anim_RoomCenter2():
    rec= pygame.Rect(WIDTH / 2, HEIGHT / 2, WIDTH / 160 * (60-Anim_Time['AnimRoomCenter2']), HEIGHT / 120 * (60-Anim_Time['AnimRoomCenter2']))
    rec.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (255, 215, 0), rec, int(max(HEIGHT / 60, 1)))

def Anim_RoomCenter3():
    global Allblack
    global Background
    global Gamekind, IntQ
    global GameTimer,Global_Time
    global coin,now_coin
    tick = 240 - Anim_Time['AnimRoomCenter3']
    adx = WIDTH * 0.3
    bdx = WIDTH * 0.7
    cdy = -0.00001 * HEIGHT * (tick - 120) * (tick - 120) * (tick - 120) + HEIGHT / 2
    recimg = Asset_dict["b049roomcload3-2"]
    gun = Asset_dict["b049roomcload3-1"]
    cube = Asset_dict["b049roomcenter3"]
    recg = gun.get_rect()
    recc = cube.get_rect()
    recg.centerx = adx
    recg.centery = cdy
    recc.centerx = bdx
    recc.centery = cdy
    if tick <= 30:
        Allblack.set_alpha(tick*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 30:
            Background = "Loading"
    elif tick <= 60:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha((60-tick)*8.5)
        screen.blit(Allblack, (0, 0))
    elif tick <= 180:
        screen.blit(recimg, (0,0))
        screen.blit(gun, recg)
        screen.blit(cube, recc)
    elif tick <= 210:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha((tick-180)*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 210:
            Gamekind = random.randint(0,1)
            if Gamekind == 0:
                GameTimer = Global_Time + FPS * 10
            elif Gamekind == 1:
                IntQ = random.randint(1,3)
                GameTimer = Global_Time + FPS * 60
            Background = "Gaming"
    elif tick <= 240:
        Allblack.set_alpha((240-tick)*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 239:
            now_coin = coin
            GameTimer = Global_Time + FPS * 10

def Anim_RoomCenter6():
    global Allblack
    global Background
    global Gamekind
    tick = 240 - Anim_Time['AnimRoomCenter6']
    rdx = WIDTH * (1-(tick-60)/120)
    rdy = HEIGHT * (-(tick-60)/300)
    recimg = Asset_dict["b049bettingb"]
    br = Asset_dict["b049bettingr"]
    if tick <= 30:
        Allblack.set_alpha(tick*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 30:
            Background = "Loading"
    elif tick <= 60:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha((60-tick)*8.5)
        screen.blit(Allblack, (0, 0))
    elif tick <= 180:
        screen.blit(recimg, (0,0))
        rbr = pygame.transform.rotate(pygame.transform.scale(br,(WIDTH * tick / 120,WIDTH * tick / 120)), tick*5)
        recr = rbr.get_rect()
        recr.center = (rdx,rdy)
        screen.blit(rbr, recr)
    elif tick <= 210:
        screen.blit(recimg, (0,0))
        Allblack.set_alpha((tick-180)*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 210:
            Background = "Betting"
    elif tick <= 240:
        Allblack.set_alpha((240-tick)*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 239:
            get_random_event_card()
            Background = "Event"

def Anim_RoomCenter8():
    rec= pygame.Rect(WIDTH / 2, HEIGHT / 2, WIDTH / 160 * (60-Anim_Time['AnimRoomCenter8']), HEIGHT / 120 * (60-Anim_Time['AnimRoomCenter8']))
    rec.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (0, 255, 0), rec, int(max(HEIGHT / 60, 1)))

def Anim_GameMVP(): #黑幕轉場可以拿這個當樣板
    global Allblack
    global Background
    global coin,now_coin
    tick = 60 - Anim_Time['AnimGameMVP']
    if tick <= 30:
        Allblack.set_alpha(tick*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 30:
            Background = "GameMVP"
    elif tick <= 60:
        Allblack.set_alpha((60-tick)*8.5)
        screen.blit(Allblack, (0, 0))

def Anim_GameFire():
    rec= pygame.Rect(WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT)
    rec.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (255, 0, 0), rec, int(max(HEIGHT / 70, 1)))

#開始運作
player = Player(WIDTH/2,HEIGHT/2) #玩家生成
b049setting = ingameSetting(WIDTH*0.970,HEIGHT*0.04)
xesc = Xesc(WIDTH*0.970,HEIGHT*0.04)
b049settingb = ingameSettingSSB(WIDTH*0.2,HEIGHT*0.1)
roomcenter = roomcenterthing(WIDTH/2,HEIGHT/2)
Allblack = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
Allblack.fill((0, 0, 0))
GameRound = 1
RoomStep = 0
Gamekind = 0
gates_group = pygame.sprite.Group() #門元件生成
refresh_gates(Pr, Pc, gates_group)
running = True
while running:
    for event in pygame.event.get(): #事件區
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: #滑鼠點擊判定區
            if event.button == 1:
                mouse_pos = event.pos
                mouse_x, mouse_y = mouse_pos
                if Background == "X_Ingame_Settings":
                    if xesc.rect.collidepoint(mouse_pos):
                        print("xesc")
                        del BackHistory[-1]
                        Background = BackHistory[-1]
                        print(BackHistory)
                    if b049settingb.rect.collidepoint(mouse_pos):
                        print("size change")
                        SS = SCREEN_SIZE[SS][0]
                        WIDTH = int(SCREEN_SIZE[SS][1]/getsysscaling())
                        HEIGHT = int(SCREEN_SIZE[SS][2]/getsysscaling())
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        MAPList, Asset_dict, CardImage, EventCardImage = assetsload(WIDTH,HEIGHT)
                        # class重新縮放
                        player = Player(WIDTH/2,HEIGHT/2)
                        b049setting = ingameSetting(WIDTH*0.970,HEIGHT*0.04)
                        xesc = Xesc(WIDTH*0.970,HEIGHT*0.04)
                        b049settingb = ingameSettingSSB(WIDTH*0.2,HEIGHT*0.1)
                        refresh_gates(Pr, Pc, gates_group)
                elif Background == "Map":
                    if b049setting.rect.collidepoint(mouse_pos):
                        print("Settings")
                        Background = "X_Ingame_Settings"
                        BackHistory.append("X_Ingame_Settings")
                elif Background == "StartWeapon":
                    for rect in weapon_positions:
                        x, y, w, h, weapon = rect
                        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                            SelectedWeapon = weapon
                            Background = "Map"
                            print("選擇武器：", SelectedWeapon["name"])
                elif Background == "Battle":
                    dice_size = int(HEIGHT * 0.12)
                    dice_gap = int(WIDTH * 0.02)
                    total_dice_width = (dice_size * 5) + (dice_gap * 4)
                    start_x = int(WIDTH * 0.5 - total_dice_width / 2)
                    dice_y = int(HEIGHT * 0.25)
                
                    for i in range(5):
                        rect_x = start_x + i * (dice_size + dice_gap)
                        if rect_x <= mouse_x <= rect_x + dice_size and dice_y <= mouse_y <= dice_y + dice_size:
                            selected_die_index = i
                            print(f"系統判定：成功點擊並選取了第 {i+1} 顆骰子！")
                            break
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
                elif Background == "Gaming":
                    if Gamekind == 0:
                        if distance(mouse_x, mouse_y,g0x1,g0y1) < WIDTH * 1.086:
                            coin += 1
                        elif distance(mouse_x, mouse_y,g0x2,g0y2) < WIDTH / 8:
                            coin += int(WIDTH / 8 / (WIDTH / 8 - distance(mouse_x, mouse_y,g0x2,g0y2)))
                        elif distance(mouse_x, mouse_y,g0x3,g0y3) < WIDTH / 305:
                            coin += int(WIDTH / 305 / (WIDTH / 305 - distance(mouse_x, mouse_y,g0x3,g0y3)))
                        print(coin)
                        Anim_Time["AnimGameFire"] = int(FPS / 5)
                    elif Gamekind == 1:
                        if mouse_x < WIDTH/3:
                            print('A')
                        elif mouse_x > WIDTH *2/3:
                            print('C')
                        else:
                            print('B')
                elif Background == "GameMVP":
                    Background = "Map"

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
                attackted = False

            # 按 M 回地圖
            if event.key == pygame.K_m and Background != "GameOver":
                Background = "Map"
                attackted = False

            # 事件一定要接受，只能按 Y
            if Background == "Event":
                if event.key == pygame.K_y:
                    apply_event_card(CurrentEventCard)
                    CurrentEventCard = None
                    Background = "Map"

            if Background == "Battle" and cheat_mode:
                if event.key == pygame.K_1:
                    dice_values[selected_die_index] = 1
                    cheat_mode = False
                    attackted = False  
                    battle_message = f"老千成功：第 {selected_die_index + 1} 顆骰子變成 1"
                elif event.key == pygame.K_2:
                    dice_values[selected_die_index] = 2
                    cheat_mode = False
                    attackted = False
                    battle_message = f"老千成功：第 {selected_die_index + 1} 顆骰子變成 2"
                elif event.key == pygame.K_3:
                    dice_values[selected_die_index] = 3
                    cheat_mode = False
                    attackted = False
                    battle_message = f"老千成功：第 {selected_die_index + 1} 顆骰子變成 3"
                elif event.key == pygame.K_4:
                    dice_values[selected_die_index] = 4
                    cheat_mode = False
                    attackted = False
                    battle_message = f"老千成功：第 {selected_die_index + 1} 顆骰子變成 4"
                elif event.key == pygame.K_5:
                    dice_values[selected_die_index] = 5
                    cheat_mode = False
                    attackted = False
                    battle_message = f"老千成功：第 {selected_die_index + 1} 顆骰子變成 5"
                elif event.key == pygame.K_6:
                    dice_values[selected_die_index] = 6
                    cheat_mode = False
                    attackted = False
                    battle_message = f"老千成功：第 {selected_die_index + 1} 顆骰子變成 6"

            if Background == "Battle":
                if (event.key == pygame.K_SPACE) and roll_times > 0:
                    if enemy_hp > 0 and player_hp > 0 :
                        if not dice_rolling:
                            dice_rolling = True
                            dice_roll_timer = 15
                        
    keys = pygame.key.get_pressed() #按鍵區
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
                MAP[Pr,Pc] = random.randint(2,6) #傳送瞬間去改 Numpy 陣列，隨機判定房間類型，這裡不處理精英怪、整備、Boss，這幾個交給RoomStep處理 (初始值2,6)
            elif RoomStep == 4:
                MAP[Pr,Pc] = 7
            elif RoomStep == 7+GameRound:
                MAP[Pr,Pc] = 8
            elif RoomStep == 8+GameRound:
                MAP[Pr,Pc] = 9
            refresh_gates(Pr, Pc, gates_group)
            Anim_Time["Anim_Room"] = 3 * FPS
            if MAP[Pr,Pc] != 5:
                mapused = False
            roomcenter.update()

    if player.check_trigger(roomcenter) and not mapused and Background == "Map": #碰撞區
        print("玩家碰到交互物品roomcenter")
        roomcenter.touch()

    #骰子戰鬥邏輯
    if Background == "Battle":
        if dice_rolling:
        # 只重骰被「選中」的那顆骰子，不影響陣列長度與其他骰子
            dice_values[selected_die_index] = random.randint(1, 6)
            dice_roll_timer -= 1

            if dice_roll_timer <= 0:
                dice_rolling = False
                roll_times -= 1
                total_pts = sum(dice_values)

                if roll_times > 0:
                        battle_message = f"重骰第 {selected_die_index + 1} 顆。點數: {dice_values} (共{total_pts}點)，剩 {roll_times} 次"
                        attackted = False
                else:
                        battle_message = f"點數為 {dice_values}，次數歸 0，換怪物攻擊"
                        monster_attack()
                        attackted = True
    
    #顯示區
    if Background == "StartWeapon":
        screen.blit(choose_weapon_back, (0,0))
        Allblack.set_alpha(100)
        screen.blit(Allblack, (0, 0))
        draw_text(
            "選擇你的初始武器",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.08),
            font_big,
            (255, 255, 255)
        )
        weapon_positions = draw_card_row(WeaponChoices, int(HEIGHT * 0.30))
        draw_text(
            "點擊一張武器卡開始遊戲",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.82),
            font_mid,
            (255, 255, 255)
        )
    elif Background == "Map":
        screen.blit(MAPList[int(MAP[Pr,Pc])-1], (0, 0))
        gates_group.draw(screen)
        screen.blit(player.image, player.rect)
        screen.blit(b049setting.image, b049setting.rect)
        if MAP[Pr,Pc] != 1 and not mapused:
            screen.blit(roomcenter.image, roomcenter.rect)
        #小地圖
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH * 0.41 / 4 , HEIGHT * 0.41 / 3),WIDTH / 12)
        miniMap()
        #道具卡
        draw_text(
            f"道具卡數量：{len(PlayerDeck)}",
            int(WIDTH * 0.7),
            int(HEIGHT * 0.03),
            font_small,
            (255, 255, 255)
        )

        if SelectedWeapon is not None:
            draw_text(
                f"武器：{SelectedWeapon['name']}",
                int(WIDTH * 0.7),
                int(HEIGHT * 0.08),
                font_small,
                (255, 255, 255))

        draw_text(
            battle_message,
            int(WIDTH * 0.5),
            int(HEIGHT * 0.92),
            font_small,
            (255, 255, 255))
    elif Background == "X_Ingame_Settings":
        screen.blit(Asset_dict["b049settingback"], (0, 0))
        screen.blit(b049settingb.image, b049settingb.rect)
        b049settingb.update(WIDTH,HEIGHT)
        screen.blit(xesc.image, xesc.rect)
    elif Background == "Gaming":
        screen.blit(Asset_dict[f'b049gaming{Gamekind}'], (0, 0))
        if Gamekind == 0:
            g0x3,g0y3 = WIDTH/2+WIDTH*0.03*math.cos(Global_Time/FPS*5),0.6*HEIGHT
            g0x2,g0y2 = WIDTH/2-WIDTH*0.10*math.sin(Global_Time/FPS*3),0.6*HEIGHT
            g0x1,g0y1 = WIDTH/2+WIDTH*0.25*math.sin(Global_Time/FPS),0.6*HEIGHT
            g0r3 = Asset_dict[f'b049gaming0-23'].get_rect()
            g0r2 = Asset_dict[f'b049gaming0-22'].get_rect()
            g0r1 = Asset_dict[f'b049gaming0-21'].get_rect()
            g0r3.center = (g0x3,g0y3)
            g0r2.center = (g0x2,g0y2)
            g0r1.center = (g0x1,g0y1)
            screen.blit(Asset_dict[f'b049gaming0-23'], g0r3)
            screen.blit(Asset_dict[f'b049gaming0-22'], g0r2)
            screen.blit(Asset_dict[f'b049gaming0-21'], g0r1)
            screen.blit(Asset_dict[f'b049gaming0-1'], (pygame.mouse.get_pos()[0]-WIDTH/2,max(pygame.mouse.get_pos()[1]-HEIGHT/2,0)))
            draw_text(f'{(GameTimer-Global_Time)/FPS:.2f}',int(WIDTH * 0.5),int(HEIGHT * 0.05),font_mid,(255, 255, 255))
            draw_text(f'{coin-now_coin}',int(WIDTH * 0.5),int(HEIGHT * 0.95),font_mid,(255, 255, 255))
            if GameTimer-Global_Time < 0 and Anim_Time.get("AnimGameMVP",0) == 0:
                            Anim_Time["AnimGameMVP"] = FPS * 1
        elif Gamekind == 1:
            g1p = Asset_dict[f'b049Q{IntQ}']
            g1r = g1p.get_rect()
            g1r.center = (WIDTH/2,HEIGHT*0.45)
            screen.blit(g1p,g1r)
            if IntQ == 1:
                draw_text('1/3',int(WIDTH*0.25),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('2/3',int(WIDTH*0.5),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('4/3',int(WIDTH*0.75),int(HEIGHT*0.7),font_small,(0,0,0))
                IntAns = 2
            elif IntQ == 2:
                draw_text('pi',int(WIDTH*0.25),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('pi/2',int(WIDTH*0.5),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('pi/3',int(WIDTH*0.75),int(HEIGHT*0.7),font_small,(0,0,0))
                IntAns = 1
            elif IntQ == 3:
                draw_text('e-1',int(WIDTH*0.25),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('(1-e)/2',int(WIDTH*0.5),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('(1-e)/3',int(WIDTH*0.75),int(HEIGHT*0.7),font_small,(0,0,0))
                IntAns = 3
                
    elif Background == "GameMVP":
        screen.blit(Asset_dict["b049gamingmvp"], (0, 0))
        gmvp = Asset_dict[f'b049coin{(Global_Time%120)//20}'].get_rect()
        gmvp.center = (WIDTH/2,HEIGHT/2)
        screen.blit(Asset_dict[f'b049coin{(Global_Time%120)//20}'],gmvp)
        draw_text(f'{coin-now_coin}',int(WIDTH * 0.5),int(HEIGHT * 0.77),font_big,(255, 255, 255))
    elif Background == "Betting":
        screen.blit(Asset_dict["b049bettingbe"], (0, 0))
    elif Background == "Event":
        screen.blit(Asset_dict["b049bettingbe"], (0, 0))
        draw_text(
            "事件發生",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.1),
            font_big,
            (255, 255, 255))
        if CurrentEventCard is not None:
            event_x = int(WIDTH * 0.5 - EVENT_CARD_W / 2)
            event_y = int(HEIGHT * 0.18)
            draw_event_card(CurrentEventCard, event_x, event_y)
        draw_text(
            "按 Y 確認事件效果",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.82),
            font_mid,
            (255, 255, 255))
        draw_text(
            battle_message,
            int(WIDTH * 0.5),
            int(HEIGHT * 0.90),
            font_small,
            (255, 255, 255))
    elif Background == "Battle":
        screen.blit(Asset_dict["b118battle_bg"], (0, 0))
        draw_text(
            f"玩家 HP：{player_hp}",
            int(WIDTH * 0.12),
            int(HEIGHT * 0.04),
            font_mid,
            (70, 190, 90))
        draw_text(
            f"敵人 HP：{enemy_hp}/{enemy_max_hp}",
            int(WIDTH * 0.88),
            int(HEIGHT * 0.04),
            font_mid,
            (220, 60, 60))
        draw_text(
            "攻擊方式：先按 R / 空白鍵擲骰，再點左邊武器卡攻擊怪物",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.09),
            font_small,
            (255, 255, 255))
        draw_text(
            "擲骰次數歸 0 後，怪物會攻擊 1~20 點；下方道具卡只能使用一次",
            int(WIDTH * 0.5),
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
        dice_size = int(HEIGHT * 0.12)
        dice_gap = int(WIDTH * 0.02) 
        total_dice_width = (dice_size * 5) + (dice_gap * 4) 
        start_x = int(WIDTH * 0.5 - total_dice_width / 2)
        dice_y = int(HEIGHT * 0.25)
                
        for idx, val in enumerate(dice_values):
            current_x = start_x + idx * (dice_size + dice_gap)
            draw_dice(current_x, dice_y, dice_size, val)
            
            if idx == selected_die_index:
                pygame.draw.rect(
                    screen, 
                    (255, 50, 50), 
                    (current_x - 5, dice_y - 5, dice_size + 10, dice_size + 10), 
                    4, 
                    border_radius=20
                )
        kind, current_multiplier = evaluate_dice_pattern(dice_values)
        pattern_img = font_mid.render(f"目前骰型：{kind}", True, (255, 215, 0))
        pattern_rect = pattern_img.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.40)))
        screen.blit(pattern_img, pattern_rect)

        info_text = f"剩餘擲骰：{roll_times}　攻擊加成：+{player_attack_bonus}　手槍雙倍：{gun_double_turns}"
        draw_text(
            info_text,
            int(WIDTH * 0.5),
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
                int(WIDTH * 0.5),
                int(HEIGHT * 0.70),
                font_mid,
                (255, 255, 255))
        else:
            draw_text(
                "道具卡：使用後會消失",
                int(WIDTH * 0.5),
                int(HEIGHT * 0.58),
                font_small,
                (255, 255, 255))
            card_positions = draw_card_row(BattleItems, int(HEIGHT * 0.63))
    elif Background == "GameOver":
        screen.fill((20, 0, 0))
        draw_text(
            "你被擊敗了！",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.32),
            font_big,
            (255, 80, 80) )
        draw_text(
            "重新遊戲請按 P 鍵",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.48),
            font_mid,
            (255, 255, 255))
        draw_text(
            "按 P 後會回到遊戲一開始，重新選擇武器",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.58),
            font_small,
            (255, 255, 255))

    Animation()
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1
    for Akey in Anim_Time.keys(): #動畫時間碼衰減
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()