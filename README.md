# River Invaders
#### Video Demo:
- [Screen recording of the game being played](https://youtu.be/3rwQIb1J0IY)

#### Description:
Game implementation based on classic arcade games River Raid and Space Invaders using Pygame Zero framework.

#### Game objective:
- Make the most points by eliminating enemies. Be careful as you can be destroyed if you touch an enemy or if you step outside the river's edge.
- With each stage, the difficulty of the game increases.
- To move the ship use LEFT and RIGHT arrow keys.
- To increase and reduce speed of the ship use UP and DOWN arrow keys.
- To fire, press SPACE BAR.  

#### Files and directories explained:
- Directory */images/*: contains all the images used in the game. The images were extracted from the website [Kenney](https://kenney.nl/) and are not copyrighted, and can be used for personal or commercial use. The only exception is the two background images that were created by me using the Gimp application.
- Directory */sounds/*: audios used in the game. The audios were also obtained from the website Kenney.
- *river-invaders.py* python module: main module that contains 100% of the game's code.
- *requirements.txt* file: dependencies of the game that in fact is reduced only to the library Pygame Zero.
- *screenshot.jpg* image file: game screenshot.

#### References used:
- https://kenney.nl
- https://simplegametutorials.github.io
- https://pygame-zero.readthedocs.io/en/stable/index.html  

To run, just clone the repository in terminal and run the following commands:  
`cd river-invaders`  
`python3 -m venv .venv`  
`source .venv/bin/activate`  
`pip install -r requirements.txt`  
`pgzrun river-invaders.py`  

If you have problems installing or running Pygame Zero, go to the following links:
- [Installing Pygame Zero](https://pygame-zero.readthedocs.io/en/stable/installation.html)
- [Running Pygame Zero in IDLE and other IDEs](https://pygame-zero.readthedocs.io/en/stable/ide-mode.html)

Remember that you need python3 installed on your system before running the above commands.

![screenshot](screenshot.jpg)
