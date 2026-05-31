import pygame
import numpy as np
import random
import os
import sys
import math
import time

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
        # AI End

#變數初始化
#系統
pygame.init()
SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,810),(4,1920,1440),(0,2880,2160)]
SS = 3
screen = pygame.display.set_mode((1000, 1000))  # By AI
img = pygame.font.Font(os.path.join("assets", "font", "NotoSansTC-Bold.ttf"), 36).render("BIOS MODE", True, (255, 255, 255))
imgr = img.get_rect()
imgr.center = (500,500)
screen.blit(img, imgr)
pygame.display.flip()
time.sleep(1)
pygame.event.pump()
keys = pygame.key.get_pressed()
if keys[pygame.K_1]:
    SS = 1
elif keys[pygame.K_2]:
    SS = 2
elif keys[pygame.K_3]:
    SS = 3
elif keys[pygame.K_4]:
    SS = 4
#AI End
print(SS)
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
End = False
#卡牌
PlayerDeck = []
UsedRooms = set()
ItemCardPool = [{"name": "腦袋尖尖的", "type": "brain"},{"name": "小草", "type": "grass"},{"name": "戰術翻滾", "type": "roll"},{"name": "菜菜撈撈", "type": "nana"},{"name": "心靈課程名單", "type": "mind"},{"name": "老千的技術", "type": "cheat"},{"name": "你從桃園到新竹", "type": "taoyuan"}]
WeaponChoices = [{"name": "傑里科941半自動手槍", "type": "gun"},{"name": "鞭子", "type": "whip"},{"name": "巨槌瑞斯", "type": "darius"}]
EventCardPool = [{"name": "橙汁汙中山羨恭喜", "type": "monster_double_attack"},{"name": "3cm 感謝祭", "type": "seal_monster_once"},{"name": "我一步都沒有退ㄟ", "type": "boss_no_immunity"},{"name": "我中了兩槍", "type": "dice_becomes_three"},{"name": "寵物溝通師", "type": "enemy_hp_double_player_attack_half"},{"name": "芒果醬", "type": "mango_bonus"},{"name": "武術大師晨晨", "type": "next_battle_cc"},{"name": "幹你敢不敢啦", "type": "player_hp_one"},{"name": "雷霆測資", "type": "all_is_fibo"}]
WeaponSkillPool = {
    "gun": [
        {"name": "賭狗加成", "var": "betdog_bonus", "cost": 15, "desc": "傷害可能歸零或翻倍"},
        {"name": "爆頭加成", "var": "headshot_bonus", "cost": 20, "desc": "基礎傷害增加"},
        {"name": "雙手持槍", "var": "double_gun", "cost": 25, "desc": "攻擊次數增加"}],
    "whip": [
        {"name": "撕裂傷", "var": "whip_bonus1", "cost": 15, "desc": "機率造成撕裂"},
        {"name": "快速揮擊", "var": "whip_bonus2", "cost": 20, "desc": "擲骰次數+2"},
        {"name": "鞭笞", "var": "caning_bonus", "cost": 25, "desc": "消耗撕裂層數造成大傷"}],
    "darius": [
        {"name": "血怒", "var": "hammer1_bonus", "cost": 15, "desc": "攻擊疊加層數提升傷害"},
        {"name": "嗜血回血", "var": "hammer2_bonus", "cost": 20, "desc": "骰數>=20回血"},
        {"name": "無情斬殺", "var": "hammer3_bonus", "cost": 25, "desc": "附加已損失生命傷害"}]}
special_card = [{"name": "賭狗", "type": "gambler"},{"name": "顆秒", "type": "gun_kill_quick"},{"name": "雙槍", "type": "double_gun"},{"name": "外圈刮", "type": "hammer_out"},{"name": "流血", "type": "hammer_bleed"},{"name": "諾克薩斯斷頭台", "type": "hammer_execute"},{"name": "撕裂傷(被動)", "type": "whip_bleed"},{"name": "纏繞(被動)", "type": "whip_bind"},{"name": "鞭刑(主動)", "type": "whip_active"}]
SelectedWeapon = None
CurrentEventCard = None
card_positions = []
weapon_positions = []
battle_weapon_position = None
#戰鬥
player_hp = 30
enemy_hp = 600
leak_layer = 0
enemy_max_hp = 600
battle_round = 1

