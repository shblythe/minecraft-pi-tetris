"""
Tetris with LEDs!

A tetris clone which uses the keyboard for control, the Ciseco PiLite for
display, and the pygame library for collision detection etc.

Controls:
     Left Arrow - Move left
    Right Arrow - Move right
       Up Arrow - Rotate
     Down Arrow - Skip down

Stephen Blythe 2014

--------------------------------------------------------------------------
TODO
- scoring?
- make it get progressively harder?
"""

import sys,pygame,random
import mcpi.minecraft as minecraft

mc=minecraft.Minecraft.create()

# Some colour constants
BLACK=(0,0,0,255)
WHITE=(255,255,255,255)
CLEAR=(0,0,0,0)

# Minecraft blocks
AIR=0
ROCK=1

# Minecraft render offset
MC_X=40
MC_Y=1
MC_Z=10

# Play area size
WIDTH=9
HEIGHT=14
SIZE=WIDTH,HEIGHT

# Number of frames per second
FRAME_RATE=5

# Number of frames between drop, so it'll take a second for each shape to drop
# one line.
DROP_RATE=3

# Blit a pygame surface onto the Minecraft world
# Anything but BLACK gets rendered as stone, everything else as air
def mc_blit(surface):
    w,h=surface.get_size()
    for y in range(14):
	for x in range(9):
	    if x>=w or surface.get_at((x,y))==BLACK:
		mc.setBlock(MC_X,MC_Y+HEIGHT-y,MC_Z+x,AIR)
	    else:
		mc.setBlock(MC_X,MC_Y+HEIGHT-y,MC_Z+x,ROCK)


# Initialise pygame
pygame.init()
clock=pygame.time.Clock()
# Create the window - we don't display on this, but we need it to capture
# keyboard events
pygame.display.set_mode((1,1))


# Create a surface for each of the possible Tetris shapes and put it in an array
shapes=[]
shape=pygame.Surface((3,2),pygame.SRCALPHA)
shape.fill(CLEAR)
shape.set_at((0,0),WHITE)
shape.set_at((1,0),WHITE)
shape.set_at((1,1),WHITE)
shape.set_at((2,1),WHITE)
shapes.append(shape)
shape=pygame.Surface((3,2),pygame.SRCALPHA)
shape.fill(CLEAR)
shape.set_at((0,1),WHITE)
shape.set_at((1,0),WHITE)
shape.set_at((1,1),WHITE)
shape.set_at((2,0),WHITE)
shapes.append(shape)
shape=pygame.Surface((3,2),pygame.SRCALPHA)
shape.fill(CLEAR)
shape.set_at((0,0),WHITE)
shape.set_at((1,0),WHITE)
shape.set_at((2,0),WHITE)
shape.set_at((1,1),WHITE)
shapes.append(shape)
shape=pygame.Surface((3,2),pygame.SRCALPHA)
shape.fill(CLEAR)
shape.set_at((0,0),WHITE)
shape.set_at((1,0),WHITE)
shape.set_at((2,0),WHITE)
shape.set_at((0,1),WHITE)
shapes.append(shape)
shape=pygame.Surface((3,2),pygame.SRCALPHA)
shape.fill(CLEAR)
shape.set_at((0,0),WHITE)
shape.set_at((1,0),WHITE)
shape.set_at((2,0),WHITE)
shape.set_at((2,1),WHITE)
shapes.append(shape)
shape=pygame.Surface((2,2),pygame.SRCALPHA)
shape.fill(WHITE)
shapes.append(shape)
shape=pygame.Surface((4,1),pygame.SRCALPHA)
shape.fill(WHITE)
shapes.append(shape)

# Randomly select a shape from the array, and place it at the top of the screen
shape=shapes[random.randrange(0,len(shapes))]
shape_pos=[2,0]

# Create the playing surface, and the background, where the blocks which have
# landed end up.
surface=pygame.Surface(SIZE,pygame.SRCALPHA)
background=pygame.Surface(SIZE,pygame.SRCALPHA)
background.fill(CLEAR)

