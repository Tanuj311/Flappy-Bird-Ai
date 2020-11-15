import pygame, random
pygame.init()

with open('highscore.txt', 'r') as f:
    highscore = f.read()

start = True

def main():
    global start, highscore
    clock = pygame.time.Clock()
    score = 0
    font = pygame.font.Font(None, 35)
    bird_img = [pygame.image.load('bird1.png'), pygame.image.load('bird2.png'), pygame.image.load('bird3.png')]
    bg_img = pygame.image.load('bg.png')
    pipe_img = pygame.image.load('pipe.png')
    base_img = pygame.image.load('base.png')

    collision = False
    WIN_WIDTH = 400
    WIN_HEIGHT = 600
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    pygame.display.set_caption('FLAPPY BIRD')

    def startscreen():
        startfont = 'Flappy Bird'
        font = pygame.font.Font('FlappybirdyRegular-KaBW.ttf', 110)
        text = font.render(startfont, True, (0,0,0))
        keypress = 'PRESS ENTER TO PLAY'
        font1 = pygame.font.Font('FlappybirdyRegular-KaBW.ttf', 60)
        text1 = font1.render(keypress,True, (0,0,0))
        win.blit(text, (50,int(WIN_HEIGHT/2-100)))
        win.blit(text1, (28,int(WIN_HEIGHT/2+ 100)))
        control = 'CONTROLS - PRESS SPACE TO JUMP'
        font2 = pygame.font.Font(None, 30)
        text2 = font2.render(control,True, (0,0,0))
        win.blit(text2, (20,int(WIN_HEIGHT/2+50)))

    class Bird:
        def __init__(self,x,y):
            self.x = x
            self.y = int(y)
            self.img_count = 0
            self.tilt = 0
            self.rotvel = 20
            self.vel = 0
            self.time_count = 0
            self.maxrotation = 25
            self.imageindex= False
            self.passed = False
            self.img = bird_img[0]
            self.jumping = False

        def jump(self):
            self.vel = -10.2
            self.time_count=0
            self.jumping = True

        def move(self):
            s = self.vel*self.time_count + 1.5*self.time_count**2
            if s > 10:
                s = 10
            if self.y + 34 < base.y:
                self.y += int(s)
            if s <= 9:
                if self.tilt < self.maxrotation:
                    self.tilt = self.maxrotation
                    self.imageindex = False
            else:
                if self.tilt > -40:
                    self.tilt -= self.rotvel
                    self.imageindex= True
            self.time_count+=1

        def draw(self):
            if self.img_count > 2:
                self.img_count = 0
            else:
                self.img = bird_img[self.img_count]        
            if self.imageindex:
                self.img = bird_img[0]
            rotated_img = pygame.transform.rotate(self.img, self.tilt)
            new = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x,self.y)).center)
            win.blit(rotated_img,new.topleft)
            self.img_count+=1
        
        def get_mask(self):
            return pygame.mask.from_surface(self.img)

    class Pipe:
        def __init__(self,x):
            self.x = x
            self.gap = 180
            self.top = 0 
            self.bottom = 0
            self.pipe_top = pygame.transform.flip(pipe_img,False,True)
            self.pipe_bottom = pipe_img
            self.vel = 5 
            self.ytop = random.randrange(50,330)
            self.ybottom = self.ytop + self.gap
            self.y = self.ytop - pipe_img.get_height()

        def move(self):
            self.x -= self.vel

        def draw(self):
            win.blit(self.pipe_top, (self.x, self.y))
            win.blit(self.pipe_bottom, (self.x, self.ybottom))

        def collide(self,bird):
            bird_mask = bird.get_mask()
            topmask = pygame.mask.from_surface(self.pipe_top)
            bottommask = pygame.mask.from_surface(self.pipe_bottom)

            t_offset = (self.x - bird.x, self.y - bird.y)
            b_offset = (self.x - bird.x, self.ybottom - bird.y)

            t_point = bird_mask.overlap(topmask, t_offset)
            b_point = bird_mask.overlap(bottommask, b_offset)

            if b_point or t_point:
                return True

            return False

    class Base:
        def __init__(self, y):
            self.x1 = 0
            self.x2 = self.x1 + base_img.get_width()
            self.y = y
            self.vel = 5

        def move(self):
            self.x1 -= self.vel
            self.x2 -= self.vel
            if self.x1 + base_img.get_width() < 0:
                self.x1 = self.x2 + base_img.get_width()
            if self.x2 + base_img.get_width() < 0:
                self.x2 = self.x1 + base_img.get_width()

        def draw(self):
            win.blit(base_img, (self.x1, self.y))
            win.blit(base_img, (self.x2, self.y))
            
    def gameover():
        overfont = 'GAME OVER'
        font = pygame.font.Font('FlappybirdyRegular-KaBW.ttf', 120)
        text = font.render(overfont, True, (0,0,0))
        win.blit(text, (40, int(WIN_WIDTH/2)))
        overpress = 'PRESS ENTER TO PLAY'
        font1 = pygame.font.Font('FlappybirdyRegular-KaBW.ttf', 60)
        text1 = font1.render(overpress,True, (0,0,0))
        win.blit(text1, (40, int(WIN_WIDTH/2+100)))
        key = pygame.key.get_pressed()
        if key[pygame.K_RETURN]:
            main()

    def redraw():
        win.blit(bg_img,(0,0))
        for pipe in pipes: 
            pipe.draw()
        base.draw()
        bird.draw()
        text = font.render(f'SCORE: {score}',True, (0,0,0))
        win.blit(text, (WIN_WIDTH-125,20))
        displayhighscore()

    def displayhighscore():
        hscore = f'HIGHSCORE: {highscore}'
        font = pygame.font.Font(None,35)
        text = font.render(hscore,True,(0,0,0))
        win.blit(text, (20,20))

    bird = Bird(175, WIN_HEIGHT/2)
    base = Base(WIN_HEIGHT - 40)
    pipes = [Pipe(WIN_WIDTH)]

    while True:
        clock.tick(30)
        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            quit()
        if start: 
            redraw()
            base.move()
            startscreen()
            key = pygame.key.get_pressed()
            if key[pygame.K_RETURN]:
                start = False
        else:
            if collision == False: 
                bird.passed = False
                key = pygame.key.get_pressed()
                bird.move()
                base.move()
                redraw()
                for pipe in pipes:
                    if pipe.collide(bird):
                        collision = True
                    pipe.move()   
                if bird.x > pipe.x:
                    bird.passed = True
                    score+=1
                    if score > int(highscore):
                        highscore = score
                if bird.passed:
                    pipes.append(Pipe(WIN_WIDTH))
                if bird.y + 34 >= base.y:
                    collision = True
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        bird.jump()
            elif collision:
                with open('highscore.txt','w') as f:
                    f.write(str(highscore))
                bird.move()
                redraw()
                gameover()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not bird.jumping:
                    bird.jump()
            if event.type == pygame.QUIT:
                quit()
        pygame.display.update()

main()
