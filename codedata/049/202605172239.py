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