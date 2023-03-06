import pygame,sys
from math import sqrt
from pygame.locals import *

BLACK=pygame.color.THECOLORS["black"]
WHITE=pygame.color.THECOLORS["white"]
RED=pygame.color.THECOLORS["red"]
GREEN=pygame.color.THECOLORS["green"]
BLUE=pygame.color.THECOLORS["blue"]
ORANGE=pygame.color.THECOLORS["orange"]
CLOCK=pygame.time.Clock()
SCREEN_WIDTH=640
SCREEN_HEIGHT=480

def collide(point,rect):
    collided=0
    if point[0]>=rect[0] and point[0]<rect[0]+rect[2] \
    and point[1]>=rect[1] and point[1]<rect[1]+rect[3]:
        collided=1
    return collided

   
def rect_collision(rect1,rect2):
    collision=0
    point1=(rect1[0],rect1[1])
    point2=(rect1[0]+rect1[2],rect1[1])
    point3=(rect1[0],rect1[1]+rect1[3])
    point4=(rect1[0]+rect1[2],rect1[1]+rect1[3])
    if collide(point1,rect2) or collide(point2,rect2) \
    or collide(point3,rect2) or collide(point4,rect2):
       collision=1
    return collision


def circle_collision(circle1,circle2):
    collision=0
    c1=circle1.center
    c2=circle2.center
    lenght=math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2)
    if circle1.radius+circle2.radius>lenght:
       collision=1
    return collision


def circle_collision2(circle1,circle2):
    #optimized circle collision detection
    #that doesn't rely on the too costly square root function        
    collision=0
    dx=circle1.center[0]-circle2.center[0]
    dy=circle1.center[1]-circle2.center[1]
    if (circle1.radius+circle2.radius)**2>dx**2+dy**2:
       collision=1
    return collision


def circle_collision3(circle1,circle2):
    #optimized circle collision detection
    #that doesn't rely on the too costly square root function    
    collision=0
    xdist=circle1.center[0]-circle2.center[0]
    ydist=circle1.center[1]-circle2.center[1]
    radius_sum=circle1.radius+circle2.radius
    if xdist<0:
       xdist*=-1
    if ydist<0:
       ydist*=-1       
    if radius_sum>xdist and radius_sum>ydist:
       collision=1
    return collision


def linear_interpolated_slope_walk(slope,player):
    """function to use for all types of slopes
         if you don't want air dash"""
    desired_y_pos=player.pos[1]
    increment=slope.increment
    if slope.slant>0:
       if player.pos[0]+player.width<=slope.end[0]+1:
          y_offset=((player.pos[0]+player.width)-slope.start[0])*increment
          top=slope.start[1]+y_offset
          if player.pos[1]+player.height>=top-(player.velocity[0]*increment) \
          and player.velocity[1]>=0:
              if top <=slope.start[1]:
                 desired_y_pos=top-player.height
              else:
                 desired_y_pos=slope.start[1]-player.height 
              player.velocity[1]=0
              player.on_ground=True
       elif player.pos[0]<=slope.pos[0]+slope.width \
       and player.pos[1]+player.height-player.velocity[1]<=slope.end[1] \
       or  player.pos[0]<=slope.pos[0]+slope.width and player.velocity[0]>=0:
           desired_y_pos=slope.end[1]-player.height
           player.velocity[1]=0
           player.on_ground=True
       else:
           player.pos[0]=slope.pos[0]+slope.width
    elif slope.slant<0:
       if player.pos[0]>=slope.start[0]:
          y_offset=(player.pos[0]-slope.start[0])*increment
          top=slope.start[1]+y_offset
          if player.pos[1]+player.height>=top-(player.velocity[0]*increment) \
          and player.velocity[1]>=0:
              if top <=slope.end[1]:
                 desired_y_pos=top-player.height
              else:
                 desired_y_pos=slope.end[1]-player.height 
              player.velocity[1]=0
              player.on_ground=True
       elif player.pos[0]<=slope.start[0] \
       and player.pos[1]+player.height-player.velocity[1]<=slope.start[1] \
       or player.pos[0]<=slope.start[0]and player.velocity[0]<=0:
          desired_y_pos=slope.start[1]-player.height
          player.velocity[1]=0
          player.on_ground=True
       else:
           player.pos[0]=slope.pos[0]-player.width             
    return desired_y_pos


