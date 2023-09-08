# Cli Menu helper/utility

I got tired of using while loops over and over again to validate user inputs in simple programs that I have in school.
I wanted to focus on the core logic there rather that spend time reinventing the same looking menus. 

How it usualy goes. You have a list of menus u want to print out pretty. Usualy with numbers in front

## That would look like something like this

Example:
```bash
Available commands: 
1) menu_item 
2) menu_item
>> 
```
or 

```bash
other title
1) menu_item 2) menu_item
>> 
```
No problem if you just have one menu. But if you have multiple menus and if your user has the option to come back to slightly diffrent menu?
It's a hassle and simply put annoying. Because u need to validate input, map it either to match the string you specified
or simply use numbers.
And what if you want to use both- numbers and the actual name as user input?

## Backstory

When I was building interactive fiction game in Python I came up with a solution.
Why not create an Menu object? And have all creating(printing) and validating logic inside there?
Yo you could even add extra function calls within those elements that are not even present by them selves
in the menu. Like in interactive fictions "hint" option. 

After I was done with my game and got my hands on new interactive menu programs, like simple book store
I created and uploaded my package on pypi so that I could use it whenever I want.

## So here is my solution :) 
## Usage:
###  Initalization
```bash 
pip install menucraft
```
Takes user options as an python list like this(mandatory to be inside an list): 
```Python
from menucraft.menu import Menu 

instance_name = Menu(["option_1", "option_2"])
```

> :warning:  **Must be writen in lower case!**

### Method show(inline, title)
Method to print out options. Takes arguments: title:str, inline:bool

1. Title: available commands (default value). inline = True(default)
```Bash 
Available commands: 1) option_1 2) option_2
```
2. title="Custom title :)", inline = False
```Bash 
Custom title :)
1) option_1 
2) option_2
```

### Method index(menu_item_index)
Method to use in if statements, simply useses the list items index
Remebember: list start with number 0. so first option_1 would be index(0)
Return the element of the index.
```python 
instance_name = Menu(["option_1", "option_2"])
instance_name.show()
choice = instance_name.validator()

if choice == instance_name.index(0): #This will be choice_1
   print("do something")
else:
   print("can only be the last element") # this will be choice_2 or last element in the list
```

###  Method validator()
```python 
choice = instance_name.validator()
```
choice is the variable that will be used in if statements to compare to instance_name.index(index)

* Takes an user input can be both numbers and full word, input is not case sensitive (human error handled)
* error messages
* returns an validated user option 

### Method all()
syntax
```python 
choice = instance_name.all()
```
uses instance_name.show()
1. prints out the options
2. Returns an validated choice from the options initiliized



## TODO
- [ ] come up with better way of adding menu items. Instead of passing them as [item...]
- [ ] Make so that you can pass in functions that require to pass in user input that is validated inside there
- [ ] More customization for example to be able to change ">> " to smth else?

