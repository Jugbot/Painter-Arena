# 🏰 Painter Arena 

![](images/1.png)

### A Full-Stack app with Flask, Vue, socket-io, sqlalchemy ORM, Mysql, Bulma/Buefy, and other miscellaneous libraries.

This is a Summer project that was meant to be a learning experience and a chance to try out modern web app building workflows.  
This app was intended to be a game of doodling, hence the title. Players enter an "Arena" where a prompt is given. The players then have a set amount of time to complete their entry and then vote for other entries. When the time is up, a change in skill is calculated based on relative skill and votes which is then used in the matchmaker. You can make custom matches with custom prompts, players, and time limits. You can edit your own avatar as well. Actions in the Arena are broadcasted to other users in the Arena through socket-io so the app is somewhat realtime. The front end is built with bulma and fully responsive. 

#### TODO:
- [ ] Contributors.
- [ ] Social features including joining the same arena as another user.
- [ ] Joining multiple Arenas.
- [ ] Custom undefined avatar for new users that fits the default drawing look.
- [ ] Custom Vue enabled drawing board so as to drop jQuery dependency and customize further
- [ ] Levelling, loot boxes, unlockable drawing tools, microtransactions. 
- [ ] Publish.

## Getting Started
Install dependencies at the `app/` folder
```
pip3 install -r requirements.txt
```
Set up whatever database engine you want. I used mySQL for this project, just make sure to set up the database uri in app.py to [dialect+driver://username:password@host:port/database](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls).
Run server.py
```
python3 server.py
```
At this point, the page should launch but fail to catch resources in the static folder (since they dont exist yet).
With Node.js run either commands in the `app/src/` folder
Debug:
```
npm start
```
Deployment:
```
npm run build
```
These will generate the required files. 
*Note: At the time of writing this in `app/templates/index.html` if you want to use the Vue debugger you will need to change vue.min.js to vue.js*


