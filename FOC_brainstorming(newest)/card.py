from mimetypes import types_map
from variable import *
from calculate import update_data
import random


colors_dict = {'B': "Blue", 'R': "Red", 'G': "Green", 'W': "White", 'O': "Orange", 'P': "Purple", 'DKG': "DarkGreen", 'C': "Cyan"}

ATKtype_tags = {'ADC': ("Bigx", "ADC"),
                'AP': ("nearest", "AP"),
                'TANK': ("cross", "TANK"),
                'HF': ("cross x", "HF"),
                'LF': ("cross", "LF"),
                'ASS': ("x", "ASS"),
                'APT': ("nearest", "APT"),
                'SP': ("farest", "SP")}
sorted_tags = sorted(colors_dict.keys(), key=len, reverse=True)

def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))


class cards:
    def __init__(self, owner, type: str, health, attack, x, y):
        self.owner = owner
        self.originalAttack = attack
        self.attack = attack
        self.health = health
        self.maxHeart = health
        self.canATK = True
        self.x = x
        self.y = y
        self.Board = x+(y*4)
        self.BoardX = x
        self.BoardY = y
        self.moving = False
        self.armor = 0
        self.type = type
        self.shape = None
        self.limited = 20
        self.anger = False
        
        name = self.type
        self.ATKtype = None
        types = (0, 0)
        for tag in sorted_tags:
                if name.endswith(tag):
                    name = name.replace(tag, "", 1)
                    break
        for tag in ATKtype_tags.keys():
            if name == tag:
                types = ATKtype_tags[tag]
                
        self.ATKtype = types[0] # type: ignore
        self.shapeType = types[1] # type: ignore
        
        if self.type == "cube":
            self.shape = "CUBE"
        if self.type == "luckyBlock":
            self.shape = "LUCKYBLOCK"
        elif self.shapeType == "ADC":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)), 
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)))
        elif self.shapeType == "HF":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.4)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.6), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.4)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)))
        elif self.shapeType == "LF":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.36), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.42)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4775), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.55)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.36), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.68)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.64), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.68)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5225), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.55)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.64), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.42)))
        elif self.shapeType == "ASS":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.4)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.2), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.8), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)))
        elif self.shapeType == "APT":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)), 
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.6), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.6), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)))
        elif self.shapeType == "SP":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.375), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.45)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.75)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.45)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.625), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)))

        if "ASS" in self.type:
            self.canATK = True
        else:
            self.canATK = False
        name = self.type
        color = 0
        for tag in sorted_tags:
            if name.endswith(tag):
                color = colors_dict[tag]
                break
        if color == 'Blue':
            self.selfColor = (60, 100, 225)
        if color == 'DarkGreen':
            self.selfColor = (85, 107, 47)
        if color == 'Green':
            self.selfColor = (51, 255, 51)
        if color == 'Orange':
            self.selfColor = (255, 69, 0)
        if color == "Purple":
            self.selfColor = (128, 0, 255)
        if color == 'Red':
            self.selfColor = (255, 0, 0)
        if color == 'White':
            self.selfColor = (255, 255, 255)
        if color == 'Cyan':
            self.selfColor = (0, 238, 238)

        if self.selfColor != (0, 238, 238):   
            self.textColor = self.selfColor
        else:
            if self.golden == 1:
                self.textColor = (255, 215, 0)
            else:
                self.textColor = self.selfColor
            
        if owner == "player1":
            player1.append(self)
        elif owner == "player2":
            player2.append(self)
        elif owner == "neutral":
            neutral.append(self)
        elif owner == "display":
            if color == 'Blue':
                displayCardB.append(self)
            if color == 'DarkGreen':
                displayCardDKG.append(self)
            if color == 'Green':
                displayCardG.append(self)
            if color == 'Orange':
                displayCardO.append(self)
            if color == "Purple":
                displayCardP.append(self)
            if color == 'Red':
                displayCardR.append(self)
            if color == 'White':
                displayCardW.append(self)
            if color == 'Cyan':
                displayCardC.append(self)

    def SPAdd(self, type: str, value: int) -> bool:#Red
        if type == "atk":
            if self.owner=="player1":
                for i in player1:
                    if i.type=="SPR":
                        i.attack+=value
                return True
            if self.owner=="player2":
                for i in player2:
                    if i.type=="SPR":
                        i.attack+=value
                    return True
        if type == "armor":
            if self.owner=="player1":
                for i in player1:
                    if i.type=="SPR":
                        i.armor+=value
                return True
            if self.owner=="player2":
                for i in player2:
                    if i.type=="SPR":
                        i.armor+=value
                return True
        if type == "hael":
            if self.owner=="player1":
                for i in player1:
                    if i.type=="SPR":
                        i.heal(value)
                return True
            if self.owner=="player2":
                for i in player2:
                    if i.type=="SPR":
                        i.heal(value)
        return False

    def reduction(self, value):
        if self.type == "TANKC":
            if self.enhance == 1:
                self.enhance = 0
                return 0
        if self.type == "APTC":
            if self.owner == "player1":
                value += int(P1Coin[0]/5)
            elif self.owner == "player2":
                value += int(P2Coin[0]/5)
            if value > 0: return 0
            return value
        return value
    
    def toteming(self, number):#DKG
        for i in range(number):
            if random.randint(1, 2) == 1:
                if self.owner == "player1":
                    P1totemHP[0] +=1
                if self.owner == "player2":
                    P2totemHP[0] +=1
            else:
                if self.owner == "player1":
                    P1totemAD[0] +=1
                if self.owner == "player2":
                    P2totemAD[0] +=1
    
    def startTurn(self, turn):
        self.moving = False
        self.sTurn(turn)
    
    def endTurn(self, turn):
        temp = 0
        self.moving = False
        temp += self.eTurn(turn)
        return temp
        
    def move(self, x, y):
        if Board[x+(y*4)].card == False:
            if (((abs(self.y-y) == 1 and (abs(self.x-x) == 1 or abs(self.x-x) == 0)) or (abs(self.y-y) == 0 and abs(self.x-x) == 1)) and (self.y != y or self.x != x) and self.moving == True) == False:
                self.moving = False
                return False
            Board[self.x+(self.y*4)].card = False
            self.x = x
            self.BoardX = x
            self.y = y
            self.BoardY = y
            self.Board = x+(y*4)
            Board[self.x+(self.y*4)].card = True
            self.moving = False

            #orange
            if self.type == "ADCO":
                self.Maction(self.owner) # type: ignore
            elif self.type == "HFO":
                self.Maction(self.owner) # type: ignore
            elif self.type == "LFO":
                self.Maction(self.owner) # type: ignore
            elif self.type == "ASSO":
                self.Maction(self.owner) # type: ignore

            if self.owner == "player2":
                for i in player1:
                    if i.type == "TANKP":
                        self.damage(2, i, self.owner)  
            if self.owner == "player1":
                for i in player2:
                    if i.type == "TANKP":
                        self.damage(2, i, self.owner)   
            if self.owner == "player1":
                for i in player1:
                    if i.type == "APTO":
                        i.armor += 1
                        self.armor += 1
                    if i.type == "SPO":
                        i.Maction(i.owner)
            if self.owner == "player2":
                for i in player2:
                    if i.type == "APTO":
                        i.armor += 1
                        self.armor += 1
                    if i.type == "SPO":
                        i.Maction(i.owner)
            if self.type == "APTO":
                self.Maction(self.owner)
            return True
        self.moving = False
        return False

    def APTAdd(self, type, value):#blue
        if type == "armor":
            if self.owner == "player1":
                for i in player1:
                    if i.type == "APTB":
                        i.armor += value

                return True
            if self.owner == "player2":
                for i in player2:
                    if i.type == "APTB":
                        i.armor += value
                return True
        return False

    def beenAttack(self, attacker: "cards"):
        print(f"{self.owner}的{self.type}被{attacker.owner}的{attacker.type}攻擊了")
        update_data(self.type, self.owner, '受到傷害次數', 1)

        #red
        if attacker.type == "APR":
            if self.attack >= 1:
                attacker.attack += self.attack//2
                attacker.SPAdd("atk", self.attack//2)
                self.attack -= self.attack//2
                
        if self.type == "TANKR":      
            if self.owner == "player1":
                temp = []
                if len(player1) > 1:
                    for i in player1:
                        if i != self:
                            temp = [i]
                            break
                elif len(player1) == 1:
                    return True
                for i in player1:
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp=[i]
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp.append(i)
                if len(temp)>1:
                    i=random.randint(0,len(temp)-1)
                    temp[i].armor+=2
                    self.SPAdd("armor",2)
                    return True
                elif len(temp)==1:
                    temp[0].armor+=2
                    self.SPAdd("armor",2)
                    return True
            elif self.owner=="player2":
                temp=[]
                if len(player2)>1:
                    for i in player2:
                        if i != self:
                            temp=[i]
                            break
                elif len(player2)==1:
                    return True
                for i in player2:
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY)<abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp=[i]
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY)==abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp.append(i)
                if len(temp)>1:
                    i=random.randint(0,len(temp)-1)
                    temp[i].armor+=2
                    self.SPAdd("armor",2)
                    return True
                elif len(temp)==1:
                    temp[0].armor+=2
                    self.SPAdd("armor",2)
                    return True

        if attacker.type == "APR":
            if self.attack >= 1:
                attacker.attack += 1
                attacker.SPAdd("attack", 1)
                self.attack -= 1

        #blue
        if self.type == "TANKB":
            if self.owner == "player1":
                P1Token[0] += 1
                self.APTAdd("armor", 1)
            if self.owner == "player2":
                P2Token[0] += 1
                self.APTAdd("armor", 1)
        #dkg
        if self.type == "TANKDKG":
                self.toteming(2)
        #green
        if self.type == "luckyBlock":
            self.ability(attacker, self.owner) # type: ignore

        if self.type == "TANKG":
            if self.owner == "player1":
                if random.randint(1, 100) <= P2Luck[0]:
                    pass
                else:
                    r = random.randint(1, 5)
                    if r == 1:
                        update_data(attacker.type,attacker.owner, '受到傷害次數', 1)
                        update_data(attacker.type,attacker.owner, '受到傷害', attacker.armor)
                        attacker.armor = 0
                    elif r == 2:
                        update_data(attacker.type,attacker.owner, '受到傷害次數', 1)
                        update_data(attacker.type,attacker.owner, '受到傷害', int(attacker.health/2))
                        attacker.health = int(attacker.health/2)
                    elif r == 3:
                        attacker.canATK = False
                    elif r == 4:
                        if attacker.health >= 2:
                            update_data(attacker.type,attacker.owner, '受到傷害次數', 1)
                            update_data(attacker.type,attacker.owner, '受到傷害', 2)
                            attacker.health -= 2
                    elif r == 5:
                        attacker.attack = int(attacker.attack/2)
                    # badluck
            if self.owner == "player2":
                if random.randint(1, 100) <= P1Luck[0]:
                    # goodluck
                    pass
                else:
                    r = random.randint(1, 5)
                    if r == 1:
                        update_data(attacker.type,attacker.owner, '受到傷害次數', 1)
                        update_data(attacker.type,attacker.owner, '受到傷害', attacker.armor)
                        attacker.armor = 0
                    elif r == 2:
                        update_data(attacker.type,attacker.owner, '受到傷害次數', 1)
                        update_data(attacker.type,attacker.owner, '受到傷害', int(attacker.health/2))
                        attacker.health = int(attacker.health/2)
                    elif r == 3:
                        attacker.canATK = False
                    elif r == 4:
                        if attacker.health >= 2:
                            update_data(attacker.type,attacker.owner, '受到傷害次數', 1)
                            update_data(attacker.type,attacker.owner, '受到傷害', 2)
                            attacker.health -= 2
                    elif r == 5:
                        attacker.attack = int(attacker.attack/2)
                    #Cyan
                    if self.type == "TANKC":
                        if self.owner == "player1":
                            P1Coin[0] += 3
                            return True
                        elif self.owner == "player2":
                            P2Coin[0] += 3
                            return True

        #orange
        if self.type == "TANKO":
            if self.owner == "player1":
                player1Hand.append("MOVEO")
            if self.owner == "player2":
                player2Hand.append("MOVEO")  
        return True

    def Kill(self):
        #blue
        if self.type == "ASSB":
            if self.owner == "player1":
                P1Token[0] += 2
                self.APTAdd("armor", 2)
                return True
            elif self.owner == "player2":
                P2Token[0] += 2
                self.APTAdd("armor", 2)
                return True
        if self.type == "ADCB":
            if self.owner == "player1":
                P1Token[0] += 1
                self.APTAdd("armor", 1)
                return True
            elif self.owner == "player2":
                P2Token[0] += 1
                self.APTAdd("armor", 1)
                return True
            
        #dkg
        if self.type == "ASSDKG":
            update_data(self.type,self.owner,'受到傷害次數', 1)
            update_data(self.type,self.owner,'受到傷害', self.health)
            self.toteming(6)
            self.health=0
            return True
        
        #green
        if self.type == "ASSG":
            if self.owner == "player1":
                P1Luck[0] += 5
                P2Luck[0] -= 5
                return True
            if self.owner == "player2":
                P2Luck[0] += 5
                P1Luck[0] -= 5
                return True
        
        #orange
        if self.type == "ASSO":
            self.moving = True
            if self.anger == 1:
                if self.owner == "player1":
                    P1atk[0] += 1
                    self.anger = 0
                if self.owner == "player2":
                    P2atk[0] += 1
                    self.anger = 0

        #purple
        if self.type == "ASSP":
            if self.owner == "player1":
                count = len(player2) - len(player1)  
                if  count > 2:
                    count = 2
                if count >= 1:
                    for i in range(0, count):
                        P1DrawCard[0] += 1
            if self.owner == "player2":
                count = len(player1) - len(player2)
                if  count > 2:
                    count = 2
                if count >= 1:
                    for i in range(0, count):
                        P2DrawCard[0] += 1
        
        #red
        if self.type == "ASSR":
            if self.owner == "player1":
                temp = []
                if len(player1) > 1:
                    for i in player1:
                        if i != self:
                            temp = [i]
                            break
                elif len(player1) == 1:
                    return True
                for i in player1:
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp = [i]
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp.append(i)
                if len(temp) > 1:
                    i = random.randint(0, len(temp)-1)
                    temp[i].attack += 2
                    self.SPAdd("atk", 2)
                    return True
                elif len(temp) == 1:
                    temp[0].attack += 2
                    self.SPAdd("atk", 2)
                    return True
            elif self.owner == "player2":
                temp = []
                if len(player2) > 1:
                    for i in player2:
                        if i != self:
                            temp = [i]
                            break
                elif len(player1) == 1:
                    return True
                for i in player2:
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp = [i]
                    if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY) and i!=self:
                        temp.append(i)
                if len(temp) > 1:
                    i = random.randint(0, len(temp)-1)
                    temp[i].attack += 2
                    self.SPAdd("atk", 2)
                    return True
                elif len(temp) == 1:
                    temp[0].attack += 2
                    self.SPAdd("atk", 2)
                    return True
        
        #Cyan
        if self.type == "ASSC":
            if self.owner == "player1":
                P1Coin[0] += 5
                return True
            elif self.owner == "player2":
                P2Coin[0] += 5
                return True
        return False
    
    def die(self, atker: "cards") -> bool:
        if self.type == "SPDKG":
            self.toteming(self.attack)
        return True

    def damage(self, value: int, atker: "cards", turn: str):
        if atker.type == "ADCDKG":
            if atker.owner == "player1":
                value += int(P1totemAD[0]/3)
            elif atker.owner == "player2":
                value += int(P2totemAD[0]/3)
        elif atker.type == "APTDKG":
            if atker.owner == "player1":
                value += int(P1totemAD[0]/2)
            elif atker.owner == "player2":
                value += int(P2totemAD[0]/2)
        elif atker.type == "ASSC":
            if atker.Enhance == 1:
                value += 3
                atker.Enhance = 0
        value = self.reduction(value)
        if value <= 0 or self.health <= 0:
            if self.selfColor == (255, 69, 0):
                self.ability(self, turn)
            return False
        if self.armor > 0 and self.armor >= value:
            if (self.type != "HFDKG" and self.owner != turn) or self.type != atker.type:
                update_data(atker.type, atker.owner, '造成傷害', value)
            update_data(self.type, self.owner, '受到傷害', value)
            if atker.type == "APTDKG":
                atker.armor += value//2 
            self.armor -= value
            self.beenAttack(atker)
            atker.ability(self, turn)           
            return True
        elif self.armor > 0 and self.armor < value:
            if self.health >= value-self.armor:
                if (self.type != "HFDKG" and self.owner != turn) or self.type != atker.type:
                    update_data(atker.type,atker.owner, '造成傷害', value)
                if atker.type == "APTDKG":
                    atker.armor += value//2
                update_data(self.type, self.owner, '受到傷害', value)
            if self.health < value-self.armor:
                if (self.type != "HFDKG" and self.owner != turn) or self.type != atker.type:
                    update_data(atker.type, atker.owner, '造成傷害', self.health+self.armor)
                if atker.type == "APTDKG":
                    atker.armor += self.health+self.armor//2
                update_data(self.type, self.owner, '受到傷害', self.health+self.armor)
            value = self.armor-value
            self.armor = 0
            self.health += value
            self.beenAttack(atker)
            atker.ability(self, turn)
            if self.health <= 0:
                atker.Kill()
                self.die(atker)
            return True
        elif self.armor == 0:
            if self.health >= value:
                if (self.type != "HFDKG" and self.owner != turn) or self.type != atker.type:
                    update_data(atker.type,atker.owner, '造成傷害', value)
                update_data(self.type, self.owner, '受到傷害', value)
            if self.health < value:
                if (self.type != "HFDKG" and self.owner != turn) or self.type != atker.type:
                    update_data(atker.type, atker.owner, '造成傷害', self.health)
                update_data(self.type, self.owner, '受到傷害', self.health)
            self.health -= value
            self.beenAttack(atker)
            atker.ability(self, turn)
            if self.health <= 0:
                atker.Kill()
                self.die(atker)
            return True
        return False

    def drawCard(self):
        if self.type == "ADCB":
            if self.canATK == False:
                self.canATK = True
                return True
            else:
                self.atk(self.owner)
                return True
        return False
    
    def heal(self, value):
        if self.health+value <= self.maxHeart:
            # if self.canATK == False:
            #     self.canATK = True
            self.health += value
            return True
        elif self.health+value > self.maxHeart:
            # if self.canATK == False:
            #     self.canATK = True
            self.health += value
            self.armor += (self.health - self.maxHeart)//2
            self.health = self.maxHeart
            return True
        # elif self.canATK == False:
        #     self.canATK = True
        #     return True
        return False

    def update(self, screen):
        if self.type == "SPG":
            drawText("HP:"+"?", text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.03), screen)
            drawText("ATK:"+"?", text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.03), screen)
            if self.owner != "display":
                drawText(str(self.owner), text_font, self.textColor,
                        ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                        (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8), screen)
            else:
                drawText(str(self.type), text_font, self.textColor,
                        ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                        (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8), screen)
            if self.canATK == False:
                drawText("numbness", small_text_font, self.textColor,
                        ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                        (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.85), screen)
            if self.armor > 0:
                drawText("arm:"+"?", small_text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.12), screen)
            if self.moving == True:
                drawText("Moving", small_text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.12), screen)
        else:
            drawText("HP:"+str(self.health), text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.03), screen)
            drawText("ATK:"+str(self.attack), text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.03), screen)
            if self.owner != "display":
                drawText(str(self.owner), text_font, self.textColor,
                        ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                        (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8), screen)
            else:
                drawText(str(self.type), text_font, self.textColor,
                        ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                        (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8), screen)
            if self.canATK == False:
                drawText("numbness", small_text_font, self.textColor,
                        ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                        (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.85), screen)
            if self.armor > 0:
                drawText("arm:"+str(self.armor), small_text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.1),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.12), screen)
            if self.moving == True:
                drawText("Moving", small_text_font, self.textColor,
                    ((display_width/2)-(blocksize*2))+(self.x*blocksize)+(blocksize*0.6),
                    (display_height/2)-(blocksize*1.65)+(self.y*blocksize)+(blocksize*0.12), screen)
            
        if self.attack < 0:
            self.attack = 0
        # shapes draw
        
        elif self.shapeType == "ADC":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)), 
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)))
        elif self.shapeType == "HF":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.4)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.6), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.4)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)))
        elif self.shapeType == "LF":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.36), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.42)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4775), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.55)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.36), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.68)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.8)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.64), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.68)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5225), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.55)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.64), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.42)))
        elif self.shapeType == "ASS":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.4)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.2), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.8), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.65)))
        elif self.shapeType == "APT":
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.4), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)), 
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.6), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.7)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.6), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)))
        elif self.shapeType == "SP":    
            self.shape = (((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.375), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.25), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.45)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.75)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.75), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.45)),
                        ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.625), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3)))

        if self.shapeType == "TANK":
            pygame.draw.rect(screen, self.selfColor,
                             ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.3), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.3), blocksize*0.4, blocksize*0.4), 4) # type: ignore
        elif self.shapeType == "AP":
            pygame.draw.circle(screen, self.selfColor,
                            ((display_width/2-blocksize*2)+(self.x*blocksize)+(blocksize*0.5), (display_height/2-blocksize*1.65)+(self.y*blocksize)+(blocksize*0.5)),
                            blocksize*0.2, 3)
        elif self.shape == "CUBE":
            pass
        elif self.shape == "LUCKYBLOCK":
            pass
        else:
            pygame.draw.lines(screen, self.selfColor, True, self.shape, 4) # type: ignore

    def Attack(self, type, time, turn, value: int=None):
        
        if self.canATK == True:
            count = 0
            if "cross" in type:
                if turn == "player1":
                    for i in player2:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                    for i in neutral:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                if turn == "player2":
                    for i in player1:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                    for i in neutral:
                        if (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX and i.BoardY == self.BoardY+1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                if count == 1 and len(type) == 1:
                    return True
            if "x" in type:
                if turn == "player1":
                    for i in player2:
                        if (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY-1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                    for i in neutral:
                        if (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY-1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                if turn == "player2":
                    for i in player1:
                        if (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY-1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                    for i in neutral:
                        if (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY+1) or (i.BoardX == self.BoardX-1 and i.BoardY == self.BoardY-1) or (i.BoardX == self.BoardX+1 and i.BoardY == self.BoardY-1):
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                if count == 1 and len(type) == 1:
                    return True
            if "Bigx" in type:
                if turn == "player1":
                    for i in player2:
                        if (i.BoardX == self.BoardX or i.BoardY == self.BoardY) and i.Board != self.Board:
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                    for i in neutral:
                        if (i.BoardX == self.BoardX or i.BoardY == self.BoardY) and i.Board != self.Board:
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                if turn == "player2":
                    for i in player1:
                        if (i.BoardX == self.BoardX or i.BoardY == self.BoardY) and i.Board != self.Board:
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                    for i in neutral:
                        if (i.BoardX == self.BoardX or i.BoardY == self.BoardY) and i.Board != self.Board:
                            if value != None: i.damage(value, self, turn)
                            else: i.damage(self.attack, self, turn)
                            count = 1
                if len(type) == 1 and count == 1:
                    return True
            if "nearest" in type:
                temp = []
                if turn == "player1":
                    if len(player2) >= 1:
                        temp = [player2[0]]
                    elif len(neutral) >= 1:
                        temp = [neutral[0]]
                    for i in player2:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    for i in neutral:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    if len(temp) > 1 and len(type) == 1:
                        i = random.randint(0, len(temp)-1)
                        if value != None: temp[i].damage(value, self, turn)
                        else: temp[i].damage(self.attack, self, turn)
                        return True
                    elif len(temp) == 1 and len(type) == 1:
                        if value != None: temp[i].damage(value, self, turn)
                        else: temp[0].damage(self.attack, self, turn)
                        return True
                if turn == "player2":
                    if len(player1) >= 1:
                        temp = [player1[0]]
                    elif len(neutral) >= 1:
                        temp = [neutral[0]]
                    for i in player1:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    for i in neutral:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) < abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    if len(temp) > 1 and len(type) == 1:
                        i = random.randint(0, len(temp)-1)
                        if value != None: temp[i].damage(value, self, turn)
                        else: temp[i].damage(self.attack, self, turn)
                        return True
                    elif len(temp) == 1 and len(type) == 1:
                        if value != None: temp[0].damage(value, self, turn)
                        else: temp[0].damage(self.attack, self, turn)
                        return True
            if "farest" in type:
                temp = [] # min暫代最遠的意思
                if turn == "player1":
                    if len(player2) >= 1:
                        temp = [player2[0]]
                    elif len(neutral) >= 1:
                        temp = [neutral[0]]
                    for i in player2:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) > abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    for i in neutral:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) > abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    if len(temp) > 1 and len(type) == 1:
                        i = random.randint(0, len(temp)-1)
                        if value != None: temp[i].damage(value, self, turn)
                        else: temp[i].damage(self.attack, self, turn)
                        return True
                    elif len(temp) == 1 and len(type) == 1:
                        if value != None: temp[0].damage(value, self, turn)
                        else: temp[0].damage(self.attack, self, turn)
                        return True
                if turn == "player2":
                    if len(player1) >= 1:
                        temp = [player1[0]]
                    elif len(neutral) >= 1:
                        temp = [neutral[0]]
                    for i in player1:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) > abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    for i in neutral:
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) > abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp = [i]
                        if abs(i.BoardX-self.BoardX)+abs(i.BoardY-self.BoardY) == abs(temp[0].BoardX-self.BoardX)+abs(temp[0].BoardY-self.BoardY):
                            temp.append(i)
                    if len(temp) > 1 and len(type) == 1:
                        i = random.randint(0, len(temp)-1)
                        if value != None: temp[i].damage(value, self, turn)
                        else: temp[i].damage(self.attack, self, turn)
                        return True
                    elif len(temp) == 1 and len(type) == 1:
                        if value != None: temp[0].damage(value, self, turn)
                        else: temp[0].damage(self.attack, self, turn)
                        return True
            if count == 1:
                return True
        else:
            return False
