## Flow State
### Arcane-inspired Flow State is designed to gamify studying/working and encourage users towards completing their goals. 
Run: open app --> start session (time/task) --> get nudged when distracted --> session is logged to leaderboard

On the main page there is the option to view the leaderboard or to choose between two studying modes: time-based and task-based. (1) The Time-Based button sends users to a pomodoro page where they can select a time to study and a number of rounds. (2) The Task-Based button opens a pop-up to-do list where users can enter their tasks, set a color-coded priority level, and strikethrough or delete tasks upon completion. 

The second key feature is a distraction monitoring pop-up, which checks to see if a user is interacting with distraction sites (e.g. Netflix, Youtube, Reddit, etc.). If so, a pop-up with a countdown and the streak time appears. The pop-up encourages three options: (1) exit the distraction site, (2) 'stressed' to redirect user to calming breathing page, and (3) 'take a break' which allows users to interact with distractions for the next 5 minutes. Both the stress and break options also display a smaller pop-up below the nudge, with randomized quotes -- some quotes being pulled directly from the show.

## House Tour 
The *'visuals'* tab has the key images, backgrounds, and button graphics that are used in this project, as well as the font style under 'styles.py'. 
The *'modules'* tab houses the different components. 
- *'arcane.py'* houses the functions creating the moving Arcane-inspired runes that appear under the two main buttons on the main landing page.
- *'custom_buttons.py'* has the code to create the buttons on the main landing page, wherein 'inactive' is a button's resting state, and 'active' is what the button changes to when a user hovers over the button.
- *'leaderboard.py'* works with 'session_tracker.py' to create a ranked list of past sessions predicated on number of distractions, session length, and a points-based system. It also displays the current session with a refresh option.
- *'nudge.py'* works with the 'monitor.py'; monitor locates and reads sites the user interacts with, and nudge sends a pop-up on the user's screen to nudge them into focusing.
- *'task_module'* gives users an option to input tasks they have and sort priority levels (low, medium, high, personal) on the right of each task, to drag-and-drop tasks to change order, and to strikethrough (left-click on bullet) or delete tasks (right click task) upon completion.
- *'timer_module.py'* allows users to select a session duration and number of rounds, which are followed by preset breaks between rounds. There is a progress bar at the top which tracks progress throughout all rounds for the given session. The monkey bomb graphic is Jinx-inspired!
- *'app.py'* is the main page :3

## SetUp / Installation
Requires Python 3.x and macOS (see Limitations & Known Issues below).
1. Create & activate virtual environment (i.e. venv):
```bash
   python -m venv venv
   source venv/bin/activate
```
2. Install libararies/dependencies:
```bash
pip install pillow pynput pyobjc
```
| Library | Purpose |
|--------|---------|
| Pillow | Image loading and processing for backgrounds and graphics |
| pynput | Mouse and keyboard activity monitoring |
| pyobjc | macOS-native window management and active tab detection |

3. Install the Cinzel font before running:
   - Option A: Navigate to `visuals`, double-click `Cinzel-VariableFont_wght.ttf`, click "Install Font"
   - Option B: Download Cinzel directly from Google Fonts at: https://fonts.google.com/specimen/Cinzel

4. Grant accessibility permissions (macOS):
   - System Preferences --> Privacy & Security --> Accessibility
   - Enable access for your terminal/Python interpreter

5. You are ready to run the app:
```bash
   python app.py
```

<The project mainly uses these as well as built-in Python (e.g. tkinter, os, json, datetime, subprocess) or pyobjc (e.g. AppKit, Quartz.CoreGraphics).>

## Debugging 
There are commented out lines with a # debug or # for debugging note. Uncomment out as needed to troubleshoot in the terminal.

## Updating Distractions
In monitor.py there are list of distractions and exceptions. Update based on what you consider distractions or exceptions; e.g. if you use facebook or other sites as distractions, place them in the distraction list. 

## Upcoming Additions/Edits
- Music options for studying
- Moving graphics
- More runes across different pages
- Option to connect phone / other devices

## Limitations & Known Issues
(1) Monitoring / nudging