def vector_slope_walk(slope,player):
    """function to use for all types of slopes
             if you want air  dash"""
    desired_y_pos=player.pos[1]
    increment=slope.increment
    if slope.slant>0:
       if player.pos[0]+player.width<=slope.end[0]+1:
          y_offset=((player.pos[0]+player.width)-slope.start[0])*increment
          top=slope.start[1]+y_offset
          if player.pos[1]+player.height>=top:
             desired_y_pos=top-player.height
             player.velocity[1]=0
             player.on_ground=True
             player.on_slope=True
             if player.right and player.velocity[0]<10:
                player.on_slope=False
             player.vector[0]=slope.vector[0]
             player.vector[1]=slope.vector[1]
       elif player.pos[0]<=slope.pos[0]+slope.width \
       and player.pos[1]+player.height-player.velocity[1]<=slope.end[1] \
       or  player.pos[0]<=slope.pos[0]+slope.width and player.velocity[0]>=0:
           if player.pos[1]+player.height>=slope.end[1]:
              desired_y_pos=slope.end[1]-player.height
              player.velocity[1]=0
              player.on_ground=True
              player.on_slope=True
              player.vector[0]=slope.vector[0]
              player.vector[1]=0 
              if player.left:
                 player.vector[1]=slope.vector[1]
       else:
          player.pos[0]=slope.pos[0]+slope.width
    elif slope.slant<0:
       if player.pos[0]>=slope.start[0]:
          y_offset=(player.pos[0]-slope.start[0])*increment
          top=slope.start[1]+y_offset
          if player.pos[1]+player.height>=top:
             desired_y_pos=top-player.height
             player.velocity[1]=0
             player.on_ground=True
             player.on_slope=True
             if player.left and player.velocity[0]>-10:
                player.on_slope=False           
             player.vector[0]=slope.vector[0]
             player.vector[1]=slope.vector[1]             
       elif player.pos[0]<=slope.start[0] \
       and player.pos[1]+player.height-player.velocity[1]<=slope.start[1] \
       or player.pos[0]<=slope.start[0]and player.velocity[0]<=0:
          if player.pos[1]+player.height>=slope.start[1]:
             desired_y_pos=slope.start[1]-player.height
             player.velocity[1]=0
             player.on_ground=True
             player.on_slope=True
             player.vector[0]=slope.vector[0]
             player.vector[1]=0 
             if player.right:
                player.vector[1]=slope.vector[1]
       else:
          player.pos[0]=slope.pos[0]-player.width
    return desired_y_pos


def similar_triangles_slope_walk(slope,player):
    """function to use for all types of slopes"""
    desired_y_pos=player.pos[1]
    if slope.slant>0:
       if player.pos[0]+player.width>=slope.start[0]:
          height=(slope.pos[1]+slope.height)-slope.end[1]
          width=slope.end[0]-slope.start[0]
          top=(slope.pos[1]+slope.height)-((player.pos[0]+player.width)-slope.start[0])*(height/width)
          if player.pos[1]+player.height>=top:
             desired_y_pos=top-player.height
             player.velocity[1]=0
             player.on_ground=True
    elif slope.slant<0:
       if player.pos[0]<=slope.end[0]:
          height=(slope.pos[1]+slope.height)-slope.start[1]
          width=slope.end[0]-slope.start[0]
          top=(slope.pos[1]+slope.height)-(slope.end[0]-player.pos[0])*(height/width)
          if player.pos[1]+player.height>=top:
             desired_y_pos=top-player.height
             player.velocity[1]=0
             player.on_ground=True
    return desired_y_pos


def slope_respond(slope,player):
    """function to use only  for 45 and -45 slopes"""
    top = None
    desired_y_pos=player.pos[1]
    if slope.slant < 0:
        if player.pos[0]>=slope.pos[0]:
            x = player.pos[0] - slope.pos[0]
            top = slope.pos[1]+x-1
    if slope.slant > 0:
        if player.pos[0]+player.width<=(slope.pos[0]+slope.width):
            x = (slope.pos[0]+slope.width) - ( player.pos[0]+player.width)
            top = slope.pos[1]+x-1
    if top:
        if player.pos[1]+player.height > top:
           desired_y_pos=top-player.height
    return desired_y_pos


   
