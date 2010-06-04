#!/usr/bin/env python

"""
Cellular automata engine.

Copyright (C) Sarah Mount, 2010.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'June 2010'

import pygame

screen_size = (width, height) = (640, 480) #(250, 250) 
fgcol = pygame.color.Color('white') # Foreground colour
bgcol = pygame.color.Color('black') # Background colour
grid = (150, 150, 150)
fps = 1


class Cell(object):
    SIZE = 15
    def __init__(self, position):
        self.image = pygame.Surface((Cell.SIZE, Cell.SIZE))
        self.image.fill(bgcol)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.state = bgcol
        self.dirty = False # For dirty rect animation.
        self.neighbours = None # (x,y) |-> Cell dictionary
        return

    def update(self, rule):
        old = self.state
        self.state = rule(self.state, self.neighbours)
        self.dirty = old != self.state
        if self.dirty: self.image.fill(self.state)
        return

    def off(self):
        return self.update(lambda state, near: bgcol)

    def flip(self):
        return self.update(lambda state, near: bgcol if state == fgcol else fgcol)


class CellWorld(object):
    GRID_SIZE = 2
    def __init__(self, rules, screen):
        self.rules = rules
        self.screen = screen
        screen.fill(grid)
        near = {'N':None, 'E':None, 'W':None, 'S':None,
                'NE':None, 'NW':None, 'SE':None, 'SW':None}
        # Create cells.
        self.cells = {}
        for x in xrange(0, width, Cell.SIZE + CellWorld.GRID_SIZE):
            for y in xrange(0, height, Cell.SIZE + CellWorld.GRID_SIZE):
                self.cells[(x,y)] = (Cell((x,y)))
                self.screen.blit(self.cells[(x,y)].image,
                                 self.cells[(x,y)].rect)
        # Generate neighbour dictionaries.
        for (x,y) in self.cells:
            near['N'] = self.get_cell((x, (y - (Cell.SIZE + CellWorld.GRID_SIZE)) % height))
            near['S'] = self.get_cell((x, (y + (Cell.SIZE + CellWorld.GRID_SIZE)) % height))
            near['E'] = self.get_cell(((x + (Cell.SIZE + CellWorld.GRID_SIZE)) % width, y))
            near['W'] = self.get_cell(((x - (Cell.SIZE + CellWorld.GRID_SIZE)) % width, y))
            near['NE'] = self.get_cell(((x + (Cell.SIZE + CellWorld.GRID_SIZE)) % width,
                                     (y - (Cell.SIZE + CellWorld.GRID_SIZE)) % height))
            near['SE'] = self.get_cell(((x + (Cell.SIZE + CellWorld.GRID_SIZE)) % width,
                                     (y + (Cell.SIZE + CellWorld.GRID_SIZE)) % height))
            near['NW'] = self.get_cell(((x - (Cell.SIZE + CellWorld.GRID_SIZE)) % width,
                                     (y - (Cell.SIZE + CellWorld.GRID_SIZE)) % height))
            near['SW'] = self.get_cell(((x - (Cell.SIZE + CellWorld.GRID_SIZE)) % width,
                                     (y + (Cell.SIZE + CellWorld.GRID_SIZE)) % height))
            self.cells[(x,y)].neighbours = near.copy()
        pygame.display.flip()
        return

    def update(self):
        map(lambda cell: cell.update(self.rules), self.cells.values())
        dirty = [cell for cell in self.cells.values() if cell.dirty]
        map(lambda cell: self.screen.blit(cell.image, cell.rect), dirty)
        return dirty
        
    def get_cell(self, (pos_x, pos_y)):
        for (x,y) in self.cells:
            if abs(pos_x - x) <= Cell.SIZE and abs(pos_y - y) <= Cell.SIZE:
                return self.cells[(x,y)]
        return None

    def create_starting_conditions(self):
        print ('Click on any cell to activate.\n' +
               'Press the spacebar to clear all cells.\n' +
               'Press return to start the simulation.')
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit()
                elif (event.type == pygame.MOUSEBUTTONDOWN or
                      event.type == pygame.MOUSEMOTION):
                    if pygame.mouse.get_pressed()[0]:
                        cell = self.get_cell(pygame.mouse.get_pos())
                        if cell is None: continue
                        cell.flip()
                        self.screen.blit(cell.image, cell.rect)
                        pygame.display.update(cell.rect)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: return
                    elif event.key == pygame.K_SPACE:
                        for cell in self.cells.values():
                            cell.off()
                            self.screen.blit(cell.image, cell.rect)
                        rects = [cell.rect for cell in self.cells.values()]
                        pygame.display.update(rects)


def game(rules):
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('PyAutomata')
    screen.fill(grid)

    text = pygame.font.Font(None, 36).render('Loading...', 1, fgcol)
    textpos = text.get_rect()
    textpos.center = screen.get_rect().center
    screen.blit(text, textpos)

    pygame.display.flip()
    world = CellWorld(rules, screen)
    world.create_starting_conditions()
    clock = pygame.time.Clock()
    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
        pygame.display.update(world.update())


def module_from_path(path):
    """
    By dF: http://stackoverflow.com/questions/863234/python-module-by-path
    """
    import imp
    import os
    filename = os.path.basename(path)
    modulename = os.path.splitext(filename)[0]
    with open(path) as f:
        return imp.load_module(modulename, f, path, ('py', 'U', imp.PY_SOURCE))


if __name__ == '__main__':
    import wx
    app = wx.PySimpleApp()
    dialog = wx.FileDialog (None, message='Open something...', style=wx.OPEN )
    if dialog.ShowModal() == wx.ID_OK:
       selected = dialog.GetPaths()[0]
    else:
       print 'Nothing was selected.'
    dialog.Destroy()
    Rules = module_from_path(selected)
    game(Rules.rules)
    
