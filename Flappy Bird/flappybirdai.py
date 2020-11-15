import pygame
import random
import os 
import neat

pygame.init()

with open('highscore.txt', 'r') as f:
    highscore = f.read()

score = 0
font = pygame.font.Font(None, 35)
bird_img = [pygame.image.load('bird1.png'), pygame.image.load('bird2.png'), pygame.image.load('bird3.png')]
bg_img = pygame.image.load('bg.png')
pipe_img = pygame.image.load('pipe.png')
base_img = pygame.image.load('base.png')
pipe_img_copy = pygame.image.load('pipe - Copy.png')

WIN_WIDTH = 400
WIN_HEIGHT = 600
win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption('FLAPPY BIRD')

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
        self.jump_list = []
        self.jumpp = False

    def jump(self):
        self.vel = -10.2
        self.time_count=0
        self.jumping = True

    def move(self, base):
        s = self.vel*self.time_count + 1.5*self.time_count**2
        if s >= 10:
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
        
        if self.jumping:
                self.jump_list.append(self.y)

        if 1 < len(self.jump_list) <= 3:
            for i in self.jump_list:
                if self.jump_list[0] > i:
                    self.jump_list = []
                    self.jumping = False

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
        self.pipe_top = pipe_img_copy
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
        
def redraw(pipes, birds, base):
    win.blit(bg_img,(0,0))
    for pipe in pipes: 
        pipe.draw()
    base.draw()
    for bird in birds:
        bird.draw()
    text = font.render(f'SCORE: {score}',True, (0,0,0))
    win.blit(text, (WIN_WIDTH-125,20))

def main(genomes,config):
    global score
    score = 0
    clock = pygame.time.Clock()
    nets = []
    ge = []
    birds = []
    pipes = [Pipe(WIN_WIDTH)]
    base = Base(WIN_HEIGHT - 40)

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        ge.append(g)
        birds.append(Bird(175, WIN_HEIGHT/2))
        g.fitness = 0

    while True and len(birds) > 0:
        clock.tick(100)

        for x, bird in enumerate(birds):
            for pipe in pipes:
                if pipe.collide(bird):
                    ge[x].fitness-=1
                    ge.pop(x)
                    nets.pop(x)
                    birds.pop(x)
                if bird.x > pipe.x + pipe_img.get_width():
                    ge[x].fitness+=10
                    if len(pipes) < 2:
                        pipes.append(Pipe(WIN_WIDTH))
                        score+=1
                if pipe.x + pipe_img.get_width() < 0:
                    pipes.pop(pipes.index(pipe)) 
            
        for x,bird in enumerate(birds):
            if bird.y+44 > base.y - 10:
                ge[x].fitness -= 1
                ge.pop(x)
                nets.pop(x)
                birds.pop(x)
    
        for pipe in pipes:
            pipe.move()
        base.move()

        pipe_i = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipe_img.get_width():
                pipe_i = 1 

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move(base)
        
            output = nets[birds.index(bird)].activate((bird.y , abs(bird.y - pipes[pipe_i].ybottom), abs(bird.y - pipes[pipe_i].ytop)))

            if output[0] > 0.5:
                if not bird.jumping:
                    bird.jump()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        redraw(pipes,birds,base)
        pygame.display.update()

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
  
    winner = p.run(main, 50)

if __name__=='__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)


