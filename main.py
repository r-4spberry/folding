# -*- coding: cp1251 -*-
import pygame
import folder, refolder
from sys import exit as exit_

def main():
    FPS = 30
    pygame.init()
    scr = pygame.display.set_mode((500, 500))
    scr.fill((200, 200, 200))
    
    fold = folder.Button((170, 170, 170), 500//2-200//2, 200, 200, 40, text="Складывание")
    refold = folder.Button((170, 170, 170), 500//2-200//2, 260, 200, 40, text="Восстановление")
    
    fold.draw(scr)
    refold.draw(scr)
    pygame.display.update()
    
    running = True
    while running:
        pygame.time.wait(1000//FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                exit = True
                
        if fold.isOver(pygame.mouse.get_pos(), events) == True:
            running = False
            next = folder.main()
            exit = False
        
        if refold.isOver(pygame.mouse.get_pos(), events) == True:
            running = False
            next = refolder.main()
            exit = False
    if not exit:
        next()
    exit_()
    

if __name__ == "__main__":
    main()
    