class Tile:

  def __init__(self,pos):
      self.pos=pos
      self.image=pygame.Surface((200,50)).convert()
      self.image.fill(GREEN)
      self.width=self.image.get_width()
      self.height=self.image.get_height()
      self.rect=[self.pos[0],self.pos[1],self.width,self.height]
      pygame.draw.rect(self.image,ORANGE,[0,0,self.width, self.height],4)
      
  def draw(self,surface,camera):
      #blit only if we are on screen
      if self.pos[0]+self.width>=camera.screen.left and self.pos[0]<=camera.screen.right  \
      and self.pos[1]+self.height>=camera.screen.top and self.pos[1]<=camera.screen.bottom:
          surface.blit(self.image,(self.pos[0]-camera.screen.x,self.pos[1]-camera.screen.y))


class Slope(Tile):
   slopes=[ ( ((0,200),(200,0),(200,200)),1), ( ((0,200),(200,0),(200,200)),-1),
            ( ((0,200),(200,50),(200,200)),1),( ((0,200),(200,50),(200,200)),-1),
            ( ((50,200),(200,0),(200,200)),1),( ((50,200),(200,0),(200,200)),-1),
            ( ((0,200),(150,0),(200,0),(200,200)),1),( ((0,200),(150,0),(200,0),(200,200)),-1) ]
   def __init__(self,pos,index=0,slant=1):
      self.pos=pos
      self.slant=slant  #1 for up slope right, -1 for down slope right
      self.image=pygame.Surface((200,200)).convert()
      self.image.fill(WHITE)
      self.alpha_color=self.image.get_at((0,0))
      self.image.set_colorkey(self.alpha_color)
      self.color=GREEN
      self.width=self.image.get_width()
      self.height=self.image.get_height()
      #self.points=[[0,self.height],[self.width,0],[self.width,self.height]]
      self.points=Slope.slopes[index][0]
      pygame.draw.polygon(self.image,self.color,self.points,0)
      self.rect=[self.pos[0],self.pos[1],self.width,self.height]
      if self.slant<0:
         self.image=pygame.transform.flip(self.image,1,0)
      self.get_ends()
      self.get_normalized_vector()
      self.increment=(self.end[1]-self.start[1])/(self.end[0]-self.start[0])

   def get_ends(self):
       start=0
       end=0
       
       if self.slant>0:      
          for y in range(self.height):
              if self.image.get_at((0,y))!=self.alpha_color:
                 start=[0,y]
                 break
          if not start:     
             for x in range(self.width):
                 if self.image.get_at((x,self.height-1))!=self.alpha_color:
                    start=[x,self.height-1]
                    break
          for x in range(self.width):
              if self.image.get_at((x,0))!=self.alpha_color:
                 end=[x,0]
                 break               
          if not end:     
             for y in range(self.height):
                 if self.image.get_at((self.width-1,y))!=self.alpha_color:
                    end=[self.width-1,y]
                    break
            
       elif self.slant<0:
          for x in range(self.width-1,-1,-1):
              if self.image.get_at((x,0))!=self.alpha_color:
                 start=[x,0]
                 break
          if not start:
             for y in range(self.height):
                 if self.image.get_at((0,y))!=self.alpha_color:
                    start=[0,y]
                    break
          for y in range(self.height):
              if self.image.get_at((self.width-1,y))!=self.alpha_color:
                 end=[self.width-1,y]
                 break
          if not end:
             for x in range(self.width-1,-1,-1):
                 if self.image.get_at((x,self.height-1))!=self.alpha_color:
                    end=[x,self.height-1]
                    break
                  
       if start and end:
          self.start=start
          self.end=end
          self._start=[start[0],start[1]]
          self._end=[end[0],end[1]]
          self.update()

   def update(self):
       self.start[0]=self.pos[0]+self._start[0]
       self.start[1]=self.pos[1]+self._start[1]
       self.end[0]=self.pos[0]+self._end[0]
       self.end[1]=self.pos[1]+self._end[1]
       self.rect[0]=self.pos[0]
       self.rect[1]=self.pos[1]

   def get_normalized_vector(self):
       vector=[self.end[0]-self.start[0],self.end[1]-self.start[1]]
       magnitude=sqrt(vector[0]**2+vector[1]**2)
       vector[0]=vector[0]/magnitude
       vector[1]=vector[1]/magnitude
       self.vector=vector
       
class Platform(Tile):

  def __init__(self,pos):
      self.pos=pos
      self.image=pygame.Surface((200,50)).convert()
      self.image.fill(GREEN)
      self.width=self.image.get_width()
      self.height=self.image.get_height()
      self.rect=[self.pos[0],self.pos[1],self.width,self.height]
        
