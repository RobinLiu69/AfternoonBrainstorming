import pygame
import random
from variable import player1Deck, player2Deck, displayCardW, displayCardR, gameDisplay, displayCardG, displayCardB, displayCardDKG, display_width, display_height, blocksize, displayCardO, displayCardP, displayCardC, small_text_font, text_font, big_text_font, Timer
# ----------
import cardWhite as cW
import cardRed as cR
import cardGreen as cG
import cardBlue as cB
import cardOrange as cO
import cardPurple as cP
import cardDKGreen as cDKG
import cardCyan as cC

# ---------

board = []
clock = pygame.time.Clock()
black = (0, 0, 0)
white = (255, 255, 255)
clock = pygame.time.Clock()
run = True
turn = "player1"

def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

class boardSpawn:
    def __init__(self, x, y, width, height, card, color):
        self.type = "Board"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.card = card
        self.size = width
        self.color = color
        self.thickness = 2
        board.append(self)

    def display(self, screen):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.width, self.height), 4)
        
def main():
    global run, board, turn, clock, black, white
    pygame.init()

    x = display_width/2-(blocksize*2)
    y = display_height/2-(blocksize*1.65)
    for i in range(3):
        x = display_width/2-(blocksize*2)
        for ii in range(4):
            boardSpawn(x, y, blocksize*1.01,
                            blocksize*1.01, False, white)
            x += blocksize
        y += blocksize

    cW.SP("display", "white", 0, 0)
    cW.APT("display", "white", 1, 0)
    cW.AP("display", "white", 2, 0)
    cW.ADC("display", "white", 3, 0)
    cW.TANK("display", "white", 0, 1)
    cW.heavyFighter("display", "white", 1, 1)
    cW.lightFighter("display", "white", 2, 1)
    cW.ASS("display", "white", 3, 1)
    CUBE = cW.cube("display", "white", 0, 2)

    cR.SP("display", "red", 0, 0)
    cR.APT("display", "red", 1, 0)
    cR.AP("display", "red", 2, 0)
    cR.ADC("display", "red", 3, 0)
    cR.TANK("display", "red", 0, 1)
    cR.heavyFighter("display", "red", 1, 1)
    cR.lightFighter("display", "red", 2, 1)
    cR.ASS("display", "red", 3, 1)

    cG.SP("display", "green", 0, 0)
    cG.APT("display", "green", 1, 0)
    cG.AP("display", "green", 2, 0)
    cG.ADC("display", "green", 3, 0)
    cG.TANK("display", "green", 0, 1)
    cG.heavyFighter("display", "green", 1, 1)
    cG.lightFighter("display", "green", 2, 1)
    cG.ASS("display", "green", 3, 1)

    cB.SP("display", "blue", 0, 0)
    cB.APT("display", "blue", 1, 0)
    cB.AP("display", "blue", 2, 0)
    cB.ADC("display", "blue", 3, 0)
    cB.TANK("display", "blue", 0, 1)
    cB.heavyFighter("display", "blue", 1, 1)
    cB.lightFighter("display", "blue", 2, 1)
    cB.ASS("display", "blue", 3, 1)

    cO.SP("display", "orange", 0, 0)
    cO.APT("display", "orange", 1, 0)
    cO.AP("display", "orange", 2, 0)
    cO.ADC("display", "orange", 3, 0)
    cO.TANK("display", "orange", 0, 1)
    cO.heavyFighter("display", "orange", 1, 1)
    cO.lightFighter("display", "orange", 2, 1)
    cO.ASS("display", "orange", 3, 1)

    cDKG.SP("display", "dkgreen", 0, 0)
    cDKG.APT("display", "dkgreen", 1, 0)
    cDKG.AP("display", "dkgreen", 2, 0)
    cDKG.ADC("display", "dkgreen", 3, 0)
    cDKG.TANK("display", "dkgreen", 0, 1)
    cDKG.heavyFighter("display", "dkgreen", 1, 1)
    cDKG.lightFighter("display", "dkgreen", 2, 1)
    cDKG.ASS("display", "dkgreen", 3, 1)


    # cP.SP("display", "purple", 0, 0)
    # cP.APT("display", "purple", 1, 0)
    cP.AP("display", "purple", 2, 0)
    # cP.ADC("display", "purple", 3, 0)
    cP.TANK("display", "purple", 0, 1)
    cP.heavyFighter("display", "purple", 1, 1)
    # cP.lightFighter("display", "purple", 2, 1)
    cP.ASS("display", "purple", 3, 1)

    cC.SP("display", "cyan", 0, 0, 0)
    cC.APT("display", "cyan", 1, 0, 0)
    cC.AP("display", "cyan", 2, 0, 0)
    cC.ADC("display", "cyan", 3, 0, 0)
    cC.TANK("display", "cyan", 0, 1, 0)
    cC.heavyFighter("display", "cyan", 1, 1, 0)
    cC.lightFighter("display", "cyan", 2, 1, 0)
    cC.ASS("display", "cyan", 3, 1, 0)

    canS = True
    canC = True
    canE = True
    canR = True
    canW = True
    canD = True
    canA = True
    canT = True
    canSEE = True
    page = 1
    while run:
        gameDisplay.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        mouseX, mouseY = pygame.mouse.get_pos()
        BX = int((mouseX-(display_width/2-blocksize*2))/blocksize)
        BY = int((mouseY-(display_height/2-blocksize*1.65))/blocksize)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            run = False
        if turn != "ready":
            drawText("chose your faction and cards", text_font, white,
                    display_width/2.4, display_height/5-(display_height/20), gameDisplay)
            drawText("key.s and mouse location to add card to your deck, key.c to remove the last card",
                    text_font, white, display_width/3.7, display_height/5-(display_height/55), gameDisplay)
            drawText("key.e to change player1/2, key.r to start the game(*2)",
                    text_font, white, display_width/3.7, display_height/5, gameDisplay)
        drawText("HEAL", text_font, white,
                 (display_width/2-(blocksize*2))+(blocksize*1)+(blocksize*0.375),
                 (display_height/2-(blocksize*1.65))+(blocksize*2)+(blocksize*0.45), gameDisplay)
        drawText("MOVE", text_font, white,
                 (display_width/2-(blocksize*2))+(blocksize*2)+(blocksize*0.375),
                 (display_height/2-(blocksize*1.65))+(blocksize*2)+(blocksize*0.45), gameDisplay)
        if keys[pygame.K_r] and canR == True:
            if len(player1Deck) == 12 and len(player2Deck) == 12:
                if turn == "ready":
                    run = False
                turn = "ready"
            canR = False
        elif not keys[pygame.K_r] and canR == False:
            canR = True
        if turn == "ready":
            drawText("ready!!!", big_text_font, white, display_width/2.2,
                    display_height/5-(display_height/20), gameDisplay)

        if keys[pygame.K_d] and canD == True:
            if page < 8:
                page += 1
            else:
                page = 1
            canD = False
        elif not keys[pygame.K_d] and canD == False:
            canD = True

        if keys[pygame.K_a] and canA == True:
            if page > 1:
                page -= 1
            else:
                page = 8
            canA = False
        elif not keys[pygame.K_a] and canA == False:
            canA = True


        if keys[pygame.K_t] and canT == True:
            if Timer[0]:
                Timer[0] = False
            else:
                Timer[0] = True
            canT = False
        elif not keys[pygame.K_t] and canT == False:
            canT = True
        if Timer[0]:
            drawText("Timer:ON", text_font, white, display_width/5,
                    display_height/1.4, gameDisplay)
        else:
            drawText("Timer:OFF", text_font, white, display_width/5,
                    display_height/1.4, gameDisplay)

        if keys[pygame.K_s] and canS == True:
            if BX <= 3 and BY <= 3 and mouseX > int((display_width/2-blocksize*2)) and mouseY > int((display_height/2-blocksize*1.65)):
                if turn == "player1" and len(player1Deck) <= 11:
                    if page == 1:
                        if BX+(BY*4) == 0 and player1Deck.count("SPW") < 2:
                            player1Deck.append("SPW")
                        if BX+(BY*4) == 1 and player1Deck.count("APTW") < 2:
                            player1Deck.append("APTW")
                        if BX+(BY*4) == 2 and player1Deck.count("APW") < 2:
                            player1Deck.append("APW")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCW") < 2:
                            player1Deck.append("ADCW")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKW") < 2:
                            player1Deck.append("TANKW")
                        if BX+(BY*4) == 5 and player1Deck.count("HFW") < 2:
                            player1Deck.append("HFW")
                        if BX+(BY*4) == 6 and player1Deck.count("LFW") < 2:
                            player1Deck.append("LFW")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSW") < 2:
                            player1Deck.append("ASSW")
                    if page == 2:
                        if BX+(BY*4) == 0 and player1Deck.count("SPR") < 2:
                            player1Deck.append("SPR")
                        if BX+(BY*4) == 1 and player1Deck.count("APTR") < 2:
                            player1Deck.append("APTR")
                        if BX+(BY*4) == 2 and player1Deck.count("APR") < 2:
                            player1Deck.append("APR")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCR") < 2:
                            player1Deck.append("ADCR")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKR") < 2:
                            player1Deck.append("TANKR")
                        if BX+(BY*4) == 5 and player1Deck.count("HFR") < 2:
                            player1Deck.append("HFR")
                        if BX+(BY*4) == 6 and player1Deck.count("LFR") < 2:
                            player1Deck.append("LFR")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSR") < 2:
                            player1Deck.append("ASSR")
                    if page == 3:
                        if BX+(BY*4) == 0 and player1Deck.count("SPG") < 2:
                            player1Deck.append("SPG")
                        if BX+(BY*4) == 1 and player1Deck.count("APTG") < 2:
                            player1Deck.append("APTG")
                        if BX+(BY*4) == 2 and player1Deck.count("APG") < 2:
                            player1Deck.append("APG")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCG") < 2:
                            player1Deck.append("ADCG")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKG") < 2:
                            player1Deck.append("TANKG")
                        if BX+(BY*4) == 5 and player1Deck.count("HFG") < 2:
                            player1Deck.append("HFG")
                        if BX+(BY*4) == 6 and player1Deck.count("LFG") < 2:
                            player1Deck.append("LFG")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSG") < 2:
                            player1Deck.append("ASSG")
                    if page == 4:
                        if BX+(BY*4) == 0 and player1Deck.count("SPB") < 2:
                            player1Deck.append("SPB")
                        if BX+(BY*4) == 1 and player1Deck.count("APTB") < 2:
                            player1Deck.append("APTB")
                        if BX+(BY*4) == 2 and player1Deck.count("APB") < 2:
                            player1Deck.append("APB")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCB") < 2:
                            player1Deck.append("ADCB")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKB") < 2:
                            player1Deck.append("TANKB")
                        if BX+(BY*4) == 5 and player1Deck.count("HFB") < 2:
                            player1Deck.append("HFB")
                        if BX+(BY*4) == 6 and player1Deck.count("LFB") < 2:
                            player1Deck.append("LFB")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSB") < 2:
                            player1Deck.append("ASSB")
                    if page == 5:
                        if BX+(BY*4) == 0 and player1Deck.count("SPO") < 2:
                            player1Deck.append("SPO")
                        if BX+(BY*4) == 1 and player1Deck.count("APTO") < 2:
                            player1Deck.append("APTO")
                        if BX+(BY*4) == 2 and player1Deck.count("APO") < 2:
                            player1Deck.append("APO")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCO") < 2:
                            player1Deck.append("ADCO")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKO") < 2:
                            player1Deck.append("TANKO")
                        if BX+(BY*4) == 5 and player1Deck.count("HFO") < 2:
                            player1Deck.append("HFO")
                        if BX+(BY*4) == 6 and player1Deck.count("LFO") < 2:
                            player1Deck.append("LFO")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSO") < 2:
                            player1Deck.append("ASSO")
                    if page == 6:
                        if BX+(BY*4) == 0 and player1Deck.count("SPDKG") < 2:
                            player1Deck.append("SPDKG")
                        if BX+(BY*4) == 1 and player1Deck.count("APTDKG") < 2:
                            player1Deck.append("APTDKG")
                        if BX+(BY*4) == 2 and player1Deck.count("APDKG") < 2:
                            player1Deck.append("APDKG")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCDKG") < 2:
                            player1Deck.append("ADCDKG")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKDKG") < 2:
                            player1Deck.append("TANKDKG")
                        if BX+(BY*4) == 5 and player1Deck.count("HFDKG") < 2:
                            player1Deck.append("HFDKG")
                        if BX+(BY*4) == 6 and player1Deck.count("LFDKG") < 2:
                            player1Deck.append("LFDKG")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSDKG") < 2:
                            player1Deck.append("ASSDKG")
                    
                    if page == 7:
                        if BX+(BY*4) == 0 and player1Deck.count("SPC") < 2:
                            player1Deck.append("SPC")
                        if BX+(BY*4) == 1 and player1Deck.count("APTC") < 2:
                            player1Deck.append("APTC")
                        if BX+(BY*4) == 2 and player1Deck.count("APC") < 2:
                            player1Deck.append("APC")
                        if BX+(BY*4) == 3 and player1Deck.count("ADCC") < 2:
                            player1Deck.append("ADCC")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKC") < 2:
                            player1Deck.append("TANKC")
                        if BX+(BY*4) == 5 and player1Deck.count("HFC") < 2:
                            player1Deck.append("HFC")
                        if BX+(BY*4) == 6 and player1Deck.count("LFC") < 2:
                            player1Deck.append("LFC")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSC") < 2:
                            player1Deck.append("ASSC")
                    
                    if page == 8:
                        # if BX+(BY*4) == 0 and player1Deck.count("SPP") < 2:
                        #     player1Deck.append("SPP")
                        # if BX+(BY*4) == 1 and player1Deck.count("APTP") < 2:
                        #     player1Deck.append("APTP")
                        if BX+(BY*4) == 2 and player1Deck.count("APP") < 2:
                            player1Deck.append("APP")
                        # if BX+(BY*4) == 3 and player1Deck.count("ADCP") < 2:
                        #     player1Deck.append("ADCP")
                        if BX+(BY*4) == 4 and player1Deck.count("TANKP") < 2:
                            player1Deck.append("TANKP")
                        if BX+(BY*4) == 5 and player1Deck.count("HFP") < 2:
                            player1Deck.append("HFP")
                        # if BX+(BY*4) == 6 and player1Deck.count("LFP") < 2:
                        #     player1Deck.append("LFP")
                        if BX+(BY*4) == 7 and player1Deck.count("ASSP") < 2:
                            player1Deck.append("ASSP")
                    
                    
                    
                    if BX+(BY*4) == 8 and player1Deck.count("CUBE") < 3:
                        player1Deck.append("CUBE")
                    if BX+(BY*4) == 9 and player1Deck.count("HEAL") < 3:
                        player1Deck.append("HEAL")
                    if BX+(BY*4) == 10 and player1Deck.count("MOVE") < 3:
                        player1Deck.append("MOVE")

                if turn == "player2" and len(player2Deck) <= 11:
                    if page == 1:
                        if BX+(BY*4) == 0 and player2Deck.count("SPW") < 2:
                            player2Deck.append("SPW")
                        if BX+(BY*4) == 1 and player2Deck.count("APTW") < 2:
                            player2Deck.append("APTW")
                        if BX+(BY*4) == 2 and player2Deck.count("APW") < 2:
                            player2Deck.append("APW")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCW") < 2:
                            player2Deck.append("ADCW")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKW") < 2:
                            player2Deck.append("TANKW")
                        if BX+(BY*4) == 5 and player2Deck.count("HFW") < 2:
                            player2Deck.append("HFW")
                        if BX+(BY*4) == 6 and player2Deck.count("LFW") < 2:
                            player2Deck.append("LFW")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSW") < 2:
                            player2Deck.append("ASSW")
                    if page == 2:
                        if BX+(BY*4) == 0 and player2Deck.count("SPR") < 2:
                            player2Deck.append("SPR")
                        if BX+(BY*4) == 1 and player2Deck.count("APTR") < 2:
                            player2Deck.append("APTR")
                        if BX+(BY*4) == 2 and player2Deck.count("APR") < 2:
                            player2Deck.append("APR")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCR") < 2:
                            player2Deck.append("ADCR")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKR") < 2:
                            player2Deck.append("TANKR")
                        if BX+(BY*4) == 5 and player2Deck.count("HFR") < 2:
                            player2Deck.append("HFR")
                        if BX+(BY*4) == 6 and player2Deck.count("LFR") < 2:
                            player2Deck.append("LFR")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSR") < 2:
                            player2Deck.append("ASSR")
                    if page == 3:
                        if BX+(BY*4) == 0 and player2Deck.count("SPG") < 2:
                            player2Deck.append("SPG")
                        if BX+(BY*4) == 1 and player2Deck.count("APTG") < 2:
                            player2Deck.append("APTG")
                        if BX+(BY*4) == 2 and player2Deck.count("APG") < 2:
                            player2Deck.append("APG")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCG") < 2:
                            player2Deck.append("ADCG")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKG") < 2:
                            player2Deck.append("TANKG")
                        if BX+(BY*4) == 5 and player2Deck.count("HFG") < 2:
                            player2Deck.append("HFG")
                        if BX+(BY*4) == 6 and player2Deck.count("LFG") < 2:
                            player2Deck.append("LFG")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSG") < 2:
                            player2Deck.append("ASSG")
                    if page == 4:
                        if BX+(BY*4) == 0 and player2Deck.count("SPB") < 2:
                            player2Deck.append("SPB")
                        if BX+(BY*4) == 1 and player2Deck.count("APTB") < 2:
                            player2Deck.append("APTB")
                        if BX+(BY*4) == 2 and player2Deck.count("APB") < 2:
                            player2Deck.append("APB")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCB") < 2:
                            player2Deck.append("ADCB")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKB") < 2:
                            player2Deck.append("TANKB")
                        if BX+(BY*4) == 5 and player2Deck.count("HFB") < 2:
                            player2Deck.append("HFB")
                        if BX+(BY*4) == 6 and player2Deck.count("LFB") < 2:
                            player2Deck.append("LFB")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSB") < 2:
                            player2Deck.append("ASSB")
                    if page == 5:
                        if BX+(BY*4) == 0 and player2Deck.count("SPO") < 2:
                            player2Deck.append("SPO")
                        if BX+(BY*4) == 1 and player2Deck.count("APTO") < 2:
                            player2Deck.append("APTO")
                        if BX+(BY*4) == 2 and player2Deck.count("APO") < 2:
                            player2Deck.append("APO")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCO") < 2:
                            player2Deck.append("ADCO")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKO") < 2:
                            player2Deck.append("TANKO")
                        if BX+(BY*4) == 5 and player2Deck.count("HFO") < 2:
                            player2Deck.append("HFO")
                        if BX+(BY*4) == 6 and player2Deck.count("LFO") < 2:
                            player2Deck.append("LFO")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSO") < 2:
                            player2Deck.append("ASSO")
                    if page == 6:
                        if BX+(BY*4) == 0 and player2Deck.count("SPDKG") < 2:
                            player2Deck.append("SPDKG")
                        if BX+(BY*4) == 1 and player2Deck.count("APTDKG") < 2:
                            player2Deck.append("APTDKG")
                        if BX+(BY*4) == 2 and player2Deck.count("APDKG") < 2:
                            player2Deck.append("APDKG")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCDKG") < 2:
                            player2Deck.append("ADCDKG")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKDKG") < 2:
                            player2Deck.append("TANKDKG")
                        if BX+(BY*4) == 5 and player2Deck.count("HFDKG") < 2:
                            player2Deck.append("HFDKG")
                        if BX+(BY*4) == 6 and player2Deck.count("LFDKG") < 2:
                            player2Deck.append("LFDKG")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSDKG") < 2:
                            player2Deck.append("ASSDKG")
                    
                    if page == 7:
                        if BX+(BY*4) == 0 and player2Deck.count("SPC") < 2:
                            player2Deck.append("SPC")
                        if BX+(BY*4) == 1 and player2Deck.count("APTC") < 2:
                            player2Deck.append("APTC")
                        if BX+(BY*4) == 2 and player2Deck.count("APC") < 2:
                            player2Deck.append("APC")
                        if BX+(BY*4) == 3 and player2Deck.count("ADCC") < 2:
                            player2Deck.append("ADCC")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKC") < 2:
                            player2Deck.append("TANKC")
                        if BX+(BY*4) == 5 and player2Deck.count("HFC") < 2:
                            player2Deck.append("HFC")
                        if BX+(BY*4) == 6 and player2Deck.count("LFC") < 2:
                            player2Deck.append("LFC")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSC") < 2:
                            player2Deck.append("ASSC")
                    
                    if page == 8:
                        # if BX+(BY*4) == 0 and player2Deck.count("SPP") < 2:
                        #     player2Deck.append("SPP")
                        # if BX+(BY*4) == 1 and player2Deck.count("APTP") < 2:
                        #     player2Deck.append("APTP")
                        if BX+(BY*4) == 2 and player2Deck.count("APP") < 2:
                            player2Deck.append("APP")
                        # if BX+(BY*4) == 3 and player2Deck.count("ADCP") < 2:
                        #     player2Deck.append("ADCP")
                        if BX+(BY*4) == 4 and player2Deck.count("TANKP") < 2:
                            player2Deck.append("TANKP")
                        if BX+(BY*4) == 5 and player2Deck.count("HFP") < 2:
                            player2Deck.append("HFP")
                        # if BX+(BY*4) == 6 and player2Deck.count("LFP") < 2:
                        #     player2Deck.append("LFP")
                        if BX+(BY*4) == 7 and player2Deck.count("ASSP") < 2:
                            player2Deck.append("ASSP")
                    
                    if BX+(BY*4) == 8 and player2Deck.count("CUBE") < 3:
                        player2Deck.append("CUBE")
                    if BX+(BY*4) == 9 and player2Deck.count("HEAL") < 3:
                        player2Deck.append("HEAL")
                    if BX+(BY*4) == 10 and player2Deck.count("MOVE") < 3:
                        player2Deck.append("MOVE")
            canS = False
        elif not keys[pygame.K_s] and canS == False:
            canS = True
        if keys[pygame.K_c] and canC == True:
            if turn == "player1" and len(player1Deck) >= 1:
                player1Deck.pop(-1)
            if turn == "player2" and len(player2Deck) >= 1:
                player2Deck.pop(-1)
            canC = False
        elif not keys[pygame.K_c] and canC == False:
            canC = True
        if keys[pygame.K_e] and canE == True:
            if turn == "player1" and canSEE == True:
                canSEE = False
                turn = 0
            elif turn == 0 and canSEE == False:
                canSEE = True
                turn = "player2"
            elif turn == "player2" and canSEE == True:
                canSEE = False
                turn = 1
            elif turn == 1 and canSEE == False:
                canSEE = True
                turn = "player1"
            canE = False
        elif not keys[pygame.K_e] and canE == False:
            canE = True
        if turn == "player1" and canSEE == True:
            drawText("yourDeck:", text_font, white, display_width/16 *
                    2, display_height-(display_height/5), gameDisplay)
            drawText("P2Deck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5/1.5), gameDisplay)
            x = display_height/14
            for i in range(len(player1Deck)):
                drawText(player1Deck[i], text_font, white, display_width/16*(i+3),
                        display_height-(display_height/5), gameDisplay)

            for i in range(len(player2Deck)):
                if i < 6:
                    drawText(player2Deck[i], text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5/1.5), gameDisplay)
                if player2Deck[i] and i > 5:
                    drawText("??", text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5)/1.5, gameDisplay)
        elif canSEE == False:
            drawText("P1Deck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5), gameDisplay)
            drawText("P2Deck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5/1.5), gameDisplay)
            for i in range(len(player1Deck)):
                if player1Deck[i]:
                    drawText("??", text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5), gameDisplay)
            for i in range(len(player2Deck)):
                if player2Deck[i]:
                    drawText("??", text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5)/1.5, gameDisplay)
        elif turn == "player2" and canSEE == True:
            drawText("P1Deck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5), gameDisplay)
            drawText("yourDeck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5/1.5), gameDisplay)
            x = display_height/14

            for i in range(len(player2Deck)):
                drawText(player2Deck[i], text_font, white, display_width/16*(i+3),
                        display_height-(display_height/5/1.5), gameDisplay)

            for i in range(len(player1Deck)):
                if i < 6:
                    drawText(player1Deck[i], text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5), gameDisplay)
                if player1Deck[i] and i > 5:
                    drawText("??", text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5), gameDisplay)
        elif turn == "ready":
            drawText("P1Deck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5), gameDisplay)
            drawText("P2Deck:", text_font, white, display_width/16*2,
                    display_height-(display_height/5/1.5), gameDisplay)
            for i in range(len(player1Deck)):
                if i < 6:
                    drawText(player1Deck[i], text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5), gameDisplay)
                if player1Deck[i] and i > 5:
                    drawText("??", text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5), gameDisplay)
            for i in range(len(player2Deck)):
                if i < 6:
                    drawText(player2Deck[i], text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5/1.5), gameDisplay)
                if player2Deck[i] and i > 5:
                    drawText("??", text_font, white, display_width/16*(i+3),
                            display_height-(display_height/5)/1.5, gameDisplay)
        for i in board:
            i.display(gameDisplay)
        if page == 1:
            for i in displayCardW:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 2:
            for i in displayCardR:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 3:
            for i in displayCardG:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 4:
            for i in displayCardB:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 5:
            for i in displayCardO:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 6:
            for i in displayCardDKG:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 7:
            for i in displayCardC:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 8:
            for i in displayCardP:
                i.display(gameDisplay)
                CUBE.display(gameDisplay)
        if page == 1:
            drawText("key.d to change the sects of the units", text_font, white, display_width/16*2,
                    display_height-(display_height/4), gameDisplay)
        if page == 2:
            drawText("Note that healing cards(key.h) can only restore health up to the maximum amount of health a player can have.", text_font, white, display_width/16*2,
                    display_height-(display_height/4), gameDisplay)

        if page == 3:
            drawText("When you use the Cube cards you can press key.p to spawn two cubes(neutral units) where you want.", text_font, white, display_width/16*2,
                    display_height-(display_height/4), gameDisplay)

        if page == 4:
            drawText("Moving cards(key.m) use it to move your units", text_font, white, display_width/16*2,
                    display_height-(display_height/4), gameDisplay)

        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)
