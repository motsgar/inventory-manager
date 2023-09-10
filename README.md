# Inventory Manager

A simple inventory manager for managing any kind of hierarchical inventory.

## Features

-   Has 2 concepts: `Location` and `Category`
    -   Both can be nested
    -   A category can have multiple parent categories
-   A single item consists of a `Category`(s) and a `Location`
    -   A items location can be either a `Location` or a another item
    -   Items can be moved between locations
    -   A item can have multiple categories
-   Example:

    -   Categories:
        -   Computer parts
            -   CPU
            -   GPU
            -   RAM
    -   Locations:
        -   My room
            -   Location: My desk
            -   Location: My shelf
                -   Item: Computer
    -   Items
        -   memory
            -   Type: DDR4
            -   Size: 8GB
            -   Categories: RAM
            -   ActualItem:
                -   Location: Computer
