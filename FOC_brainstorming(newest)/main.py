from variable import *
from displayblocks import *
from calculate import update_data
import random
from start import main as start_main
from end import main as end_main

import cardGreen as cG
import cardRed as cR
import cardWhite as cW
import cardBlue as cB
import cardOrange as cO
import cardPurple as cP
import cardDKGreen as cDKG
import cardCyan as cC

import pygame
start_main()
print("Starting")
print(f"P1Deck:{player1Deck}")
print(f"P2Deck:{player2Deck}")
pygame.init()


black = (0, 0, 0)
white = (255, 255, 255)
clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT, 1000)
pygame.display.set_caption('afternoon brainstorming!!')

#-----------
if Timer[0]:
    P1Clock=600
    P2Clock=600
else:
    P1Clock= 0
    P2Clock= 0
#-----------



def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

def TimeCountDown(turn, booling):
    global P2Clock, P1Clock
    if booling:
        if turn == "player1" and P1Clock>0:
            P1Clock-=1
        elif turn == "player2" and P2Clock>0:
            P2Clock-=1
        if P1Clock == 0:
            print("player2 win")
            WHOwin[0] =2
            return False
        elif P2Clock == 0:
            print("player1 win")
            WHOwin[0] =1
            return False
    else:
        if turn == "player1":
            P1Clock+=1
        elif turn == "player2":
            P2Clock+=1
    return True
    

def displayHand(screen):
    dis = (display_width/2-(display_width/2.75), display_width/2+(display_width/4))
    for i in range(0, len(player1Hand)):
        if i < 9:
            if player1Hand[i] == "MOVEO":
                drawText("P1hand " + str(i+1) + " :"+player1Hand[i], text_font, (255, 69, 0), dis[0], display_height/15*(i+1), screen)
            else:
                drawText("P1hand " + str(i+1) + " :"+player1Hand[i], text_font, (255, 255, 255), dis[0], display_height/15*(i+1), screen)
        if i == 9:
            if player1Hand[i] == "MOVEO":
                drawText("P1hand " + str(0) + " :"+player1Hand[i], text_font, (255, 69, 0), dis[0], display_height/15*(i+1), screen)
            else:
                drawText("P1hand " + str(0) + " :"+player1Hand[i], text_font, (255, 255, 255), dis[0], display_height/15*(i+1), screen)
        if i == 10:
            if player1Hand[i] == "MOVEO":
                drawText("P1hand " + str(0) + " :"+player1Hand[i], text_font, (255, 69, 0), dis[0], display_height/15*(i+1), screen)
            else:
                drawText("P1hand " + "key.u" + " :"+player1Hand[i], text_font, (255, 255, 255), dis[0], display_height/15*(i+1), screen)
        if i == 11:
            if player1Hand[i] == "MOVEO":
                drawText("P1hand " + str(0) + " :"+player1Hand[i], text_font, (255, 69, 0), dis[0], display_height/15*(i+1), screen)
            else:
                drawText("P1hand " + "key.i" + " :"+player1Hand[i], text_font, (255, 255, 255), dis[0], display_height/15*(i+1), screen)

    for i in range(0, len(player2Hand)):
        if i < 9:
            if player2Hand[i] == "MOVEO":
                drawText("P2hand " + str(i+1) + " :"+player2Hand[i], text_font, (255, 69, 0), dis[1], display_height/15*(i+1), screen)
            else:
                drawText("P2hand " + str(i+1) + " :"+player2Hand[i], text_font, (255, 255, 255), dis[1], display_height/15*(i+1), screen)
        if i == 9:
            if player2Hand[i] == "MOVEO":
                drawText("P2hand " + str(0) + " :"+player2Hand[i], text_font, (255, 69, 0), dis[1], display_height/15*(i+1), screen)
            else:
                drawText("P2hand " + str(0) + " :"+player2Hand[i], text_font, (255, 255, 255), dis[1], display_height/15*(i+1), screen)
        if i == 10:
            if player2Hand[i] == "MOVEO":
                drawText("P2hand " + str(0) + " :"+player2Hand[i], text_font, (255, 69, 0), dis[1], display_height/15*(i+1), screen)
            else:
                drawText("P2hand " + "key.u" + " :"+player2Hand[i], text_font, (255, 255, 255), dis[1], display_height/15*(i+1), screen)
        if i == 11:
            if player2Hand[i] == "MOVEO":
                drawText("P2hand " + str(0) + " :"+player2Hand[i], text_font, (255, 69, 0), dis[1], display_height/15*(i+1), screen)
            else:
                drawText("P2hand " + "key.i" + " :"+player2Hand[i], text_font, (255, 255, 255), dis[1], display_height/15*(i+1), screen)


