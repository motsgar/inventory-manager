# Inventory Manager

A simple-ish inventory manager for managing any kind of hierarchical inventory.

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

-   Install venv
-   Create venv: `python3 -m venv venv`
-   Activate venv: `source venv/bin/activate`
-   Install dependencies: `pip install -r requirements.txt`
-   setup postgres
-   Create database: `docker exec -i inventory-dev-postgres psql -U postgres postgres < schema.sql`
-   Run: `flask --app src/app run --debug`
