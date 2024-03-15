from variable import *
from calculate import update_data
from card import cards
import random
import pygame

def playCardWhite(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPW":
                SP("player1", "white", BX, BY)

                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTW":
                APT("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APW":
                AP("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCW":
                ADC("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKW":
                TANK("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFW":
                heavyFighter("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFW":
                lightFighter("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSW":
                ASS("player1", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            
        if card == "CUBE":
            P1Cube[0] += 2
            tag = 1
        if card == "HEAL":
            P1Heal[0] += 1
            tag = 1
        if card == "MOVE":
            P1Move[0] += 1
            tag = 1
        if tag == 1:
            player1Trash.append(card)
            player1Hand.remove(card)
            return True
    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPW":
                SP("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTW":
                APT("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APW":
                AP("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCW":
                ADC("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKW":
                TANK("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFW":
                heavyFighter("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFW":
                lightFighter("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSW":
                ASS("player2", "white", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            
        if card == "CUBE":
            P2Cube[0] += 2
            tag = 1
        if card == "HEAL":
            P2Heal[0] += 1
            tag = 1
        if card == "MOVE":
            P2Move[0] += 1
            tag = 1
        if tag == 1:
            player2Trash.append(card)
            player2Hand.remove(card)
            return True
    return False



class cube(cards):
    def __init__(self, owner, color, x, y, hp=4, atk=0):
        if color == "white":
            self.ATKtype = ""
            color = (255, 255, 255)
            self.selfColor = color
            super().__init__(owner, "cube", hp, atk, x, y)

    def display(self, screen):
        pygame.draw.rect(screen, self.selfColor,
                         ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.425),
                          (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.425),
                          blocksize*0.15, blocksize*0.15), 4) # type: ignore
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        return False

    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        return 0

class TANK(cards):
    def __init__(self, owner, color, x, y, hp=15, atk=1):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "TANKW", hp, atk, x, y)
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


class ADC(cards):
    def __init__(self, owner, color, x, y, hp=5, atk=4):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "ADCW", hp, atk, x, y)

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


class ASS(cards):
    def __init__(self, owner, color, x, y, hp=2, atk=5):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "ASSW", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=4, atk=3):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "APW", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        enemy.canATK = False
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
    def __init__(self, owner, color, x, y, hp=9, atk=2):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "HFW", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
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
    def __init__(self, owner, color, x, y, hp=7, atk=3):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "LFW", hp, atk, x, y)

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


class SP(cards):
    def __init__(self, owner, color, x, y, hp=1, atk=5):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "SPW", hp, atk, x, y)

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
            update_data(self.type, self.owner, '得分數', 2) 
            return 1


class APT(cards):
    def __init__(self, owner, color, x, y, hp=8, atk=2):
        if color == "white":
            self.ATKtype = ""
            super().__init__(owner, "APTW", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if turn == "player1":
            Min = []
            if len(player1) > 1:
                for i in player1:
                    if i != self:
                        Min = [i]
                        break
            elif len(player1) == 1:
                self.armor += 2
                return True
            for i in player1:
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min = [i]
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min.append(i)
            if len(Min) > 1:
                i = random.randint(0, len(Min)-1)
                self.armor += 2
                Min[i].armor += 2
                return True
            elif len(Min) == 1:
                self.armor += 2
                Min[0].armor += 2
                return True
        elif turn == "player2":
            Min = []
            if len(player2) > 1:
                for i in player2:
                    if i != self:
                        Min = [i]
                        break
            elif len(player2) == 1:
                self.armor += 2
                return True
            for i in player2:
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min = [i]
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min.append(i)
            if len(Min) > 1:
                i = random.randint(0, len(Min)-1)
                self.armor += 2
                Min[i].armor += 2
                return True
            elif len(Min) == 1:
                self.armor += 2
                Min[0].armor += 2
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
