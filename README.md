# Lux Backend

## Running the Project

### Setting up your .env

`.env` files tend to hold secrets so we don't ever commit them to the codebase.
But an example file is included in `.env.sample`.

Simply copy that file into a `.env` file.
The default values from that sample file are fine to get you running.
If you ever want to change any of those parameters during your testing,
be sure to edit your local `.env` and not the sample file.

### Building the docker containers

Make sure you have Docker Desktop running before running any docker commands.
Windows requires this program to be running to run the "docker server" so to speak.

We are running multiple containers.
The `docker-compose.yml` file configures everything we need to run all of the different containers.

Everything should be baked into the following command:

```
docker-compose up --build
```

NOTE: For the your first time running these containers you will need to perform a
few initial setup procedures outlined below in [First Time Setup](#first-time-setup)

NOTE: If you receive 401 unauthorized error, try the following command

```sh
docker logout
```

## First Time Setup

### Setting up the DB

Before this program can interact with the database, we need to:

- Setup the tables
- (Optionally) Initialize and starting values in the tables.

1. Connect to the web container.
   (If you are new to docker there is more info below on how to do this [Getting Inside a Docker Container](#getting-inside-a-docker-container))
2. Run the "migrations" that set up each table in the database.

```bash
python manage.py migrate
```

3. (Optionally) Seed the database with fixtures data.
   You can still run integration tests, but manual tests benefit from having some data in the DB.

```bash
python manage.py seed_fixtures
```

## Setting Up Your Dev Environment

### For VSCode

Included in the repo is `.vscode/` folder.
We use this to share extension settings and recommendation between team members who are also using VSCode.
(Currently all the devs are)

That folder currently includes 2 key things:

1. The recommended extensions, which include things like:
   - Language support for the languages we use.
   - Linters to keep our code clean and avoid mistakes.
   - Spell Checkers
   - Django specific stuff
2. Spell checker dictionary.

   - If you find any words that are not in the dictionary that should be added, please contribute.
   - Once you have the spell checker extension you can just right click on words and add them to the dictionary.
     (`Spelling` > `Add Words to Workspace Settings`)

3. Ensure that you have installed python locally and set the python interpreter to the one you installed.
4. Install all dependencies in the `requirements.txt` and `requirements_dev.txt` files.

```bash
pip install -r server/requirements.txt
pip install -r server/requirements_dev.txt
```

## Testing

### Running the Automated Tests

1. Connect to the oracle-db container that spun up in Docker.
   (If you are new to docker there is more info below on how to do this [Getting Inside a Docker Container](#getting-inside-a-docker-container))

```bash
python manage.py test
```

### Running the Linter

The linter is typically run through your IDE extensions.
e.g. For Visual Studio there is the PyLint extension.

But it can also be run from the command line with the following:

```bash
pylint $(git ls-files '*.py') --rcfile .pylintrc
```

### Resetting the DB

Sometimes we want to refresh the data in ur test DB.

1. Open a terminal in the DB container.
2. Open an sql terminal.

```sh
psql -U lux
```

3. Drop all the tables.

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

4. Open a terminal in the web container.
5. Run the migrations again.

## Docker Tips

### Getting Inside a Docker Container

#### From Docker Desktop

1. Navigate to the Containers Tab
2. Click on the container you want to enter.
3. Click on the Exec tab.

Notably from here, you can also access logs and files from the same interface.

#### From The Command Line

You can use the following command to determine the container ID of the container you want to connect to.

```sh
docker ps
```

Once you have that `CONTAINER ID` we connect by 'exec'uting a bash terminal inside the container, with the following command:

```sh
docker exec -it {container_id} bash
```

## Additional Notes

### Manually applying Fixtures

```bash
python manage.py loaddata ./{app}/fixtures/{Fixture_file}.json
```
