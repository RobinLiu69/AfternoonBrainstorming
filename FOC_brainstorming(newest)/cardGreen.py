from card import cards
from variable import *
from calculate import update_data
import random
import pygame

def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

def spawnLuckyBlock(x: int, y: int, bx: int=None, by: int=None) -> bool:
    global Board
    if x == bx and y == by: return False
    for i in Board:
        if i.BoardX == x and i.BoardY == y and i.card == False:
            luckyBlock("neutral", "green", x, y)
            i.card = True
            return True
    return False

def playCardGreen(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPG":
                SP("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTG":
                APT("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APG":
                AP("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCG":
                ADC("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKG":
                TANK("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFG":
                heavyFighter("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFG":
                lightFighter("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSG":
                ASS("player1", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPG":
                SP("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTG":
                APT("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APG":
                AP("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCG":
                ADC("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKG":
                TANK("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFG":
                heavyFighter("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFG":
                lightFighter("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSG":
                ASS("player2", "green", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
    return False



class TANK(cards):
    def __init__(self, owner, color, x, y, hp=10, atk=1):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "TANKG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class luckyBlock(cards):
    def __init__(self, owner, color, x, y, hp=1, atk=0):
        if color == "green":
            self.ATKtype = ""
            color = (51, 255, 51)
            self.selfColor = color
            super().__init__(owner, "luckyBlock", hp, atk, x, y)

    def display(self, screen):
        pygame.draw.rect(screen, self.selfColor,
                         ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.425),
                          (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.425),
                          blocksize*0.15, blocksize*0.15), 4) # type: ignore
        drawText("?", text_font, (51, 255, 51), (display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4625), 
                 (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.425), screen)
        self.update(screen)

    def ability(self, enemy, turn):
        global P1Luck, P2Luck
        if enemy.owner == "player1" and enemy.limited > 0:
            enemy.limited -= 1
            if enemy.limited == 0:
                enemy.limited = 20
                return False
            if enemy.type == "HFG":
                P1Luck[0] += 5
                enemy.ability("oo", "oo")
            if random.randint(1, 100) <= P1Luck[0]:
                # goodluck
                P1Luck[0] += 1
                r = random.randint(1, 5)
                if r == 1:
                    enemy.armor += 4
                elif r == 2:
                    enemy.atk(enemy.owner)
                elif r == 3:
                    enemy.attack = int(enemy.attack*2)
                elif r == 4:
                    enemy.moving = True
                elif r == 5:
                    for i in Board:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if i.card == False:
                                luckyBlock("neutral", "green", i.BoardX, i.BoardY)
                                i.card = True
                return True
            else:
                P1Luck[0] -= 1
                r = random.randint(1, 5)
                if r == 1:
                    update_data(enemy.type,enemy.owner,'受到傷害次數', 1)
                    update_data(enemy.type,enemy.owner,'受到傷害', enemy.armor)
                    enemy.armor = 0
                elif r == 2:
                    update_data(enemy.type,enemy.owner,'受到傷害次數', 1)
                    update_data(enemy.type,enemy.owner,'受到傷害', int(enemy.health/2))
                    enemy.health = int(enemy.health/2)
                elif r == 3:
                    enemy.canATK = False
                elif r == 4:
                    if enemy.health >= 2:
                        update_data(enemy.type,enemy.owner,'受到傷害次數', 1)
                        update_data(enemy.type,enemy.owner,'受到傷害', 2)
                        enemy.health -= 2
                elif r == 5:
                    enemy.attack = int(enemy.attack/2)
                return True
                # badluck
        if enemy.owner == "player2" and enemy.limited > 0:
            enemy.limited -= 1
            if enemy.limited == 0:
                enemy.limited = 20
                return False
            if enemy.type == "HFG":
                P2Luck[0] += 5
                enemy.ability("oo", "oo")
            if random.randint(1, 100) <= P2Luck[0]:
                # goodluck
                P2Luck[0] += 1
                r = random.randint(1, 5)
                if r == 1:
                    enemy.armor += 4
                elif r == 2:
                    enemy.atk(enemy.owner)
                elif r == 3:
                    enemy.attack = int(enemy.attack*2)
                elif r == 4:
                    enemy.moving = True
                elif r == 5:
                    for i in Board:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if i.card == False:
                                luckyBlock("neutral", "green", i.BoardX, i.BoardY)
                                i.card = True
                return True
            else:
                P2Luck[0] -= 1
                r = random.randint(1, 5)
                if r == 1:
                    update_data(enemy.type,enemy.owner,'受到傷害次數', 1)
                    update_data(enemy.type,enemy.owner,'受到傷害', enemy.armor)
                    enemy.armor = 0
                elif r == 2:
                    update_data(enemy.type,enemy.owner,'受到傷害次數', 1)
                    update_data(enemy.type,enemy.owner,'受到傷害', int(enemy.health/2))
                    enemy.health = int(enemy.health/2)
                elif r == 3:
                    enemy.canATK = False
                elif r == 4:
                    if enemy.health >= 2:
                        update_data(enemy.type,enemy.owner,'受到傷害次數', 1)
                        update_data(enemy.type,enemy.owner,'受到傷害', 2)
                        enemy.health -= 2
                elif r == 5:
                    enemy.attack = int(enemy.attack/2)
                return True
        return False

    def atk(self, turn):
        return False
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        return 0


class ADC(cards):  
    def __init__(self, owner, color, x, y, hp=3, atk=3):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "ADCG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        print("atk")
        if self.Attack(self.ATKtype.split(" "), 1, turn):
            for i in Board:
                if (i.BoardX == self.BoardX or i.BoardY == self.BoardY) and i.Board != self.Board:
                    if i.card == False:
                        if random.randint(1, 2) == 2:
                            luckyBlock(
                                "neutral", "green", i.BoardX, i.BoardY)
                            i.card = True
            return True
        return False
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class ASS(cards):  
    def __init__(self, owner, color, x, y, hp=2, atk=4):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "ASSG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class AP(cards):  
    def __init__(self, owner, color, x, y, hp=3, atk=2):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "APG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy: cards, turn):
        enemy.canATK = False
        r = 0
        if self.owner == "player1":
            if random.randint(1, 100) <= P1Luck[0]:
                r = random.randint(1, 5)
            else:
                r = 0
        if self.owner == "player2":
            if random.randint(1, 100) <= P2Luck[0]:
                r = random.randint(1, 5)
            else:
                r = 0
        if r == 1:
            self.armor += 4
        elif r == 2:
            self.atk(self.owner)
        elif r == 3:
            self.attack = int(self.attack*2)
        elif r == 4:
            self.moving = True
        elif r == 5:
                    for i in Board:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if i.card == False:
                                luckyBlock("neutral", "green", i.BoardX, i.BoardY)
                                i.card = True
                                
        if self.owner == "player1":
            if random.randint(1, 100) > P2Luck[0]:
                r = random.randint(1, 5)
            else:
                r = 0
        if self.owner == "player2":
            if random.randint(1, 100) > P1Luck[0]:
                r = random.randint(1, 5)
            else:
                r = 0
        if r == 1:
            update_data(enemy.type, enemy.owner,'受到傷害次數', 1)
            update_data(enemy.type, enemy.owner,'受到傷害', enemy.armor)
            enemy.armor = 0
        elif r == 2:
            update_data(enemy.type, enemy.owner,'受到傷害次數', 1)
            update_data(enemy.type, enemy.owner,'受到傷害', int(enemy.health/2))
            enemy.health -= int(enemy.health/2)
        elif r == 3:
            enemy.canATK = False
        elif r == 4:
            if enemy.health >= 2:
                update_data(enemy.type, enemy.owner,'受到傷害次數', 1)
                update_data(enemy.type, enemy.owner,'受到傷害', 2)
                enemy.health -= 2
            elif r == 5:
                enemy.attack = int(enemy.attack/2)
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class heavyFighter(cards):  
    def __init__(self, owner, color, x, y, hp=8, atk=1):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "HFG", hp, atk, x, y)
            
    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if enemy == "oo" and turn == "oo":
            Min = []
            for i in Board:
                if i.card == False:
                    Min.append(i)
            if len(Min) > 0:
                r = random.randint(0, len(Min)-1)
                luckyBlock("neutral", "green", Min[r].BoardX, Min[r].BoardY)
                Min[r].card = True
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 2, turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class lightFighter(cards):  
    def __init__(self, owner, color, x, y, hp=6, atk=2):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "LFG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if self.owner == "player1":
            if random.randint(1, 100) <= P1Luck[0]:
                r = random.randint(0, 2)
                if r == 0:
                    self.moving = True
                elif r == 1:
                    P1atk[0] += 1
                else:
                    self.attack += 2
                    self.armor += 2
                return True
        elif self.owner == "player2":
            if random.randint(1, 100) <= P2Luck[0]:
                r = random.randint(0, 2)
                if r == 0:
                    self.moving = True
                elif r == 1:
                    P2atk[0] += 1
                else:
                    self.attack += 2
                    self.armor += 2
                return True
        return False

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class SP(cards):  
    def __init__(self, owner, color, x, y, hp=1, atk=5):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "SPG", hp, atk, x, y)
            if owner == "player1":
                P1Luck[0] += 10
            if owner == "player2":
                P2Luck[0] += 10
        if self.owner == "player1":
            num = max(0, P1Luck[0] - 50) // 10
            for i in range(num):
                while not spawnLuckyBlock(random.randint(0, 3), random.randint(0, 3), x, y): pass
        elif self.owner == "player2":
            num = max(0, P2Luck[0] - 50) // 10
            for i in range(num):
                while not spawnLuckyBlock(random.randint(0, 3), random.randint(0, 3), x, y): pass

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)
            return 0


class APT(cards):  
    def __init__(self, owner, color, x, y, hp=6, atk=0):
        if color == "green":
            self.ATKtype = ""
            super().__init__(owner, "APTG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return False

    def atk(self, turn):
        if self.Attack(self.ATKtype.split(" "), 1, turn):
            for i in Board:
                if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                    if i.card == False:
                        luckyBlock("neutral", "green", i.BoardX, i.BoardY)
                        i.card = True
                        self.armor += 1
            return True
        return False
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0
