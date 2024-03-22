from variable import *
from calculate import update_data
from card import cards

def playCardDKGreen(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPDKG":
                SP("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTDKG":
                APT("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APDKG":
                AP("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCDKG":
                ADC("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKDKG":
                TANK("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFDKG":
                heavyFighter("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFDKG":
                lightFighter("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSDKG":
                ASS("player1", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPDKG":
                SP("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTDKG":
                APT("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APDKG":
                AP("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCDKG":
                ADC("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKDKG":
                TANK("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFDKG":
                heavyFighter("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFDKG":
                lightFighter("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSDKG":
                ASS("player2", "dkgreen", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
    return False



class TANK(cards):
    def __init__(self, owner, color, x, y, hp=9, atk=1):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "TANKDKG", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=4, atk=2):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "ADCDKG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        self.toteming(1)
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
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "ASSDKG", hp, atk, x, y)
            self.D = 0

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
    def __init__(self, owner, color, x, y, hp=4, atk=0):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "APDKG", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=8, atk=2):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "HFDKG", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        self.heal(1)
        return True

    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "), 2, turn)
    
    def sTurn(self, turn):
        self.damage(2, self, self.owner)
        self.toteming(2)
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0


class lightFighter(cards):
    def __init__(self, owner, color, x, y, hp=6, atk=3):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "LFDKG", hp, atk, x, y)
            if owner=="player1":
                for i in player2:
                    self.toteming(1)
            if owner=="player2":
                for i in player1:
                    self.toteming(1)

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
    def __init__(self, owner, color, x, y):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "SPDKG", 1, 3, x, y)
            if owner=="player1":
                if P1totemHP[0]>=2:
                    self.armor+=int(P1totemHP[0]-1)
                    P1totemHP[0]=0
                if P1totemAD[0]>=2:
                    self.attack+=int(P1totemAD[0])
                    P1totemAD[0]=0
            if owner=="player2":
                if P2totemHP[0]>=2:
                    self.armor+=int(P2totemHP[0]-1)
                    P2totemHP[0]=0
                if P2totemAD[0]>=2:
                    self.attack+=int(P2totemAD[0])
                    P2totemAD[0]=0

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
    def __init__(self, owner, color, x, y):
        if color == "dkgreen":
            self.ATKtype = ""
            super().__init__(owner, "APTDKG", 2, 2, x, y)
            if owner=="player1":
                self.armor+=int(P1totemHP[0]/2)
            if owner=="player2":
                self.armor+=int(P2totemHP[0]/2)

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
