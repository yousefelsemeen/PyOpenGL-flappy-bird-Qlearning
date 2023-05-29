from pathlib import Path
from pygame import mixer, image
from classes import *


class FlappyBirdGame:
    def __init__(self):
        self.cur_path = str(Path(__file__).parent.resolve())
        self.PERIOD = 8
        # ######## to control the game ###############
        self.GAME_STATES = ["welcome", "main", "over"]
        self.STATE_SEQUENCE = cycle([1, 2, 0])
        self.STATE_INDEX = 0
        ################################################
        self.DISTANCE = SCREENWIDTH / 2  # distance between pipes
        self.SCORE = 0
        self.BP_SPEED = -3
        # ######## bird's control ########################
        self.ANGULAR_SPEED = 3
        # control bird jump.
        self.JUMP_VELOCITY = 5
        self.GRAVITY = -0.22
        ###################################################
        self.pipes = []  # contains all displayed pipes on the screen
        self.bird = None
        self.base = None
        self.window = None
        self.is_window_open = True
        ###########################################
        self.TEXTURES = {}  # at the start of game, all textures will be created once time and saved in it.
        self.SOUNDS = {}
        self.PLAYERS_LIST = (
            self.cur_path + '/assets/sprites/up.png',
            self.cur_path + '/assets/sprites/mid.png',
            self.cur_path + '/assets/sprites/down.png')

        self.run()

    def run(self):
        glutInit()
        glutInitWindowPosition(10, 10)
        glutInitWindowSize(SCREENWIDTH, SCREENHEIGHT)
        glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
        self.window = glutCreateWindow(b"Flappy Bird")

        glutDisplayFunc(self.display)
        glutTimerFunc(self.PERIOD, self.timer, 1)
        glutKeyboardFunc(self.keyboard)
        glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF)

        self.init()
        glutMainLoop()

    def init(self):
        glClearColor(1, 1, 1, 0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.init_texture()
        self.init_sounds()
        self.init_objects()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREENWIDTH, 0, SCREENHEIGHT, -3, 3)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def init_sounds(self):
        SOUNDEXT = ".ogg"
        mixer.init()

        self.SOUNDS["die"] = mixer.Sound(self.cur_path + "/assets/audio/die" + SOUNDEXT)
        self.SOUNDS["jump"] = mixer.Sound(self.cur_path + "/assets/audio/jump" + SOUNDEXT)
        self.SOUNDS["point"] = mixer.Sound(self.cur_path + "/assets/audio/point" + SOUNDEXT)

    def init_texture(self):
        # Initialize textures
        # ################### Pipe Textures ###########################################################
        img_pipe_load = image.load(self.cur_path + '/assets/sprites/pipe-green.png')
        width = img_pipe_load.get_width()
        height = img_pipe_load.get_height()
        img_pipe = [
            image.tostring(img_pipe_load, "RGBA", True),  # lower image
            image.tostring(img_pipe_load, "RGBA", False)]  # upper image "image is reflected".

        # creating 2 textures for pipes
        tex = glGenTextures(2)
        # adjust texture and uploading its image
        for i in [0, 1]:
            glBindTexture(GL_TEXTURE_2D, tex[i])
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_pipe[i])

        self.TEXTURES["pipe"] = tex
        # ################### Bird Textures ############################################################
        img_bird_load = [image.load(Address) for Address in self.PLAYERS_LIST]
        width = [img.get_width() for img in img_bird_load]
        height = [img.get_height() for img in img_bird_load]
        img_bird = [image.tostring(img, "RGBA", True) for img in img_bird_load]

        # creating 3 textures for bird
        tex = glGenTextures(3)
        # adjust texture and uploading its image
        for i in [0, 1, 2]:
            glBindTexture(GL_TEXTURE_2D, tex[i])
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width[i], height[i], GL_RGBA, GL_UNSIGNED_BYTE, img_bird[i])

        self.TEXTURES["bird"] = tex
        # ################### Background Texture ############################################################
        img_backG_load = image.load(self.cur_path + '/assets/sprites/background-day.png')
        width = img_backG_load.get_width()
        height = img_backG_load.get_height()
        img_backG = image.tostring(img_backG_load, "RGBA", True)

        # creating 1 texture for BackG
        tex = glGenTextures(1)
        # adjust texture and uploading its image
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_backG)

        self.TEXTURES["BackG"] = tex
        # ################### numbers Textures ############################################################
        img_num_load = [image.load(self.cur_path + f'/assets/sprites/{i}.png') for i in range(10)]
        width = [img.get_width() for img in img_num_load]
        height = [img.get_height() for img in img_num_load]
        img_num = [image.tostring(img, "RGBA", True) for img in img_num_load]

        # creating 10 textures for numbers
        tex = glGenTextures(10)
        # adjust texture and uploading its image
        for i in range(10):
            glBindTexture(GL_TEXTURE_2D, tex[i])
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width[i], height[i], GL_RGBA, GL_UNSIGNED_BYTE, img_num[i])

        self.TEXTURES["numbers"] = {f'{i}': tex[i] for i in range(10)}
        # ################### base Texture ############################################################
        img_base_load = image.load(self.cur_path + '/assets/sprites/base.png')
        width = img_base_load.get_width()
        height = img_base_load.get_height()
        img_base = image.tostring(img_base_load, "RGBA", True)

        # creating 1 texture
        tex = glGenTextures(1)
        # adjust texture and uploading its image
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_base)

        self.TEXTURES["base"] = tex
        # ################### message Texture ############################################################
        img_msg_load = image.load(self.cur_path + '/assets/sprites/message.png')
        width = img_msg_load.get_width()
        height = img_msg_load.get_height()
        img_msg = image.tostring(img_msg_load, "RGBA", True)

        # creating 1 texture
        tex = glGenTextures(1)
        # adjust texture and uploading its image
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_msg)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_msg)

        self.TEXTURES["msg"] = tex
        # ################### game over Texture ############################################################
        img_gameO_load = image.load(self.cur_path + '/assets/sprites/gameover.png')
        width = img_gameO_load.get_width()
        height = img_gameO_load.get_height()
        img_gameO = image.tostring(img_gameO_load, "RGBA", True)

        # creating 1 texture
        tex = glGenTextures(1)
        # adjust texture and uploading its image
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_gameO)

        self.TEXTURES["game over"] = tex
        # ################### start Texture ############################################################
        img_msg_load = image.load(self.cur_path + '/assets/sprites/start.png')
        width = img_msg_load.get_width()
        height = img_msg_load.get_height()
        img_msg = image.tostring(img_msg_load, "RGBA", True)
        # creating 1 texture
        tex = glGenTextures(1)
        # adjust texture and uploading its image
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_msg)

        self.TEXTURES["start"] = tex
        # ################### restart Texture ############################################################
        img_msg_load = image.load(self.cur_path + '/assets/sprites/res.png')
        width = img_msg_load.get_width()
        height = img_msg_load.get_height()
        img_msg = image.tostring(img_msg_load, "RGBA", True)
        # creating 1 texture
        tex = glGenTextures(1)
        # adjust texture and uploading its image
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img_msg)

        self.TEXTURES["restart"] = tex

    def init_objects(self):
        self.pipes.append(Pipe(self.TEXTURES["pipe"]))
        self.bird = Bird(self.TEXTURES["bird"], self.GRAVITY, self.ANGULAR_SPEED)
        self.base = Base(self.TEXTURES["base"], 0.1)

