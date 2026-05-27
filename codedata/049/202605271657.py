import pygame
import numpy as np
import random
import os
import sys

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
SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,810),(4,1920,1440),(0,2880,2160)]
SS = 3
WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]/getsysscaling()), int(SCREEN_SIZE[SS][2]/getsysscaling())
FPS = 60
Pr,Pc = 11,11
PlayerV = 5.0
Background = "Map" #這個是到時候切背景可以改的東東
Global_Time = 0 #系統級時間碼，暫停的時候會暫停
Anim_Time = {} #各動畫時間碼專用辭典
BackHistory = [] #紀錄頁面類型跳轉歷史，方便esc返回
MAPListName = ["無","出生點","小寶箱","闖關區","大寶箱","交易所","零和遊戲","菁英怪","整備區","Boss"]

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
pygame.display.set_caption('迷因大亂鬥')
clock = pygame.time.Clock()

#圖檔載入
def assetsload(WIDTH,HEIGHT):
    '''圖檔尺寸、載入刷新'''
    global MAPList
    MAPList = [] #地圖類型背景庫
    for i in range(1,10): #共1~9種房間的底圖
        MAPList.append(pygame.transform.scale(pygame.image.load(os.path.join("assets", f'map{str(i)}.png')).convert(), (WIDTH, HEIGHT)))
    global Asset_dict
    Asset_dict = {
        "b049anim_room1":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049anim_room1.png")).convert_alpha(), (int(WIDTH / 5 * 2), int(WIDTH / 25 * 2))),
        "b049setting":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049setting.png")).convert_alpha(), (int(WIDTH / 20), int(WIDTH / 20))),
        "xesc":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","xesc.png")).convert_alpha(), (int(WIDTH / 20), int(WIDTH / 20))),
        "b049settingback":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background","b049settingback.png")).convert_alpha(), (WIDTH, HEIGHT)),
        "b049settingb":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049settingb.png")).convert_alpha(), (int(WIDTH / 5 * 1.5), int(WIDTH / 25 * 1.5))),
        "b049roomcenter8":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049roomcenter8.png")).convert_alpha(), (int(WIDTH / 8), int(WIDTH / 8))),
        "b049roomcenter7":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Enemy","Golem.png")).convert_alpha(), (int(WIDTH / 3), int(HEIGHT / 4))),
        "b049roomcload3-1":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049roomcload3-1.png")).convert_alpha(), (int(WIDTH / 3), int(HEIGHT / 3))),
        "b049roomcload3-2":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049roomcload3-2.png")).convert_alpha(), (int(WIDTH), int(HEIGHT))),
        "b049gaming0-1":pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict","b049gaming0-1.png")).convert_alpha(), (int(WIDTH), int(HEIGHT))),
    }
    for i in range(1,7):
        Asset_dict[f'b049roomcenter{i}'] = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","animdict",f'b049roomcenter{i}.png')).convert_alpha(), (int(WIDTH / 8), int(WIDTH / 8)))
    for j in range(0,1):
        Asset_dict[f'b049gaming{j}'] = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets","Background",f'b049gaming{j}.png')).convert_alpha(), (WIDTH, HEIGHT))
    return MAPList, Asset_dict

MAPList, Asset_dict = assetsload(WIDTH,HEIGHT)

#字體載入
FHeadPath = os.path.join("assets","font","NotoSansTC-Bold.ttf") #粗字
FTextPath = os.path.join("assets","font","NotoSansTC-Light.ttf") #細字

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
        """
        檢查自己是否碰觸到目標物件（例如 roomcenter）
        """
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
        self.rect.center = rec
    def touch(self):
        global mapused
        global Anim_Time
        if MAP[Pr,Pc] == 2 or MAP[Pr,Pc] == 4:
            mapused = True
            Anim_Time['AnimRoomCenter2'] = 1 * FPS
        if MAP[Pr,Pc] == 3:
            mapused = True
            Anim_Time['AnimRoomCenter3'] = 4 * FPS
        if MAP[Pr,Pc] == 6:
            mapused = True
            Anim_Time['AnimRoomCenter6'] = 4 * FPS
        if MAP[Pr,Pc] == 8:
            mapused = True
            Anim_Time['AnimRoomCenter8'] = 1 * FPS

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

def event(head,color,text):
    """地圖事件觸發"""
    return True

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
    global Gamekind
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
            Gamekind = random.randint(0,0)
            Background = "Gaming"
    elif tick <= 240:
        Allblack.set_alpha((240-tick)*8.5)
        screen.blit(Allblack, (0, 0))

def Anim_RoomCenter6(): #這裡要改(零和遊戲區)
    global Allblack
    global Background
    global Gamekind
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
            Gamekind = random.randint(0,0)
            Background = "Betting"
    elif tick <= 240:
        Allblack.set_alpha((240-tick)*8.5)
        screen.blit(Allblack, (0, 0))

def Anim_RoomCenter8():
    rec= pygame.Rect(WIDTH / 2, HEIGHT / 2, WIDTH / 160 * (60-Anim_Time['AnimRoomCenter8']), HEIGHT / 120 * (60-Anim_Time['AnimRoomCenter8']))
    rec.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (0, 255, 0), rec, int(max(HEIGHT / 60, 1)))

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
        if event.type == pygame.MOUSEBUTTONDOWN: #按鈕點擊判定區
            if event.button == 1:
                mouse_pos = event.pos
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
                        MAPList, Asset_dict = assetsload(WIDTH,HEIGHT)
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
                MAP[Pr,Pc] = random.randint(2,6) #傳送瞬間去改 Numpy 陣列，隨機判定房間類型，這裡不處理精英怪、整備、Boss，這幾個交給RoomStep處理
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

    if player.check_trigger(roomcenter) and not mapused: #碰撞區
        print("玩家碰到交互物品roomcenter")
        roomcenter.touch()
    
    #顯示區
    if Background == "Map":
        screen.blit(MAPList[int(MAP[Pr,Pc])-1], (0, 0))
        gates_group.draw(screen)
        screen.blit(player.image, player.rect)
        screen.blit(b049setting.image, b049setting.rect)
        if MAP[Pr,Pc] != 1 and not mapused:
            screen.blit(roomcenter.image, roomcenter.rect)
        #小地圖
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH * 0.41 / 4 , HEIGHT * 0.41 / 3),WIDTH * 18 / 240)
        miniMap()
    if Background == "X_Ingame_Settings":
        screen.blit(Asset_dict["b049settingback"], (0, 0))
        screen.blit(b049settingb.image, b049settingb.rect)
        b049settingb.update(WIDTH,HEIGHT)
        screen.blit(xesc.image, xesc.rect)
    if Background == "Gaming": #這裡要改，闖關區
        screen.blit(Asset_dict[f'b049gaming{Gamekind}'], (0, 0))
        if Gamekind == 0:
            screen.blit(Asset_dict[f'b049gaming0-1'], (pygame.mouse.get_pos()[0]-WIDTH/2,max(pygame.mouse.get_pos()[1]-HEIGHT/2,0)))
    if Background == "Betting": #這裡要改，零和遊戲
        screen.blit(Asset_dict[f'b049gaming{Gamekind}'], (0, 0))
    
    Animation()
    clock.tick(FPS)
    pygame.display.flip()
    Global_Time += 1
    for Akey in Anim_Time.keys(): #動畫時間碼衰減
        if Anim_Time[Akey] > 0:
            Anim_Time[Akey] -= 1

pygame.quit()