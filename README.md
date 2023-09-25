# Inventory Manager

A simple-ish inventory manager for managing any kind of hierarchical inventory.

Deployed at [https://inventory-manager.motsgar.fi/location](https://inventory-manager.motsgar.fi/location)

## Current state

Recursive data structures are working and the project structure has been figured out. I am kind of late on actual
feature implementations, but i'll get the main data structures / features done in the next few days. The UI is still
very much a work in progress. It is something that I will work on after the main features are done. The previous
week was spent on other stuff and trying to get the project structure right and the dependencies / deployment working.

The current database initialization is also kind of work in progress. I need to get some kind of database migration
system working. Currently the database is cleared and re-initialized every time the app is started.

## Features

-   Has 3 concepts: `Location` and `Category` and `Item`
    -   All of them can be nested
-   There are item types and actual items. A item type describes the item, and an actual item is an instance of an item type.
    -   For example, a `CPU` item type describes a CPU, and an actual item is the physical CPU(s).
-   Additionally there are users and groups. Users can be in groups. A single category can be assigned to a group, and only users in that group can see that category. A user can only see the locations and items that are in categories that they can see.

## Example structure

-   Categories:
    -   Electronics
        -   Computers
        -   Computer parts
            -   CPU
            -   GPU
            -   RAM
                -   DDR5
                -   DDR4
-   Locations:
    -   My room
        -   My desk
        -   My shelf
-   Items
    -   memory
        -   Size: 4GB
        -   Categories: DDR4
        -   ActualItems:
            -   My shelf: 4
    -   memory
        -   Size: 16GB
        -   Categories: DDR4
        -   ActualItems:
            -   mainComputer: 2
            -   My shelf: 2
    -   cpu
        -   Type: Some CPU
        -   Cores: 4
        -   Categories: CPU
        -   ActualItems:
            -   mainComputer: 1
    -   computer
        -   Categories: Computers
        -   ActualItems:
            -   MyDesk: 1
    -   gpu
        -   Type: Some GPU
        -   Categories: GPU
        -   ActualItems:
            -   mainComputer: 1

## How to run

### To just locally run the prod application with docker

Run `docker-compose up` and the application will be available at `http://localhost:5001/location`

### For development

The database copy paste commands are for docker, but you can also host postgres in any other way.

-   Install poetry
-   Install dependenciees: `poetry install`
-   setup postgres db with docker: `docker run --name inventory-dev-postgres -e POSTGRES_USER=db-user -e POSTGRES_PASSWORD=db-password -e POSTGRES_DB=db-name -d -p 5432:5432 postgres`
-   Initialize database with schema: `docker exec -i inventory-dev-postgres psql -U db-user db-name < schema.sql`
-   Create `.env` file with the following contents:
    -   `DATABASE_URL=postgresql://db-username:db-password@localhost/db-name`
-   Run: `poetry run flask --app src/app run --debug`