# 武術大師晨晨
enemy_name = "敵人"
enemy_phase = "normal"      #normal/cc/original
pending_original_enemy_hp = 0
pending_original_enemy_max_hp = 0

dice_value = [1,1,1,1,1]
selected_die_index = 0
dice_rolling = False
dice_roll_timer = 0
roll_times = 8

battle_message = "第一層"

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
next_battle_fibo_dice = False
fibo_dice_active = False
#交易區變數
coin = 30
card_price = 20
shop_card =[]
shop_positions = []
shop_room = None
#武器技能效果，先設啟動
betdog_bonus = False
headshot_bonus = False
double_gun = False
whip_bonus1 = False
whip_bonus2 = False
caning_bonus = False
surround_bonus = False
hammer1_layer = 0
hammer1_bonus = False
hammer2_bonus = False
hammer3_bonus = False
first_gun = True
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
        "choose_weapon_back":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","choose_weapon_back.png")).convert_alpha(), (WIDTH, HEIGHT)),
        "GateG":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","GateG.png")).convert_alpha(), (int(WIDTH / 12), int(HEIGHT / 9))),
        "Endback":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","endback.png")).convert_alpha(), (WIDTH, HEIGHT)),
        "change_area":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","change_area.png")).convert_alpha(), (WIDTH, HEIGHT)),
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
        "巨槌瑞斯": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","S__76242972.png")).convert_alpha(), (CARD_W, CARD_H)),
        "賭狗": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","gunskill1.jpg")).convert_alpha(), (CARD_W, CARD_H)),
        "顆秒": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","gunskill2.jpg")).convert_alpha(), (CARD_W, CARD_H)),
        "雙槍": pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","gunskill3.png")).convert_alpha(), (CARD_W, CARD_H)),
        "外圈刮" :pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","hammerskill1.png")).convert_alpha(), (CARD_W, CARD_H)),
        "流血":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","hammerskill2.jpg")).convert_alpha(), (CARD_W, CARD_H)),
        "諾克薩斯斷頭台":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","hammmerskill3.jpg")).convert_alpha(), (CARD_W, CARD_H)),
        "撕裂傷(被動)":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","whipskill1.jpg")).convert_alpha(), (CARD_W, CARD_H)),
        "纏繞(被動)":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","whipskill2.png")).convert_alpha(), (CARD_W, CARD_H)),
        "鞭刑(主動)":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","card","whipskill3.png")).convert_alpha(), (CARD_W, CARD_H))
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
    #字體載入
    FHeadPath = os.path.join("assets","font","NotoSansTC-Bold.ttf") #粗字
    FTextPath = os.path.join("assets","font","NotoSansTC-Light.ttf") #細字
    font_big = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), int(WIDTH / 22))
    font_mid = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), int(WIDTH / 32))
    font_small = pygame.font.Font(os.path.join("assets","font","NotoSansTC-Regular.ttf"), int(WIDTH / 46))
    return MAPList, Asset_dict, CardImage, EventCardImage, FHeadPath, FTextPath, font_big, font_mid, font_small

