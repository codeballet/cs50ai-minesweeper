import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # Remove cell from sentence and decrease count
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # Remove cell from sentence
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def mark_cells(self, changed):
        print('inside mark_cells')
        # Mark cells as mines or safes
        if not changed:
            return None

        changed = False

        for sentence in self.knowledge:
            # Check for mines
            check_mines = sentence.known_mines()
            if check_mines:
                fcheck_mines = frozenset(check_mines)
                if len(fcheck_mines) != 0:
                    for mine in fcheck_mines:
                        self.mark_mine(mine)
                    changed = True
            # Check for safes
            check_safes = sentence.known_safes()
            if check_safes:
                fcheck_safes = frozenset(check_safes)
                if len(fcheck_safes) != 0:
                    for safe in fcheck_safes:
                        self.mark_safe(safe)
                    changed = True

        # Check if new sentences can be inferred from existing knowledge
        self.infer_knowledge(changed)


    def infer_knowledge(self, changed):
        print('inside infer_knowledge')
        if not changed:
            return None

        changed = False
        subset_found = False
        changed_sentences = []

        for sentence1 in self.knowledge:
            print(f'sentence1: {sentence1}')
            for sentence2 in self.knowledge:
                print(f'sentence2: {sentence2}')
                if sentence2 != sentence1:
                    if sentence2.cells.issubset(sentence1.cells):
                        subset_found = True
                        # Create a new set from the difference
                        new_set =  sentence1.cells.difference(sentence2.cells)

                        # Adjust the count for the new set
                        new_count = sentence1.count - sentence2.count

                        # Add new sentence to knowledge
                        new_sentence = Sentence(new_set, new_count)
                        self.knowledge.append(new_sentence)

            if subset_found:
                # Register changed sentence
                changed_sentences.append(sentence1)

                # Change to knowledge has been made
                changed = True

        # Remove changed sentences
        for sentence in changed_sentences:
            if sentence in self.knowledge:
                self.knowledge.remove(sentence)

        # Check for new cells to mark
        self.mark_cells(changed)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # raise NotImplementedError
        
        # 1. Mark cell as move made
        self.moves_made.add(cell)

        # 2. Mark cell as safe
        self.mark_safe(cell)

        # 3. Add new sentence to knowledge base
        # 3.1 Create a set for nearby cells
        nearby_cells = []

        # 3.2 Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] +2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore already determined cells
                if (i,j) in self.moves_made or (i,j) in self.mines or (i,j) in self.safes:
                    continue
                
                # add cell in bounds to new_set
                if 0 <=i < self.height and 0<= j < self.width:
                    nearby_cells.append((i, j))

        # 3.3 Append sentence to knowledge base with set and count
        self.knowledge.append(Sentence(nearby_cells, count))

        # 4. Mark additional cells as safe or as mines and, recursively:
        # 5. Check if new sentences can be inferred from existing knowledge
        self.mark_cells(True)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Get a list of all available safe cells
        safe_list = []

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in self.safes and (i, j) not in self.moves_made and (i, j) not in self.mines:
                    safe_list.append((i, j))

        # Return randomly selected safe move or None
        if len(safe_list) != 0:
            return random.choice(safe_list)
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Get a list of all cells not already chosen and not mines
        random_list = []

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    random_list.append((i, j))

        # Return randomly selected move from list
        return random.choice(random_list)