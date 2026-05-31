#第二版
import pygame
import numpy as np
import random
import os
import sys
import math
import time
import unicodedata  # 整合自第二個檔案，並統一改為第一個檔案的單行引用格式

# 運行路徑鎖死到py檔同層與雙軌智慧路徑鎖定 By AI
ORIGINAL_CWD = os.getcwd()  # 整合自第二個檔案，保留跨平台工作目錄追蹤
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
print(f'目前遊戲的絕對路徑已鎖定在：{os.getcwd()}')
print(f'VS Code 目前工作目錄：{ORIGINAL_CWD}')

# ==========================================
# 工具函式整合區
# ==========================================

# 系統縮放取得（第一個檔案）
def getsysscaling():
    if sys.platform == "darwin":  # macOS 的系統代號
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

# 全自動特徵檢索載入核心（整合自第二個檔案，改用第一個檔案的單引號風格與排版）
def safe_load_image(filename, width, height):
    """
    🛡️ 全自動特徵檢索載入核心：
    1. 修正 Mac / Windows 中文字元編碼不一致問題。
    2. 自動模糊匹配帶有去背後綴或副檔名不符的圖檔。
    """
    def clean_str(s):
        return unicodedata.normalize('NFC', str(s)).lower().strip()
    
    target_clean = clean_str(filename)
    target_core = os.path.splitext(target_clean)[0]
    
    # 核心特徵碼交叉對照表
    feature_map = {
        '主背景': ['主背景', 'main_bg', '主畫面'],
        '戰鬥背景': ['戰鬥背景', 'battle_bg'],
        '鼠標1': ['鼠標1', '1_彩色', 'cursor1'],
        '鼠標2': ['鼠標2', '2_彩色', 'cursor2'],
        '鼠標3': ['鼠標3', '3_彩色', 'cursor3'],
        '答應_文字': ['答應_文字', '答應'],
        '拒絕_文字': ['拒絕_文字', '拒絕']
    }
    
    active_tokens = []
    for core_key, tokens in feature_map.items():
        if core_key in filename:
            active_tokens = tokens
            break
    if not active_tokens:
        active_tokens = [target_core]

    # 多重防線路徑搜尋集
    search_dirs = [BASE_DIR, ORIGINAL_CWD, os.path.join(ORIGINAL_CWD, '..'), '.']
    
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
                    if any(token in norm_f for token in active_tokens) and norm_f.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        full_p = os.path.join(sd, f)
                        print(f'🎯 [特徵識別成功] 實體檔案「{f}」已成功配對匯入！')
                        return pygame.transform.smoothscale(pygame.image.load(full_p).convert_alpha(), (width, height))
            except:
                pass

    # 【第三防線】向量科技感防崩潰保底層
    fallback = pygame.Surface((width, height), pygame.SRCALPHA)
    if '鼠標' in filename or 'cursor' in filename:
        color = (50, 255, 100) if '1' in filename else ((255, 220, 30) if '2' in filename else (255, 40, 40))
        pts = [(0, 0), (int(width * 0.75), int(height * 0.45)), (int(width * 0.45), int(height * 0.55)), (int(width * 0.25), int(height * 0.85))]
        pygame.draw.polygon(fallback, color, pts)
        pygame.draw.polygon(fallback, (255, 255, 255), pts, width=2)
        return fallback
    elif any(x in filename for x in ['長槍', '雙刃劍', '盾牌']):
        pygame.draw.circle(fallback, (70, 140, 240, 120), (width // 2, height // 2), width // 3)
        pygame.draw.circle(fallback, (255, 255, 255), (width // 2, height // 2), width // 3, width=2)
        return fallback

    fallback.fill((30, 45, 65))
    pygame.draw.rect(fallback, (70, 135, 240), (0, 0, width, height), width=4)
    return fallback

# 安全矩形繪製（第二個檔案）
def safe_draw_rect(surface, color, rect, width=0, border_radius=0):
    try:
        if border_radius > 0 and hasattr(pygame.draw, 'rect'):
            pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)
        else:
            pygame.draw.rect(surface, color, rect, width)
    except TypeError:
        pygame.draw.rect(surface, color, rect, width)

# ==========================================
# 系統初始化與視窗設定區
# ==========================================
pygame.init()
pygame.mixer.init()
pygame.font.init()

# 解析度與縮放配置（結合第一個檔案的動態選單與第二個檔案的基準）
SCREEN_SIZE = [(1, 480, 360), (2, 720, 540), (3, 1080, 810), (4, 1920, 1440), (0, 2880, 2160)]
SS = 3

# BIOS MODE 啟動偵測畫面（第一個檔案）
screen = pygame.display.set_mode((1000, 1000))
img = pygame.font.Font(os.path.join('assets', 'font', 'NotoSansTC-Bold.ttf'), 36).render('BIOS MODE', True, (255, 255, 255))
imgr = img.get_rect()
imgr.center = (500, 500)
screen.blit(img, imgr)
pygame.display.flip()
time.sleep(1)

pygame.event.pump()
keys = pygame.key.get_pressed()
if keys[pygame.K_1]: SS = 1
elif keys[pygame.K_2]: SS = 2
elif keys[pygame.K_3]: SS = 3
elif keys[pygame.K_4]: SS = 4

# 計算最終實體視窗大小
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1] / getsysscaling()), int(SCREEN_SIZE[SS][2] / getsysscaling())
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('骰子迷因大亂鬥 - 完美整合版')
clock = pygame.time.Clock()

# 虛擬基礎畫布配置（整合自第二個檔案，用於 UI 渲染標準對齊）
canvas = pygame.Surface((1024, 768))

# ==========================================
# 遊戲變數初始化（請依序在此處黏貼原本的卡牌、戰鬥與地圖生成變數）
# ==========================================
# （此處省略原 001-202605311555.py 的大量變數定義，如 PlayerSkills, Enemy_hp 等...）