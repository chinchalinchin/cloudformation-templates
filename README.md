# InnoLab Backend

This repository is a template for a [django](https://docs.djangoproject.com/en/3.2/)-[django-rest-framework](https://www.django-rest-framework.org/) project. It has been containerized with [Docker](https://docs.docker.com/) through the *Dockerfile* in the project root directory and orchestrated with a [Postgres](https://www.postgresql.org/docs/) instance via the *docker-compose.yml* in the project root directory. The application comes pre-configured to connect to this instance when running as a container. It can also be run locally, in which case, it will switch to a **SQLite** model backend.

## Quickstart

1. Configure Enviroment

Copy the */env/.sample.build.env* and */env/.sample.runtime.env* into new */env/build.env* and */env/runtime.env* files respectively. Adjust the environment variables in these files to your specific situation. The *build.env* get injected into the */scripts/docker/build-image* shell script to configure the `docker build`. The *runtime.env* gets into injected into the */scripts/run-server*, */scripts/docker/entrypoint.sh* and the */scripts/docker/run-container* shell scripts. These define the different starting points of the application and *runtime.env* configures the environment from which these entrypoints bootstrap.

The main environment variable of interest is **APP_ENV**. This variables is parsed in the */app/core/settings.py* and determines how **Django** will configure its application settings. If set to `local`, **Django** will use a **SQLite** database and set the **CORS** and **ALLOWED_HOSTS** to their most permissive settings. The **DEBUG** setting will be set to **True** in `local` mode.

If set to `container`, **Django** will configure a **Postgres** connection through the **POSTGRES_** environment variables and restrict the allowed origins to the comma separated list defined by the **ALLOWED_ORIGINS** environment variable. The **DEBUG** setting be set to **False** in `container` mode.

2. Install Dependencies

If running locally, activate your virtual environment (if using one) and install the **python** dependencies from the project root directory,

```
pip install -r requirements.txt
```

This step is captured in the **Dockerfile** and is not required if running the application as a container.

3. Launch Application Server

**Local Server**

All of the necessary steps to start a local server have been included in the */scripts/run-server* shell script, but if you want to do it manually, initialize the environment file, migrate your models (if you have any) and collect your static files. 

First, source the */env/runtime.env* environment file to load these variables into your shell session,

```shell
source ./env/runtime.env
```

Next, from the */app/* directory, perform the necessary pre-startup tasks for a **Django** application,

```shell
python manage.py makemigrations
python manage.py migrate
```

After these preliminary steps have been taken care of, you can either start the server in development mode,

```shell
python manage.py runserver
```

Or deploy the application onto a WSGI application server like **gunicorn**,

```shell
gunicorn core:wsgi.appplcation --bind localhost:8000 --workers 3 --access-logfile '-'
```

**Containerized Server**

All of the necessary steps to start a server inside of a container have been included in the */scripts/docker/build-image* and */scripts/docker/run-container*. These steps have been separated because sometime it is desirable to build an image without running a container and visa versa. If you wish to build and run the application manually,

```shell
docker build -t innolab-django:latest .
```

To start up the container, make sure you pass in the */env/runtime.env* file,

```shell
docker run --env-file ./env/runtime.env --publish 8000:8000 innolab-django:latest
```

If you want to start the application in a cluster with a **Postgres** service, use the configuration from the *docker-compose.yml* instead of `docker run`, i.e. execute,

```shell
docker-compose up
```

to bring up a container of the application and a container of **Postgres**. You may need to adjust the image names in the YAML if you named your image differently.

## Development

### Model Migrations

If you modify a model locally, be sure to generate and check in the new migration,

```shell
python manage.py makemigrations
git add .
git commit -m 'new migrations!'
```

Migrations **must** be commited to version control!

## Application Structure

### Django

The *core* app contains all the Django configuration. The *defaults* app creates suitable defaults for various **Django** features using data migrations; It will create default groups, users, etc. 

The groups are configured by the **GROUPS** environment variable. This variable is a comma-separated list of all the default groups you want to create.

### Authentication

Middleware from the *app/defaults/cognito.py* module is hooked into the request/response lifecycle. This middleware will validate the token in the `Authorization` header, expecting a value of `Bearer <token>`. Once the token is validated through **AWS Cognito**, a `user` attribute is added to the `request`, i.e. `request.user`. If the token was not validated, this value will be set to `None`. If the token was validated, this will be set to `django.contrib.auth.models.User`.

In other words, the **Django** `django.contrib.auth.models.User` model is only used to store metadata about a user (email, address, business name, etc.), whereas **Cognito** handles authentication and all that goes with that (password storage, encryption, identity management, etc.). The **Django** `django.contrib.auth.models.User`s are initialized with a dummy password from the **MASTER_PASSWORD** environment variable, since `password` is a required property of `django.contrib.auth.models.User`, but this password is not actually used for any sort of user access within the application.

However, the application does manage user groups and permissions, i.e. authorization. Once **Cognito** authenticates the incoming request, all authorization access is governed through the **Django** `django.contrib.auth.models.Group` schema and programmatically enforced in the request handlers within the **Django** app. See next section for more information.

### Authorization

Pass a `request` into the `app.util.authorizer.belongs_to_groups(request, [group_name_1, group_name_2, ..])` to determine if an incoming request belongs to a particular group. In the following example, the statement `hello world` only prints if the user associated with the incoming request belongs to the `developer` group.

```python
if app.util.authorizer.belongs_to_groups(request, ['developer']):
    print('hello world')
```

### Docker

The */app/* and */scripts/* folder are copied in the */home/* directory of the **Docker** file system. A user with the name *makpar* is assigned to the group *admin* during the **Docker** build. This user is granted ownership of the application files. The permissions on the application files are set to **read** and **write** for everyone and **execute** for this user only. 

The **Dockerfile** exposes port 8000, but the environment variable **APP_PORT** is what determines the port on which the application server listens. This variable is used to start up the **gunicorn** server in the *entrypoint.sh* script. 

The **Dockerfile** installs dependences for **Postgres** clients. These are the system dependencies required by the **python** library, **psycopg2**, which **django** uses under the hood to manage the model migrations when the model backend has been set to **postgres**.  

## Container Orchestration

The *docker-compose* in the project root directory will bring up an application container and orchestrate it with a **postgres** container. Both containers use the *runtime.env* environment file to configure their environments. The **POSTGRES_** variables injected at runtime are used by the **postgres** container to configure the root user, the default database name and the port the database container listens on internally. 

## Deploying to AWS App Runner With Copilot

Note: these steps are only needed to provision the resources and initialize the application. Once they have been completed, they do not need run again.

1. In project root, run the following command to initialize application,

```
copilot app init
```

Follow the prompts: 1. enter the application namespace. 2. Select the Dockerfile used to build the service.

2. Create a deployment environment. Note, we have reached the soft limit for our VPCs on AWS, so you will need to deploy your environment into an existing VPC using the `--import-vpd-id` option. This will require importing subnets with `--import-private-subnets` and `--import-public-subnets`,

```
copilot env init --name dev --import-vpc-id <vpc-id>
```

3. Import secrets into environment. First, copy the */ecs/copilot/django-app/.sample.secrets.yml* into a new file, say */ecs/copilot/django-app/secrets.yml* (this file is on the gitignore; if you name it something else, make sure to add the file name to the gitignore so secrets are committed to the version control),

```
cp ./ecs/copilot/django-app/.sample.secrets.yml ./ecs/copilot/django-app/secrets.yml
```

Then import the secrets into your application

```
copilot secret init --cli-input-yaml path/to/secrets.yml
```

Configure the application.

4. Initalize an App Runner service,

```
copilot svc init 
```

Follow the prompts: Enter a name for the service. (For what follows, assume the name of the service is `django-app`)

5. Deploy the service,

```
copilot deploy svc --name django-app
```

## Shell Scripts

Included in this repository are a collection of shell scripts (written for **BASH**) that perform common, repetitious tasks.

1. **/scripts/run-server**

**Arguments**: Accepts a `--prod` flag to signal the server should be started in production mode. If no argument is provided, the argument defaults to a development server. Optionally, a `--install` argument can be passed in to install the project dependencies through the script.

**Description**: Performs start up tasks, like collecting static files and migrating **django** models, and then starts up an application server. If `--prod` is passed in, the application will be deployed onto a **gunicorn** *WSGI* server. If `--prod` is not passed in, a local **Django** server will be started with `python manage.py runserver`. 

2. **/scripts/docker/build-image**

**Description**: Initializes the *build.env* variables and uses them in calling `docker build`. Creates a **Docker** image of the application.

3. **/scripts/docker/run-container**

**Description**: Initializes the *runtime.env* variables and feeds them into the container runtime. Starts up a container with the image name and tag created by the *build-image* script.

4. **/scripts/docker/entrypoint**

**Description**: Tne entrypoint script that gets copied into the **Docker** image. Analogous to the *run-server* script in a containerized environment. Starts up the **Docker** container from inside of the container. 

5. **/scripts/util/env-vars**

**Arguments**: The name of the enviroment file in the */env/* directory you wanted loaded into the current shell session.

**Description**: Used to load in environment variables from a particular *.env* file.

6. **/scripts/util/sys-util**

**Description**: Useful functions. Source this script, `source ./scripts/util/sys-util.sh`, to load these functions into your current shell session. *clean_docker* is a particularly useful function for cleaning up dangling **Docker** images, cleaning the cache and pruning orphaned volumes and networks. 

## Useful Commands

### Run Postgres Container

```shell
docker run --publish 5431:5432 --env POSTGRES_USER=admin --env POSTGRES_PASSWORD=root --env POSTGRES_DB=innloab postgres:latest
```

### Bash Into Container

List the containers currently running on your local and grab the name of the one you want to exec into,

```shell
docker container ps
```

Then run the following command,

```shell
winpty docker exec --it <container name> bash
```
**Note**: you may not need the `winpty` if your terminal is interactive. 

### PSQL session

```shell
psql -U <username> -p <port> -d <dbname> -W
```