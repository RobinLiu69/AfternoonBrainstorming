import pygame
pygame.init()
Board = []
BoardUI = []
neutral = []
displayCardW = []
displayCardR = []
displayCardG = []
displayCardB = []
displayCardO = []
displayCardP = []
displayCardDKG = []
displayCardC = []
player1 = []
player2 = []
player1Deck = []
player2Deck = []
player1Trash = []
player2Trash = []
player1Hand = []
player2Hand = []
P1Token = [0]
P2Token = [0]
P1totemHP = [0]
P2totemHP = [0]
P1totemAD = [0]
P2totemAD = [0]
P1atk = [1]
P2atk = [0]
P1Cube = [0]
P2Cube = [0]
P1Move = [0]
P2Move = [0]
P1Heal = [0]
P2Heal = [0]
P1Luck = [50]
P2Luck = [50]
P1DrawCard = [0]
P2DrawCard = [0]
P1Coin = [0]
P2Coin = [0]
Timer = [False]
TimeLine = []
Turns = [1]


display_info= pygame.display.get_desktop_sizes()
display_width = display_info[0][0]
display_height = display_info[0][1]

# display_info= pygame.display.get_desktop_sizes()
# display_width = 1920
# display_height = 1080


print(display_width, display_height)
if display_width/display_height == 1.6:
    gameDisplay = pygame.display.set_mode(
        (display_width, display_height), pygame.FULLSCREEN)
    blocksize = (display_width/8)/1.2
else:
    maxvalue = [0, 0]
    for H in range(display_height, 0, -1):
        for W in range(display_width, 0, -1):
            if W/H == 1.6:
                maxvalue = [W, H]
                break
        if maxvalue != [0, 0]:
            break
    display_width = maxvalue[0]
    display_height = maxvalue[1]
    gameDisplay = pygame.display.set_mode(
        (display_width, display_height))
    blocksize = (display_width/8)/1.2
print(display_width, display_height)


text_font_size = int(display_width/1500*16.5)
text_font = pygame.font.Font("8bitOperatorPlus-Bold.ttf", text_font_size)
big_text_font = pygame.font.Font(
    "8bitOperatorPlus-Bold.ttf", int(display_width/1500*25))
small_text_font = pygame.font.Font("8bitOperatorPlus-Bold.ttf", int(text_font_size/15*8.66))

WHOwin = [0]

P1matrix = [['角色', '攻擊次數', '造成傷害', '受到傷害次數', '受到傷害', '得分數']]
P2matrix = [['角色', '攻擊次數', '造成傷害', '受到傷害次數', '受到傷害', '得分數']]
