## NBA Games and Stats

Python/Flask application with Nginx proxy and a Mongo database

## Project structure:
```
.
├── compose.yaml
├── flask
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── server.py
│   ├── helpers.py
│   ├── .env
│   └── templates
|       ├── index.html
│       ├── gamedate.html
│       ├── gameid.html
│       └── teamcsv.html
└── nginx
    └── nginx.conf

```

[_compose.yaml_](compose.yaml)
```
services:
  web:
    build: app
    ports:
    - 80:80
  backend:
    build: flask
    ...
  mongo:
    image: mongo
```
The compose file defines an application with three services `web`, `backend` and `db`.
When deploying the application, docker compose maps port 80 of the web service container to port 80 of the host as specified in the file.
Make sure port 80 on the host is not being used by another container, otherwise the port should be changed.

## Deploy with docker compose
  
> :warning: **WARNING**: Before the deployment, please, make sure to add your RapidAPI Key to the **.env**. Note that for safety reasons the key is not present and without this key, the application can't run.

```
$ docker compose up -d
✔ Network nba-app_default      Created 
✔ Container nba-app-mongo-1    Started   
✔ Container nba-app-backend-1  Started    
✔ Container nba-app-web-1      Started  

```
> :warning: **WARNING**: If "docker compose up -d" does not work, try docker compose build first.

## Expected result

Listing containers must show three containers running and the port mapping as below:
```
$ docker container ls
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS          PORTS                NAMES
5c17a4fdfce9   nginx             "/docker-entrypoint.…"   25 seconds ago   Up 10 seconds   0.0.0.0:80->80/tcp   nba-app-web-1
ac5dc8dc032f   nba-app-backend   "python3 server.py"      25 seconds ago   Up 10 seconds                        nba-app-backend-1
ca6d62911c9f   mongo             "docker-entrypoint.s…"   25 seconds ago   Up 11 seconds   27017/tcp            nba-app-mongo-1
```

After the application starts, navigate to `http://localhost:80`. There, you will find 3 buttons:  
- Games By Date -> Insert specific date, format 'YYYY-MM-DD' and it will return a dataset with games for the date;
- Game By ID -> Insert specific ID, and it will return a dataset with games for the date;
> :warning: **WARNING**: The IDs from Games By Date section and Game BY ID do not match. Do not try to use the same ID for both as they come from different datasets. Game By ID follow a format of integers in a range from 1 to 49153.  
- Teams Stats -> Insert a date range, format 'YYYY-MM-DD' and it will download a csv with stats of teams that played in that period.

To stop and remove the containers
```
$ docker compose down
```
## Datasets

### Game By Date:
  
The Game By Date dataset originates from the nba-api package. Due to problems using the original link (I was unable to return data for specific dates, instead, the entire dataset would be requested), I understood that would be better to use the package.   
  
GAME_ID: Unique ID for that specific match in this specific dataset;  
AWAY_SCORE: Points scored by the visitor team;  
AWAY_TEAM: Abbreviation of the visitor team's name;  
GAME_DATE: The date where the match happened;  
HOME_SCORE: Points scored by the home team;  
HOME_TEAM: Abbreviation of the home team's name;  
MATCHUP: The teams playing against each other and where;  
WINNER: Indicates which team won that match.  


### Game By ID:
  
The Game By ID dataset originates from the original link[](https://rapidapi.com/theapiguy/api/free-nba/endpoints). AAs mentioned before, the ID's are within a range from 1 to 49153. Those ID's do not match the ID's for the previous dataset.  
  
GAME_ID: Unique ID for that specific match in this specific dataset;  
AWAY_SCORE: Points scored by the visitor team;  
AWAY_TEAM: Abbreviation of the visitor team's name;  
GAME_DATE: The date where the match happened;  
HOME_SCORE: Points scored by the home team;  
HOME_TEAM: Abbreviation of the home team's name.  

## Teams Stats:
  
This dataset indicates the some stats for each team that played a specific period of time. The csv is download immediatelly after clicking the option. The name of the report follows the format: *start-date_to_end-date_report.csv*, example: *2023-09-10_to_2023-09-13_report*.  
  
TEAM_NAME: The name of the team which the entry is referring to;  
PTS_AVG: Average of points scored in the given period;  
HOME_AVG: Average of points scored at home in the given period;  
AWAY_AVG: Average of points scored when visiting in the given period;  
TOTAL_GAMES: Total number of games that team played in that period. Note that the total sum of games will be the double of actual games as each team has its own entry.  
TOTAL_WIN: Number of victories the team had in that period;  
TOTAL_LOSS: Number of defeats the team had in that period;  
WIN_PERCENTAGE: Percentage of games won;  
LOSS_PERCENTAGE Percentage of games lost.  

## Conclusion

I would like to conclude explaining my reasoning and how I would deal with some of the points mentioned in the challenge.  
- Troubleshooting -> I used and would personally suggest the logs for each docker container. When having a problem, that was where I was checking to better understand the problems the application was facing. Maybe a better solution would be to have a specific place to cache the logs and create metrics based on that. Honestly, I did not do it as for me, checking the logs was enough. In a production environment, naturally, that would not be enough.  
- Traffic/SLA -> I thought about using nginx for load balance and scale the backend container when necessary. This could also be done if the application was running on kubernetes instead. ReplicaSet could be used to help with scalability.  
- Problems and erros -> This can also fall on testing. Honestly, I do believe that for testing the application could be better. My lack of experience on this matter really affects my code. Same can be said about handling problems like informing IDs not present within the dataset or dates where no games were played. This returns erros and I am not sure how to work out the html.  
- Databse -> I used MongoDb in this project because believed it would be easier to set up and run. A SQL database would require more configuration, however I do understand that this project would run perfectly well in a SQL database (everything was treated using pandas dataframes), maybe even better. Another reason for using it was that I was partly curious to see how Mongo would work with this application.  
- API -> My application used two different datasets, the original link informed in the challenge and the nba-api package, which can be found in the "About" section of the same website. I am really sorry if that was not allowed but I could not see a better way of doing it. Because of the different datasets, I was not sure how to bring the data from each player in each match. I also was not sure how to create a readable schema for that. Would players names and their points be a column with a list/dict or a column for each player? Mongo could be helpful for the NoSQL but I could not get to a solution on how to arrange that.  
  
Though this application is far from perfect, I am very happy with the challenge and the experience. That was my first time creating an app with flask and learning so many things was rewarding. Also would like to say that please, any advise or guidance on how to improve would be deeply appreciated. If there is any reading or studying material that you believe could be useful here, I will be more than happy to look.
