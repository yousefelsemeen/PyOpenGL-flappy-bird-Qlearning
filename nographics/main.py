from classes import *
from qlearn_agent import *
import pandas as pd


EXPLORATION = False
LEARNING = False


class FlappyBirdGame:
    agent: Q_learn
    next_pipe: Pipe

    def __init__(self):
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
        ###########################################
        ##################################################
        self.frames_per_step = 5  # number of frames after it the agent will take a decision
        self.counter = self.frames_per_step  # counter down to accumulate the number of frames
        self.agent = None
        self.next_pipe = None  # the pipe that the bird should focus on

        self.run()

    def run(self):
        self.init_objects()
        self.frames()


    def init_objects(self):
        self.pipes.append(Pipe())
        self.next_pipe = self.pipes[0]
        self.bird = Bird(self.GRAVITY, self.ANGULAR_SPEED)
        self.bird.fly_speed = 0
        self.base = Base()
        self.agent = Q_learn(self.get_state())

# control the game loop ################################################################
    def frames(self):
        try:
            while True:
                self.update_frame()
                self.counter -= 1
        except KeyboardInterrupt:
            if LEARNING:
                print("=" * 20)
                print("Saving data...")
                self.save_data(True, True)


    def update_frame(self):
        if self.GAME_STATES[self.STATE_INDEX] == "welcome":
            # start the game automatically
            if self.counter == 0:
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
            self.pipes.append(Pipe())

    def update_score(self):
        pipe = self.pipes[0]
        # increase score if all bird's body crossed the pipe's right side
        if not pipe.count and pipe.right <= self.bird.left:
            self.SCORE += 1
            pipe.count = True
            # make the agent focus on the next pipe
            self.next_pipe = self.pipes[1]

    # Render ##############

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
                self.bird.velocity = self.JUMP_VELOCITY  # make self.bird go up

    # helpful methods ##############################################################
    def save_data(self, force=False, skip=False):
        if not skip:
            print(f"Episode: {self.agent.num_episodes}, Score: {self.SCORE},  Highest Score= {self.highest_score}")
            self.csv_episodes.append(self.agent.num_episodes)
            self.csv_score.append(self.SCORE)
        if LEARNING and force:
            self.agent.save_q_table()
        if LEARNING and (len(self.csv_episodes) == 500 or force):
            # Create a DataFrame with the episode and score data
            data = pd.DataFrame({"episode": self.csv_episodes, "score": self.csv_score})
            # Append the data to the CSV file
            data.to_csv(csv_file, mode="a", index=False, header=False)
            self.csv_episodes.clear()
            self.csv_score.clear()

    def reset(self):
        self.save_data()
        self.pipes = [Pipe()]
        self.next_pipe = self.pipes[0]
        self.bird.reset()

        # update the highest score
        if self.SCORE > self.highest_score:
            self.highest_score = self.SCORE
        self.SCORE = 0
        self.STATE_INDEX = 0
        self.counter = self.frames_per_step


if __name__ == "__main__":
    env = FlappyBirdGame()
