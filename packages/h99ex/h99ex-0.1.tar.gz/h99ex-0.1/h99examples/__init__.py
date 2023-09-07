from h99ex.h99examples.aiogram_example.aiogram import create_aiogram

example_choose = str(input("""
| 1. Aiogram Bot Example
 - Enter number of example: """))

if int(example_choose) == int(1):
    create_aiogram()