def drawCard(turn):
    global player1Deck, player2Deck, player1Trash, player2Trash, player1Hand, player2Hand
    if turn == "player1":
        if len(player1Deck) == 0:
            for i in range(0, len(player1Trash)):
                a = random.randint(0, len(player1Trash)-1)
                player1Deck.append(player1Trash[a])
                player1Trash.pop(a)
        if len(player1Deck) > 0:
            a = player1Deck[random.randint(0, len(player1Deck)-1)]
            player1Hand.append(a)
            player1Deck.remove(a)
            print(f"player1 drew {a}, player1Deck:{player1Deck}, player1Trash:{player1Trash}")
            return True
    elif turn == "player2":
        if len(player2Deck) == 0:
            for i in range(0, len(player2Trash)):
                a = random.randint(0, len(player2Trash)-1)
                player2Deck.append(player2Trash[a])
                player2Trash.pop(a)
        if len(player2Deck) > 0:
            a = player2Deck[random.randint(0, len(player2Deck)-1)]
            player2Hand.append(a)
            player2Deck.remove(a)
            print(f"player2 drew {a}, player2Deck:{player2Deck}, player2Trash:{player2Trash}")
            return True
    return False


def playCard(turn, card, BX, BY, mouseX, mouseY):
    if cW.playCardWhite(turn, card, BX, BY, mouseX, mouseY):return True
    if cR.playCardRed(turn, card, BX, BY, mouseX, mouseY):return True
    if cG.playCardGreen(turn, card, BX, BY, mouseX, mouseY):return True
    if cB.playCardBlue(turn, card, BX, BY, mouseX, mouseY):return True
    if cO.playCardOrange(turn, card, BX, BY, mouseX, mouseY):return True
    if cP.playCardPurple(turn, card, BX, BY, mouseX, mouseY):return True
    if cDKG.playCardDKGreen(turn, card, BX, BY, mouseX, mouseY):return True
    if cC.playCardCyan(turn, card, BX, BY, mouseX, mouseY):return True
    return False


class boardSpawn:
    def __init__(self, x, y, width, height, card, color, BX, BY):
        self.type = "Board"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.card = card
        self.size = width
        self.color = color
        self.BoardX = BX
        self.BoardY = BY
        self.Board = BX+(BY*4)
        self.thickness = 2
        Board.append(self)

    def display(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 4)


class UIBlock():
    def __init__(self, X, Y, BX, BY, width, height):
        self.X = X
        self.Y = Y
        self.width = width
        self.height = height
        self.type = 0
        self.BX = BX
        self.BY = BY
        self.alpha = 0
        self.Board = BX+(BY*4)
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image.fill((200, 200, 200))
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center= (self.X+(self.width/2), self.Y+(self.height/2)))
        BoardUI.append(self)
        
    def update(self, screen):
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center= (self.X+(self.width/2), self.Y+(self.height/2)))
        screen.blit(self.image, self.rect)
        
        
