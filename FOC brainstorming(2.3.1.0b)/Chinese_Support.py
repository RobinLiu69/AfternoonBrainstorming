from variable import *
import pygame

def drawText(text: str, font: pygame.font.Font, textColor: tuple[int, int, int], x: int, y: int, screen: pygame.surface.Surface) -> None:
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))
    
def split_lines(s: str) -> list[str]:
    return s.split('\n')

libary = {"ADCW":"5/4-長十字", 
          "APW":"4/3-單體最近/攻擊附帶麻痺",
          "TANKW":"15/1-小十字",
          "HFW":"9/2-九宮格", 
          "LFW":"7/3-小十字", 
          "APTW":"8/2-單體最近/攻擊為自己及最近友方附加兩點\n護盾", 
          "SPW":"1/5-單體最遠/每回合額外多得一分", 
          "ASSW":"2/5-斜十字",
          "ADCR":"4/1-長十字/造成傷害後+1攻擊力", 
          "APR":"3/2-單體最近/攻擊附帶麻痺並偷取敵方一半攻擊\n力",
          "TANKR":"9/1-小十字/承受傷害後為最近隊友附加n點護\n盾",
          "HFR":"9/1-九宮格/紅重裝效果改為每次造成傷害則減少\n1點血且獲得1點攻擊且此傷害不會直接使紅重裝死亡而\n是延遲至回合結束(其不會獲得分數)", 
          "LFR":"5/2-小十字/造成傷害後+1/+1", 
          "APTR":"6/2-單體最近/攻擊給自己及最近隊友+1/+1", 
          "SPR":"1/2-單體最遠/所有紅色系所獲得的增益都會疊加\n在他身上", 
          "ASSR":"2/4-斜十字/斬殺敵人後為最近隊友攻擊力+2",
          "ADCB":"4/2-長十字/利用藍球抽牌後會自動攻擊 若當下\n為麻痹效果則解除麻痹但不攻擊 斬殺後獲得1點藍球", 
          "APB":"4/2-單體最近/攻擊附帶麻痺並獲得兩顆藍球",
          "TANKB":"10/1-小十字/承受傷害後會獲得一顆藍球",
          "HFB":"8/2-九宮格/攻擊以現有藍球造成額外傷害", 
          "LFB":"6/3:小十字/造成傷害會獲得一顆藍球", 
          "APTB":"5/3-單體最近/獲得藍球時會獲得1護盾 攻擊時\n每4點護盾獲得1顆藍球", 
          "SPB":"1/5-單體最遠/放置時對隨機敵人造成一點傷害重\n複(我方棄牌堆+我方場上堆)次", 
          "ASSB":"2/4-斜十字/斬殺後獲得兩顆藍球",
          "ADCG":"3/3-長十字/攻擊後會在攻擊範圍內50%生成幸\n運寶箱", 
          "APG":"3/2-單體最近/攻擊附帶麻痺和依幸運值隨機壞運\n效果 並依幸運值獲得隨機好運效果或無",
          "TANKG":"10/1-小十字/承受傷害後為敵方附加壞運效果\n或無",
          "HFG":"8/1-九宮格/破壞方塊會增加5%運氣值並隨機位置\n放一個幸運方塊", 
          "LFG":"6/2:小十字/破壞幸運方塊後50%返還刀", 
          "APTG":"6/0-單體最近/攻擊後會將小十字內的空格放上\n幸運方塊 自己每放置方塊獲得1點護盾", 
          "SPG":"?/?-單體最遠/運氣值永久增加10% 隨機位置放置\n(每十個幸運值(需大於五十))個幸運方塊(血量絕對不\n是1,攻擊絕對不是5)", 
          "ASSG":"2/4-斜十字/斬殺後獲得5%運氣值且敵方運氣值\n減少5%",
          "ADCO":"5/2-長十字/攻擊後可移動,該移動後會自動攻擊", 
          "APO":"3/2-單體最近/攻擊附帶麻痺 回合開始會獲得一\n個本回合可使用的移動魔法牌",
          "TANKO":"10/1-小十字/承受傷害後會獲得一個本回合可\n使用的移動魔法牌",
          "HFO":"9/1-九宮格/攻擊後可移動並獲得+1攻擊力 回合\n結束會消失", 
          "LFO":"6/3-小十字/攻擊後可移動並對單體最近再次造成\n傷害", 
          "APTO":"6/0-單體最近/隊友移動後為自己及移動友方附\n加一點護盾 自身移動則自己加一點護盾(先) 自身移動\n後護盾以2比1轉為攻擊力(後)", 
          "SPO":"1/5-單體最遠/隊友移動後對單體最遠造成3點傷\n害", 
          "ASSO":"2/4-斜十字/斬殺後可移動並進入狂暴\n狂暴狀態下斬殺會返回刀並解除狀態",
          "ADCDKG":"5/1-長十字/攻擊時額外造成圖騰的攻擊力的\n1/3的傷害", 
          "APDKG":"3/3-單體最近/攻擊刻印5層",
          "TANKDKG":"9/1-小十字/受到傷害刻印2 ",
          "HFDKG":"8/2-九宮格/取造成的傷害量的血量 回合開始\n時扣2刻印2", 
          "LFDKG":"6/3:小十字/置時對攻擊範圍內敵人造成圖騰血\n量1/4傷害 攻擊依範圍內每單位獲得2刻印", 
          "APTDKG":"6/0-攻擊時依序觸發:額外造成圖騰的攻擊力\n的1/2的傷害、獲得護盾量1/2的刻印層數、獲得造成\n傷害的1/2的護盾", 
          "SPDKG":"1/5-將圖騰數值轉移到其身上 死亡時 刻印(攻\n擊力)量", 
          "ASSDKG":"2/4-斜十字/斬殺後死亡 刻印6",
          "ADCP":1, 
          "APP":"3/1-單體最近/攻擊附帶麻痺、破盾並將攻擊力降\n為該單位原本的攻擊力",
          "TANKP":"9/1-小十字/敵人移動後損失2點生命值(不被麻\n痹效果所無效化)",
          "HFP":"8/1-九宮格/當自己回合開始時計算所有在他攻擊\n範圍內的敵方單位(不包含中立單位) 並增加(該數值/3\n)的攻擊次數", 
          "LFP":2, 
          "APTP":2, 
          "SPP":2, 
          "ASSP":"2/3-斜十字/斬殺後抽(敵方場上堆-我方場上堆)\n張牌斬殺單之單位最多抽2張",
          "MOVE":"移動到九宮格內位置( M )",
          "moveO":"移動到九宮格位置 此牌會在回合結束消失( M )",
          "HEAL":"恢復5點血量 溢出則2比1兌換為護盾( H )",
          "CUBE":"放置兩個中立的箱子( P )",
          "cube":"中立的箱子",
          "luckyBlock":"會依照你的幸運值給予好運或壞運"
          }

