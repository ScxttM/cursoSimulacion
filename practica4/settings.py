X, Y = (720, 720)  # Resolution of display window

SAVE_VIDEO = False  # Setting to True requires ffmpeg
PATH_TO_FILE = "./video.mp4"
BIT_RATE = '6000k'
VIDEO_FPS = 60

NUMBER_OF_PARTICLES = 16  # Number of initial particles
PARTICLE_RADIUS = 8  # Pixels
PARTICLE_SPEED = 150  # Pixels per second
START_DIR = 4  # Integer offset of starting direction (mod NUMBER_OF_PARTICLES)

NUMBER_OF_SMALLGONS = 32  # Layers of recursions of polygons
DARK = (0, 0, 0)  # Dark colour of polygons (fades from dark to light)
LIGHT = (93, 173, 226)  # Light colour of polygons
LINE_WIDTH = 1

BACKGROUND_COLOR = (0, 0, 0)
GRID_SIZE = 4  # Optimises collision checks if equals sqrt(NUMBER_OF_PARTICLES)
SHOW_GRID = False
