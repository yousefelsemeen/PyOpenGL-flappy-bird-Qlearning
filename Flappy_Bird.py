from pathlib import Path
from pygame import mixer, image
from classes import *
from qlearn_agent import *
import matplotlib.pyplot as plt
import pandas as pd

DISPLAYING = True
EPISODES_BEFORE_DISPLAY = 3000
PERIOD = 5


def plot():
    data = pd.read_csv(csv_file)

    episode_data = data["episode"].tolist()
    score_data = data["score"].tolist()

    # Create lists to store the colors for each point and count the color occurrences
    colors = []
    color_counts = {'Red': 0, 'Blue': 0, 'Green': 0}
    total = len(score_data)

    # Assign colors based on score range
    for score in score_data:
        if score < 50:
            colors.append('red')
            color_counts['Red'] += 1
        elif score < 100:
            colors.append('blue')
            color_counts['Blue'] += 1
        else:
            colors.append('green')
            color_counts['Green'] += 1

    # Create legend with color counts for the scatter plot
    legend_labels = ['Red (<50) - ratio: {}'.format(round(color_counts['Red'] / total, 2)),
                     'Blue (50-100) - ratio: {}'.format(round(color_counts['Blue'] / total, 2)),
                     'Green (>100) - ratio: {}'.format(round(color_counts['Green'] / total, 2))]

    legend_handles = [plt.Line2D([], [], marker='o', markersize=10, color=c, linestyle='None') for c in
                      ['red', 'blue', 'green']]

    if LEARNING:
        plt.scatter(episode_data, score_data, c=colors)
        plt.legend(legend_handles, legend_labels, fontsize=8)
        plt.xlabel("Number of Episodes")
        plt.ylabel("SCORE")
        plt.title("Flappy Bird")

    else:
        # Create a figure with three subplots
        fig, (points, columns, box) = plt.subplots(1, 3, figsize=(12, 6))

        # Plot the scatter plot in the first subplot
        points.scatter(episode_data, score_data, c=colors)

        # Set labels and title for the first subplot
        points.set_xlabel("Number of Episodes")
        points.set_ylabel("SCORE")
        points.set_title("Flappy Bird")
        points.legend(legend_handles, legend_labels, fontsize=8)

        # Calculate the histogram data
        highest_score = 7001  # max(score_data)
        num_bins = highest_score // 200 + 1
        hist_data = [0] * num_bins

        #  ###############  To draw the histogram and boxplot in all the range of the scores  ##################
        #      1) in the previous line make the highest_score = max(score_data)
        #      2) comment the following line
        #      3) replace "filtered" with => "score_data"

        filtered = list(filter(lambda i: i <= 7000, score_data))

        for score in filtered:
            bin_index = score // 200
            hist_data[bin_index] += 1

        # Create the histogram in the second subplot
        bin_edges = [i * 200 for i in range(num_bins + 1)]
        columns.hist(filtered, bins=bin_edges, edgecolor='black')

        # Create the boxplot in the third subplot
        box.boxplot(filtered)

        # Set labels and title for the second subplot
        columns.set_xlabel("SCORE")
        columns.set_ylabel("Frequency")
        columns.set_title("Score Distribution")

        #   automatically adjust the subplots' positions and sizes
        plt.tight_layout()

    plt.show()


