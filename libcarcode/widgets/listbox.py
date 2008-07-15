from OpenGL.GL import *
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_8_BY_13

from pygame.locals import *

from button import Button
from constants import *
from events import EventDispatcher
from label import Label
from utils import Clipper, mangle_event
from widget import Widget

def Quad(v1, v2):
    glBegin(GL_LINE_STRIP)
    glVertex2f(v1[0], v1[1])
    glVertex2f(v2[0], v1[1])
    glVertex2f(v2[0], v2[1])
    glVertex2f(v1[0], v2[1])
    glVertex2f(v1[0], v1[1])
    glEnd()

class Arrow:
    def __init__(self, size, orientation):
        self.size = size
        self.orientation = orientation
    def draw(self):
        glPushMatrix()
        glScalef(self.size[0], self.size[1], 1.0)
        glBegin(GL_TRIANGLES)
        glColor4f(*COLOR_WHITE)
        if self.orientation == 1:
            glVertex2f(0.0, 1.0)
            glVertex2f(0.5, 0.0)
            glVertex2f(1.0, 1.0)
        else:
            glVertex2f(0.0, 0.0)
            glVertex2f(0.5, 1.0)
            glVertex2f(1.0, 0.0)
        glEnd()
        glPopMatrix()
        
class ListBox(Widget):
    """ Simple text item list """
    def __init__(self, *args,  **kargs):
        """ ListBox
        
            @param pos tuple with widget position (x, y)
            @param size tuple with widget size (width, height)
        """
        Widget.__init__(self,  *args,  **kargs)
        self.items = []
        self.maxrows = self.size[1] / 14
        self.selected = -1
        self.onSelected = EventDispatcher()
        self.visible = True
        self.arrowup = Button(Arrow((10,10), 1), (self.size[0]- 12 ,0), (12,12), backcolor=self.backcolor)
        self.arrowdown = Button(Arrow((10,10), 0), (self.size[0]- 12 ,self.size[1]-12), (12,12), backcolor=self.backcolor)
        self.arrowup.onClick.subscribe(self.scrollup)
        self.arrowdown.onClick.subscribe(self.scrolldown)
        self.startitem = 0
        self.maxoffset = 0
    
    def scrollup(self, btn):
        if self.startitem > 0:
            self.startitem -= 1;
            
    def scrolldown(self, btn):
        if self.startitem < self.maxoffset:
            self.startitem += 1;
        
    def events(self, event):
        if event.type == MOUSEBUTTONUP:
            inX = lambda x: x >= self.pos[0] and x <= self.pos[0]+self.size[0]
            inY = lambda y: y >= self.pos[1] and y <= self.pos[1]+self.size[1]
            
            nevent = mangle_event(event, self.pos)
            
            if inX(event.pos[0]) and inY(event.pos[1]):
                if self.arrowup.events(nevent) or self.arrowdown.events(nevent):
                    return True
                if event.pos[0] > self.size[0] - 13:
                    return True
                y = event.pos[1] - self.pos[1]
                self.selected = (y / 13)
                if self.selected >= len(self.items) or self.selected == self.maxrows:
                    self.selected = -1
                else:
                    self.selected += self.startitem
                    self.onSelected.dispatch(self)
                return True
        return False
                
    def update(self):
        i = 0
        for item in self.items:
            item.pos[1] = i * 13 + 1
            i += 1
        self.maxoffset = len(self.items) - self.maxrows
        self.selected = -1
        
    def add_list(self, items):
        """ Add a list with items
        
            @param items list with strings to add
        """
        for item in items:
            self.items.append(Label(item, (0,0), fontcolor=COLOR_WHITE))
        self.update()
            
    def add_item(self, item):
        """ Add a item to the list
        
            @param item string to add
        """
        self.items.append(Label(item, (0,0), fontcolor=COLOR_WHITE))
        self.update()
        
    def remove_item(self, n):
        """ Remove an item from the list
        
            @param n index of the item starting from 0
        """
        if n < len(self.items) and n >= 0:
            item = self.items[n]
            del item
            del self.items[n]
            self.update()
            return True
        return False
    
    def empty(self):
        """ Empty the item list """
        self.items = []
        self.maxoffset = 0
        self.startitem = 0
        self.selected = -1
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], 0)
        
        glColor4f(*self.forecolor)
        glRecti(0, 0, self.size[0], self.size[1])
        
        glColor4f(*self.backcolor)
        glRecti(1, 1, self.size[0]-1, self.size[1]-1)
        
        self.arrowup.draw()
        self.arrowdown.draw()
        
        glColor4f(*self.forecolor)
        Quad((self.size[0]-13, 0), (self.size[0],self.size[1]-1))
        
        clip = Clipper()
        clip.begin((1, 1, self.size[0]-14, self.size[1]-1))
        
        glTranslatef(2, -(self.startitem * 13), 0)
        i = self.startitem
        e = self.startitem+self.maxrows
        if e > len(self.items):
            e = len(self.items)
        for item in self.items[self.startitem:e]:
            #print "rendering item", i, self.selected
            if i == self.selected:
                glColor4f(0.5,0,0, 0.5)
                glRecti(0, item.pos[1], self.size[0]-3, item.pos[1]+13)
            item.draw()
            i += 1
            
        clip.end()
        glPopMatrix()