The browser monitoring only works on macOS currently. A user is also able to bypass nudging system by interacting with distractions on mobile devices or second devices. a further expansion may be to connect other devices to allow comprehensiveness. 
MacOS additionally needs to manually grant permissions to FLow State in System Preferences (similar to apps such as Zoom) to allow monitor.py to work correctly. 
Monitoring also relies on exact URL/site name matching, so variations may bypass the system, and 'exceptions list' may not be comprehensive enough. For instance, if a user wants music that isn't in exceptions but they are using it to study, it will be marked as a distraction unless they manually add it to a list of allowed exceptions. Idea for improvement: add a temporary list that will delete upon the termination of the app/session and checks in the monitor.py.

(2) Leaderboard
Local, as intention was to compete with oneself. However, there is not an option to study with friends or compete with others. 
The leaderboard additionally has weighting based on 'points'. Later iterations could use session length, number of distractions, and/or tasks complete to determine final points rather than arbitrary points score.
Leaderboard has a min size for the screen under the open() function -- may not be compatible for all devices.

(2.5) Session Tracker
Session tracking for idle has a few bugs; when laptop is shut then the countdown contines until the app is terminated. Need to update.

(3) Timer
No persistence; if a user mistakenly presses the reset button, closes the app, or the app crashes, then the timer isn't saved. Break times are fixed and study times are preset, so there is limited flexibility in time selection.

(4) General
In order for the nudge system to work, the app is placed *above* other layers on the device. However, this means that other apps cannot be dragged in front of flow-app while open. This cannot be toggled yet, which means users either accept or have to close the app to temporarily disable this behavior. 

(5) Accessibility
App has been screened via color filters from mac System Preferences; Greyscale, Red/Green filter for deuteranopia, green/red filter for protanopia, and blue/yellow for tritanopia were tested to ensure instructions and visuals remained accessible. 

## Acknowledgements
**Inspiration**
- Arcane (2021) — created by Riot Games, produced by Fortiche, distributed by Netflix
  Arcane's visual art, arcane/hextech/rune designs, and character colors/references are heavily inspired by the series!
  Used for non-commercial, fan purposes only <see licensing below>
  This app is not affiliated with or endorsed by Riot Games or Netflix.

**Visuals / Backgrounds**
- Main background — AI-generated in Arcane art style via prompti.ai at:
  https://prompti.ai/arcane-art-style-illustrated-story-backgrounds/
  -> Also inspired by the temple of Janna, where the fight between Jinx and Vi occurred. 

- Leaderboard background — Screenshot from Arcane (2021), 
  © Fortiche, Riot Games, Netflix
  Upscaled version sourced via u/barooned (Reddit, r/arcane, 2024) at: https://www.reddit.com/r/arcane/comments/1hiudgu/2300_4k_upscaled_and_native_wallpapersscreenshots/
  Upscaling method originally credited to u/Mewthree1

- Monkey bomb graphic — Fan art, original artist unknown; possibly Justingeth 
  based on references found in the Arcane: League of Legends Facebook community 
  and Shiina's YouTube channel. Inspired by Jinx's design in Arcane 
  © Fortiche, Riot Games, Netflix. If you are the original artist, please reach out.

**Quotes/Dialogue**
- Select dialogue quoted from Arcane Season 1 (2021) & Season 2 (2024)
  Characters: Vi, Jinx, Ekko, Vander, Viktor, Jayce, Silco, Heimerdinger.
  © Fortiche, Riot Games, Netflix. All rights reserved.

**Academic**
- Yeung, K. (2017). Hypernudge: Big Data as a mode of regulation by design. Information, Communication & Society, 20(1), 118–136.
  -> Your piece on hyper-nudges, coupled with gamification, encouraged me to consider how to employ powers of nudging for good.

## Licensing 
© Alexia Gallon, 2026. All rights reserved.
This project is non-commercial and intended for a personal/educational use. The source code is licensed under MIT License — you are free to use and 
modify it for personal and educational purposes with proper attribution.
No copyright infringement intended. 
All third-party assets remain the property of their respective creators.
