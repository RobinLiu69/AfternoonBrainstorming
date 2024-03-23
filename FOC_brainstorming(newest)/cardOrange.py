from variable import *
from calculate import update_data
from card import cards
import random

def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

def playCardOrange(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPO":
                SP("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTO":
                APT("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APO":
                AP("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCO":
                ADC("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKO":
                TANK("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFO":
                heavyFighter("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFO":
                lightFighter("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSO":
                ASS("player1", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
        if card == "MOVEO":
            P1Move[0] += 1
            player1Hand.remove(card)

            return True

    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPO":
                SP("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTO":
                APT("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APO":
                AP("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCO":
                ADC("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKO":
                TANK("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFO":
                heavyFighter("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFO":
                lightFighter("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSO":
                ASS("player2", "orange", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
        if card == "MOVEO":
            P2Move[0] += 1
            player2Hand.remove(card)
            return True
    return False



class TANK(cards):
    def __init__(self, owner, color, x, y, hp=10, atk=1):
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "TANKO", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=5, atk=2):
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "ADCO", hp, atk, x, y)
            self.M = 0

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if self.M == 0:
            self.M = 1
            self.moving = True
        return True
    
    def Maction(self, turn):
        if self.M == 1:
            self.Attack(self.ATKtype.split(" "), 1, turn)
            self.M = 0
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
    def __init__(self, owner, color, x, y, hp=2, atk=4):
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "ASSO", hp, atk, x, y)
            self.anger = 0

    def display(self, screen):
        if self.anger == 1:
            drawText("anger", small_text_font, self.selfColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8), screen)
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def Maction(self, turn):
        if self.anger == 0:
            self.anger = 1
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
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "APO", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        enemy.canATK = False
        return True

    def Maction(self, turn):
        if self.owner == "player1":
            player1Hand.append("MOVEO")
        if self.owner == "player2":
            player2Hand.append("MOVEO")
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        self.Maction(self.owner)
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class heavyFighter(cards):
    def __init__(self, owner, color, x, y, hp=9, atk=1):
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "HFO", hp, atk, x, y)
            self.M = 0

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        self.moving = True
        return True

    def Maction(self, turn):
        if turn == self.owner:
            self.M += 1
            self.attack += 1
        else:
            self.attack -= self.M
            self.M = 0
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 2, turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        self.Maction("None")
        
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class lightFighter(cards):
    def __init__(self, owner, color, x, y, hp=6, atk=2):
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "LFO", hp, atk, x, y)
            self.M = 0

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if self.M == 0:
            self.moving = True
        if self.M == 1:
            self.M = 0
        return True
    
    def Maction(self, turn):
        self.M = 1
        self.Attack(["nearest"], 1, turn)
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
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "SPO", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True
    
    def Maction(self, turn):
        self.M = self.attack
        self.attack = 5
        self.Attack(["farest"], 1, turn)
        self.attack = self.M
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
    def __init__(self, owner, color, x, y, hp=4, atk=3):
        if color == "orange":
            self.ATKtype = ""
            super().__init__(owner, "APTO", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return False
    
    def Maction(self, turn):
        if turn == "player1":
            Min = []
            if len(player1) > 1:
                for i in player1:
                    if i != self:
                        Min = [i]
                        break
            elif len(player1) == 1:
                self.armor += 1
                return True
            for i in player1:
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min = [i]
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min.append(i)
            if len(Min) > 1:
                i = random.randint(0, len(Min)-1)
                self.armor += 1
                Min[i].armor += 1
                return True
            elif len(Min) == 1:
                self.armor += 1
                Min[0].armor += 1
                return True
        elif turn == "player2":
            Min = []
            if len(player2) > 1:
                for i in player2:
                    if i != self:
                        Min = [i]
                        break
            elif len(player2) == 1:
                self.armor += 1
                return True
            for i in player2:
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min = [i]
                if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(Min[0].BoardX-self.BoardX)+abs(Min[0].BoardY-self.BoardY) and i != self:
                    Min.append(i)
            if len(Min) > 1:
                i = random.randint(0, len(Min)-1)
                self.armor += 1
                Min[i].armor += 1
                return True
            elif len(Min) == 1:
                self.armor += 1
                Min[0].armor += 1
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