def detectATKArea(BX, BY, turn):
    for i in BoardUI:
        if i.Board == BX+(BY*4):
            i.alpha = 70
            i.image.fill(white)
        else:
            i.alpha = 0
            i.image.fill(white)
    players = player1 + player2
    for i in players:
        if i.Board == BX+(BY*4):
            for n in BoardUI:
                if n.Board == BX+(BY*4):
                    if i.owner == turn:
                        n.image.fill((255, 255, 255))
                    else:
                        n.image.fill((200, 0, 0))

        if i.Board == BX+(BY*4):
            if i.ATKtype.split(" ") == ["cross"]:
                for n in BoardUI:
                    if (n.BX == BX and n.BY == BY-1) or (n.BX == BX and n.BY == BY+1) or (n.BX == BX-1 and n.BY == BY) or (n.BX == BX+1 and n.BY == BY):
                        n.alpha = 70
                        if i.owner == turn:
                            n.image.fill((255, 255, 255))
                        else:
                            n.image.fill((200, 0, 0))
            if i.ATKtype.split(" ") == ["cross" , "x"]:
                for n in BoardUI:
                    if (n.BX == BX and n.BY == BY-1) or (n.BX == BX and n.BY == BY+1) or (n.BX == BX-1 and n.BY == BY) or (n.BX == BX+1 and n.BY == BY) or (n.BX == BX-1 and n.BY == BY-1) or (n.BX == BX-1 and n.BY == BY+1) or (n.BX == BX+1 and n.BY == BY-1) or (n.BX == BX+1 and n.BY == BY+1):
                        n.alpha = 70
                        if i.owner == turn:
                            n.image.fill((255, 255, 255))
                        else:
                            n.image.fill((200, 0, 0))
            if i.ATKtype.split(" ") == ["x"]:
                for n in BoardUI:
                    if (n.BX == BX-1 and n.BY == BY-1) or (n.BX == BX-1 and n.BY == BY+1) or (n.BX == BX+1 and n.BY == BY-1) or (n.BX == BX+1 and n.BY == BY+1):
                        n.alpha = 70
                        if i.owner == turn:
                            n.image.fill((255, 255, 255))
                        else:
                            n.image.fill((200, 0, 0))
            if i.ATKtype.split(" ") == ["Bigx"]:
                for n in BoardUI:
                    if n.BX == BX or n.BY == BY:
                        n.alpha = 70
                        if i.owner == turn:
                            n.image.fill((255, 255, 255))
                        else:
                            n.image.fill((200, 0, 0))
            if i.ATKtype.split(" ") == ["nearest"]:
                    Min = []
                    if i.owner == "player1":
                        if len(player2) >= 1:
                            Min = [player2[0]]
                        elif len(neutral) >= 1:
                            Min = [neutral[0]]
                    if i.owner == "player2":
                        if len(player1) >= 1:
                            Min = [player1[0]]
                        elif len(neutral) >= 1:
                            Min = [neutral[0]]
                    if i.owner == "player1":
                        for n in player2:
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) < abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min = [n]
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) == abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min.append(n)
                    if i.owner == "player2":
                        for n in player1:
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) < abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min = [n]
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) == abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min.append(n)
                    for n in neutral:
                        if abs(n.BoardX-BX)+abs(n.BoardY-BY) < abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                            Min = [n]
                        if abs(n.BoardX-BX)+abs(n.BoardY-BY) == abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                            Min.append(n)
                    for n in BoardUI:
                        for m in Min:
                            if n.Board == m.Board:
                                n.alpha = 50
                                if i.owner == turn:
                                    n.image.fill((255, 255, 255))
                                else:
                                    n.image.fill((200, 0, 0))
            if i.ATKtype.split(" ") == ["farest"]:  
                    Min = []
                    if i.owner == "player1":
                        if len(player2) >= 1:
                            Min = [player2[0]]
                        elif len(neutral) >= 1:
                            Min = [neutral[0]]
                    if i.owner == "player2":
                        if len(player1) >= 1:
                            Min = [player1[0]]
                        elif len(neutral) >= 1:
                            Min = [neutral[0]]
                    if i.owner == "player1":
                        for n in player2:
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) > abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min = [n]
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) == abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min.append(n)
                    if i.owner == "player2":
                        for n in player1:
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) > abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min = [n]
                            if abs(n.BoardX-BX)+abs(n.BoardY-BY) == abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                                Min.append(n)
                    for n in neutral:
                        if abs(n.BoardX-BX)+abs(n.BoardY-BY) > abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                            Min = [n]
                        if abs(n.BoardX-BX)+abs(n.BoardY-BY) == abs(Min[0].BoardX-BX)+abs(Min[0].BoardY-BY):
                            Min.append(n)
                    for n in BoardUI:
                        for m in Min:
                            if n.Board == m.Board:
                                n.alpha = 50
                                if i.owner == turn:
                                    n.image.fill((255, 255, 255))
                                else:
                                    n.image.fill((200, 0, 0))
