#VERSION16
import pygame
import numpy as np
import random
import os
import sys
import unicodedata

# ==========================================
# 核心修正：跨平台雙軌智慧模糊路徑鎖定系統
# ==========================================
# 同時捕捉 VS Code 啟動時的根目錄與腳本實際目錄，雙重保障素材搜尋路徑
ORIGINAL_CWD = os.getcwd() 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

print(f"🚀 [路徑追蹤] 腳本所在真實目錄: {BASE_DIR}")
print(f"🚀 [路蹤追蹤] VS Code 目前工作目錄: {ORIGINAL_CWD}")

def safe_load_image(filename, width, height):
    """
    🛡️ 全自動特徵檢索載入核心：
    1. 修正 Mac / Windows 中文字元（NFC/NFD）編碼不一致導致找不到檔案的問題。
    2. 同時遍歷腳本資料夾與 VS Code 專案工作區，不論素材怎麼放都能順利匯入。
    3. 自動模糊匹配帶有去背後綴（如 -removebg-preview）或副檔名不符的圖檔。
    """
    def clean_str(s):
        return unicodedata.normalize('NFC', str(s)).lower().strip()
    
    target_clean = clean_str(filename)
    target_core = os.path.splitext(target_clean)[0]
    
    # 核心特徵碼交叉對照表
    feature_map = {
        "主背景": ["主背景", "main_bg", "主畫面"],
        "戰鬥背景": ["戰鬥背景", "battle_bg"],
        "鼠標1": ["鼠標1", "1_彩色", "cursor1"],
        "鼠標2": ["鼠標2", "2_彩色", "cursor2"],
        "鼠標3": ["鼠標3", "3_彩色", "cursor3"],
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

    # 多重防線路徑搜尋集
    search_dirs = [BASE_DIR, ORIGINAL_CWD, os.path.join(ORIGINAL_CWD, ".."), "."]
    
    # 【第一防線】標準精準檔名匹配
    for sd in search_dirs:
        if os.path.exists(sd):
            try:
                for f in os.listdir(sd):
                    if clean_str(f) == target_clean:
                        full_p = os.path.join(sd, f)
                        return pygame.transform.smoothscale(pygame.image.load(full_p).convert_alpha(), (width, height))
            except:
                pass

    # 【第二防線】跨平台智慧特徵碼模糊匹配
    for sd in search_dirs:
        if os.path.exists(sd):
            try:
                for f in os.listdir(sd):
                    norm_f = clean_str(f)
                    # 只要包含任一特徵關鍵字，且是常見圖片格式，即視為目標素材載入
                    if any(token in norm_f for token in active_tokens) and norm_f.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        full_p = os.path.join(sd, f)
                        print(f"🎯 [特徵識別成功] 實體檔案「{f}」已成功配對匯入！")
                        return pygame.transform.smoothscale(pygame.image.load(full_p).convert_alpha(), (width, height))
            except:
                pass

    # 【第三防線】向量科技感防崩潰保底層 (若遺失檔案，自動繪製去背素材，拒絕顯示死板方框)
    fallback = pygame.Surface((width, height), pygame.SRCALPHA)
    if "鼠標" in filename or "cursor" in filename:
        color = (50, 255, 100) if "1" in filename else ((255, 220, 30) if "2" in filename else (255, 40, 40))
        pts = [(0, 0), (int(width * 0.75), int(height * 0.45)), (int(width * 0.45), int(height * 0.55)), (int(width * 0.25), int(height * 0.85))]
        pygame.draw.polygon(fallback, color, pts)
        pygame.draw.polygon(fallback, (255, 255, 255), pts, width=2)
        return fallback
    elif any(x in filename for x in ["長槍", "雙刃劍", "盾牌"]):
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
# Pygame 系統初始化與虛擬畫布配置
# ==========================================
pygame.init()
pygame.font.init() 

WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('迷因大亂鬥 - 完美整合版')
clock = pygame.time.Clock()

# 🎯 虛擬畫布配置：所有 UI 與畫面元件皆以此 1024x768 解析度為基準進行渲染
canvas = pygame.Surface((1024, 768))

# --- 顏色定義 ---
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

# --- 中文字體智慧安全相容系統 ---
def get_font(size):
    preferred_fonts = ["microsoftjhenghei", "notosanstc", "pingfangtc", "simhei", "stxihei"]
    for name in preferred_fonts:
        try:
            font = pygame.font.SysFont(name, size)
            if font: return font
        except:
            continue
    return pygame.font.SysFont(None, size)

font_med = get_font(24)
font_title = get_font(42)  
font_small = get_font(16)

# ==========================================
# 資源載入配置 (✨ 核心優化字典區塊)
# ==========================================
print("\n--- 📝 開始執行智慧化遊戲素材資源載入 ---")

B019 = {
    # 1. 滿版背景素材 (精確對應：主背景.png 與 戰鬥背景.png)
    "主背景.png": safe_load_image("主背景.png", 1024, 768),
    "戰鬥背景.png": safe_load_image("戰鬥背景.png", 1024, 768),
    
    # 2. 文字面板去背元件
    "答應_文字.png": safe_load_image("答應_文字-removebg-preview.png", 150, 50),
    "拒絕_文字.png": safe_load_image("拒絕_文字-removebg-preview.png", 150, 50),
    
    # 3. 三段式動態自訂彩色游標素材 (徹底解決方框問題)
    "鼠標_一般.png": safe_load_image("鼠標1_彩色-removebg-preview.png", 45, 45),
    "鼠標_懸置.png": safe_load_image("鼠標2_彩色-removebg-preview.png", 45, 45),
    "_鼠標_點擊.png": safe_load_image("鼠標3_彩色-removebg-preview.png", 45, 45),
    
    # 4. 右側輪播武器素材
    "長槍.png": safe_load_image("長槍.png", 150, 150),
    "雙刃劍.png": safe_load_image("雙刃劍.png", 150, 150),
    "盾牌.png": safe_load_image("盾牌.png", 150, 150)
}

weapons_pool = [B019["長槍.png"], B019["雙刃劍.png"], B019["盾牌.png"]]
print("--- 🎉 遊戲素材環境雙軌配置成功 ---\n")

current_weapon_idx = random.randint(0, len(weapons_pool) - 1)
last_weapon_switch_time = pygame.time.get_ticks() 
state_1_start_time = 0                           

# 徹底關閉原廠系統滑鼠游標
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
# 狀態控制核心與變數
# ==========================================
show_settings = False          
enter_game_click_state = 0 # 0: 主頁面, 1: 轉場過渡載入中, 2: 切換至純淨戰鬥背景.png    
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
# 元件佈局初始化 (座標鎖定於 1024x768 基準)
# ==========================================
cursor_manager = CursorManager(B019["鼠標_一般.png"], B019["鼠標_懸置.png"], B019["_鼠標_點擊.png"])
main_panel_rect = pygame.Rect(1024 * 0.4, 768 * 0.1, 1024 * 0.55, 768 * 0.85)

# 高級設置按鈕配置 (右上角)
side_btns = []
icon_surface_3 = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(icon_surface_3, WHITE, (12, 12), 10, width=2)
left_btn_3 = SideIconButton(830, 20, icon_surface_3, "高級設置", bg_color=(70, 80, 90), action=open_settings_menu)
side_btns.append(left_btn_3)

# 右側面板基礎參數
px = main_panel_rect.x + 40
py = main_panel_rect.y + 200 

name_label = font_med.render("玩家名稱:", True, WHITE)
input_rect = pygame.Rect(px + 120, py, 300, 40)
player_name = ""

res_options = [
    {"label": "720x540", "w": 720, "h": 540},
    {"label": "1024x768", "w": 1024, "h": 768},
    {"label": "1080x810", "w": 1080, "h": 810},
    {"label": "1920x1440", "w": 1920, "h": 1440}
]
res_label = font_med.render("螢幕尺寸:", True, WHITE)
res_buttons = []
res_start_x = px + 100  
res_start_y = py + 80

for i, opt in enumerate(res_options):
    res_buttons.append({
        "rect": pygame.Rect(res_start_x + (i * 92), res_start_y, 82, 32), 
        "w": opt["w"], "h": opt["h"], "label": opt["label"], "is_hovered": False
    })

partial_label = font_med.render("部分顯示:", True, WHITE)
partial_checkbox_rect = pygame.Rect(px + 100, py + 145, 32, 32)

# 🎯 需求 3 修正：原按鈕圖檔邏輯完全刪除。此處為純程式碼繪製 START 按鈕的觸發熱區
enter_game_rect = pygame.Rect(main_panel_rect.centerx - 130, main_panel_rect.centery + 120, 260, 65)

# 保存設定按鈕
save_btn_w = 220
save_btn_h = 48
main_action_btn = Button(main_panel_rect.centerx - save_btn_w // 2, main_panel_rect.bottom - save_btn_h - 50, save_btn_w, save_btn_h, "保存設定", save_settings_data)

# ==========================================
# 遊戲主迴圈
# ==========================================
running = True
while running:
    current_time_ms = pygame.time.get_ticks()

    # 滑鼠實體座標對應到邏輯畫布的縮放投射轉換
    mx, my = pygame.mouse.get_pos()
    logical_mx = int(mx * (1024 / WIDTH))
    logical_my = int(my * (768 / HEIGHT))
    logical_mouse_pos = (logical_mx, logical_my)

    # 影格即時懸停狀態判定
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

    # 🎯 需求 4 修正：點擊 START 進入過渡狀態 1 後，滿 2000 毫秒 (2秒) 自動無縫切換至戰鬥畫面
    if enter_game_click_state == 1:
        if current_time_ms - state_1_start_time >= 2000:
            enter_game_click_state = 2

    # 武器輪播間隔計時控制
    if current_time_ms - last_weapon_switch_time >= 1500:
        current_weapon_idx = (current_weapon_idx + 1) % len(weapons_pool)
        last_weapon_switch_time = current_time_ms

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
        for btn in side_btns: 
            btn.handle_event(event, logical_mouse_pos)
            
        if show_settings:
            main_action_btn.handle_event(event, logical_mouse_pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rb in res_buttons:
                    if rb["rect"].collidepoint(logical_mouse_pos):
                        WIDTH, HEIGHT = rb["w"], rb["h"]
                        screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
                
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
        else:
            # 監聽全新高質感 START 按鈕的點擊事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if enter_game_click_state == 0 and enter_game_rect.collidepoint(logical_mouse_pos):
                    enter_game_click_state = 1
                    state_1_start_time = current_time_ms 

    # --------------------------------------
    # 畫面渲染繪製 Pipeline (繪製到虛擬畫布 canvas)
    # --------------------------------------
    
    # 1. 根據狀態分流繪製滿版背景圖層
    if enter_game_click_state == 2:
        # ✨ 完美修正：此處僅渲染乾淨滿版的「戰鬥背景.png」，原有的 ROUND FIGHT 文字覆蓋邏輯已徹底移除！
        canvas.blit(B019["戰鬥背景.png"], (0, 0)) 
    else:
        # 順利載入並顯示「主背景.png」
        canvas.blit(B019["主背景.png"], (0, 0))        

    # 2. 將功能選單按鈕常駐繪製在右上角
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

    # 4. 右側主交互面板渲染邏輯
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
        
    elif enter_game_click_state < 2:
        # 🎯 需求 3 修正：使用純程式碼渲染每 3 秒自動在 耀眼金黃 與 霓虹幻紫 之間完美切換的 START 圓角按鈕
        if enter_game_click_state == 0:
            start_toggle = (current_time_ms // 3000) % 2
            btn_color = (255, 210, 10) if start_toggle == 0 else (160, 40, 240)
            text_color = BLACK if start_toggle == 0 else WHITE
            
            safe_draw_rect(canvas, btn_color, enter_game_rect, border_radius=12)
            safe_draw_rect(canvas, WHITE, enter_game_rect, width=3, border_radius=12)
            
            start_text_surf = font_title.render("START", True, text_color)
            canvas.blit(start_text_surf, start_text_surf.get_rect(center=(enter_game_rect.centerx, enter_game_rect.centery - 2)))
            
        elif enter_game_click_state == 1:
            # 點擊 START 後、在切換背景前的 2 秒內，呈現加載文字特效
            display_str = "★ LOADING BATTLE... ★"
            surf_green = font_med.render(display_str, True, NEON_GREEN)
            canvas.blit(surf_green, surf_green.get_rect(center=(enter_game_rect.centerx, enter_game_rect.centery)))  

        # 武器輪播元件渲染
        if enter_game_click_state == 0:
            weapon_img = weapons_pool[current_weapon_idx]
            canvas.blit(weapon_img, (main_panel_rect.x + (main_panel_rect.width - weapon_img.get_width()) // 2, main_panel_rect.y + 80))

    # 5. 滑鼠光標最上層無損貼合渲染 Pipeline (完美顯示自訂彩色鼠標)
    any_hovered = any(btn.is_hovered for btn in side_btns) or main_action_btn.is_hovered or any(rb["is_hovered"] for rb in res_buttons)
    if show_settings:
        any_hovered = any_hovered or partial_checkbox_rect.collidepoint(logical_mouse_pos)
    else:
        if enter_game_click_state == 0 and enter_game_rect.collidepoint(logical_mouse_pos):
            any_hovered = True
            
    is_mouse_clicking = pygame.mouse.get_pressed()[0]
    current_cursor_pos = cursor_manager.update(logical_mouse_pos, any_hovered, is_mouse_clicking)
    cursor_manager.draw(canvas, current_cursor_pos)

    # ==========================================
    # 視窗等比例投射縮放刷新
    # ==========================================
    screen.blit(pygame.transform.scale(canvas, (WIDTH, HEIGHT)), (0, 0))

    pygame.event.pump()
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1

pygame.quit()
sys.exit()