class CHIsupport:
    def __init__(self, width: int, height: int) -> None:
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def displayBlocks(self, screen: pygame.surface.Surface):
        self.x, self.y = pygame.mouse.get_pos()
        
        BX = int((self.x-(display_width/2-blocksize*2))/blocksize)
        BY = int((self.y-(display_height/2-blocksize*1.65))/blocksize)
        if BX+(BY*4)>=0 and BX+(BY*4)<16:
            if Board[BX+(BY*4)].card == True:
                n = 0
                m = 0
                for i in player1:
                    if i.BoardX+(i.BoardY*4) == BX+(BY*4):
                        n = i.type
                for i in player2:
                    if i.BoardX+(i.BoardY*4) == BX+(BY*4):
                        n = i.type
                for i in neutral:
                    if i.BoardX+(i.BoardY*4) == BX+(BY*4):
                        n = i.type
                x = split_lines(libary[n])
                pygame.draw.rect(screen, (0,0,0), (self.x, self.y, self.width, self.height), round(self.width))
                pygame.draw.rect(screen, (200,200,200), (self.x+5, self.y+5, self.width-10, self.height-10), round(self.width/50))
                for i in x:
                    if m == 0:
                        drawText(str(n)+":" + str(i), text_fontCHI, (255, 255, 255),
                                self.x+20, self.y+20, gameDisplay)
                    else:
                        drawText(str(i), text_fontCHI, (255, 255, 255),
                                self.x+20, self.y+20+m, gameDisplay)
                    m+=20
        if self.x > 230 and self.x < 425:
            if len(player1Hand)+1 >= (self.y/62) and self.y > 62:
                m = 0
                n = player1Hand[(self.y//62-1)]
                x = split_lines(libary[n])
                pygame.draw.rect(screen, (0,0,0), (self.x, self.y, self.width, self.height), round(self.width))
                pygame.draw.rect(screen, (200,200,200), (self.x+5, self.y+5, self.width-10, self.height-10), round(self.width/50))
                for i in x:
                    if m == 0:
                        drawText(str(n)+":" + str(i), text_fontCHI, (255, 255, 255),
                                self.x+20, self.y+20, gameDisplay)
                    else:
                        drawText(str(i), text_fontCHI, (255, 255, 255),
                                self.x+20, self.y+20+m, gameDisplay)
                    m+=20
        if self.x > 1295 and self.x < 1480:
            if len(player2Hand)+1 >= (self.y/62) and self.y > 62:
                m = 0
                n = player2Hand[(self.y//62-1)]
                x = split_lines(libary[n])
                pygame.draw.rect(screen, (0,0,0), (self.x-200, self.y, self.width, self.height), round(self.width))
                pygame.draw.rect(screen, (200,200,200), (self.x-195, self.y+5, self.width-10, self.height-10), round(self.width/50))
                for i in x:
                    if m == 0:
                        drawText(str(n)+":" + str(i), text_fontCHI, (255, 255, 255),
                                self.x-180, self.y+20, gameDisplay)
                    else:
                        drawText(str(i), text_fontCHI, (255, 255, 255),
                                self.x-180, self.y+20+m, gameDisplay)
                    m+=20