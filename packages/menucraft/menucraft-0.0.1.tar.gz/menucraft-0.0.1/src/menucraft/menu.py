class Menu:
    """Intializes a menu. asks for user input. Validates it and returns the menu_item

        Example:

        Available commands: 
        1) menu_item 
        2) menu_item 

        or 

        custom title
        1) menu_item 2) menu_item


    menu_item : str 
    args: list[menu_item...]

    """
    def __init__(self, options: list) -> None:  
        self.items= options

    def show(self,inline: bool =True, title="Available commands: "): #Custom title possible + to chose if its either inline or vertical
        """ Prints out the menu in either vertical or horizontal position.

        Args: inline: bool [default= True]
        Args: title:str [default='Available commands: ']

        returns nothing
        """
        count = 0
        menus = ""
        if inline == False:
            if self.items[-1] == "" and len(self.items) == 1:           #when menu is just an empty string
                print("Press enter...")
                
            else:
                print(title)
                for item in filter(None, self.items):               #filter removes empty string, as for inputs for pressing enter
                    count += 1
                    print(f"{count}) {item} ", end="\n")  #remove \n and unComment next line to get inline menu.
        else:
            for item in filter(None, self.items):
                count += 1
                menus += f"{count}) {item} "    # Makes an string which is then added to the final
            if self.items[-1] == "" and len(self.items) == 1:
                # If no menu_item is present acts as press enter to continue
                result = "Press enter..."
            else:
                result = title + menus
            print(result)
    
    def index(self, index):                             #To get index of an menu in the list, to make an if statement.
        return self.items[index]

    def validator(self):                #user input validator
        """
        Returns user chosen menu_item
        """
        while True:
            choice = input(">> ").lower().strip()      #making input lower, and removing whitespace from begining and end of the input. (not between words tho))
            isnum = choice.isnumeric()                  #if string is only number returns true or false
            if choice in self.items:
                return choice
            elif isnum == True:
                index = int(choice)                         # typecasts str input into an int
                index -= 1                                  # list index starts with 0 but for the user menu starts at 1)
                if index < len(self.items) and index >= 0:  #validating that the number is in the right range of the menu
                    choice = self.items[index]              #Maps index element to an word answer then returns its value.
                    return choice
                else:
                    print("Number out of range")
                
    def all(self): 
        """Combines show and validator

        returns user chosen menu_item
        """
        self.show()
        return self.validator()


