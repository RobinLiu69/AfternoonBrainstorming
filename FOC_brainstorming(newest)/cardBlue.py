from variable import *
from calculate import update_data
from card import cards
import random

def playCardBlue(turn, card, BX, BY, mouseX, mouseY):
    if turn == "player1":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPB":
                SP("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTB":
                APT("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APB":
                AP("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCB":
                ADC("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKB":
                TANK("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFB":
                heavyFighter("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFB":
                lightFighter("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSB":
                ASS("player1", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True

    elif turn == "player2":
        tag = 0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2857) and Board[BX+(BY*4)].card == False:
            if card == "SPB":
                SP("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTB":
                APT("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APB":
                AP("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCB":
                ADC("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKB":
                TANK("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFB":
                heavyFighter("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFB":
                lightFighter("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSB":
                ASS("player2", "blue", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True


class TANK(cards):
    def __init__(self, owner, color, x, y, hp=10, atk=1):
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "TANKB", hp, atk, x, y)

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
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "ADCB", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=2, atk=4):
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "ASSB", hp, atk, x, y)

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
    def __init__(self, owner, color, x, y, hp=4, atk=2):
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "APB", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        enemy.canATK = False
        if self.type == "APB":
            if self.owner == "player1":
                P1Token[0] += 2
                self.APTAdd("armor", 2)
                return True
            elif self.owner == "player2":
                P2Token[0] += 2
                self.APTAdd("armor", 2)
                return True
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
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "HFB", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True

    def atk(self, turn):
        if self.owner == "player1":
            self.attack += P1Token[0]
        if self.owner == "player2":
            self.attack += P2Token[0]
        temp = self.Attack(self.ATKtype.split(" "), 2, turn)
        if self.owner == "player1":
            self.attack -= P1Token[0]
        if self.owner == "player2":
            self.attack -= P2Token[0]
        return temp
    
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
    def __init__(self, owner, color, x, y, hp=6, atk=3):
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "LFB", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        if self.owner == "player1":
            P1Token[0] += 1
            self.APTAdd("armor", 1)
            return True
        elif self.owner == "player2":
            P2Token[0] += 1
            self.APTAdd("armor", 1)
            return True
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
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "SPB", hp, atk, x, y)
            if self.owner == "player1":
                if len(player1Trash)+len(player1) >= 2:
                    for i in range(0, len(player1Trash)+len(player1)):
                        if len(player2) >= 1 or len(neutral) >= 1:
                            Min = []
                            for i in player2:
                                Min.append(i)
                            for i in neutral:
                                Min.append(i)
                            Min[random.randint(0, len(Min)-1)].damage(1, self, self.owner)
                    update_data(self.type, owner,'攻擊次數',1)
            if self.owner == "player2":
                if len(player2Trash)+len(player2) >= 2:
                    for i in range(0, len(player2Trash)+len(player2)):
                        if len(player1) >= 1 or len(neutral) >= 1:
                            Min = []
                            for i in player1:
                                Min.append(i)
                            for i in neutral:
                                Min.append(i)
                            Min[random.randint(0, len(Min)-1)].damage(1, self, self.owner)
                    update_data(self.type, owner,'攻擊次數',1)

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
    def __init__(self, owner, color, x, y, hp=4, atk=2):
        if color == "blue":
            self.ATKtype = ""
            super().__init__(owner, "APTB", hp, atk, x, y)

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