class Camera:
    
  def __init__(self,target,level_end=2000):  
      self.target=target
      self.level_end=level_end
      self.screen=pygame.Rect((0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
    
  def update(self):
      if self.target.pos[0]>self.screen.centerx:
         if self.screen.right<self.level_end[0]:
            dx=self.target.pos[0]-self.screen.centerx
            self.screen.move_ip(dx,0)
            if self.screen.right>self.level_end[0]:
               self.screen.right=self.level_end[0]
      elif self.target.pos[0]<self.screen.centerx:
         if self.screen.left>0:
            dx=self.target.pos[0]-self.screen.centerx
            self.screen.move_ip(dx,0)
            if self.screen.left<0:
               self.screen.left=0
      if self.target.pos[1]>self.screen.centery:
         if self.screen.bottom<self.level_end[1]:
            dy=self.target.pos[1]-self.screen.centery
            self.screen.move_ip(0,dy)
            if self.screen.bottom>self.level_end[1]:
               self.screen.bottom=self.level_end[1]
      elif self.target.pos[1]<self.screen.centery:
         if self.screen.top>0:
            dy=self.target.pos[1]-self.screen.centery
            self.screen.move_ip(0,dy)
            if self.screen.top<0:
               self.screen.top=0
            
class Player:
   
   def __init__(self,pos):
      self.pos=pos
      self.image=pygame.Surface((50,50)).convert()
      self.width=self.image.get_width()
      self.height=self.image.get_height()
      self.image.fill(RED)
      self.move_speed=10
      self.vector=[0,0]
      self.velocity=[0,0]
      self.temp_xvel=0
      self.gravity=0.7
      self.friction=0.3
      self.fall_through=0
      self.on_ground=False
      self.on_slope=False
      self.left=self.right=self.down=self.running=False
      self.rect=[self.pos[0],self.pos[1],self.width,self.height]
      
   def controls(self):
       for event in pygame.event.get():    #wait for events
           if event.type == QUIT:
               pygame.quit()
               sys.exit()
               
           if event.type == KEYDOWN:
              if event.key == K_RIGHT:
                 self.right=True
              elif event.key == K_LEFT:
                 self.left=True
              if event.key == K_DOWN:
                 self.down=True
              if event.key == K_SPACE:
                 self.running=True                               
              if event.key == K_UP:
                 if self.on_ground:
                    if self.down:
                       self.fall_through=3
                       self.velocity[1]=5
                    else:
                       self.velocity[1] -= 12
                       self.gravity=0.3
                    self.on_ground=False
           elif event.type == KEYUP:
                if event.key == K_UP:
                   self.gravity=0.7
                if event.key == K_RIGHT:
                   self.right=False
                elif event.key == K_LEFT:
                   self.left=False
                if event.key == K_DOWN:
                   self.down=False
                if event.key == K_SPACE:
                   self.running=False                               
   

   def move_rect(self):
       self.rect[0]=self.pos[0]
       self.rect[1]=self.pos[1]

   def collision_handler(self,level):
       self.move_rect()
       for tile in level.tiles:
           if rect_collision(self.rect,tile.rect):
                 if self.velocity[1]>0:
                    if self.pos[1]+self.height-self.velocity[1]<=tile.pos[1]:
                       self.pos[1]=tile.pos[1]-self.height
                       self.velocity[1]=0
                       self.on_ground=True
                       break
                 elif self.velocity[1]<0:
                   if self.pos[1]-self.velocity[1]>=tile.pos[1]+tile.height:  
                      self.pos[1]=tile.pos[1]+tile.height
                      self.velocity[1]=0
                 if self.velocity[0]>0:
                    if self.pos[0]+self.width-self.velocity[0]<=tile.pos[0]:
                       self.pos[0]=tile.pos[0]-self.width
                       self.velocity[0]=0
                 elif self.velocity[0]<0:
                    if self.pos[0]-self.velocity[0]>=tile.pos[0]+tile.width:   
                       self.pos[0]=tile.pos[0]+tile.width
                       self.velocity[0]=0
                 self.move_rect()
               
       for slope in level.slopes:
           if rect_collision(self.rect,slope.rect):
              #desired_y_pos=linear_interpolated_slope_walk(slope,self)
              desired_y_pos=vector_slope_walk(slope,self)  
              self.pos[1]=desired_y_pos
              self.move_rect()
                          
       if not self.fall_through: 
          for platform in level.platforms:
              if rect_collision(self.rect,platform.rect):
                 if self.velocity[1]>=0:
                    if self.pos[1]+self.height-self.velocity[1]<=platform.pos[1]:
                       self.pos[1]=platform.pos[1]-self.height
                       self.velocity[1]=0
                       self.on_ground=True
                       break

   def walk_control(self,level):
       
       if self.right:
          if self.velocity[0]==0:
             self.velocity[0]+=5
          elif self.velocity[0]<0:
             self.velocity[0]+=1.3
             if self.velocity[0]>0:
                 self.velocity[0]=0
          else:
             self.velocity[0]+=0.2
             if self.velocity[0]>20:
                self.velocity[0]=20
          if self.running:
             self.velocity[0]+=10
             
       elif self.left:
          if self.velocity[0]==0:
             self.velocity[0]-=5
          elif self.velocity[0]>0:
             self.velocity[0]-=1.3
             if self.velocity[0]<0:
                 self.velocity[0]=0                               
          else:
             self.velocity[0]-=0.2
             if self.velocity[0]<-20:
                self.velocity[0]=-20
          if self.running:
             self.velocity[0]-=10
                             
       if self.velocity[0]>0 and not self.right:
          self.velocity[0]-=self.friction
          if self.velocity[0]<0:
             self.velocity[0]=0
             
       elif self.velocity[0]<0 and not self.left:
          self.velocity[0]+=self.friction
          if self.velocity[0]>0:
             self.velocity[0]=0
             
       if self.on_slope:
          self.temp_xvel=(self.velocity[0]*self.vector[0])
          self.pos[0]+=self.temp_xvel
       else:   
          self.pos[0]+=self.velocity[0]
       
       if self.pos[0]<0:
          self.pos[0]=0
       elif self.pos[0]+self.width>level.end[0]:
          self.pos[0]=level.end[0]-self.width

   
   def jump_control(self,floor_pos=1400):
       #self.on_ground=False
       self.velocity[1]+=self.gravity
       if self.velocity[1]>100:
          self.velocity[1]=100
       if self.on_slope :
          if self.on_ground:
             self.velocity[1]=(self.velocity[0]*self.vector[1])
          self.on_slope=False
       self.on_ground=False
       self.pos[1]+=self.velocity[1]
       if self.pos[1]+self.height>floor_pos:
          self.pos[1]=floor_pos-self.height
          self.velocity[1]=0
          self.on_ground=True
       if self.fall_through>0:
          self.fall_through-=1

   def update(self,level):
       self.controls()
       self.walk_control(level)
       self.jump_control(floor_pos=level.end[1])
       self.collision_handler(level)
       
   def draw(self,surface,camera):
       surface.blit(self.image,(self.pos[0]-camera.screen.x,self.pos[1]-camera.screen.y))


class Level:
                       
   def __init__(self):
       self.objects=[]
       self.slopes=[]
       self.platforms=[]
       self.tiles=[]
       self.end=None
       self.start_pos=None
       
   def make_level(self,level):
       x=0
       y=200
       self.end=[len(level[0])*200,len(level)*200+200]
       for string in level:
           for char in string:
               if char!=" ":
                  if char=="a":
                     self.start_pos=[x,y]
                  elif char=="p":
                     p=Platform((x,y))
                     self.objects.append(p)
                     self.platforms.append(p)
                  elif char=="t":
                     t=Tile((x,y))
                     self.objects.append(t)
                     self.tiles.append(t)
                  else:
                     char=int(char)
                     s=Slope((x,y),index=char,slant=Slope.slopes[char][1])
                     self.slopes.append(s)
                     self.objects.append(s)
               x+=200
           x=0
           y+=200
       
def main():

   pygame.init()

   #Open Pygame window
   screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),) #add  RESIZABLE or FULLSCREEN
   #Title
   pygame.display.set_caption("slope walk")
   _level=["  6 p 7 p  67   ",
           " ptppptppppttpp ",
           "  4 t  0  t 45  ",
           " ptppppptpppttp ",
           "  2  3  1   2   ",
           " ptpptpptppptpp ",
           " a 4 6  01 t 22 ",
           "tttttttttttttttt"]
   level=Level()
   level.make_level(_level)
   player=Player(level.start_pos)
   camera=Camera(player,level_end=level.end)
   
   while True:
       
       #loop speed limitation
       #30 frames per second is enought
       CLOCK.tick(30)

              
       player.update(level)
       camera.update()
           
              
       screen.fill(BLUE)
       for obj in level.objects:
           obj.draw(screen,camera)
       player.draw(screen,camera)
       pygame.display.flip()
       
if __name__=='__main__':
    main()
