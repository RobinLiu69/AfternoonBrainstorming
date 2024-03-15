from variable import *
from calculate import makebarchart, makepiechart, makeplot
import os, sys
import pygame
import concurrent.futures
pygame.init()

white = (255, 255, 255)
black = (0, 0, 0)
run = True

loading_font = pygame.font.Font(None, 36)
loading_text = loading_font.render("Loading...", True, "white")
loading_animation = 0

code_path = os.getcwd()


def drawText(text, font, textColor, x, y, screen):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

display = []

class Object:
    def __init__(self, type, x, y, width, height, visule):
        self.type = type
        self.x = x
        self.y = y
        self.width = int(width)
        self.height = int(height)
        self.visule = visule
        display.append(self)

class Piechart(Object):
    def __init__(self, player, part, x, y):
        super().__init__('piechart', x, y, display_width/5, display_width/5, False)
        self.player = player
        self.part = part
        file_path = os.path.join(code_path, f'output/P{player}-{part}piechart.png')
        if os.path.exists(file_path):
            self.img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), ( self.width, self.height ))
        else:
            self.img = None
    def draw(self, screen):
        if self.visule == True and self.img!= None:
            screen.blit(self.img, (self.x, self.y))

class Plotchart(Object):
    def __init__(self, x, y):
        super().__init__('plotchart', x, y, display_width/30*20, display_width/30*8, True)
        file_path = os.path.join(code_path, f'output/plotchart.png')
        if os.path.exists(file_path):
            self.img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), ( self.width, self.height ))
        else:
            self.img = None
    def draw(self, screen):
        if self.visule == True and self.img!= None:
            screen.blit(self.img, (self.x, self.y))

class Barchart(Object):
    def __init__(self, player, part, x, y):
        super().__init__('barchart', x, y, display_width/6, display_width/6, False)
        self.player = player
        self.part = part
        file_path = os.path.join(code_path, f'output/P{player}-{part}barchart.png')
        if os.path.exists(file_path):
            self.img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), ( self.width, self.height ))
        else:
            self.img = None
    def draw(self, screen):
        if self.visule == True and self.img!= None:
            screen.blit(self.img, (self.x, self.y))

class briefing(Object):
    def __init__(self, x, y, width, height, text_size, text_color, player):
        super().__init__('briefing', x, y, width, height, True)
        self.rect = pygame.Rect(x, y, width, height)
        self.player = player
        self.text_size = int(text_size)
        self.text_color = text_color
        self.Listheight = (display_height/2)-50
        self.Listwidth = (display_width/2)-(display_width/5)
        self.matrix = ['Type', 'NoA', 'DD', 'NoHT', 'HT', 'Score']

    def draw(self, screen):
        if self.player == 1:
            if self.visule == True:
                for n in range(len(P1matrix)):
                    sitey = ((self.Listheight/len(P1matrix))*n)+(display_height/18)
                    for i in range(len(P1matrix[0])):
                        sitex = (self.Listwidth/len(P1matrix[0]))*i
                        if n == 0:
                            text_surface = text_font.render(self.matrix[i], True, self.text_color)
                            screen.blit(text_surface, ((sitex+(display_width/5)), sitey))
                        else:
                            text_surface = text_font.render(str(P1matrix[n][i]), True, self.text_color)
                            screen.blit(text_surface, ((sitex+(display_width/5)), sitey))
        if self.player == 2:
            if self.visule == True:
                for n in range(len(P2matrix)):
                    sitey = ((self.Listheight/len(P2matrix))*n)+(display_height/18)
                    for i in range(len(P2matrix[0])):
                        sitex = (self.Listwidth/len(P2matrix[0]))*i
                        if n == 0:
                            text_surface = text_font.render(self.matrix[i], True, self.text_color)
                            screen.blit(text_surface, ((sitex+(display_width/2)+100), sitey))
                        else:
                            text_surface = text_font.render(str(P2matrix[n][i]), True, self.text_color)
                            screen.blit(text_surface, ((sitex+(display_width/2)+100), sitey))
                     
