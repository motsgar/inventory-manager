# Inventory Manager

A simple inventory manager for managing any kind of hierarchical inventory.

Deployed at [https://inventory-manager.motsgar.fi](https://inventory-manager.motsgar.fi)

## Current state

The application functionality is basically done. Only deletion of some items isn't implemented yet.
The UI is a basic html UI that doesn't yet have any fancy css. Even if the application visually isn't

I had to drop the feature of item locations possibly being other items, as I didn't really manage
my time well to implement any additional features. Something else to this category of features would
be eg. ability to search and filter based on properties.

### Finalizations that would be done after the night of the official deadline

-   Deletion of categories, locations and items (item instance / count deletion works)
-   Cleaner UI
-   Better error messages for invalid inputs

## Features

-   Has 3 concepts: `Location` and `Category` and `Item`
    -   Locations and Categories can be nested.
-   There are item types and actual items. A item type describes the item, and an actual item is where and how many of that item exists.
    -   For example, a `CPU` item type describes a CPU, and an actual item is the count of the physical CPU(s) in different locations.

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
            -   Computer
        -   My shelf
-   Items
    -   memory
        -   Properties
            -   Size: 4GB
        -   Category: DDR4
        -   ActualItems:
            -   My shelf: 4
    -   memory
        -   Properties
            -   Size: 16GB
        -   Category: DDR4
        -   ActualItems:
            -   Computer: 2
            -   My shelf: 2
    -   cpu
        -   Properties
            -   Type: Some CPU
            -   Cores: 4
        -   Category: CPU
        -   ActualItems:
            -   Computer: 1
    -   computer
        -   Category: Computers
        -   ActualItems:
            -   MyDesk: 1
    -   gpu
        -   Properties
            -   Type: Some GPU
        -   Category: GPU
        -   ActualItems:
            -   Computer: 1

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
