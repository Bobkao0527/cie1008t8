#第三版
import pygame
import numpy as np
import random
import os
import sys
import math
import time
import unicodedata

# ==========================================
# 核心路徑與跨平台雙軌智慧鎖定系統
# ==========================================
ORIGINAL_CWD = os.getcwd() 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

print(f"🚀 [路徑追蹤] 腳本所在真實目錄: {BASE_DIR}")
print(f"🚀 [路蹤追蹤] 工作區目錄: {ORIGINAL_CWD}")

# 系統縮放比例獲取
def getsysscaling():
    if sys.platform == "darwin":  # macOS
        try:
            from AppKit import NSScreen
            return NSScreen.mainScreen().backingScaleFactor()
        except ImportError:
            import subprocess
            cmd = "system_profiler SPDisplaysDataType | grep 'Retina'"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            if "Retina" in result.stdout:
                return 2.0
    if sys.platform == "win32":   # Windows
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

# ==========================================
# 智慧素材特徵檢索與保底載入核心
# ==========================================
def safe_load_image(filename, width, height):
    def clean_str(s):
        return unicodedata.normalize('NFC', str(s)).lower().strip()
    
    target_clean = clean_str(filename)
    target_core = os.path.splitext(target_clean)[0]
    
    # 核心特徵碼交叉對照
    feature_map = {
        "主背景": ["主背景", "main_bg", "主畫面", "choose_weapon_back"],
        "戰鬥背景": ["戰鬥背景", "battle_bg", "battleback2nog"],
        "鼠標1": ["鼠標1", "1_彩色", "cursor1", "鼠標_一般"],
        "鼠標2": ["鼠標2", "2_彩色", "cursor2", "鼠標_懸置"],
        "鼠標3": ["鼠標3", "3_彩色", "cursor3", "_鼠標_點擊"],
        "答應_文字": ["答應_文字", "答應"],
        "拒絕_文字": ["拒絕_文字", "拒絕"]
    }
    
    active_tokens = []
    for core_key, tokens in feature_map.items():
        if core_key in filename:
            active_tokens = tokens
            break
    if not active_tokens:
        active_tokens = [target_core]

    search_dirs = [BASE_DIR, ORIGINAL_CWD, os.path.join(ORIGINAL_CWD, ".."), ".", "assets", os.path.join("assets", "Background"), os.path.join("assets", "card")]
    
    # 【第一防線】精準匹配
    for sd in search_dirs:
        if os.path.exists(sd):
            try:
                for f in os.listdir(sd):
                    if clean_str(f) == target_clean:
                        full_p = os.path.join(sd, f)
                        return pygame.transform.smoothscale(pygame.image.load(full_p).convert_alpha(), (width, height))
            except:
                pass

    # 【第二防線】特徵碼模糊匹配
    for sd in search_dirs:
        if os.path.exists(sd):
            try:
                for f in os.listdir(sd):
                    norm_f = clean_str(f)
                    if any(token in norm_f for token in active_tokens) and norm_f.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        full_p = os.path.join(sd, f)
                        return pygame.transform.smoothscale(pygame.image.load(full_p).convert_alpha(), (width, height))
            except:
                pass

    # 【第三防線】向量防崩潰保底生成
    fallback = pygame.Surface((width, height), pygame.SRCALPHA)
    if "鼠標" in filename or "cursor" in filename:
        color = (50, 255, 100) if "1" in filename or "一般" in filename else ((255, 220, 30) if "2" in filename or "懸置" in filename else (255, 40, 40))
        pts = [(0, 0), (int(width * 0.75), int(height * 0.45)), (int(width * 0.45), int(height * 0.55)), (int(width * 0.25), int(height * 0.85))]
        pygame.draw.polygon(fallback, color, pts)
        pygame.draw.polygon(fallback, (255, 255, 255), pts, width=2)
        return fallback
    elif any(x in filename for x in ["長槍", "雙刃劍", "盾牌", "weapon"]):
        pygame.draw.circle(fallback, (70, 140, 240, 120), (width // 2, height // 2), width // 3)
        pygame.draw.circle(fallback, (255, 255, 255), (width // 2, height // 2), width // 3, width=2)
        return fallback

    fallback.fill((30, 45, 65))
    pygame.draw.rect(fallback, (70, 135, 240), (0, 0, width, height), width=4)
    return fallback

def safe_draw_rect(surface, color, rect, width=0, border_radius=0):
    try:
        if border_radius > 0 and hasattr(pygame.draw, 'rect'):
            pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)
        else:
            pygame.draw.rect(surface, color, rect, width)
    except TypeError:
        pygame.draw.rect(surface, color, rect, width)

# ==========================================
# 遊戲基礎變數與系統配置
# ==========================================
pygame.init()
pygame.mixer.init()

SCREEN_SIZE = [(1, 480, 360), (2, 720, 540), (3, 1080, 810), (4, 1920, 1440), (0, 1024, 768)]
SS = 4  # 預設採用 1024x768 完美整合解析度
WIDTH, HEIGHT = SCREEN_SIZE[SS][1], SCREEN_SIZE[SS][2]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('骰子迷因大亂鬥 - 完美整合版')
clock = pygame.time.Clock()

# 核心渲染虛擬畫布 (所有UI基準點皆以 1024x768 計算)
canvas = pygame.Surface((1024, 768))

# 顏色資源定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 45, 50)
TRANSPARENT_BLACK = (15, 22, 35, 220)
BLUE = (70, 140, 240)
LIGHT_BLUE = (100, 180, 255) 
NEON_GREEN = (50, 255, 50)  

FPS = 60
Global_Time = 0
Anim_Time = {}
BackHistory = []
Background = "MainMenu"  # 起始狀態改為主選單

# 遊戲資料庫定義
coin = 30
now_coin = coin
End = False
PlayerSkills = []
PlayerDeck = []
UsedRooms = set()
ItemCardPool = [{"name": "腦袋尖尖的", "type": "brain"}, {"name": "小草", "type": "grass"}, {"name": "戰術翻滾", "type": "roll"}, {"name": "菜菜撈撈", "type": "nana"}, {"name": "心靈課程名單", "type": "mind"}, {"name": "老千的技術", "type": "cheat"}, {"name": "你從桃園到新竹", "type": "taoyuan"}]
WeaponChoices = [{"name": "傑里科941半自動手槍", "type": "gun"}, {"name": "鞭子", "type": "whip"}, {"name": "巨槌瑞斯", "type": "darius"}]
EventCardPool = [{"name": "橙汁汙中山羨恭喜", "type": "monster_double_attack"}, {"name": "3cm 感謝祭", "type": "seal_monster_once"}, {"name": "我一步都沒有退ㄟ", "type": "boss_no_immunity"}, {"name": "我中了兩槍", "type": "dice_becomes_three"}, {"name": "寵物溝通師", "type": "enemy_hp_double_player_attack_half"}, {"name": "芒果醬", "type": "mango_bonus"}, {"name": "武術大師晨晨", "type": "next_battle_cc"}, {"name": "幹你敢不敢啦", "type": "player_hp_one"}, {"name": "雷霆測資", "type": "all_is_fibo"}]

WeaponSkillPool = {
    "gun": [{"name": "賭狗加成", "var": "betdog_bonus", "cost": 15, "desc": "傷害可能歸零或翻倍"}, {"name": "爆頭加成", "var": "headshot_bonus", "cost": 20, "desc": "基礎傷害增加"}, {"name": "雙手持槍", "var": "double_gun", "cost": 25, "desc": "攻擊次數增加"}],
    "whip": [{"name": "撕裂傷", "var": "whip_bonus1", "cost": 15, "desc": "機率造成撕裂"}, {"name": "快速揮擊", "var": "whip_bonus2", "cost": 20, "desc": "擲骰次數+2"}, {"name": "鞭笞", "var": "caning_bonus", "cost": 25, "desc": "消耗撕裂層數造成大傷"}],
    "darius": [{"name": "血怒", "var": "hammer1_bonus", "cost": 15, "desc": "攻擊疊加層數提升傷害"}, {"name": "嗜血回血", "var": "hammer2_bonus", "cost": 20, "desc": "骰數>=20回血"}, {"name": "無情斬殺", "var": "hammer3_bonus", "cost": 25, "desc": "附加已損失生命傷害"}]
}

SelectedWeapon = None
CurrentEventCard = None
card_positions = []
weapon_positions = []
battle_weapon_position = None

# 戰鬥屬性變數
player_hp = 30
enemy_hp = 600
leak_layer = 0
enemy_max_hp = 600
battle_round = 1
enemy_name = "敵人"
enemy_phase = "normal"
pending_original_enemy_hp = 0
pending_original_enemy_max_hp = 0

dice_values = [1, 1, 1, 1, 1]
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

# 商店技能標記
betdog_bonus = False
headshot_bonus = False
double_gun = False
whip_bonus1 = False
whip_bonus2 = False
caning_bonus = False
hammer1_layer = 0
hammer1_bonus = False
hammer2_bonus = False
hammer3_bonus = False
first_gun = True

# 地圖陣列初始化
MAP = np.zeros((23, 23), dtype=int)
MAP[11, 11] = 1
MAP[10, 11] = 2
MAP[12, 11] = 2
MAP[11, 12] = 2
MAP[11, 10] = 2
BackHistory.append("MainMenu")
mapused = True

# ==========================================
# 字體智慧相容載入模組
# ==========================================
def get_font(size):
    preferred_fonts = ["microsoftjhenghei", "notosanstc", "pingfangtc", "simhei", "stxihei"]
    for name in preferred_fonts:
        try:
            font = pygame.font.SysFont(name, size)
            if font: return font
        except:
            continue
    return pygame.font.SysFont(None, size)

font_small = get_font(16)
font_med = get_font(24)
font_mid = get_font(28)
font_big = get_font(36)
font_title = get_font(42)

# ==========================================
# 資源載入總成配置 (支援動態解析度變更刷新)
# ==========================================
def assetsload(W, H):
    global MAPList, Asset_dict, CardImage, EventCardImage, B019, weapons_pool
    global gun_sound, whip_sound, hammer_sound, got_two_shot_sound, no_back_sound, enemy_dead_sound, dareyou_sound, congrat3shot_sound
    
    # 載入音效
    try:
        gun_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "bombom.wav"))
        whip_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "whip.wav"))
        hammer_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "doulwow.wav"))
        got_two_shot_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "gottwoshot.wav"))
        no_back_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "noback.wav"))
        enemy_dead_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "rrrrrrrrr(man).wav"))
        dareyou_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "dareyou.wav"))
        congrat3shot_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "congrat3shot.wav"))
        gun_sound.set_volume(0.8)
        hammer_sound.set_volume(0.3)
    except:
        print("⚠️ 提示：部分音效檔未就緒，系統啟用靜音保底模式。")

    MAPList = []
    for i in range(1, 10):
        MAPList.append(safe_load_image(f'map{i}.png', W, H))
        
    Asset_dict = {
        "b049anim_room1": safe_load_image("b049anim_room1.png", int(W / 5 * 2), int(W / 25 * 2)),
        "b049setting": safe_load_image("b049setting.png", int(W / 20), int(W / 20)),
        "xesc": safe_load_image("xesc.png", int(W / 20), int(W / 20)),
        "b049settingback": safe_load_image("b049settingback.png", W, H),
        "b049settingb": safe_load_image("b049settingb.png", int(W / 5 * 1.5), int(W / 25 * 1.5)),
        "b049roomcenter8": safe_load_image("b049roomcenter8.png", int(W / 8), int(W / 8)),
        "b049roomcenter7": safe_load_image("Golem.png", int(W / 3), int(H / 4)),
        "b049roomcenter9": safe_load_image("level1 boss.png", int(W / 3), int(W / 3)),
        "b049roomcload3-1": safe_load_image("b049roomcload3-1.png", int(W / 3), int(H / 3)),
        "b049roomcload3-2": safe_load_image("b049roomcload3-2.png", W, H),
        "b049gaming0-1": safe_load_image("b049gaming0-1.png", W, H),
        "b118battle_bg": safe_load_image("battleback2nog.jpeg", W, H),
        "b049bettingb": safe_load_image("b049bettingb.jpeg", W, H),
        "b049bettingr": safe_load_image("b049bettingr.png", int(W / 3), int(W / 3)),
        "b049gamingmvp": safe_load_image("b049gamingmvp.jpeg", W, H),
        "b049bettingbe": safe_load_image("b049bettingbe.jpeg", W, H),
        "choose_weapon_back": safe_load_image("choose_weapon_back.png", W, H),
        "GateG": safe_load_image("GateG.png", int(W / 12), int(H / 9)),
        "Endback": safe_load_image("endback.png", W, H),
        "change_area": safe_load_image("change_area.png", W, H),
    }
    
    for i in range(1, 7):
        Asset_dict[f'b049roomcenter{i}'] = safe_load_image(f'b049roomcenter{i}.png', int(W / 8), int(W / 8))
    for j in range(0, 2):
        Asset_dict[f'b049gaming{j}'] = safe_load_image(f'b049gaming{j}.png', W, H)
    for k in range(0, 6):
        Asset_dict[f'b049coin{k}'] = safe_load_image(f'b049coin{k}.png', int(W / 6), int(W / 6))
    for l in range(1, 4):
        Asset_dict[f'b049Q{l}'] = safe_load_image(f'b049Q{l}.png', int(W / 3 * 0.8), int(W / 4 * 0.8))

    global CARD_H, CARD_W, EVENT_CARD_H, EVENT_CARD_W
    CARD_W, CARD_H = int(W * 0.15), int(H * 0.33)
    EVENT_CARD_W, EVENT_CARD_H = int(W * 0.25), int(H * 0.55)

    CardImage = {
        "腦袋尖尖的": safe_load_image("S__76242953.png", CARD_W, CARD_H),
        "小草": safe_load_image("S__76242954.png", CARD_W, CARD_H),
        "戰術翻滾": safe_load_image("S__76242955.png", CARD_W, CARD_H),
        "菜菜撈撈": safe_load_image("S__76242956.png", CARD_W, CARD_H),
        "心靈課程名單": safe_load_image("S__76242957.png", CARD_W, CARD_H),
        "老千的技術": safe_load_image("S__76242958.png", CARD_W, CARD_H),
        "你從桃園到新竹": safe_load_image("S__76242959.png", CARD_W, CARD_H),
        "傑里科941半自動手槍": safe_load_image("S__76242970.png", CARD_W, CARD_H),
        "鞭子": safe_load_image("S__76242971.png", CARD_W, CARD_H),
        "巨槌瑞斯": safe_load_image("S__76242972.png", CARD_W, CARD_H),
        "賭狗": safe_load_image("gunskill1.jpg", CARD_W, CARD_H),
        "顆秒": safe_load_image("gunskill2.jpg", CARD_W, CARD_H),
        "雙槍": safe_load_image("gunskill3.png", CARD_W, CARD_H),
        "外圈刮": safe_load_image("hammerskill1.png", CARD_W, CARD_H),
        "流血": safe_load_image("hammerskill2.jpg", CARD_W, CARD_H),
        "諾克薩斯斷頭台": safe_load_image("hammmerskill3.jpg", CARD_W, CARD_H),
        "撕裂傷(被動)": safe_load_image("whipskill1.jpg", CARD_W, CARD_H),
        "纏繞(被動)": safe_load_image("whipskill2.png", CARD_W, CARD_H),
        "鞭刑(主動)": safe_load_image("whipskill3.png", CARD_W, CARD_H)
    }

    # 整合 UI 專用資源字典 B019
    B019 = {
        "主背景.png": safe_load_image("主背景.png", 1024, 768),
        "戰鬥背景.png": safe_load_image("戰鬥背景.png", 1024, 768),
        "答應_文字.png": safe_load_image("答應_文字-removebg-preview.png", 150, 50),
        "拒絕_文字.png": safe_load_image("拒絕_文字-removebg-preview.png", 150, 50),
        "鼠標_一般.png": safe_load_image("鼠標1_彩色-removebg-preview.png", 45, 45),
        "鼠標_懸置.png": safe_load_image("鼠標2_彩色-removebg-preview.png", 45, 45),
        "_鼠標_點擊.png": safe_load_image("鼠標3_彩色-removebg-preview.png", 45, 45),
        "長槍.png": safe_load_image("長槍.png", 150, 150),
        "雙刃劍.png": safe_load_image("雙刃劍.png", 150, 150),
        "盾牌.png": safe_load_image("盾牌.png", 150, 150)
    }
    weapons_pool = [B019["長槍.png"], B019["雙刃劍.png"], B019["盾牌.png"]]