buttons = []

class Button(Object):
    def __init__(self, x, y, width, height, text, text_size, text_color, bg_color, action, player):
        super().__init__('button', x, y, width, height, True)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.player = player
        self.text_size = int(text_size)
        self.text_color = text_color
        self.bg_color = bg_color
        self.action = action
        buttons.append(self)

    def draw(self, screen):
        if self.visule == True:
            pygame.draw.rect(screen, self.bg_color, self.rect)
            text_surface = text_font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action(self, self.player)
last_time = 0
wait_time = 0
countdown = 0
def playerDisplay(self, player):
    global last_time, countdown
    if countdown == 0:
        for i in range(len(display)):
            if display[i].type == "button" and display[i]!=self:
                if display[i].bg_color == (50, 50, 50):
                    return False  
        for i in display:
            if i.type == "barchart":
                if i.player == player:
                    if i.visule == False:
                        i.visule = True
                        self.bg_color = (50, 50, 50)
                    else:
                        i.visule = False
                        self.bg_color = (0, 0, 0)
            if i.type == "plotchart":
                if i.visule == False:
                    i.visule = True
                else:
                    i.visule = False
        for i in display:
            if i.type == "piechart":
                if i.player == player:
                    if i.visule == False:
                        countdown = 4
                        last_time = pygame.time.get_ticks()
                        self.bg_color = (50, 50, 50)
                        return True
                    else:
                        i.visule = False
                        self.bg_color = (0, 0, 0)
            if i.type == "briefing":
                if i.visule == False:
                    i.visule = True
                else:
                    i.visule = False
        return True
    return False

def exit(self, player):
    global run
    run = False
    return True
def makeimg():
    for i in range(1,6):
        it = i
        iP = i
        if iP > 2:
            iP -= 1
        if i == 3:
            continue
        makepiechart(P1matrix, i, "P1-")
        makepiechart(P2matrix, i, "P2-")
        Piechart(1, it, display_width/30*iP*6-display_width*0.08, display_height/3*iP*0.25)
        Piechart(2, it, display_width/30*iP*6-display_width*0.08, display_height/3*iP*0.25)
        print(f"makeingPieChat:{i}")
    for i in range(1,5):
        makebarchart(P1matrix, i, "P1-")
        Barchart(1, i, display_width/13*i*2.25, display_height/3*3*0.7)
        makebarchart(P2matrix, i, "P2-")
        Barchart(2, i, display_width/13*i*2.25, display_height/3*3*0.7)
        print(f"makeingBarChart:{i}")
    makeplot(TimeLine)
    Plotchart(display_width/13*2.25, display_height/3*3*0.55)
    print("makeTimeLine")
    return True


button1 = Button(display_width/10*2, display_height/10*5, 100, 50, "P1", text_font_size*1.5, white, black, playerDisplay, 1)
button2 = Button(display_width/10*3, display_height/10*5, 100, 50, "P2", text_font_size*1.5, white, black, playerDisplay, 2)
button3 = Button(display_width/10*4, display_height/10*5, 100, 50, "esc", text_font_size*1.5, white, black, exit, None)
button4 = briefing(display_width/10*4, display_height/10*5, 100, 50, text_font_size*1.5, white, 1)
button5 = briefing(display_width/10*4, display_height/10*5, 100, 50, text_font_size*1.5, white, 2)
mouse_clicked = False

time_delay = 75

loading_text = "Loading"
loading_animation = 0

waiting = True
clock = pygame.time.Clock()
loading_x = display_width/2*0.9

