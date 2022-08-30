# Author: Chance Back
# GitHub username: chanceback
# Date: 5/24/2022
# Description: This program contains classes that work together as a simple version of the 'Monopoly' board game.
#              How to play the game: Players start at the "GO" space on the board. Players take turns rolling a single
#              die (values 1-6), and moving around the board spaces. The spaces are arranged in a circle, and players
#              will pass each space repeatedly. Each player receives a certain amount of money at the start, and also
#              every time they land on or pass the "GO" space. Each space on the board may be purchased except for "GO".
#              Once purchased, the player owner charges rent to other players who land on the space. When a player runs
#              out of money, that player becomes inactive, and cannot move or own spaces. The game continues until all
#              players, but one, have run out of money. The last player with money is declared the winner.

class RealEstateGame:
    """
    Represents the game as played.
    """
    def __init__(self):
        self._gameboard = []
        self._players = {}

    def create_spaces(self, go_payout, rent_amounts):
        """Initialize the gameboard with a GO space followed by property spaces. Must be exactly 24 property spaces.

        :param go_payout: the amount that will be paid out when a player lands on or passes a GO space.
        :param rent_amounts: a list of integers to represent how much each property space will deduct from a player's
            account if the property space has an owner. Only uses the first 24 values in the list.

        :return: fills self._gameboard with space objects
        """
        # Create and append GO space to gamebaord
        go_space = GoSpace("GO", go_payout)
        self._gameboard.append(go_space)

        # For the first 24 amounts in the list, create property space and append it to gameboard
        for index in range(24):
            rent = rent_amounts[index]
            property_space = PropertySpace("Property", rent)
            self._gameboard.append(property_space)

    def create_player(self, name, account_balance):
        """Create a player object to represent a player in the game. Starting account balance must be greater than 0.

        :param name: name of the new player
        :param account_balance: amount to start the new player's account balance

        :return: creates player object and adds it to self._players
        """
        #Check if account balance is <= 0
        if account_balance <= 0:
            return

        # Create player object and add it to player's dictionary
        player_obj = Player(name, account_balance)
        self._players[name] = player_obj

    def get_player_account_balance(self, player_name):
        """Takes a player's name as a parameter and returns the player's account balance.

        :param player_name: name of the player

        :return: player's current account balance
        """
        balance = self._players[player_name].get_account_balance()
        return balance

    def get_player_current_position(self, player_name):
        """Takes a player's name as a parameter and returns their current position.

        :param player_name: name of the player

        :return: player's current position
        """
        current_position = self._players[player_name].get_position()
        return current_position

    def buy_space(self, player_name):
        """Takes a player's name as a parameter. If the player has enough funds then, the purchase price is deducted from
        the player's account, the player is set as the owner of the current space, and the method returns True.
        Otherwise, the method returns false.

        :param player_name: name of the player

        :return: True if successful in property purchase
        :return: False if player has insufficent funds in account balance or property is already owned
        """
        space = self._gameboard[self._players[player_name].get_position()]

        if space.get_space_type() != "GO" and space.get_owner() is None:
            account_balance = self.get_player_account_balance(player_name)
            buy_price = space.get_buy_price()
            player = self._players[player_name]
            if account_balance > buy_price:
                # Set player as owner of property space
                space.new_owner(player)
                # Subract buy price from player's account
                player.sub_account_balance(buy_price)
                return True
        return False

    def move_player(self, player_name, number_of_spaces):
        """Takes a player's name and the number of spaces to move as parameters. Moves player the appropriate amount of
        spaces and subtracts rent from balance if required. If the player passes GO, adds the funds to the player's
        account.

        :param player_name: name of player
        :param number_of_spaces: number of spaces player will move on gameboard

        :return: None if player is out of game or if number_of_spaces is outside specified range
        """
        player = self._players[player_name]

        # Player is no longer in the game.
        if player.get_account_balance() == 0:
            return

        # Number_of_spaces to move is outside the designated range
        if number_of_spaces < 1 or number_of_spaces > 6:
            return

        old_position = player.get_position()
        player.move_player(number_of_spaces, len(self._gameboard))
        new_position = player.get_position()

        # If player passed GO, add payout to account balance
        if new_position < old_position:
            go_payout = self._gameboard[0].get_payout_amount()
            player.add_account_balance(go_payout)

        # If player lands on GO space do not check space rent or ownership
        if self._gameboard[new_position].get_space_type() == "GO":
            return

        # Deduct property space rent from player's account if owned by another player
        current_property = self._gameboard[new_position]
        if current_property.get_owner() != player and current_property.get_owner() is not None:
            property_owner = current_property.get_owner()
            property_rent = current_property.get_rent()
            if player.get_account_balance() < property_rent:
                property_owner.add_account_balance(player.get_account_balance())
                self.remove_player(player)
            else:
                property_owner.add_account_balance(property_rent)
                player.sub_account_balance(property_rent)

    def check_game_over(self):
        """The game is over if all players but one have an account balance of zero. If the game is over, the method
        returns the winning player's name. Otherwise, returns an empty string.

        :return: Empty string if game is not over
        :return: Name of winning player if game is over
        """
        # Find and store player's not out in list
        players_not_out = []
        for player in self._players:
            account_balance = self.get_player_account_balance(player)
            if account_balance != 0:
                players_not_out.append(player)

        # Return winning player's name if only 1 player in list
        if len(players_not_out) == 1:
            return players_not_out[0]

        return ""

    def remove_player(self, player_obj):
        """Remove player from the game if they lose. This clears them as the owner of any property and sets their
        account balance to zero.

        :param player_obj: player object from the Player class

        :return: none
        """
        # set the player's account balance to zero
        player_obj.sub_account_balance(player_obj.get_account_balance())

        # remove the player as owner from any properties
        for space in self._gameboard:
            if space.get_space_type() == "Property" and space.get_owner() == player_obj:
                space.new_owner(None)