# 初始化首輪載入
assetsload(WIDTH, HEIGHT)

current_weapon_idx = random.randint(0, len(weapons_pool) - 1)
last_weapon_switch_time = pygame.time.get_ticks() 
state_1_start_time = 0                           

# 完全接管系統原生游標
pygame.mouse.set_visible(False)

# ==========================================
# UI 核心類別定義
# ==========================================
class CursorManager:
    def __init__(self, normal, hover, click):
        self.normal = normal
        self.hover = hover
        self.click = click
        self.current_img = self.normal

    def update(self, logical_mouse_pos, is_hovering, is_clicking):
        if is_clicking:
            self.current_img = self.click
        elif is_hovering:
            self.current_img = self.hover
        else:
            self.current_img = self.normal
        return logical_mouse_pos

    def draw(self, surface, pos):
        surface.blit(self.current_img, (pos[0], pos[1]))

class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.is_hovered = False

    def update_hover(self, logical_mouse_pos):
        self.is_hovered = self.rect.collidepoint(logical_mouse_pos)

    def draw(self, surface):
        btn_color = (60, 140, 240) if self.is_hovered else (45, 100, 190)
        safe_draw_rect(surface, btn_color, self.rect, border_radius=8)
        safe_draw_rect(surface, WHITE, self.rect, width=2, border_radius=8)
        
        txt_surf = font_med.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_event(self, event, logical_mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(logical_mouse_pos) and self.action:
                self.action()

class SideIconButton:
    def __init__(self, x, y, icon_image, text, bg_color=DARK_GRAY, text_color=WHITE, padding=12, action=None):
        self.icon_image = icon_image
        self.text_surf = font_med.render(text, True, text_color)
        btn_w = self.icon_image.get_width() + self.text_surf.get_width() + padding * 3
        btn_h = max(self.icon_image.get_height(), self.text_surf.get_height()) + padding * 2
        self.rect = pygame.Rect(x, y, btn_w, btn_h)
        self.icon_pos = (x + padding, y + (btn_h - self.icon_image.get_height()) // 2)
        self.text_pos = (x + padding * 2 + self.icon_image.get_width(), y + (btn_h - self.text_surf.get_height()) // 2)
        self.bg_color = bg_color
        self.is_hovered = False
        self.action = action  

    def update_hover(self, logical_mouse_pos):
        self.is_hovered = self.rect.collidepoint(logical_mouse_pos)

    def draw(self, surface):
        color = tuple(min(255, c + 40) for c in self.bg_color) if self.is_hovered else self.bg_color
        safe_draw_rect(surface, color, self.rect, border_radius=10)
        safe_draw_rect(surface, WHITE, self.rect, width=2, border_radius=10)
        surface.blit(self.icon_image, self.icon_pos)
        surface.blit(self.text_surf, self.text_pos)

    def handle_event(self, event, logical_mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(logical_mouse_pos) and self.action:
                self.action()

# ==========================================
# 設置與主選單控制狀態變數
# ==========================================
show_settings = False          
enter_game_click_state = 0   # 0: 主頁面, 1: 轉場過渡, 2: 進入遊戲
has_saved = False              
saved_player_name = ""         
input_active = False           
partial_display_active = False

def open_settings_menu():
    global show_settings
    show_settings = True

def save_settings_data():
    global show_settings, has_saved, saved_player_name, input_active
    show_settings = False
    input_active = False
    saved_player_name = "未命名玩家" if player_name.strip() == "" else player_name
    has_saved = True

# ==========================================
# UI 元件配置佈局初始化
# ==========================================
cursor_manager = CursorManager(B019["鼠標_一般.png"], B019["鼠標_懸置.png"], B019["_鼠標_點擊.png"])
main_panel_rect = pygame.Rect(1024 * 0.4, 768 * 0.1, 1024 * 0.55, 768 * 0.85)

side_btns = []
icon_surface_3 = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(icon_surface_3, WHITE, (12, 12), 10, width=2)
left_btn_3 = SideIconButton(830, 20, icon_surface_3, "高級設置", bg_color=(70, 80, 90), action=open_settings_menu)
side_btns.append(left_btn_3)

px = main_panel_rect.x + 40
py = main_panel_rect.y + 200 

name_label = font_med.render("玩家名稱:", True, WHITE)
input_rect = pygame.Rect(px + 120, py, 300, 40)
player_name = ""

res_options = [
    {"label": "720x540", "w": 720, "h": 540, "ss": 1},
    {"label": "1024x768", "w": 1024, "h": 768, "ss": 4},
    {"label": "1080x810", "w": 1080, "h": 810, "ss": 2},
    {"label": "1920x1440", "w": 1920, "h": 1440, "ss": 3}
]
res_label = font_med.render("螢幕尺寸:", True, WHITE)
res_buttons = []
res_start_x = px + 100  
res_start_y = py + 80

for i, opt in enumerate(res_options):
    res_buttons.append({
        "rect": pygame.Rect(res_start_x + (i * 92), res_start_y, 82, 32), 
        "w": opt["w"], "h": opt["h"], "ss": opt["ss"], "label": opt["label"], "is_hovered": False
    })

partial_label = font_med.render("部分顯示:", True, WHITE)
partial_checkbox_rect = pygame.Rect(px + 100, py + 145, 32, 32)

enter_game_rect = pygame.Rect(main_panel_rect.centerx - 130, main_panel_rect.centery + 120, 260, 65)

save_btn_w, save_btn_h = 220, 48
main_action_btn = Button(main_panel_rect.centerx - save_btn_w // 2, main_panel_rect.bottom - save_btn_h - 50, save_btn_w, save_btn_h, "保存設定", save_settings_data)

# ==========================================
# 核心戰鬥功能繪製與計算函式
# ==========================================
def draw_text(text, x, y, font, color=(255, 255, 255)):
    img = font.render(text, True, color)
    imgr = img.get_rect()
    imgr.center = (x, y)
    canvas.blit(img, imgr)

def draw_dice(x, y, size, value):
    pygame.draw.rect(canvas, (245, 245, 245), (x, y, size, size), border_radius=20)
    pygame.draw.rect(canvas, (0, 0, 0), (x, y, size, size), 5, border_radius=20)
    text = font_big.render(str(value), True, (0, 0, 0))
    rect = text.get_rect(center=(x + size // 2, y + size // 2))
    canvas.blit(text, rect)

def evaluate_dice_pattern(dice):
    counts = [dice.count(x) for x in range(1, 7)]
    unique_vals = sorted(list(set(dice)))
    if 5 in counts: return "五條 (傷害 x3.0)", 3.0
    elif 4 in counts: return "鐵支 (傷害 x2.0)", 2.0
    elif 3 in counts and 2 in counts: return "葫蘆 (傷害 x1.5)", 1.5
    elif len(unique_vals) == 5 and (unique_vals[-1] - unique_vals[0] == 4): return "順子 (傷害 x2.5)", 2.5
    elif 3 in counts: return "三條 (傷害 x1.2)", 1.2
    elif counts.count(2) == 2: return "兩對 (傷害 x1.1)", 1.1
    elif 2 in counts: return "一對", 1.0
    else: return "高牌", 1.0

def basic_damage():
    kind, multiplier = evaluate_dice_pattern(dice_values)
    base_damage = sum(dice_values) + player_attack_bonus
    damage = int(base_damage * multiplier)
    if mango_bonus: damage += int(damage * 0.3)
    if player_attack_half: damage = max(damage // 2, 1)
    return damage

def check_enemy_dead():
    global enemy_hp, enemy_max_hp, battle_message, battle_round, roll_times, dice_values, enemy_name, enemy_phase, pending_original_enemy_hp, pending_original_enemy_max_hp
    if enemy_hp <= 0:
        try: enemy_dead_sound.play()
        except: pass
        if enemy_phase == "chengchen":
            enemy_name = "Boss" if MAP[Pr, Pc] == 9 else "菁英怪"
            enemy_phase = "original"
            enemy_max_hp = pending_original_enemy_max_hp
            enemy_hp = pending_original_enemy_hp
            pending_original_enemy_max_hp = 0
            pending_original_enemy_hp = 0
            battle_round = 1
            roll_times = 8
            dice_values = [random.randint(1, 6) for _ in range(5)]
            battle_message = "武術大師退場，原本的怪物回來了！"
        else:
            battle_message = "敵人已被擊敗！按 M 鍵返回地圖"

def reset_game():
    global Pr, Pc, Background, PlayerDeck, UsedRooms, SelectedWeapon, player_hp, enemy_hp, enemy_max_hp, battle_message, coin, PlayerSkills
    Pr, Pc = 11, 11
    Background = "MainMenu"
    player_hp = 30
    enemy_hp = 600
    enemy_max_hp = 600
    coin = 30
    PlayerSkills = []
    PlayerDeck = []
    UsedRooms.clear()
    battle_message = "新冒險開始"

# ==========================================
# 遊戲主循環管線
# ==========================================
running = True
while running:
    current_time_ms = pygame.time.get_ticks()

    # 計算滑鼠於 1024x768 虛擬畫布中的對應邏輯座標
    mx, my = pygame.mouse.get_pos()
    logical_mx = int(mx * (1024 / WIDTH))
    logical_my = int(my * (768 / HEIGHT))
    logical_mouse_pos = (logical_mx, logical_my)

    # UI 狀態即時更新
    for btn in side_btns:
        btn.update_hover(logical_mouse_pos)
        
    if show_settings:
        main_action_btn.update_hover(logical_mouse_pos)
        for rb in res_buttons:
            rb["is_hovered"] = rb["rect"].collidepoint(logical_mouse_pos)
    else:
        main_action_btn.is_hovered = False
        for rb in res_buttons:
            rb["is_hovered"] = False

    # 處理主選單 START 載入計時器
    if Background == "MainMenu" and enter_game_click_state == 1:
        if current_time_ms - state_1_start_time >= 2000:
            enter_game_click_state = 2
            Background = "StartWeapon"  # 進入核心玩法武器挑選畫面

    # 主選單武器預覽動態輪播
    if current_time_ms - last_weapon_switch_time >= 1500:
        current_weapon_idx = (current_weapon_idx + 1) % len(weapons_pool)
        last_weapon_switch_time = current_time_ms

    # --------------------------------------
    # 事件處理事件流的分流派發
    # --------------------------------------
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        for btn in side_btns: 
            btn.handle_event(event, logical_mouse_pos)

        # 優先級：高級選單交互處理
        if show_settings:
            main_action_btn.handle_event(event, logical_mouse_pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rb in res_buttons:
                    if rb["rect"].collidepoint(logical_mouse_pos):
                        SS = rb["ss"]
                        WIDTH, HEIGHT = rb["w"], rb["h"]
                        screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
                        assetsload(WIDTH, HEIGHT) # 動態刷新拉伸比例
                
                if partial_checkbox_rect.collidepoint(logical_mouse_pos):
                    partial_display_active = not partial_display_active

                input_active = input_rect.collidepoint(logical_mouse_pos)

            if hasattr(pygame, 'TEXTINPUT') and event.type == pygame.TEXTINPUT and input_active:
                if len(player_name) < 12: player_name += event.text

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif not hasattr(pygame, 'TEXTINPUT') and hasattr(event, 'unicode') and event.unicode.isprintable():
                    if len(player_name) < 12: player_name += event.unicode
            continue

        # 狀態分流：主選單事件流
        if Background == "MainMenu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if enter_game_click_state == 0 and enter_game_rect.collidepoint(logical_mouse_pos):
                    enter_game_click_state = 1
                    state_1_start_time = current_time_ms 

        # 狀態分流：核心遊戲局內事件流
        elif Background == "StartWeapon":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 簡單點擊區域選擇武器並切換至地圖
                if logical_mx < 340: SelectedWeapon = "gun"
                elif logical_mx < 680: SelectedWeapon = "whip"
                else: SelectedWeapon = "darius"
                Background = "Map"

        elif Background == "Map":
            if event.type == pygame.KEYDOWN:
                moved = False
                if event.key in [pygame.K_UP, pygame.K_w] and Pr > 0: Pr -= 1; moved = True
                if event.key in [pygame.K_DOWN, pygame.K_s] and Pr < 22: Pr += 1; moved = True
                if event.key in [pygame.K_LEFT, pygame.K_a] and Pc > 0: Pc -= 1; moved = True
                if event.key in [pygame.K_RIGHT, pygame.K_d] and Pc < 22: Pc += 1; moved = True
                
                if moved:
                    # 地圖房間隨機或遭遇固定戰鬥
                    if MAP[Pr, Pc] == 0:
                        MAP[Pr, Pc] = random.choice([2, 3, 7, 8, 9])
                    if MAP[Pr, Pc] in [7, 8, 9]:
                        Background = "Battle"
                        enemy_hp = 600 if MAP[Pr, Pc] == 7 else (1200 if MAP[Pr, Pc] == 8 else 3000)
                        enemy_max_hp = enemy_hp
                        battle_round = 1
                        roll_times = 8
                        battle_message = f"遭遇 {MAPListName[MAP[Pr, Pc]]}！按空白鍵擲骰"

        elif Background == "Battle":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and roll_times > 0 and not dice_rolling:
                dice_rolling = True
                dice_roll_timer = 15
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not dice_rolling:
                # 點擊發動攻擊
                dmg = basic_damage()
                enemy_hp -= dmg
                battle_message = f"你使出致命一擊，造成 {dmg} 點傷害！"
                roll_times -= 1
                check_enemy_dead()
                if roll_times == 0 and enemy_hp > 0:
                    # 怪物反擊
                    p_dmg = random.randint(1, 20)
                    player_hp -= p_dmg
                    battle_message += f" 怪物反擊造成 {p_dmg} 傷害！"
                    roll_times = 8
                    battle_round += 1
                    if player_hp <= 0: Background = "GameOver"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m and enemy_hp <= 0:
                Background = "Map"

        elif Background == "GameOver":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                reset_game()

    # --------------------------------------
    # 畫面渲染管線 Pipeline (全數繪製到畫布 canvas)
    # --------------------------------------
    canvas.fill(BLACK)

    if Background == "MainMenu":
        # 1. 主選單繪製
        canvas.blit(B019["主背景.png"], (0, 0))
        
        if enter_game_click_state == 0:
            start_toggle = (current_time_ms // 3000) % 2
            btn_color = (255, 210, 10) if start_toggle == 0 else (160, 40, 240)
            text_color = BLACK if start_toggle == 0 else WHITE
            
            safe_draw_rect(canvas, btn_color, enter_game_rect, border_radius=12)
            safe_draw_rect(canvas, WHITE, enter_game_rect, width=3, border_radius=12)
            
            start_text_surf = font_title.render("START", True, text_color)
            canvas.blit(start_text_surf, start_text_surf.get_rect(center=(enter_game_rect.centerx, enter_game_rect.centery - 2)))
            
            # 武器預覽輪播
            weapon_img = weapons_pool[current_weapon_idx]
            canvas.blit(weapon_img, (main_panel_rect.x + (main_panel_rect.width - weapon_img.get_width()) // 2, main_panel_rect.y + 80))
            
        elif enter_game_click_state == 1:
            display_str = "★ LOADING BATTLE... ★"
            surf_green = font_med.render(display_str, True, NEON_GREEN)
            canvas.blit(surf_green, surf_green.get_rect(center=(enter_game_rect.centerx, enter_game_rect.centery)))

    elif Background == "StartWeapon":
        canvas.blit(Asset_dict["choose_weapon_back"], (0, 0))
        draw_text("請選擇你的初始武器 (點擊左/中/右區域選擇)", 512, 100, font_big, WHITE)
        draw_text("手槍區域", 200, 400, font_med, LIGHT_BLUE)
        draw_text("鞭子區域", 512, 400, font_med, LIGHT_BLUE)
        draw_text("巨槌區域", 824, 400, font_med, LIGHT_BLUE)

    elif Background == "Map":
        canvas.blit(Asset_dict["b049gaming0-1"], (0, 0))
        draw_text(f"【冒險探索中】當前位置: ({Pr}, {Pc}) - 房間類型: {MAPListName[MAP[Pr, Pc]]}", 512, 50, font_med, WHITE)
        draw_text("使用 W、A、S、D 或方向鍵進行探索移動", 512, 100, font_small, GRAY)
        
        # 簡易渲染周圍局部小地圖
        for r in range(max(0, Pr-2), min(23, Pr+3)):
            for c in range(max(0, Pc-2), min(23, Pc+3)):
                bx, by = 412 + (c - Pc) * 45, 384 + (r - Pr) * 45
                color = (255, 50, 50) if (r == Pr and c == Pc) else (100, 100, 100) if MAP[r, c] > 0 else (30, 30, 30)
                pygame.draw.rect(canvas, color, (bx, by, 40, 40), border_radius=4)

    elif Background == "Battle":
        canvas.blit(Asset_dict["b118battle_bg"], (0, 0))
        
        # 處理骰子滾動動畫
        if dice_rolling:
            dice_values[selected_die_index] = random.randint(1, 6)
            dice_roll_timer -= 1
            if dice_roll_timer <= 0:
                dice_rolling = False
                selected_die_index = (selected_die_index + 1) % 5
                
        # 繪製五顆骰子
        for idx, val in enumerate(dice_values):
            draw_dice(180 + idx * 140, 500, 100, val)
            
        # 戰鬥血條與狀態文字
        draw_text(f"玩家生命: {player_hp} / 30", 250, 200, font_mid, NEON_GREEN)
        draw_text(f"{enemy_name}生命: {enemy_hp} / {enemy_max_hp}", 750, 200, font_mid, (255, 80, 80))
        draw_text(f"回合: {battle_round}  |  剩餘擲骰數: {roll_times}", 512, 300, font_med, WHITE)
        draw_text(battle_message, 512, 380, font_small, GRAY)
        draw_text("按【空白鍵】重骰當前骰子，【滑鼠左鍵】點擊任意處發動技能攻擊！", 512, 680, font_small, WHITE)

    elif Background == "GameOver":
        canvas.fill((20, 0, 0))
        draw_text("你被擊敗了！", 512, 300, font_big, (255, 80, 80))
        draw_text("重新遊戲請按 P 鍵", 512, 450, font_mid, WHITE)

    # 2. 右上角功能選單按鈕常駐繪製
    for btn in side_btns: 
        btn.draw(canvas)

    # 3. 玩家 ID 常駐顯示模組 (左下角)
    if has_saved:
        info_rect = pygame.Rect(20, 698, 280, 50)
        if not partial_display_active:
            info_surf = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
            info_surf.fill((15, 22, 35, 200))  
            safe_draw_rect(info_surf, (90, 120, 160), info_surf.get_rect(), width=2, border_radius=8) 
            canvas.blit(info_surf, info_rect)
            info_text = font_med.render(f"玩家: {saved_player_name}", True, WHITE)
            canvas.blit(info_text, (info_rect.x + 15, info_rect.y + (info_rect.height - info_text.get_height()) // 2))
        else:
            info_text = font_med.render(f"👤 {saved_player_name}", True, NEON_GREEN)
            canvas.blit(info_text, (info_rect.x + 10, info_rect.y + (info_rect.height - info_text.get_height()) // 2))

    # 4. 高級設置選單模組浮層
    if show_settings:
        panel_surf = pygame.Surface((main_panel_rect.width, main_panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill(TRANSPARENT_BLACK)
        safe_draw_rect(panel_surf, (100, 120, 150), panel_surf.get_rect(), width=3, border_radius=14)
        canvas.blit(panel_surf, main_panel_rect)

        title_surf = font_title.render("遊戲設置選單", True, WHITE)
        canvas.blit(title_surf, title_surf.get_rect(center=(main_panel_rect.centerx, main_panel_rect.y + 55)))

        canvas.blit(name_label, (px, py + (input_rect.height - name_label.get_height()) // 2))
        safe_draw_rect(canvas, (245, 245, 250), input_rect, border_radius=6)
        safe_draw_rect(canvas, LIGHT_BLUE if input_active else BLUE, input_rect, width=3, border_radius=6)
        
        if player_name != "":
            name_surf = font_med.render(player_name, True, BLACK)
            canvas.blit(name_surf, (input_rect.x + 12, input_rect.y + (input_rect.height - name_surf.get_height()) // 2))

        canvas.blit(res_label, (px, res_start_y + (32 - res_label.get_height()) // 2))
        for rb in res_buttons:
            btn_bg_color = (40, 120, 220) if rb["w"] == WIDTH else ((60, 75, 100) if rb["is_hovered"] else (45, 50, 65))
            safe_draw_rect(canvas, btn_bg_color, rb["rect"], border_radius=6)
            safe_draw_rect(canvas, NEON_GREEN if rb["w"] == WIDTH else (WHITE if rb["is_hovered"] else GRAY), rb["rect"], width=2, border_radius=6)
            txt_surf = font_small.render(rb["label"], True, WHITE)
            canvas.blit(txt_surf, txt_surf.get_rect(center=rb["rect"].center))

        canvas.blit(partial_label, (px, partial_checkbox_rect.y + (32 - partial_label.get_height()) // 2))
        safe_draw_rect(canvas, (45, 50, 65), partial_checkbox_rect, border_radius=4)
        safe_draw_rect(canvas, GRAY, partial_checkbox_rect, width=2, border_radius=4)
        if partial_display_active:
            safe_draw_rect(canvas, NEON_GREEN, partial_checkbox_rect.inflate(-12, -12), border_radius=2)

        main_action_btn.draw(canvas)

    # 5. 滑鼠自訂彩色光標渲染管線層 (置於最上層貼合渲染)
    any_hovered = any(btn.is_hovered for btn in side_btns) or main_action_btn.is_hovered or any(rb["is_hovered"] for rb in res_buttons)
    if show_settings:
        any_hovered = any_hovered or partial_checkbox_rect.collidepoint(logical_mouse_pos)
    else:
        if Background == "MainMenu" and enter_game_click_state == 0 and enter_game_rect.collidepoint(logical_mouse_pos):
            any_hovered = True
            
    is_mouse_clicking = pygame.mouse.get_pressed()[0]
    current_cursor_pos = cursor_manager.update(logical_mouse_pos, any_hovered, is_mouse_clicking)
    cursor_manager.draw(canvas, current_cursor_pos)

    # ==========================================
    # 視窗等比例投射與畫面刷新刷新
    # ==========================================
    screen.blit(pygame.transform.scale(canvas, (WIDTH, HEIGHT)), (0, 0))

    pygame.event.pump()
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1

pygame.quit()
sys.exit()