class changeTurn:
    def __init__(self, x, y, width, height, color):
        self.type = "Board"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = width
        self.color = color
        self.thickness = 2

    def display(self, screen):
        global turn, player1, player2
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.width, self.height), 4)
        drawText("End turn", text_font, self.color,
                 display_width/2-(blocksize*0.275), display_height/5-(blocksize*0.15), screen)
        if turn == "player1":
            drawText("Player1", text_font, self.color,
                     display_width/2-(blocksize*0.25), display_height/5-(blocksize*0.04), screen)
        elif turn == "player2":
            drawText("Player2", text_font, self.color,
                     display_width/2-(blocksize*0.25), display_height/5-(blocksize*0.04), screen)

def main():
    global turn
    score = 0
    run = True

    x = display_width/2-(blocksize*2)
    y = display_height/2-(blocksize*1.65)

    for i in range(4):
        x = display_width/2-(blocksize*2)
        for ii in range(4):
            BX = round((x-(display_width/2-blocksize*2-1))/blocksize)
            BY = round((y-(display_height/2-blocksize*1.65))/blocksize)
            boardSpawn(x, y, blocksize*1.01,
                            blocksize*1.01, False, white, BX, BY)
            UIBlock(x, y, BX, BY, blocksize,
                            blocksize)
            x += blocksize
        y += blocksize
    Button = changeTurn(display_width/2-(display_width/17/1.6), display_height/5-(display_height/34),
                        display_width/17/1.6*2, display_height/17, (200, 200, 200))
    canA = True
    canE = True
    canH = True
    canM = True
    can1 = True
    can2 = True
    can3 = True
    can4 = True
    can5 = True
    can6 = True
    can7 = True
    can8 = True
    can9 = True
    can0 = True
    canU = True
    canI = True
    turn = "player1"
    ScoreGraph = ScoreDisplay(display_width/2-display_width/1.6/45/2, display_height/10, display_width/1.6/45, display_height/45)
    
    P1atkGraph = AtkDisplay(display_width/10, display_height/10*9, display_width/1.6/50, display_height/50)
    P2atkGraph = AtkDisplay(display_width/10*8.75, display_height/10*9, display_width/1.6/50, display_height/50)
    
    P1TokenGraph = TokenDisplay(display_width/10/2, display_height/10*9, display_width/1.6/45)
    P2TokenGraph = TokenDisplay(display_width/10*9.5, display_height/10*9, display_width/1.6/45)
    
    for i in range(0, 3):
        drawCard("player1")
        drawCard("player2")
    while run:
        if P1DrawCard[0]>=1:
            drawCard("player1")
            P1DrawCard[0]-=1
        if P2DrawCard[0]>=1:
            drawCard("player2")
            P2DrawCard[0]-=1
        gameDisplay.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                run = TimeCountDown(turn, Timer[0])
            if event.type == pygame.QUIT:
                quit()
        mouseX, mouseY = pygame.mouse.get_pos()
        
        BX = int((mouseX-(display_width/2-blocksize*2))/blocksize)
        BY = int((mouseY-(display_height/2-blocksize*1.65))/blocksize)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            run = False
        if keys[pygame.K_e] and canE == True:
            if turn == "player1":
                Turns[0] += 1
                score -= len(player1)
                for i in player1:
                    score -= i.endTurn(turn)
                if len(player1Hand)>=1:
                    for i in range(player1Hand.count("MOVEO")):
                        for i2 in player1Hand:
                            if i2 == "MOVEO":
                                playCard(turn, i2, BX, BY, mouseX, mouseY)
                                break
                print("Player1 end turn")
                if score <= -10:
                    print("Player1 Win")
                    WHOwin[0] =1
                    run = False
                drawCard("player2")
                P1Heal[0] = 0
                P1Cube[0] = 0
                P1Move[0] = 0
                P2atk[0] += 1
                for i in player2:
                    i.startTurn(turn)
                turn = "player2"
            elif turn == "player2":
                Turns[0] += 1
                score += len(player2)
                for i in player2:
                    score += i.endTurn(turn)
                if len(player2Hand)>=1:
                    for i in range(player2Hand.count("MOVEO")):
                        for i2 in player2Hand:
                            if i2 == "MOVEO":
                                playCard(turn, i2, BX, BY, mouseX, mouseY)
                                break
                print("Player2 end turn")
                if score >= 10:
                    print("Player2 Win")
                    WHOwin[0] =2
                    run = False
                drawCard("player1")
                P2Heal[0] = 0
                P2Cube[0] = 0
                P2Move[0] = 0
                P1atk[0] += 1
                for i in player1:
                    i.startTurn(turn)
                turn = "player1"
            TimeLine.append(score)
            canE = False
        elif not keys[pygame.K_e] and canE == False:
            canE = True

        displayHand(gameDisplay)
        if keys[pygame.K_p]:
            if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)):
                if Board[BX+(BY*4)].card == False:
                    if turn == "player1" and P1Cube[0] >= 1:
                        cW.cube("neutral", "white", BX, BY)
                        P1Cube[0] -= 1
                        Board[BX+(BY*4)].card = True
                        print(f"{turn} spawn cube on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    if turn == "player2" and P2Cube[0] >= 1:
                        cW.cube("neutral", "white", BX, BY)
                        P2Cube[0] -= 1
                        Board[BX+(BY*4)].card = True
                        print(f"{turn} spawn cube on BX:{BX}, BY:{BY} at turns:{Turns[0]}")

        if keys[pygame.K_h] and canH == True:
            if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)):
                if Board[BX+(BY*4)].card == True:
                    if turn == "player1" and P1Heal[0] >= 1:
                        for i in player1:
                            if i.Board == BX+(BY*4):
                                if i.heal(5):
                                    P1Heal[0] -= 1
                                    print(f"{turn} heal {i.type} on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    if turn == "player2" and P2Heal[0] >= 1:
                        for i in player2:
                            if i.Board == BX+(BY*4):
                                if i.heal(5):
                                    P2Heal[0] -= 1
                                    print(f"{turn} heal {i.type} on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
            canH = False
        elif not keys[pygame.K_h] and canH == False:
            canH = True
        if keys[pygame.K_m] and canM == True:
            if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)):
                tag = 0
                if turn == "player1":
                    for i in player1:
                        if i.moving == True:
                            tag = i
                            break
                if turn == "player2":
                    for i in player2:
                        if i.moving == True:
                            tag = i
                            break
                if Board[BX+(BY*4)].card == True and (P1Move[0] >= 1 or P2Move[0] >= 1):
                    if tag == 0:
                        if turn == "player1":
                            for i in player1:
                                if i.Board == BX+(BY*4) and i.canATK == True:
                                    i.moving = True
                                    P1Move[0] -= 1
                                    break
                        elif turn == "player2":
                            for i in player2:
                                if i.Board == BX+(BY*4) and i.canATK == True:
                                    i.moving = True
                                    P2Move[0] -= 1
                                    break
                if Board[BX+(BY*4)].card == False:
                    if tag != 0:
                        targetY=i.BoardY # type: ignore
                        targetX=i.BoardX # type: ignore
                        if i.move(BX, BY): # type: ignore
                            print(f"{turn} move {i.type} from BX:{targetX}, BY:{targetY} to BX:{BX}, BY:{BY} at turns:{Turns[0]}") # type: ignore
            canM = False
        elif not keys[pygame.K_m] and canM == False:
            canM = True
        if keys[pygame.K_1] and can1 == True:
            if turn == "player1":
                if len(player1Hand) >= 1:
                    print(f"{turn} used {player1Hand[0]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[0], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 1:
                    print(f"{turn} used {player2Hand[0]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[0], BX, BY, mouseX, mouseY)
            can1 = False
        elif not keys[pygame.K_1] and can1 == False:
            can1 = True
        if keys[pygame.K_2] and can2 == True:
            if turn == "player1":
                if len(player1Hand) >= 2:
                    print(f"{turn} used {player1Hand[1]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[1], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 2:
                    print(f"{turn} used {player2Hand[1]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[1], BX, BY, mouseX, mouseY)
            can2 = False
        elif not keys[pygame.K_2] and can2 == False:
            can2 = True
        if keys[pygame.K_3] and can3 == True:
            if turn == "player1":
                if len(player1Hand) >= 3:
                    print(f"{turn} used {player1Hand[2]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[2], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 3:
                    print(f"{turn} used {player2Hand[2]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[2], BX, BY, mouseX, mouseY)
            can3 = False
        elif not keys[pygame.K_3] and can3 == False:
            can3 = True
        if keys[pygame.K_4] and can4 == True:
            if turn == "player1":
                if len(player1Hand) >= 4:
                    print(f"{turn} used {player1Hand[3]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[3], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 4:
                    print(f"{turn} used {player2Hand[3]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[3], BX, BY, mouseX, mouseY)
            can4 = False
        elif not keys[pygame.K_4] and can4 == False:
            can4 = True
        if keys[pygame.K_5] and can5 == True:
            if turn == "player1":
                if len(player1Hand) >= 5:
                    print(f"{turn} used {player1Hand[4]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[4], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 5:
                    print(f"{turn} used {player2Hand[4]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[4], BX, BY, mouseX, mouseY)
            can5 = False
        elif not keys[pygame.K_5] and can5 == False:
            can5 = True
        if keys[pygame.K_6] and can6 == True:
            if turn == "player1":
                if len(player1Hand) >= 6:
                    print(f"{turn} used {player1Hand[5]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[5], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 6:
                    print(f"{turn} used {player2Hand[5]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[5], BX, BY, mouseX, mouseY)
            can6 = False
        elif not keys[pygame.K_6] and can6 == False:
            can6 = True
        if keys[pygame.K_7] and can7 == True:
            if turn == "player1":
                if len(player1Hand) >= 7:
                    print(f"{turn} used {player1Hand[6]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[6], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 7:
                    print(f"{turn} used {player2Hand[6]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[6], BX, BY, mouseX, mouseY)
            can7 = False
        elif not keys[pygame.K_7] and can7 == False:
            can7 = True
        if keys[pygame.K_8] and can8 == True:
            if turn == "player1":
                if len(player1Hand) >= 8:
                    print(f"{turn} used {player1Hand[7]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[7], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 8:
                    print(f"{turn} used {player2Hand[7]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[7], BX, BY, mouseX, mouseY)
            can8 = False
        elif not keys[pygame.K_8] and can8 == False:
            can8 = True
        if keys[pygame.K_9] and can9 == True:
            if turn == "player1":
                if len(player1Hand) >= 9:
                    print(f"{turn} used {player1Hand[8]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[8], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 9:
                    print(f"{turn} used {player2Hand[8]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[8], BX, BY, mouseX, mouseY)
            can9 = False
        elif not keys[pygame.K_9] and can9 == False:
            can0 = True
        if keys[pygame.K_0] and can0 == True:
            if turn == "player1":
                if len(player1Hand) >= 10:
                    print(f"{turn} used {player1Hand[9]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[9], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 10:
                    print(f"{turn} used {player2Hand[9]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[9], BX, BY, mouseX, mouseY)
            can0 = False
        elif not keys[pygame.K_0] and can0 == False:
            can0 = True
        if keys[pygame.K_u] and canU == True:
            if turn == "player1":
                if len(player1Hand) >= 11:
                    print(f"{turn} used {player1Hand[10]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[10], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 11:
                    print(f"{turn} used {player2Hand[10]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[10], BX, BY, mouseX, mouseY)
            canU = False
        elif not keys[pygame.K_u] and canU == False:
            canU = True
        if keys[pygame.K_i] and canI == True:
            if turn == "player1":
                if len(player1Hand) >= 12:
                    print(f"{turn} used {player1Hand[11]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player1Hand[11], BX, BY, mouseX, mouseY)
            if turn == "player2":
                if len(player2Hand) >= 12:
                    print(f"{turn} used {player1Hand[11]}card on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                    playCard(turn, player2Hand[11], BX, BY, mouseX, mouseY)
            canI = False
        elif not keys[pygame.K_i] and canI == False:
            canI = True
        if keys[pygame.K_a] and canA == True:
            if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)):
                if turn == "player1" and P1atk[0] >= 1:
                    for i in player1:
                        if i.Board == BX+(BY*4) and i.owner == "player1":
                            if i.atk(turn):
                                update_data(i.type, i.owner, '攻擊次數', 1)
                                print(f"{turn} attack, use {i.type} on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                                P1atk[0] -= 1
                elif turn == "player2" and P2atk[0] >= 1:
                    for i in player2:
                        if i.Board == BX+(BY*4) and i.owner == "player2":
                            if i.atk(turn):
                                update_data(i.type, i.owner, '攻擊次數', 1)
                                print(f"{turn} attack, use {i.type} on BX:{BX}, BY:{BY} at turns:{Turns[0]}")
                                P2atk[0] -= 1
                canA = False
        elif not keys[pygame.K_a] and canA == False:
            canA = True
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)):
            detectATKArea(BX, BY, turn)
        for i in Board:
            i.display(gameDisplay)
        
        for i in BoardUI:
            i.update(gameDisplay)
        
        for i in player1:
            if i.health <= 0:
                player1Trash.append(i.type)
                Board[i.Board].card = False
                player1.remove(i)
                del i
                continue
            i.display(gameDisplay)
        for i in player2:
            if i.health <= 0:
                player2Trash.append(i.type)
                Board[i.Board].card = False
                player2.remove(i)
                del i
                continue
            i.display(gameDisplay)
        for i in neutral:
            if i.health <= 0:
                Board[i.Board].card = False
                neutral.remove(i)
                del i
                continue
            i.display(gameDisplay)
            
        drawText("P1ATK:"+str(P1atk[0]), text_font, (255, 255, 255),
                display_width/10*0.85, display_height/10*9, gameDisplay)
        drawText("P2ATK:"+str(P2atk[0]), text_font, (255, 255, 255),
                display_width/10*8.6, display_height/10*9, gameDisplay)
        drawText("P1Luck:"+str(P1Luck[0])+"%", text_font, (51, 255, 51),
                display_width/2-(display_width/6), display_height/5, gameDisplay)
        drawText("P2Luck:"+str(P2Luck[0])+"%", text_font, (51, 255, 51),
                display_width/2+(display_width/8), display_height/5, gameDisplay)
        drawText("P1Coin: $"+str(P1Coin[0]), text_font, (255, 215, 0),
                display_width/2-(display_width/4), display_height/5, gameDisplay)
        drawText("P2Coin: $"+str(P2Coin[0]), text_font, (255, 215, 0),
                display_width/2+(display_width/4.5), display_height/5, gameDisplay)
        
        if P1Coin[0] >= 0:
            pygame.draw.circle(gameDisplay, (255, 215, 0),
                             (display_width/2-display_width/3.2, display_height/1.2), blocksize*0.4, int(text_font_size/4))
        if P2Coin[0] >= 0:
            pygame.draw.circle(gameDisplay, (255, 215, 0),
                             (display_width/2+display_width/3.2, display_height/1.2), blocksize*0.4, int(text_font_size/4))
            
        if len(str(P1Clock%60))==1:
            drawText("P1Clock:"+str(int(P1Clock/60))+":0"+str(int(P1Clock%60)), text_font, (255, 255, 255),
                display_width/2-(display_width/6), display_height/6.4, gameDisplay)
        else:
            drawText("P1Clock:"+str(int(P1Clock/60))+":"+str(int(P1Clock%60)), text_font, (255, 255, 255),
                display_width/2-(display_width/6), display_height/6.4, gameDisplay)
        if len(str(P2Clock%60))==1:
            drawText("P2Clock:"+str(int(P2Clock/60))+":0"+str(int(P2Clock%60)), text_font, (255, 255, 255),
                display_width/2+(display_width/8), display_height/6.4, gameDisplay)
        else:
            drawText("P2Clock:"+str(int(P2Clock/60))+":"+str(int(P2Clock%60)), text_font, (255, 255, 255),
                display_width/2+(display_width/8), display_height/6.4, gameDisplay)
        

        drawText("P1DeckInfo-" + " P1TrashDeck: " + str(len(player1Trash)) + " /P1Deck: " + str(len(player1Deck)), text_font, (200, 200, 200),
                display_width/2-(display_width/3), display_height/1.1, gameDisplay)
        drawText("P2DeckInfo-" + " P2TrashDeck: " + str(len(player2Trash)) + " /P2Deck: " + str(len(player2Deck)), text_font, (200, 200, 200),
                display_width/2+(display_width/20), display_height/1.1, gameDisplay)
        drawText("Turns:" + str(Turns[0]), text_font, (200, 200, 200),
                display_width/2-(display_width/35), display_height/7, gameDisplay)
        drawText(str(P1totemHP[0])+"/"+str(P1totemAD[0]), text_font, (85, 107, 47),
                display_width/2-(display_width/4.25),  display_height/6.4, gameDisplay)
        drawText(str(P2totemHP[0])+"/"+str(P2totemAD[0]), text_font, (85, 107, 47),
                display_width/2+(display_width/4.51),  display_height/6.4, gameDisplay)
        
        if P1Token[0] >= 4:
            P1Token[0] -= 4
            drawCard("player1")
            for i in player1:
                i.drawCard()
        if P2Token[0] >= 4:
            P2Token[0] -= 4
            drawCard("player2")
            for i in player2:
                i.drawCard()
                
        Button.display(gameDisplay)
        P1atkGraph.displayBlocks(gameDisplay, P1atk[0])
        P2atkGraph.displayBlocks(gameDisplay, P2atk[0])
        P1TokenGraph.displayCircle(gameDisplay, P1Token[0])
        P2TokenGraph.displayCircle(gameDisplay, P2Token[0])
        ScoreGraph.displayBlocks(gameDisplay, score, turn)
        
        if score < 0:
            drawText("P1score:"+str(abs(score)), text_font, (255, 255, 255),
                    ScoreGraph.x+ScoreGraph.width*score*1.5, ScoreGraph.y/2, gameDisplay)
        if score > 0:
            drawText("P2score:"+str(score), text_font, (255, 255, 255),
                    ScoreGraph.x+ScoreGraph.width*score*1.5, ScoreGraph.y/2, gameDisplay)
        pygame.display.flip()
        clock.tick(60)
    if not Timer[0]:
        if len(str(P1Clock%60))==1:
            print("P1Clock:"+str(int(P1Clock/60))+":0"+str(int(P1Clock%60)))
        else:
            print("P1Clock:"+str(int(P1Clock/60))+":"+str(int(P1Clock%60)))
        if len(str(P2Clock%60))==1:
            print("P2Clock:"+str(int(P2Clock/60))+":0"+str(int(P2Clock%60)))
        else:
            print("P2Clock:"+str(int(P2Clock/60))+":"+str(int(P2Clock%60)))
    print(f"Turns:{Turns[0]}")
    
main()
end_main()
pygame.quit()
