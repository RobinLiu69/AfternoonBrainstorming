from variable import *
from calculate import update_data
from card import cards
import random
import pygame

def playCardCyan(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPC":
                SP("player1", "cyan", BX, BY, False)

                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTC":
                APT("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APC":
                AP("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCC":
                ADC("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKC":
                TANK("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFC":
                heavyFighter("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFC":
                lightFighter("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSC":
                ASS("player1", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "SPC$":
                SP("player1", "cyan", BX, BY, True, hp=2, atk=5)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTC$":
                APT("player1", "cyan", BX, BY, True, hp=7, atk=2)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APC$":
                AP("player1", "cyan", BX, BY, True, hp=5, atk=3)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCC$":
                ADC("player1", "cyan", BX, BY, True, hp=5, atk=3)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKC$":
                TANK("player1", "cyan", BX, BY, True, hp=11, atk=1)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFC$":
                heavyFighter("player1", "cyan", BX, BY, True, hp=9, atk=2)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFC$":
                lightFighter("player1", "cyan", BX, BY, True, hp=7, atk=4)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSC$":
                ASS("player1", "cyan", BX, BY, True, hp=2, atk=4)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True

    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPC":
                SP("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTC":
                APT("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APC":
                AP("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCC":
                ADC("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKC":
                TANK("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFC":
                heavyFighter("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFC":
                lightFighter("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSC":
                ASS("player2", "cyan", BX, BY, False)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "SPC$":
                SP("player2", "cyan", BX, BY, True, hp=2, atk=5)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTC$":
                APT("player2", "cyan", BX, BY, True, hp=7, atk=2)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APC$":
                AP("player2", "cyan", BX, BY, True, hp=5, atk=3)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCC$":
                ADC("player2", "cyan", BX, BY, True, hp=5, atk=3)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKC$":
                TANK("player2", "cyan", BX, BY, True, hp=11, atk=1)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFC$":
                heavyFighter("player2", "cyan", BX, BY, True, hp=9, atk=2)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFC$":
                lightFighter("player2", "cyan", BX, BY, True, hp=7, atk=4)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSC$":
                ASS("player2", "cyan", BX, BY, True, hp=2, atk=4)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True


class TANK(cards):
    def __init__(self, owner, color, x, y, golden, hp=9, atk=1):
        self.golden = golden
        self.enhance = 0
        if golden == True:
            self.enhance = 1
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "TANKC", hp, atk, x, y)
            
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
    def __init__(self, owner, color, x, y, golden, hp=4, atk=1):
        self.golden = golden
        self.enhance = 0
        if golden == True:
            self.enhance = 1
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "ADCC", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
            if self.owner == "player1":
                P1Coin[0] += 2
                return True
            elif self.owner == "player2":
                P2Coin[0] += 2
                return True

    def atk(self, turn):
        if self.enhance == 1:
            self.Attack(self.ATKtype.split(" "), 1, turn)
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
    def __init__(self, owner, color, x, y, golden, hp=1, atk=3):
        self.golden = golden
        self.enhance = 0
        if golden == True:
            self.enhance = 1
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "ASSC", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, golden, hp=4, atk=1):
        self.golden = golden
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "APC", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, golden, hp=7, atk=1):
        self.golden = golden
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "HFC", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
            if self.owner == "player1":
                P1Coin[0] += 2
                return True
            elif self.owner == "player2":
                P2Coin[0] += 2
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
    def __init__(self, owner, color, x, y, golden, hp=5, atk=2):
        self.golden = golden
        self.enhance = 0
        if golden == True:
            self.enhance = 1
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "LFC", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if self.enhance == 1:
            if self.owner == "player1":
                P1Coin[0] += 4
                return True
            elif self.owner == "player2":
                P2Coin[0] += 4
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
    def __init__(self, owner, color, x, y, golden, hp=1, atk=2):
        self.golden = golden
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "SPC", hp, atk, x, y)
        if color == "cyan":
            if self.owner == "player1":
                P1Coin[0] += 10
            elif self.owner == "player2":
                P2Coin[0] += 10

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
    def __init__(self, owner, color, x, y, golden, hp=2, atk=1):
        self.golden = golden
        self.enhance = 0
        if golden == True:
            self.enhance = 1
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "APTC", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 1, turn)
    
    def sTurn(self, turn):
        if self.enhance == 1:
            if self.owner == "player1":
                P1Coin[0] += 4
                return True
            elif self.owner == "player2":
                P2Coin[0] += 4
                return True
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0
