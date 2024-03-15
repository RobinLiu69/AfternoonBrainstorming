from variable import *
from calculate import update_data
from card import cards
import random


def playCardPurple(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPP":
                SP("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTP":
                APT("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APP":
                AP("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCP":
                ADC("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKP":
                TANK("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFP":
                heavyFighter("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFP":
                lightFighter("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSP":
                ASS("player1", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPP":
                SP("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTP":
                APT("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APP":
                AP("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCP":
                ADC("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKP":
                TANK("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFP":
                heavyFighter("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFP":
                lightFighter("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSP":
                ASS("player2", "purple", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
    return False



class TANK(cards):
    def __init__(self, owner, color, x, y, hp=9, atk=1):
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "TANKP", hp, atk, x, y)

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
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "ADCP", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=2, atk=3):
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "ASSP", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=3, atk=1):
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "APP", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        enemy.canATK = False
        enemy.armor = 0
        enemy.attack = enemy.originalAttack
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
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "HFP", hp, atk, x, y)
            
    def display(self, screen):
        self.update(screen)
        
    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 2, turn)
    
    def sTurn(self, turn):
        if turn == "player2":
            count = 0
            if len(player2) > 2:
                for i in player2:
                    if (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY-1):
                        count += 1
                        print(count)
                    if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                        count += 1
                        print(count)
            P1atk[0] += int(count/3)
            return True
        elif turn == "player1":
            count = 0
            if len(player1) > 2:
                for i in player1:
                    if (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY-1):
                        count += 1
                        print(count)
                    if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                        count += 1
                        print(count)
            P2atk[0] += int(count/3)
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
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "LFP", hp, atk, x, y)

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
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "SPP", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=8, atk=2):
        if color == "purple":
            self.ATKtype = ""
            super().__init__(owner, "APTP", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
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
