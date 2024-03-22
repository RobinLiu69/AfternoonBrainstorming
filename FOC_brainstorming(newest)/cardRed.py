from variable import *
from calculate import update_data
from card import cards

def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))


def playCardRed(turn, card, BX, BY,mouseX,mouseY):
    if turn == "player1":
        tag=0
        if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)) and Board[BX+(BY*4)].card == False:
            if card == "SPR":
                SP("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APTR":
                APT("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "APR":
                AP("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ADCR":
                ADC("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "TANKR":
                TANK("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "HFR":
                heavyFighter("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "LFR":
                lightFighter("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
            if card == "ASSR":
                ASS("player1", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player1Hand.remove(card)
                return True
    elif turn == "player2":
        tag=0
        if BX <= 3 and BY <= 3 and mouseX > (display_width/3.25) and mouseY > (display_height/4.2858) and Board[BX+(BY*4)].card == False:
            if card == "SPR":
                SP("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APTR":
                APT("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "APR":
                AP("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ADCR":
                ADC("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "TANKR":
                TANK("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "HFR":
                heavyFighter("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "LFR":
                lightFighter("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
            if card == "ASSR":
                ASS("player2", "red", BX, BY)
                Board[BX+(BY*4)].card = True
                player2Hand.remove(card)
                return True
    return False



class TANK(cards):
    def __init__(self, owner, color, x, y, hp=9, atk=1):
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "TANKR", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
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
    def __init__(self, owner, color, x, y, hp=4, atk=1):
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "ADCR", hp, atk, x, y)
            
    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        self.attack+=1
        self.SPAdd("atk",1)
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
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
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "ASSR", hp, atk, x, y)
            
    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
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
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "APR", hp, atk, x, y)

    def display(self, screen):
        self.update(screen)

    def ability(self, enemy, turn):
        enemy.canATK=False
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
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
    def __init__(self, owner, color, x, y, hp=9, atk=1):
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "HFR", hp, atk, x, y)
            self.anger = False
            
    def display(self, screen):
        if self.anger == True:
            drawText("anger", small_text_font, self.color,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8), screen)
        self.update(screen)
        
    def ability(self, enemy, turn):
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),2,turn)
    
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
    def __init__(self, owner, color, x, y, hp=5, atk=2):
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "LFR", hp, atk, x, y)
            
    def display(self, screen):
        self.update(screen)
        
    def ability(self, enemy, turn):
        self.armor+=1
        self.attack+=1
        self.SPAdd("atk",1)
        self.SPAdd("armor",1)
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
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
    def __init__(self, owner, color, x, y, hp=1, atk=2):
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "SPR", hp, atk, x, y)
            
    def display(self, screen):
        self.update(screen)
        
    def ability(self, enemy, turn):
        return True
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
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
    def __init__(self, owner, color, x, y, hp=3, atk=3):
        if color == "red":
            self.ATKtype = ""
            super().__init__(owner, "APTR", hp, atk, x, y)
            count = 0
            if owner=="player1":
                for i in player1:
                    if i !=self:
                        count+=i.attack
                self.armor+=int(count/2)
                self.SPAdd("armor",int(count/2))
            if owner=="player2":
                for i in player2:
                    if i !=self:
                        count+=i.attack
                self.armor+=int(count/2)
                self.SPAdd("armor",int(count/2))
    def display(self, screen):
        self.update(screen)
        
    def ability(self, enemy, turn):
        return False
    
    def atk(self, turn):
        return self.Attack(self.ATKtype.split(" "),1,turn)
    
    def sTurn(self, turn):
        return True
    
    def eTurn(self, turn):
        if self.canATK == False:
            self.canATK = True
            return -1
        else:
            update_data(self.type, self.owner, '得分數', 1)    
            return 0