# control the game loop ###########################################################
    def timer(self, t=1):
        if self.is_window_open:
            self.update_frame()
            self.display()
            glutTimerFunc(self.PERIOD, self.timer, t)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.set_background()
        self.base.draw()

        if self.GAME_STATES[self.STATE_INDEX] == "welcome":
            self.welcome()
        elif self.GAME_STATES[self.STATE_INDEX] == "main":
            self.main_game()
        elif self.GAME_STATES[self.STATE_INDEX] == "over":
            self.game_over()

        glutSwapBuffers()

    def update_frame(self):
        if self.GAME_STATES[self.STATE_INDEX] == "welcome":
            self.bird.fly()

        elif self.GAME_STATES[self.STATE_INDEX] == "main":
            self.base.move(self.BP_SPEED)
            for pipe in self.pipes:
                pipe.move(self.BP_SPEED)
            self.update_pipes()
            self.update_score()

            self.bird.move()
            if self.check_crash():
                self.STATE_INDEX = next(self.STATE_SEQUENCE)

        elif self.GAME_STATES[self.STATE_INDEX] == "over":
            self.bird.die()

    # ############################### Render game states ########################################################
    def welcome(self):
        self.show_welcome()
        self.bird.draw()

    def main_game(self):
        for pipe in self.pipes:
            pipe.draw()
        self.show_score(str(self.SCORE))
        self.bird.draw()

    def game_over(self):
        for pipe in self.pipes:
            pipe.draw()
        self.bird.draw()
        self.show_score(str(self.SCORE))
        self.show_game_over()

    # #################### assistant Methods ######################################
    # Logic ##############
    def check_crash(self):
        # Check if the bird has crashed into a pipe
        pipe = self.pipes[0]
        if self.bird.right > pipe.left and self.bird.left < pipe.right:
            if self.bird.bottom < pipe.lower_y or self.bird.top > pipe.upper_y:
                return True

        # crash with the ground
        if self.bird.bottom <= BASEY:
            return True

        return False

    def update_pipes(self):
        if self.pipes[0].right < 0:
            self.pipes.pop(0)
        if self.pipes[-1].left <= self.DISTANCE:
            self.pipes.append(Pipe(self.TEXTURES["pipe"]))

    def update_score(self):
        pipe = self.pipes[0]
        # increase score if self.bird crossed the pipe's centre
        if not pipe.count and pipe.right - (pipe.width / 2) <= self.bird.right:
            self.SCORE += 1
            self.SOUNDS["point"].play()
            pipe.count = True

    # Render #############
    def show_score(self, score):
        """
        take score as a string and display it.
        """
        width = 40
        height = width * 1.5

        glPushMatrix()
        glTranslate(-(len(score) / 2 + 1) * width, 0, 0)  # centre the text.
        for n in score:
            glTranslate(width, 0, 0)  # to show numbers beside each other one, not over.
            draw_rectangle_with_tex(0.5 * SCREENWIDTH, 0.5 * SCREENWIDTH + width,
                                    0.85 * SCREENHEIGHT, 0.85 * SCREENHEIGHT + height,
                                    self.TEXTURES["numbers"][n], 0.5)
        glPopMatrix()

    def set_background(self):
        draw_rectangle_with_tex(0, SCREENWIDTH, 0, SCREENHEIGHT + 5, self.TEXTURES["BackG"], -1)

    def show_game_over(self):
        draw_rectangle_with_tex(100, 500, 400, 600, self.TEXTURES["game over"], 0.5)
        draw_rectangle_with_tex(0, SCREENWIDTH, 0, BASEY + 200, self.TEXTURES["restart"], 0.9)

    def show_welcome(self):
        draw_rectangle_with_tex(50, 550, 420, 720, self.TEXTURES["msg"], 0.5)
        draw_rectangle_with_tex(0, SCREENWIDTH, 0, BASEY + 200, self.TEXTURES["start"], 0.2)

    ######################################################################################################
    def keyboard(self, key, a, b):
        if key == b" ":
            if self.STATE_INDEX == 1:  # state is MAIN GAME, hence make the self.bird jump.
                self.SOUNDS["jump"].play()
                self.bird.velocity = self.JUMP_VELOCITY  # make self.bird go up

            elif self.STATE_INDEX == 0:  # state is WELCOME.
                self.SOUNDS["jump"].play()
                self.bird.reset()
                self.bird.velocity = self.JUMP_VELOCITY  # make self.bird go up
                self.STATE_INDEX = next(self.STATE_SEQUENCE)

            elif self.STATE_INDEX == 2:  # state is GAME OVER.
                self.pipes = [Pipe(self.TEXTURES["pipe"])]
                self.bird.reset()
                self.SCORE = 0
                self.STATE_INDEX = next(self.STATE_SEQUENCE)

        if key == b"q":
            self.is_window_open = False
            glutDestroyWindow(self.window)


if __name__ == "__main__":
    env = FlappyBirdGame()
