# Painter Arena
A Full-Stack app with Flask, Vue, socket-io, sqlalchemy ORM, Mysql, Bulma/Buefy, and other miscellaneous libraries.

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


