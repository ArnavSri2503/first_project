# first_project

Designed and implemented a neon arcade runner in Python (Pygame), leveraging iterative prototyping and AI-assisted development while focusing on gameplay systems, debugging, and optimization.

Attached earlier iterations to document progress but kept earlier versions as they had some ideas that could have been expanded further.

Cube Runner: Neo Edition

A fast-paced neon arcade runner built with Python + Pygame, featuring dynamic difficulty, boss patterns, and polished visual effects inspired by TRON-style aesthetics.

Features:

> Core Gameplay
Lane-based movement (6 lanes)  
Smooth jumping + gravity physics  
Increasing difficulty over time  
Score-based progression  

> Enemy System
Normal blocks – standard obstacles  
Wall patterns – full-lane blockers  
Fake gaps – bait-and-punish patterns  
Moving enemies – lateral threats with trails  

> Boss Mode
Triggered at high score

> Pattern-based attacks:
Gap walls  
Sequential waves  
Fake + real combinations  
Screen shake + warning system  

> Visual Polish
Neon/TRON-inspired aesthetic  
Dynamic glowing lanes  
Player trail with:  
velocity-based particles  
difficulty + health color shift  
(cyan → blue → purple → red)  
Moving enemy trails (horizontal motion-based)  
Impact particles on collision  
Screen shake + flash feedback  

> Player Systems
Health system with regeneration  
Invulnerability frames after hit  

> Collision-based damage:
normal = 1  
wall = 2

> Controls
Key	Action:  
← / →	         Move lanes  
↑           	 Jump  
SPACE	         Pause / Resume  
R	             Restart (Game Over)  
ESC	           Quit  

> Design Highlights
Pattern spacing system  
Prevents unfair back-to-back wall/fake patterns  
Balanced enemy mix  
Moving enemies are frequent and integral, not rare gimmicks  
Performance optimized  
Removed expensive full-screen surfaces  
Direct rendering for trails/particles  
Reduced allocation overhead  
Game feel focus  
Immediate feedback (shake, flash)  
Smooth motion (no artificial slowdown)  
Readable visual language

> Tech Used
Python 3  
Pygame

> Future Improvements (most probably not)
Sound effects + music  
Menu system / mode selection  
Power-ups / abilities  
Procedural boss phases  
Mobile/web port  

> Inspiration
TRON-style neon visuals  
Arcade runners  
Bullet-hell readability principles  

> Author
Arnav Srivastava  
Manipal University Jaipur, Jaipur  
Ist Year (at the time of writing this)
