from variable import *
import random
import pygame


class AtkDisplay:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def displayBlocks(self, screen, number):
        for i in range(1, 11):
            color = (255, 255, 255)
            if number > 10:
                if number < 20:
                    if number%10 - i+1%10 >0:
                        color = (100, 255, 255)
                        pygame.draw.rect(screen, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                    else:
                        color = (255, 255, 255)
                        pygame.draw.rect(screen, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                elif number < 30:
                    if number%10 - i+1%10 >0:
                        color = (255, 100, 100)
                        pygame.draw.rect(screen, color, (self.x+random.randint(0, round(self.width*0.1*(number*0.05)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(number*0.05)))*random.random(), self.width, self.height), round(self.width))
                    else:
                        color = (100, 255, 255)
                        pygame.draw.rect(screen, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                else:
                    color = (255, 100, 100)
                    pygame.draw.rect(screen, color, (self.x+random.randint(0, round(self.width*0.1*(number*0.1)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(number*0.1)))*random.random(), self.width, self.height), round(self.width))
            elif i <= number:
                pygame.draw.rect(screen, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
            else:
                pygame.draw.rect(screen, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width/10))
                
                

class ScoreDisplay:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.booling = 1
           
    def displayBlocks(self, screen, number, turn):
        if self.booling < 5:
            self.booling += 1
        else:
            self.booling = 1
        P1Score = 0
        P2Score = 0
        for i in player1:
            if i.canATK == True:
                P1Score -= 1
                if i.type == "SPW":
                    P1Score -= 1
        for i in player2:
            if i.canATK == True:
                P2Score += 1
                if i.type == "SPW":
                    P2Score += 1
        if turn == "player1":
            color1 = (100, 100, 255)
            color2 = (255, 100, 100)
            color1D = (100, 100, 255, 160)
            color2D = (255, 100, 100, 50)
            P1Score += number
            P2Score += P1Score
        elif turn == "player2":
            color2 = (100, 100, 255)
            color1 = (255, 100, 100)
            color2D = (100, 100, 255, 160)
            color1D = (255, 100, 100, 50)
            P2Score += number
            P1Score += P2Score
        else:
            return False
            
        for i in range(-10, 11):
            if number == i:
                pygame.draw.rect(screen, (255, 255, 255), (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width))
                if i == P1Score and P1Score != P2Score:
                    if turn == "player2":
                        pygame.draw.rect(screen, color1D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
                if i == P2Score and P2Score != P1Score:
                    if turn == "player1":
                        pygame.draw.rect(screen, color2D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
            elif i == P2Score and i == P1Score:
                if i == 10:
                    if P2Score > 9:
                        pygame.draw.rect(screen, color2, (self.x+self.width*i*1.25+random.randint(0, round(self.width*0.2))*random.random(), self.y+random.randint(0, round(self.height*0.2))*random.random(), self.width*1, self.height*1), round(self.width))
                    else:
                        pygame.draw.rect(screen, color2, (self.x+self.width*i*1.25, self.y, self.width*1, self.height*1), round(self.width))
                elif i == -10:
                    if P1Score < -9:
                        pygame.draw.rect(screen, color1, (self.x+self.width*i*1.25+random.randint(0, round(self.width*0.2))*random.random(), self.y+random.randint(0, round(self.height*0.2))*random.random(), self.width*1, self.height*1), round(self.width))
                    else:
                        pygame.draw.rect(screen, color1, (self.x+self.width*i*1.25, self.y, self.width*1, self.height*1), round(self.width))
                else:
                    if turn == "player1":
                        pygame.draw.rect(screen, color1D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width))
                        pygame.draw.rect(screen, color2D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
                    if turn == "player2":
                        pygame.draw.rect(screen, color2D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width))
                        pygame.draw.rect(screen, color1D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
            elif i == P1Score:
                    if turn == "player1":
                        pygame.draw.rect(screen, color1D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width))
                    if turn == "player2":
                        pygame.draw.rect(screen, color1D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
            elif i == P2Score:
                if turn == "player2":
                    pygame.draw.rect(screen, color2D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width))
                if turn == "player1":
                    pygame.draw.rect(screen, color2D, (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
            else:
                if i == 10:
                    if P2Score > 9:
                        pygame.draw.rect(screen, color2, (self.x+self.width*i*1.25+random.randint(0, round(self.width*0.2))*random.random(), self.y+random.randint(0, round(self.height*0.2))*random.random(), self.width*1, self.height*1), round(self.width))
                    else:
                        pygame.draw.rect(screen, color2, (self.x+self.width*i*1.25, self.y, self.width*1, self.height*1), round(self.width))
                elif i == -10:
                    if P1Score < -9:
                        pygame.draw.rect(screen, color1, (self.x+self.width*i*1.25+random.randint(0, round(self.width*0.2))*random.random(), self.y+random.randint(0, round(self.height*0.2))*random.random(), self.width*1, self.height*1), round(self.width))
                    else:
                        pygame.draw.rect(screen, color1, (self.x+self.width*i*1.25, self.y, self.width*1, self.height*1), round(self.width))
                else:
                    pygame.draw.rect(screen, (255, 255, 255), (self.x+self.width*i*1.25, self.y, self.width, self.height), round(self.width/10))
                
        
class TokenDisplay:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.time = 0
        self.bool = True
    
    def displayCircle(self, screen, number):
        if  self.bool:
            self.time += 1
            if self.time == 60:
                self.bool = not self.bool
        else:
            self.time -= 1
            if self.time == 0:
                self.bool = not self.bool
        if number > 0:
            for i in range(0, number):
                pygame.draw.circle(screen, (60*min(1, self.time/30), 100*min(1, self.time/30), 225*min(1, self.time/30)), (self.x, self.y-self.radius*i*2.2), self.radius)
            