MAPList, Asset_dict, CardImage, EventCardImage, FHeadPath, FTextPath, font_big, font_mid, font_small = assetsload(WIDTH,HEIGHT)
choose_weapon_back = Asset_dict["choose_weapon_back"]

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
        global battle_message
        if MAP[Pr,Pc] == 2 or MAP[Pr,Pc] == 4:
            mapused = True
            Anim_Time['AnimRoomCenter2'] = 1 * FPS
            get_random_item_card()
            if MAP[Pr,Pc] == 4:
                get_random_item_card()
        if MAP[Pr,Pc] == 3:
            mapused = True
            Anim_Time['AnimRoomCenter3'] = 4 * FPS
        if MAP[Pr,Pc] == 5:
            mapused = True
            generate_shop_cars()
            battle_message = "點擊卡牌購買道具卡"
            Background = "change_area"
        if MAP[Pr,Pc] == 6:
            mapused = True
            Anim_Time['AnimRoomCenter6'] = 4 * FPS
            get_random_event_card()
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
    global next_battle_fibo_dice

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

    elif event_type == "next_battle_cc":
        next_battle_cc = True
        battle_message = "事件：下一場戰鬥生成武術大師晨晨"

    elif event_type == "player_hp_one":
        player_hp = 1
        battle_message = "事件：生命值變成 1 點"

    elif event_type == "all_is_fibo":
        next_battle_fibo_dice = True
        battle_message = "事件：下一場戰鬥骰子只會骰出 1、2、3、5"

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
    global enemy_hp, battle_message, gun_double_turns, attackted, player_hp
    global battle_round, first_gun, leak_layer, caning_damage, hammer1_layer

    if enemy_hp <= 0 or player_hp <= 0:
        return

    # 如果已經攻擊過，直接攔截不執行傷害
    if attackted:
        battle_message = "本回合已使用過武器攻擊！請重新擲骰"
        return

    damage = basic_damage()

    if card_type == "gun":
        if betdog_bonus:
            x = random.randint(1, 10)
            if x <= 4:
                damage = 0
            elif 5 <= x <= 8:
                damage = int(damage *1.5)
            else:
                damage = int(damage * 3)
        if headshot_bonus:
            damage = int(damage * headshot_multiplier)
        if gun_double_turns > 0:
            damage *= 2
            gun_double_turns -= 1
            if double_gun and first_gun:
                enemy_hp -= damage*0.7
                battle_message = f"雙槍攻擊！前三次雙倍，造成 {damage} 點，剩 {gun_double_turns} 次雙倍，第一次攻擊"
            elif double_gun and not first_gun:
                enemy_hp -= damage*0.7
                battle_message = f"手槍攻擊！前三次雙倍，造成 {damage} 點，剩 {gun_double_turns} 次雙倍"
            else:
                enemy_hp -= damage
                battle_message = f"槍械攻擊！前三次雙倍，造成 {damage} 點，剩 {gun_double_turns} 次雙倍"
        else:
            if double_gun and first_gun:
                enemy_hp -= damage*0.7
                battle_message = f"雙槍攻擊！造成 {damage} 點，第一次攻擊"
            elif double_gun and not first_gun:
                enemy_hp -= damage*0.7
                battle_message = f"手槍攻擊！造成 {damage} 點傷害"
            else:
                enemy_hp -= damage
                battle_message = f"手槍攻擊！造成 {damage} 點傷害"
        if double_gun and first_gun:
            attackted = False
            first_gun = False
        else:
            first_gun = True
            attackted = True

    elif card_type == "whip":
        x = 0
        x = random.randint(1, 10)
        if whip_bonus1:
                if x <= 5:
                    leak_layer = 3
        if caning_bonus:
                if leak_layer > 0:
                    caning_damage = max(int(max(enemy_max_hp*0.25), 1.0))
                    seal_monster_once = True
                else:
                    caning_damage = 0
        elif not caning_bonus:
            caning_damage = 0       
                    
        if enemy_color == (0, 0, 0):
            damage *= 2
            enemy_hp -= damage
            battle_message = f"鞭子攻擊！黑色敵人雙倍傷害，造成 {damage}"
        else:
            enemy_hp -= damage
            battle_message = f"鞭子攻擊！造成 {damage} 傷害"
        attackted = True
        if leak_layer > 0:
            leak_layer -= 1
            if MAP[Pr, Pc] == 9:
                leak_damage = max(int(enemy_hp * 0.02), 1)
                enemy_hp -= leak_damage
                battle_message += f"，敵人撕裂傷數剩 {leak_layer} 層，造成 {leak_damage} 傷害"
                enemy_hp -= caning_damage
                if caning_damage > 0:
                    battle_message += f"，鞭笞造成 {caning_damage} 傷害"
            else:
                leak_damage = max(int(enemy_hp * 0.04), 1)
                battle_message += f"，敵人撕裂傷數剩 {leak_layer} 層，造成 {leak_damage} 傷害"
                enemy_hp -= int(leak_damage )
                enemy_hp -= int(caning_damage )
                if caning_damage > 0:
                    battle_message += f"，鞭笞造成 {int(caning_damage )} 傷害"

    elif card_type == "darius":
        if hammer3_bonus:
            damage += int((enemy_max_hp-enemy_hp) * 0.2)
        if  sum(dice_values) >= 15:
            if MAP[Pr, Pc] == 9:
                hook_damage = max(int(enemy_hp * 0.2), 1)
                enemy_hp -= int((hook_damage + damage)*(max(1.5*hammer1_layer,1)))
                battle_message = f"巨槌瑞斯鉤中 Boss！造成 {int((hook_damage + damage)*(max(1.5*hammer1_layer,1)))} 傷害"
                if hammer1_bonus:
                    if hammer1_layer < 5:
                        hammer1_layer += 1
            else:
                hook_damage = max(enemy_hp // 2, 1)
                enemy_hp -= int((hook_damage + damage)*(max(1.5*hammer1_layer,1)))
                battle_message = f"巨槌瑞斯鉤中！造成敵人一半血量 {int((hook_damage + damage)*(max(1.5*hammer1_layer,1)))}"
                if hammer1_bonus and hammer1_layer < 5:
                    hammer1_layer += 1
        else:
            if hammer1_bonus and hammer1_layer > 0:
                damage = int(damage * (1.5 * hammer1_layer))
                if hammer1_bonus:
                    if hammer1_layer < 5:
                        hammer1_layer += 1
            else:
                damage = int(damage)
            enemy_hp -= damage
            battle_message = f"巨槌瑞斯普通攻擊，造成 {damage} 傷害"
            if hammer1_bonus:
                    if hammer1_layer < 5:
                        hammer1_layer += 1
        attackted = True
    if sum(dice_values) >= 20 and hammer2_bonus:
        player_hp += int(player_hp * 0.2)
    if double_gun and card_type == "gun" and not first_gun:
        battle_round = battle_round
    else:
        battle_round += 1
    battle_message += f"第 {battle_round} 回合"

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
    global enemy_hp, enemy_max_hp, battle_message
    global battle_round, headshot_multiplier
    global hammer1_layer
    global enemy_name, enemy_phase
    global pending_original_enemy_hp, pending_original_enemy_max_hp
    global attackted, roll_times, dice_values
    global fibo_dice_active
    if enemy_hp <= 0:
        # 如果打死的是武術大師晨晨，就切換到原本敵人
        if enemy_phase == "chengchen":
            enemy_name = "Boss" if MAP[Pr, Pc] == 9 else "菁英怪"
            enemy_phase = "original"
            enemy_max_hp = pending_original_enemy_max_hp
            enemy_hp = pending_original_enemy_hp
            pending_original_enemy_max_hp = 0
            pending_original_enemy_hp = 0

            # 換敵人後重置部分戰鬥狀態
            battle_round = 1
            roll_times = 8
            dice_values = [random.randint(1, 6) for _ in range(5)]
            attackted = False

            battle_message = f"武術大師晨晨已被擊敗！"
            return
        # 一般敵人死亡
        enemy_hp = 0
        fibo_dice_active = False
        if battle_round <= 3:
            headshot_multiplier += 1.0
        else:
            headshot_multiplier *= 0.5
        battle_message = f"{enemy_name} 被擊敗了！按 M 回地圖"
        if hammer1_bonus and hammer1_layer == 5:
            hammer1_layer = 3
            battle_message += f"，血怒觸發，下回合倍率 {max(1.5 * hammer1_layer, 1)}"


def monster_attack():
    global player_hp, battle_message, roll_times, Background
    global enemy_double_attack_times, seal_monster_once
    global roll_immunity, hit_count, boss_no_immunity
    global battle_round

    if enemy_hp <= 0 or player_hp <= 0:
        return

    if seal_monster_once and not boss_no_immunity:
        seal_monster_once = False
        if whip_bonus2:
            roll_times = 10
        else:
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
            if whip_bonus2:
                roll_times = 10
            else:
                roll_times = 8
            battle_message = "戰術翻滾觸發！免疫這次怪物攻擊，輪到你重新擲骰"
            return

    player_hp -= monster_damage

    if player_hp <= 0:
        player_hp = 0
        battle_message = f"怪物攻擊造成 {monster_damage} 點傷害，你被擊敗了！"
        Background = "GameOver"
    else:
        if whip_bonus2:
            roll_times = 10
        else:
            roll_times = 8
        battle_message = f"怪物攻擊！造成 {monster_damage} 點傷害，輪到你重新擲骰"

def generate_shop_cars():
    global shop_card, shop_positions, shop_room, ItemCardPool
    shop_card = []
    shop_positions = []
    shop_room = (Pr, Pc)
    
    # 根據玩家當前武器過濾技能卡
    available_cards = []
    if SelectedWeapon is not None:
        weapon_type = SelectedWeapon["type"]
        if weapon_type == "gun":
            valid_names = ["賭狗", "顆秒", "雙槍"]
        elif weapon_type == "whip":
            valid_names = ["撕裂傷(被動)", "纏繞(被動)", "鞭刑(主動)"]
        elif weapon_type == "darius":
            valid_names = ["外圈刮", "流血", "諾克薩斯斷頭台"]
        else:
            valid_names = []
        available_cards = [card for card in special_card if card["name"] in valid_names]
    else:
        # 防呆機制
        available_cards = special_card.copy()
    if len(available_cards) >= 2:
        shop_card = random.sample(available_cards, 2)
    else:
        shop_card = available_cards.copy()
    print("商店特殊卡：", [card["name"] for card in shop_card])

def buy_card(card):
    global coin, battle_message, card_price
    global betdog_bonus, headshot_bonus, double_gun
    global whip_bonus1, whip_bonus2, caning_bonus
    global hammer1_bonus, hammer2_bonus, hammer3_bonus
    if len(shop_card) == 0:
        battle_message = "商店沒有卡片可供購買！"
        return
    if coin >= card_price:
        coin -= card_price
        PlayerDeck.append(card)
        battle_message = f"購買成功！獲得 {card['name']}，剩餘金幣 {coin}"
        name = card["name"]
        if name == "賭狗": betdog_bonus = True
        elif name == "顆秒": headshot_bonus = True
        elif name == "雙槍": double_gun = True
        elif name == "撕裂傷(被動)": whip_bonus1 = True
        elif name == "纏繞(被動)": whip_bonus2 = True
        elif name == "鞭刑(主動)": caning_bonus = True
        elif name == "外圈刮": hammer1_bonus = True
        elif name == "流血": hammer2_bonus = True
        elif name == "諾克薩斯斷頭台": hammer3_bonus = True
        if card in shop_card:
            shop_card.remove(card)
    else:
        battle_message = "金幣不足，無法購買！"
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
    global battle_round, headshot_multiplier, leak_layer
    global hammer1_layer2
    global next_battle_cc
    global enemy_name, enemy_phase
    global next_battle_fibo_dice, fibo_dice_active
    global pending_original_enemy_hp, pending_original_enemy_max_hp
# 先決定原本這場戰鬥的敵人血量
if MAP[Pr, Pc] == 9:
    original_enemy_max_hp = 900
    original_enemy_name = "Boss"
else:
    original_enemy_max_hp = 600
    original_enemy_name = "菁英怪"

original_enemy_max_hp *= enemy_hp_multiplier

# 如果有武術大師晨晨事件，先打晨晨
if next_battle_cc:
    enemy_name = "武術大師晨晨"
    enemy_phase = "chengchen"
    enemy_max_hp = 450
    enemy_hp = enemy_max_hp

    # 暫存原本敵人，等晨晨死後再換出來
    pending_original_enemy_max_hp = original_enemy_max_hp
    pending_original_enemy_hp = original_enemy_max_hp

    next_battle_cc = False
    battle_message = "武術大師晨晨！需先擊敗他後才可繼續打原本敵人"

else:
    enemy_name = original_enemy_name
    enemy_phase = "normal"
    enemy_max_hp = original_enemy_max_hp
    enemy_hp = enemy_max_hp

    pending_original_enemy_max_hp = 0
    pending_original_enemy_hp = 0
    if next_battle_fibo_dice:
        fibo_dice_active = True
        next_battle_fibo_dice = False
        dice_values = [random.choice([1, 2, 3, 5]) for _ in range(5)]
        battle_message = "雷霆測資啟動：本場戰鬥骰子只會出現 1、2、3、5"
    else:
        fibo_dice_active = False
        dice_values = [random.randint(1, 6) for _ in range(5)]

    selected_die_index = 0

    dice_rolling = False
    dice_roll_timer = 0
    whip_bonus2 = False
    roll_times = 8
    battle_round = 1
    headshot_multiplier = 1.0
    next_battle_fibo_dice = False
    fibo_dice_active = False

    player_attack_bonus = 0
    cheat_mode = False
    roll_immunity = False
    hit_count = 0
    stored_damage_turns = 0
    stored_damage = 0
    leak_layer = 0
    hammer1_layer = 0

    if SelectedWeapon is not None and SelectedWeapon["type"] == "gun":
        gun_double_turns = 3
    else:
        gun_double_turns = 0

    enemy_hp_multiplier = 1
    player_attack_half = False

    if next_dice_fixed_three:
        dice_values = [3, 3, 3, 3, 3]
        next_dice_fixed_three = False
        attackted = False  #  3 點，直接攻擊
        battle_message = "事件效果：這場戰鬥骰子先變成 3"
    else:
        attackted = False   # 進入戰鬥還沒擲骰，鎖定攻擊
        battle_message = "先按空白鍵擲骰，再點左邊武器卡攻擊怪物"


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
    global selected_die_index, t
    global battle_round, headshot_multiplier
    global betdog_bonus, headshot_bonus, double_gun, whip_bonus1, caning_bonus, surround_bonus, first_gun, leak_layer, whip_bonus2
    global hammer1_layer, hammer1_bonus, hammer2_bonus, hammer3_bonus
    global shop_card, shop_positions, shop_room
    global card_price
    global enemy_name, enemy_phase, pending_original_enemy_hp, pending_original_enemy_max_hp

    Pr, Pc = 11, 11
    Background = "StartWeapon"

    Global_Time = 0
    Anim_Time = {}
    battle_round = 1

    PlayerDeck = []
    UsedRooms = set()
    SelectedWeapon = None
    CurrentEventCard = None

    card_positions = []
    weapon_positions = []
    battle_weapon_position = None

    player_hp = 30
    enemy_hp = 600
    enemy_max_hp = 600
    enemy_name = "敵人"
    enemy_phase = "normal"
    pending_original_enemy_hp = 0
    pending_original_enemy_max_hp = 0


    dice_values = [random.randint(1, 6) for _ in range(5)]
    selected_die_index = 0
    dice_rolling = False
    dice_roll_timer = 0
    roll_times = 8
    battle_round = 1
    headshot_multiplier = 1.0
    leak_layer = 0
    hammer1_layer = 0
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
    betdog_bonus = False
    headshot_bonus = False
    double_gun = False
    whip_bonus1 = False
    hammer1_layer = 0
    hammer1_bonus = False
    hammer2_bonus = False
    hammer3_bonus = False
    caning_bonus = False
    surround_bonus = False
    first_gun = True
    whip_bonus2 = False

    shop_card = []
    card_price = 20
    shop_positions = []
    shop_room = None

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
    if 'AnimEnd' in Anim_Time and Anim_Time.get('AnimEnd') > 0:
        AnimEnd()

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
    global IntTryTime, IntQStop
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
                IntQStop = 0
                IntTryTime = 0
                GameTimer = Global_Time + FPS * 60
            Background = "Gaming"
    elif tick <= 240:
        Allblack.set_alpha((240-tick)*8.5)
        screen.blit(Allblack, (0, 0))
        if tick == 239:
            now_coin = coin
            if Gamekind == 0:
                GameTimer = Global_Time + FPS * 10
            elif Gamekind == 1:
                GameTimer = Global_Time + FPS * 60

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

def AnimEnd():
    global Background
    global Asset_dict
    tick = 120 - Anim_Time['AnimEnd']
    br = Asset_dict["GateG"]
    rbr = pygame.transform.rotate(pygame.transform.scale(br,(max(WIDTH * tick / 60 + 1,1),max(WIDTH * tick / 60 + 1,1))), tick*5)
    recr = rbr.get_rect()
    recr.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(rbr, recr)
    if tick > 70:
        Background = "End"
        print("遊戲結束")

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
                        MAPList, Asset_dict, CardImage, EventCardImage, FHeadPath, FTextPath, font_big, font_mid, font_small = assetsload(WIDTH,HEIGHT)
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
                        IntTryTime += 1
                        if mouse_x < WIDTH/3:
                            if IntAns == 1:
                                coin += int((GameTimer-Global_Time)/FPS) / IntTryTime
                                Background = "GameMVP"
                            else:
                                Anim_Time["AnimGameFire"] = FPS * 2
                        elif mouse_x > WIDTH * 2/3:
                            if IntAns == 3:
                                coin += int((GameTimer-Global_Time)/FPS) / IntTryTime
                                Background = "GameMVP"
                            else:
                                Anim_Time["AnimGameFire"] = FPS * 2
                        else:
                            if IntAns == 2:
                                coin += int((GameTimer-Global_Time)/FPS) / IntTryTime
                                Background = "GameMVP"
                            else:
                                Anim_Time["AnimGameFire"] = FPS * 2
                        print(IntTryTime)

                elif Background == "GameMVP":
                    Background = "Map"
                elif Background == "change_area":
                    for a in shop_positions:
                        x, y, w, h, card = a
                        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                            buy_card(card)
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
                attackted = False

            # 按 M 回地圖
            if event.key == pygame.K_m :
                if Background == "Battle" and enemy_hp <= 0 :
                    Background = "Map"
                    attackted = False
                if MAP[Pr, Pc] == 9 and GameRound < 3 and mapused == True:
                    GameRound += 1
                    print(f"進入第 {GameRound} 輪！")
                    RoomStep = 0
                    #地圖生成
                    MAP = np.zeros((23,23),dtype=int)
                    MAP[11,11] = 1
                    MAP[10,11] = 2
                    MAP[12,11] = 2
                    MAP[11,12] = 2
                    MAP[11,10] = 2
                    BackHistory.append("Map")
                    battle_message = f'第{GameRound+1}層'
                    mapused = True
                    Pr,Pc = 11,11
                    gates_group = pygame.sprite.Group()
                    refresh_gates(Pr, Pc, gates_group)
                elif MAP[Pr, Pc] == 9 and GameRound == 3 and mapused == True and End == False:
                    print("已完成所有輪數，無法繼續進行！")
                    End = True
                    Anim_Time["AnimEnd"] = int(FPS * 3)
                elif Background == "change_area":
                    Background = "Map"

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
            print("接觸傳送門")
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
                MAP[Pr,Pc] = random.randint(2, 6) #傳送瞬間去改 Numpy 陣列，隨機判定房間類型，這裡不處理精英怪、整備、Boss，這幾個交給RoomStep處理 (初始值2,6)
            elif RoomStep == 4:
                MAP[Pr,Pc] = 7
            elif RoomStep == 7+GameRound:
                MAP[Pr,Pc] = 8
            elif RoomStep == 8+GameRound:
                MAP[Pr,Pc] = 9
            refresh_gates(Pr, Pc, gates_group)
            Anim_Time["Anim_Room"] = 3 * FPS
            mapused = False
            roomcenter.update()

    if player.check_trigger(roomcenter) and not mapused and Background == "Map": #碰撞區
        print("玩家碰到交互物品roomcenter")
        roomcenter.touch()

    #骰子戰鬥邏輯
    if Background == "Battle":
        if dice_rolling:
        # 只重骰被選中的那顆骰子，不影響陣列長度與其他骰子
            if fibo_dice_active:
                dice_values[selected_die_index] = random.choice([1, 2, 3, 5])
            else:
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
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH * 0.41 / 4 , HEIGHT * 0.41 / 3),WIDTH / 10)
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
                draw_text('1/3',int(WIDTH*0.27),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('2/3',int(WIDTH*0.5),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('4/3',int(WIDTH*0.73),int(HEIGHT*0.7),font_small,(0,0,0))
                IntAns = 2
            elif IntQ == 2:
                draw_text('pi',int(WIDTH*0.27),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('pi/2',int(WIDTH*0.5),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('pi/3',int(WIDTH*0.73),int(HEIGHT*0.7),font_small,(0,0,0))
                IntAns = 1
            elif IntQ == 3:
                draw_text('e-1',int(WIDTH*0.27),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('(1-e)/2',int(WIDTH*0.5),int(HEIGHT*0.7),font_small,(0,0,0))
                draw_text('(1-e)/3',int(WIDTH*0.73),int(HEIGHT*0.7),font_small,(0,0,0))
                IntAns = 3
            if (GameTimer-Global_Time < 0 or IntTryTime > 1) and IntQStop != 1:
                IntQStop = 1 
                Anim_Time["AnimGameMVP"] = FPS * 1
                
    elif Background == "GameMVP":
        screen.blit(Asset_dict["b049gamingmvp"], (0, 0))
        gmvp = Asset_dict[f'b049coin{(Global_Time%120)//20}'].get_rect()
        gmvp.center = (WIDTH/2,HEIGHT/2)
        screen.blit(Asset_dict[f'b049coin{(Global_Time%120)//20}'],gmvp)
        draw_text(f'{coin-now_coin}',int(WIDTH * 0.5),int(HEIGHT * 0.72),font_big,(255, 255, 255))
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
    elif Background == "change_area":
        screen.blit(Asset_dict["change_area"], (0, 0))
        coin_icon = pygame.transform.scale(Asset_dict["b049coin0"],(int(HEIGHT * 0.1), int(HEIGHT * 0.1)))
        coin_icon_rect = coin_icon.get_rect()
        coin_icon_rect.topleft = (int(WIDTH * 0.05), int(HEIGHT * 0.05))
        screen.blit(coin_icon, coin_icon_rect)
        draw_text(
            f'{coin}',
            coin_icon_rect.right + int(WIDTH * 0.04),
            coin_icon_rect.top + int(HEIGHT * 0.05),
            font_big,
            (255, 255, 255)
        )
        draw_text(
            "點擊卡片購買，按 M 回地圖",
            int(WIDTH * 0.5),
            int(HEIGHT * 0.9),
            font_small,
            (255, 255, 255)
        )

        shop_positions = []
        shop_x_lst = [int(WIDTH*0.32),int(WIDTH*0.52),]
        shop_y = int(HEIGHT*0.5)

        for i, card in enumerate(shop_card):
            if i >= 2:
                break
            x = shop_x_lst[i]
            y = shop_y
            pos = draw_card(card,x,y)
            shop_positions.append((x,y, CARD_W, CARD_H, card))

        if len(shop_card) == 0:
            draw_text(
                "商店沒有卡片可購買！",
                int(WIDTH * 0.5),
                int(HEIGHT * 0.5),
                font_mid,(255, 0, 0)
            )

        draw_text(
            battle_message,
            int(WIDTH * 0.5),
            int(HEIGHT * 0.95),
            font_small,(255, 255, 255)
        )
    elif Background == "Battle":
        screen.blit(Asset_dict["b118battle_bg"], (0, 0))
        draw_text(
            f"玩家 HP：{player_hp}",
            int(WIDTH * 0.15),
            int(HEIGHT * 0.04),
            font_mid,
            (70, 190, 90))
        draw_text(
            f"{enemy_name} HP：{enemy_hp}/{enemy_max_hp}",
            int(WIDTH * 0.85),
            int(HEIGHT * 0.04),
            font_mid,
            (220, 60, 60))
        draw_text(
            "攻擊方式：先按空白鍵擲骰，再點左邊武器卡攻擊怪物",
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
        draw_text(
            f"第 {battle_round} 回合",
            int (WIDTH * 0.5),
            int(HEIGHT * 0.20),
            font_small,
            (255, 255, 255))
        battle_weapon_position = None
        if SelectedWeapon is not None:
            weapon_x = int(WIDTH * 0.03)
            weapon_y = int(HEIGHT * 0.18)
            draw_text(
                "武器卡",
                weapon_x + int(CARD_W * 0.5),
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
            
            player_card_names = [c["name"] for c in PlayerDeck] #畫技能區
            weapon_type = SelectedWeapon["type"]
            if weapon_type == "gun": # 定義各武器對應的順序
                skills = ["賭狗", "顆秒", "雙槍"]
            elif weapon_type == "whip":
                skills = ["撕裂傷(被動)", "纏繞(被動)", "鞭刑(主動)"]
            elif weapon_type == "darius":
                skills = ["外圈刮", "流血", "諾克薩斯斷頭台"]
            else:
                skills = []
            box_size = int(CARD_W * 0.26)
            box_gap = int(CARD_W * 0.11)
            start_x = weapon_x + int((CARD_W - (3 * box_size + 2 * box_gap)) / 2)
            box_y = weapon_y + CARD_H + int(HEIGHT * 0.02)
            for i in range(3):
                is_lit = i < len(skills) and skills[i] in player_card_names
                box_rect = (start_x + i * (box_size + box_gap), box_y, box_size, box_size)
                
                if is_lit:
                    pygame.draw.rect(screen, (255, 215, 0), box_rect, border_radius=5) 
                    pygame.draw.rect(screen, (255, 255, 255), box_rect, 2, border_radius=5)
                else:
                    pygame.draw.rect(screen, (60, 60, 60), box_rect, border_radius=5)
                    pygame.draw.rect(screen, (120, 120, 120), box_rect, 2, border_radius=5)
        
                num_color = (0, 0, 0) if is_lit else (150, 150, 150)
                num_text = font_small.render(str(i + 1), True, num_color)
                num_rect = num_text.get_rect(center=(box_rect[0] + box_size // 2, box_rect[1] + box_size // 2))
                screen.blit(num_text, num_rect)
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

        info_text = f"剩餘擲骰：{roll_times}攻擊加成：+{player_attack_bonus}手槍雙倍：{gun_double_turns}"
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
    elif Background == "End":
        screen.blit(Asset_dict["Endback"], (0, 0))

    Animation()
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1
    for Akey in Anim_Time.keys(): #動畫時間碼衰減
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()