The simulated contests work by inserting fake submissions with the original judging results into the DB without the interference of the judgehost.
For this simulation to work, you need a jury account on the DOMJudge the contest will be running in and DB access with write privileges.

# Setup
## First time setup
### DOMJudge

Choose a language that the simulated teams will be using i.e. f95 fortran
 - Disable judging for that language in DOMJudge settings - so that judgehosts do not crash on 404s because the fake submissions do not have any code associated with them

Insert dummy teams
 - Create ~100 (or whatever amount is required) dummy teams that the simulation will use for submissions
 - The teams must have ids in ascending order
 - Save the id of the first dummy team
 - You can add all these teams into a team category (i.e. Simulated teams) to easily add them to contests
   - The category should have these options set:
     - Visible: yes
     - Sort order should be set to:
       - the same number as the teams competing to show them in the same scoreboard group
       - a different number to have the simulated teams in a different scoreboard group


### Project files
Edit login files
 - dblogin.txt
   - Create based on the dblogin.template.txt
   - Fill in the login information required
 - domjudgelogin.txt
   - Create based on the domjudgelogin.template.txt
   - Fill in the required login information
     - First line is url
     - Second line is jury username
     - Third line is password



## Before contest setup

### Contest setup
Create your contest as you normally do, and assign the dummy team category as competing teams.
Take note of the contest id and the problem ids.
### Project files
Edit the main.py file and set the CONTEST_ID=x, where x is the id of the contest to have the simulation.

### Data preparation
The data should be in a csv file with these colums in order:
 - time of submission in minutes (maybe in the future I will chage to use seconds)
 - problem id
 - team id
 - result - i.e. correct, wrong-answer,...
#### Converting from scoreboard data
The data_prep/data_prep.py file is capable of converting the scoreboard data to submissions data. It does not do it fully correctly - because the wrong answer times are not shown in scoreboard data - so it randomizes the wrong submissions to happen some time before the final submit.
For the script you need to specify the id of the first dummy team and the map of: problems from the contest → ids in your domjudge system.
The data shoul be in the format:
 - TODO :D, write when the script is finished

# Running the contest
After all setup you just run the main.py file and watch the fake submits go :D.
Try not to interfere with the fake submits in any way.

When this program crashes or stops working midway through - make sure to edit the submissions csv file to remove the already created submissions, because the program will insert hem again.