render=True
drop_count=DROP_RATE
try:
    while True:
	# background mask for collision checking
	m_bg=pygame.mask.from_surface(background)
	# check for full lines and remove them
	# we remove them by setting the clipping area to be a rectangle from the
	# top to the line to be removed, and scrolling down.  Nifty! :)
	for row in range(HEIGHT):
	    bgcheck=pygame.Surface(SIZE,pygame.SRCALPHA)
	    bgcheck.fill(CLEAR)
	    pygame.draw.line(bgcheck,WHITE,(0,row),(WIDTH-1,row))
	    m_bgc=pygame.mask.from_surface(bgcheck)
	    if m_bg.overlap_area(m_bgc,(0,0))==WIDTH:
		background.set_clip(pygame.Rect((0,0),(WIDTH,row+1)))
		background.scroll(0,1)
		background.set_clip(None)
		m_bg=pygame.mask.from_surface(background)
	    
	# check for collision with background
	bgcheck=pygame.Surface(SIZE,pygame.SRCALPHA)
	bgcheck.fill(CLEAR)
	bgcheck.blit(shape,shape_pos,special_flags=pygame.BLEND_RGBA_ADD)
	m_bgc=pygame.mask.from_surface(bgcheck)
	# store the result of a possible collision in each direction, so we're
	# prediction a collision in each of these directions
	collide_down=m_bg.overlap(m_bgc,(0,1))
	collide_left=m_bg.overlap(m_bgc,(-1,0))
	collide_right=m_bg.overlap(m_bgc,(1,0))

	# only allow one move event per frame, to prevent the player from
	# skipping round the collision detection
	moved=False
	for event in pygame.event.get():
	    if event.type==pygame.QUIT:
		pygame.quit()
		sys.exit()
	    if event.type==pygame.KEYDOWN:
		# only process move events if we're rendering, i.e. not on a
		# skip down to the bottom, and if we haven't already had one
		if render and not moved:
		    if event.key==pygame.K_LEFT and not collide_left:
			shape_pos[0]-=1
			moved=True
		    if event.key==pygame.K_RIGHT and not collide_right:
			shape_pos[0]+=1
			moved=True
		    if event.key==pygame.K_UP:
			shape=pygame.transform.rotate(shape,90)
			moved=True
		    if event.key==pygame.K_DOWN:
			# Down arrow skips the shape down to the bottom, we do
			# this by processing the frames normally, but skipping
			# the render and the delay
			render=False
	# Clear the surface, then blit the background on
	surface.fill(BLACK)
	surface.blit(background,(0,0))
	# Make sure the shape hasn't left the side of the surface
	if shape_pos[0]<0:
	    shape_pos[0]=0
	if shape_pos[0]>WIDTH-shape.get_width():
	    shape_pos[0]=WIDTH-shape.get_width()
	# Then blit the shape on
	r=surface.blit(shape,shape_pos,special_flags=pygame.BLEND_RGBA_ADD)

	# Check for a downward collision, or reaching the bottom of the screen
	if collide_down or surface.get_rect().bottom==r.bottom:
	    # We've collided downwards, if we're still at the top, that's
	    # game over!
	    if shape_pos[1]==0:
		print "Game over!"
		pygame.quit()
		sys.exit()
	    # If it isn't game over, blit the current shape on to the background
	    # then create a new shape
	    background.blit(shape,shape_pos)
	    shape_pos=[2,0]
	    shape=shapes[random.randrange(0,len(shapes))]
	    render=True
	else:
	    # Only drop the shape down a line when the drop count reaches 0, so
	    # we can control how many frames we render between each drop
	    drop_count-=1
	    if drop_count==0:
		shape_pos[1]+=1
		drop_count=DROP_RATE
	# If we're not on a skip down, blit onto the world, and wait for the
	# next frame
	if render:
	    mc_blit(surface)
	    clock.tick(FRAME_RATE)
except KeyboardInterrupt:
    # Tidy up if the player hits ctrl-C - those LEDs are blinding!
    pygame.quit()
    sys.exit()