def waitscreen():
    global loading_text, loading_animation, waiting, loading_animation, loading_x, wait_time, display_width, display_height
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        gameDisplay.fill(black)
        wait_time += 1
        if wait_time > 200:
            loading_x = display_width/3*1.2
            loading_text = "Error:Runtimeout"
            if wait_time > 250:
                waiting = False
                pygame.quit()
        else:
            if loading_animation <20:
                loading_animation += 1
                loading_x -= loading_animation/15
            else:
                loading_animation = 0
                loading_x = display_width/2*0.9
        drawText(loading_text, big_text_font, white, loading_x, display_height/2, gameDisplay)
        
        if loading_animation == 0:
            loading_text = "Loading"
        if loading_animation == 5:
            loading_text = "Loading."
        if loading_animation == 10:
            loading_text = "Loading.."
        if loading_animation == 15:
            loading_text = "Loading..."
        pygame.display.update()
        clock.tick(10)
def main():
    global waiting, run, countdown, last_time, time_delay, display_width, display_height, P1matrix, P2matrix, TimeLine
    pygame.init()

    print (P1matrix)
    print (P2matrix)
    print (TimeLine)

    if P1matrix == [['角色', '攻擊次數', '造成傷害', '受到傷害次數', '受到傷害', '得分數']] and P2matrix == [['角色', '攻擊次數', '造成傷害', '受到傷害次數', '受到傷害', '得分數']] and TimeLine == []:
        P1matrix = [['角色', '攻擊次數', '造成傷害', '受到傷害次數', '受到傷害', '得分數'], ['ADCR', 2, 22, 1, 4, 1], ['ASSB', 1, 6, 1, 2, 2], ['LFR', 0, 0, 3, 5, 2], ['HFO', 0, 0, 3, 9, 0], ['HFB', 0, 0, 3, 8, 0]]
        P2matrix = [['角色', '攻擊次數', '造成傷害', '受到傷害次數', '受到傷害', '得分數'], ['TANKR', 0, 0, 3, 10, 6], ['SPR', 0, 0, 2, 8, 0], ['ASSR', 1, 4, 1, 2, 1], ['TANKG', 0, 0, 0, 0, 3], ['LFR', 3, 11, 0, 0, 2], ['ADCR', 3, 13, 0, 0, 1], ['APTR', 0, 0, 0, 0, 1], ['ASSO', 0, 0, 0, 0, 1]]
        TimeLine = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 3, 1, 4, 2, 10]


    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(waitscreen)
        makeimg()
        waiting = False
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not mouse_clicked:
                    mouse_clicked = True
                    for i in buttons:
                        i.handle_event(event)
        if pygame.mouse.get_pressed()[0] == 0:
            mouse_clicked = False
        
        current_time = pygame.time.get_ticks()
        
        if current_time - last_time >= time_delay and countdown > 0:
            player = 0
            for i in range(len(buttons)):
                if buttons[i].bg_color == (50, 50, 50):
                    if buttons[i].player == 1:
                        player = 1
                        break
                    if buttons[i].player == 2:
                        player = 2
                        break
            if player != 0:
                for i in range(len(display)):
                    if display[i].type == "piechart":
                        if display[i].player == player:
                            if display[i].visule == False:
                                countdown -= 1
                                display[i].visule = True
                                last_time = pygame.time.get_ticks()
                                break


        gameDisplay.fill(black)
        # drawText("P1", small_text_font, white, 10, 10, gameDisplay)
        # drawText("P2", small_text_font, white, 10, 30, gameDisplay)
        for i in display:
            i.draw(gameDisplay)
        pygame.display.update()
        clock.tick(60)
    file_path = "output/"

    
    for i in range(1,6):
        if i == 3:
            continue
        try:
            os.unlink(f"{file_path}P1-{i}piechart.png")
        except OSError as e:
            print(f"删除失败：{e}")
        try:
            os.unlink(f"{file_path}P2-{i}piechart.png")
        except OSError as e:
            print(f"删除失败：{e}")
    for i in range(1,5):
        try:
            os.unlink(f"{file_path}P1-{i}barchart.png")
        except OSError as e:
            print(f"删除失败：{e}")
        try:
            os.unlink(f"{file_path}P2-{i}barchart.png")
        except OSError as e:
            print(f"删除失败：{e}")
    try:
        os.unlink(f"{file_path}plotchart.png")
    except OSError as e:
        print(f"删除失败：{e}")
    pygame.quit()