# FlappyBird-Q-Learning
This project showcases the implementation of a Q-learning algorithm
to train an AI agent to play the classic game of Flappy Bird.

## About
This was a project for the AI subject in college with my team.
Flappy Bird Q-Learning is an exciting endeavor that combines
artificial intelligence and gaming.
The goal of this project is to develop an AI agent that learns
to navigate through a series of obstacles in the Flappy Bird game 
using reinforcement learning techniques, specifically Q-learning.
By leveraging the Q-learning algorithm,
the agent can learn optimal actions through trial and error,
ultimately achieving impressive results.

## Features
- Q-learning implementation: The repository includes a comprehensive implementation of the Q-learning algorithm, enabling the AI agent to learn and improve its performance over time.
- State representation: The project employs a state representation approach that captures important information about the game environment, allowing the agent to make informed decisions.
- Game simulation: The repository contains a simulated Flappy Bird environment that enables the AI agent to interact with the game and learn from its experiences.
- Training and evaluation: The project offers scripts for training the AI agent as well as evaluating its performance, allowing users to witness the learning process and assess the agent's abilities.

## Requirements
To run the Flappy Bird Q-Learning project, you need to have the following dependencies installed:
- Python (version 3.6 or higher)
- Pygame library
- NumPy library
- pandas
- matplotlib
- PyOpenGL

You can install the required dependencies using the following command:
```
pip install -r requirements.txt
```

## Usage
1. Clone this repository to your local machine using the following command:
   ```
   git clone https://github.com/yousefelsemeen/PyOpenGL-flappy-bird-QLearning
   ```

2. Navigate to the project directory:
   ```
   cd FlappyBird-Q-Learning
   ```

3. To see the performance of the agent after it has learned, simply run the 'Flappy_Bird.py' file:
   ```
   python Flappy_Bird.py
   ```
This will showcase the AI agent playing the game using the learned Q-values.
4. If you want to train the AI agent from scratch, follow these steps:

- Delete the 'q_table.npy', 'learning.csv', and 'playing.csv' files in the project directory.
- Open the `qlearn_agent.py` file and set `LEARNING = True` and `EXPLORATION = True` instead of `False`.
- Open the `Flappy_Bird.py` file and set `DISPLAYING = False` and adjust the number of episodes `EPISODES_BEFORE_DISPLAY` after that the displaying will start automatically .
- Adjust the `PERIOD` to control the speed of displaying.  
- Run the `Flappy_Bird.py` file:
   ```
   python Flappy_Bird.py
   ```
- During training, you can terminate the window by pressing the 'q' key on your keyboard to save the learning progress.

Please note that training the AI agent from scratch may take some time, depending on your hardware and the number of training iterations. Feel free to experiment and adjust the learning parameters in the code to achieve the desired results.


Thank you for your interest in the Flappy Bird Q-Learning project! Happy gaming! 🐦💥
