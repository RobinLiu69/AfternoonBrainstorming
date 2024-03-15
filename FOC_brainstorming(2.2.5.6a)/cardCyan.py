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
                SP("player1", "cyan", BX, BY)

                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTC":
                APT("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APC":
                AP("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCC":
                ADC("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKC":
                TANK("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFC":
                heavyFighter("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFC":
                lightFighter("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSC":
                ASS("player1", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPC":
                SP("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTC":
                APT("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APC":
                AP("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCC":
                ADC("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKC":
                TANK("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFC":
                heavyFighter("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFC":
                lightFighter("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSC":
                ASS("player2", "cyan", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
        if tag == 1:
            player2Trash.append(card)
            player2Hand.remove(card)
            return True
    return False



class TANK(cards):
    def __init__(self, owner, color, x, y, hp=15, atk=1):
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
    def __init__(self, owner, color, x, y, hp=5, atk=4):
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "ADCC", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=4, atk=3):
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
    def __init__(self, owner, color, x, y, hp=9, atk=2):
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "HFC", hp, atk, x, y)

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
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "LFC", hp, atk, x, y)

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
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "SPC", hp, atk, x, y)

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
        if color == "cyan":
            self.ATKtype = ""
            super().__init__(owner, "APTC", hp, atk, x, y)

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