class Player:
    """
    Represents a player object in the game. Getters for account balance, position. Other methods for changing a player's
    position on the gameboard and changing account balance.
    """
    def __init__(self, name, account_balance):
        self._name = name
        self._account_balance = account_balance
        self._position = 0

    def get_account_balance(self):
        """ Returns player's account balance."""
        return self._account_balance

    def get_position(self):
        """Returns player's position on the gameboard."""
        return self._position

    def add_account_balance(self, amount):
        """Adds a specified amount to a player's account balance.

        :param amount: amount to be added to a player's account balance

        :return: none
        """
        self._account_balance += amount

    def sub_account_balance(self, amount):
        """Subtract a specified amount from a player's account balance.

        :param amount: amount to be subtracted from a player's account balance

        :return: none
        """
        # Check if subtracted amount would drop account balance below zero
        if amount - self._account_balance > 0:
            self._account_balance = 0
        else:
            self._account_balance -= amount

    def move_player(self, number_of_spaces, board_size):
        """Moves a player on a circular gameboard by a specified number of spaces.

        :param number_of_spaces: number of spaces to move player's position
        :param board_size: number of total spaces on the gameboard

        :return: none
        """
        self._position += number_of_spaces

        # Check if player has completed a full circle on the gameboard
        if self._position >= board_size:
            self._position = self._position - board_size


class BoardSpace:
    """
    Represents a space on the gameboard. BoardSpace objects should only be created through its subclasses PropertySpace
    and GoSpace. Contains a getter for a space's type.
    """
    def __init__(self, space_type):
        self._space_type = space_type

    def get_space_type(self):
        """Returns the space's type."""
        return self._space_type


class PropertySpace(BoardSpace):
    """
    Represents a property space in the game. PropertySpace subclass of BoardSpace with an additional parameter for rent.
    Getters for rent, buy price and owner. Setters for owner.
    """
    def __init__(self, space_type, rent):
        super().__init__(space_type)
        self._rent = rent
        self._owner = None

    def get_owner(self):
        """Returns the owner of the property space."""
        return self._owner

    def get_rent(self):
        """Return rent price of space."""
        return self._rent

    def get_buy_price(self):
        """Return buy price of the space.

        :return: property's rent * 5
        """
        # buy price is 5x the amount of rent
        buy_price = self._rent * 5
        return buy_price

    def new_owner(self, player_obj):
        """Set new player to owner of the property.

        :param player_obj: player object to be set as new property owner

        :return: none
        """
        self._owner = player_obj


class GoSpace(BoardSpace):
    """
    Represents a GO space on the gameboard. GoSpace subclass of BoardSpace with an additional parameter for GO space's
    payout amount. Getters for payout amount.
    """
    def __init__(self, space_type, payout_amount):
        super().__init__(space_type)
        self._payout_amount = payout_amount

    def get_payout_amount(self):
        """Returns the payout amount of the GO space."""
        return self._payout_amount