class FlappyBirdGame:
    agent: Q_learn
    next_pipe: Pipe

    def __init__(self):
        self.cur_path = str(Path(__file__).parent.resolve())
        self.PERIOD = PERIOD if DISPLAYING else 0
        # ######## to control the game ###############
        self.GAME_STATES = ["welcome", "main", "over"]
        self.STATE_SEQUENCE = cycle([1, 2, 0])
        self.STATE_INDEX = 0
        ################################################
        self.DISTANCE = SCREENWIDTH / 2  # distance between pipes
        self.SCORE = 0
        self.previous_score = 0
        try:
            data = pd.read_csv(csv_file)
            self.highest_score = data["score"].max()
        except FileNotFoundError:
            data = pd.DataFrame({"episode": [0], "score": [0]})
            # Append the data to the CSV file
            data.to_csv(csv_file, mode="a", index=False, header=True)
            self.highest_score = 0
        self.csv_episodes = []
        self.csv_score = []
        self.BP_SPEED = -4
        # ######## bird's control ########################
        self.ANGULAR_SPEED = 3
        # control bird jump.
        self.JUMP_VELOCITY = 3
        self.GRAVITY = -0.2
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
        ##################################################
        self.frames_per_step = 5  # number of frames after it the agent will take a decision
        self.counter = self.frames_per_step  # counter down to accumulate the number of frames
        self.agent = None
        self.next_pipe = None  # the pipe that the bird should focus on

        self.run()

    def run(self):
        glutInit()
        glutInitWindowPosition(10, 10)
        glutInitWindowSize(SCREENWIDTH, SCREENHEIGHT)
        glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
        self.window = glutCreateWindow(b"Flappy Bird")

        glutDisplayFunc(self.display)
        glutKeyboardFunc(self.keyboard)
        glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF)
        self.init()
        self.frames(1)
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
        self.next_pipe = self.pipes[0]
        self.bird = Bird(self.TEXTURES["bird"], self.GRAVITY, self.ANGULAR_SPEED)
        self.bird.fly_speed = 0
        self.base = Base(self.TEXTURES["base"], 0.1)
        self.agent = Q_learn(self.get_state())

    # control the game loop ################################################################
    def frames(self, t=1):
        global DISPLAYING
        if self.is_window_open:
            if self.agent.num_episodes == self.agent.last_episode + EPISODES_BEFORE_DISPLAY:
                DISPLAYING = True
                self.PERIOD = PERIOD
            if DISPLAYING:
                self.display()
            self.update_frame()
            self.counter -= 1
            glutTimerFunc(self.PERIOD, self.frames, t)

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
            # start the game automatically
            if self.counter == 0:
                if DISPLAYING:
                    self.SOUNDS["jump"].play()
                self.bird.reset()
                self.bird.velocity = self.JUMP_VELOCITY  # make self.bird go up
                self.STATE_INDEX = next(self.STATE_SEQUENCE)

                self.counter = self.frames_per_step

        elif self.GAME_STATES[self.STATE_INDEX] == "main":
            # agent take decision
            if self.counter == 0:
                state = self.get_state()
                if LEARNING:
                    self.agent.learn(state, self.get_reward())
                self.agent_decide(state)
                self.counter = self.frames_per_step

            # update the frame
            self.base.move(self.BP_SPEED)
            for pipe in self.pipes:
                pipe.move(self.BP_SPEED)
            self.update_pipes()
            self.update_score()

            self.bird.move()
            if self.check_crash():
                self.STATE_INDEX = next(self.STATE_SEQUENCE)

        elif self.GAME_STATES[self.STATE_INDEX] == "over":
            if LEARNING:
                self.agent.learn(self.get_state(), self.get_reward(), done=True)
            else:
                self.agent.reset()
            self.reset()

    # ###################### Render game states ########################################
    def welcome(self):
        self.show_welcome()
        self.bird.draw()

    def main_game(self):
        for pipe in self.pipes:
            pipe.draw()
        self.show_score(str(self.SCORE))
        self.bird.draw()

    def game_over(self):
        self.show_game_over()

    # #################### assistant Methods ##################################
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
        # increase score if all bird's body crossed the pipe's right side
        if not pipe.count and pipe.right <= self.bird.left:
            self.SCORE += 1
            if DISPLAYING:
                self.SOUNDS["point"].play()
            pipe.count = True
            # make the agent focus on the next pipe
            self.next_pipe = self.pipes[1]

    # Render ##############
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

    #################################################################################
    # AI agent methods ##############################################################
    def get_state(self):
        # Return the current state of the game
        state = {
            'bird_y': (self.bird.bottom + self.bird.top) / 2,  # centre of the bird
            'bird_v': self.bird.velocity,
            'pipe_positions': (self.next_pipe.left + self.next_pipe.width * 0.5, self.next_pipe.gap_y),
            'score': self.SCORE,
            'game_state': self.GAME_STATES[self.STATE_INDEX]
        }
        return state

    def get_reward(self):
        state = self.get_state()

        # if crashed ...........................
        if state['game_state'] == 'over':
            return -200

        # if it didn't crash ...................
        reward = 0
        # score bonus
        if self.SCORE > self.previous_score:
            reward += 100
            self.previous_score = self.SCORE

        bird_centre = state['bird_y']
        bird_v = state['bird_v']
        gap_x = state['pipe_positions'][0] - self.next_pipe.width * 0.5
        gap_y = state['pipe_positions'][1]
        gap_top = self.next_pipe.upper_y
        gap_down = self.next_pipe.lower_y
        bird_height = self.bird.height
        gap_size_quarter = self.next_pipe.gap_size * 0.35

        # encourage the bird to be inside the scope of the gap
        if gap_down + gap_size_quarter <= bird_centre <= gap_top - gap_size_quarter:
            reward += 60
        elif gap_down + bird_height <= bird_centre <= gap_top - bird_height:  # within the gap exactly
            if bird_centre < gap_y and bird_v >= 0:
                reward += 10
            if bird_centre > gap_y and bird_v <= 0:
                reward += 10
            reward += 20
        elif bird_centre < gap_down + bird_height:  # bird lower than the gap
            pipe_bird_distance_x = gap_x - self.bird.right
            pipe_bird_distance_y = gap_down - bird_centre
            if pipe_bird_distance_y < pipe_bird_distance_x:  # scope within 45deg lower than the gap
                if bird_v <= 0:
                    reward -= 10
                else:
                    reward += 10
            else:
                reward -= 10
        elif bird_centre > gap_top - bird_height:  # bird higher than the gap
            pipe_bird_distance_x = gap_x - self.bird.right
            pipe_bird_distance_y = bird_centre - gap_top
            if pipe_bird_distance_y < pipe_bird_distance_x:  # scope within 45deg higher than the gap
                if bird_v > 0:
                    reward -= 10
                else:
                    reward += 10
            else:
                reward -= 10

        return reward

    def agent_decide(self, state):
        action = self.agent.take_action(state, EXPLORATION)
        if action == "jump":
            if self.STATE_INDEX == 1:  # state is MAIN GAME, hence make the self.bird jump.
                if DISPLAYING:
                    self.SOUNDS["jump"].play()
                self.bird.velocity = self.JUMP_VELOCITY  # make self.bird go up

    # helpful methods ##############################################################
    def save_data(self, force=False):
        print(f"Episode: {self.agent.num_episodes}, Score: {self.SCORE},  Highest Score= {self.highest_score}")
        self.csv_episodes.append(self.agent.num_episodes)
        self.csv_score.append(self.SCORE)

        if len(self.csv_episodes) == 500 or force:
            # Create a DataFrame with the episode and score data
            data = pd.DataFrame({"episode": self.csv_episodes, "score": self.csv_score})
            # Append the data to the CSV file
            data.to_csv(csv_file, mode="a", index=False, header=False)
            self.csv_episodes.clear()
            self.csv_score.clear()

    def reset(self):
        self.save_data()
        self.pipes = [Pipe(self.TEXTURES["pipe"])]
        self.next_pipe = self.pipes[0]
        self.bird.reset()

        # update the highest score
        if self.SCORE > self.highest_score:
            self.highest_score = self.SCORE
        self.SCORE = 0
        self.STATE_INDEX = 0
        self.counter = self.frames_per_step

    # keyboard handler ################################################################
    def keyboard(self, key, a, b):
        if key == b"q":
            if LEARNING:
                self.agent.save_q_table()
            self.save_data(True)
            self.is_window_open = False
            glutDestroyWindow(self.window)

            plot()


if __name__ == "__main__":
    env = FlappyBirdGame()
    print("hello")
