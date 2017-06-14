# Let's import collections package for Counter
import collections


def cross(A, B):
    """
        Cross product of elements in A and elements in B.
        Args:
            A(string) - Left part.
            B(string) - Right part.
        Returns:
            An array with the cross product.
    """

    return [s + t for s in A for t in B]



assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

# for diagonal Sudoku implementation
diagonal_units = [[rows[i] + cols[i] for i in range(len(row_units))],
                  [rows[i] + cols[::-1][i] for i in range(len(row_units))]]

unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def set_units_peers(is_diagonal):
    """
        Set the values of the global variables: unitlist, units and peers.
        Args:
            is_diagonal(bool) - If the sudoku is diagonal or not.
    """

    global unitlist, units, peers
    unitlist = row_units + column_units + square_units + (diagonal_units if is_diagonal else [])

    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
        Assigns a value to a given box. If it updates the board record it.
        Args:
            values(dict) - The sudoku in dictionary form.
            box(string) - The key of the box.
            value(string) - The value of the box.
        Returns:
            The sudoku in dictionary form.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())

    return values


def grid_values(grid):
    """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        Args:
            grid(string) - A grid in string form.
        Returns:
            A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    all_digits = '123456789'

    if len(grid) != 81:
        raise ValueError("The length of the parameter must be 81")

    gridDict = dict()

    for item in zip(boxes, grid):
        gridDict[item[0]] = item[1] if item[1] != '.' else all_digits

    return gridDict


def display(values):
    """
        Display the values as a 2-D grid.
        Args:
            values(dict): The sudoku in dictionary form.
    """

    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def naked_twins(values):
    """
        Eliminate values using the naked twins strategy.
        Args:
            values(dict): a dictionary of the form {'box_name': '123456789', ...}.
        Returns:
            the values dictionary with the naked twins eliminated from peers.
    """

    stalled = False
    while not stalled:

        pre_solved_boxes = len([unit_key for unit_key in boxes if len(values[unit_key]) == 1])

        possible_twins = [unit_key for (unit_key, unit_value) in values.items() if len(unit_value) == 2]

        while len(possible_twins) > 1:

            x_key = possible_twins.pop()

            if len([k for k in peers[x_key] if values[k] == values[x_key]]) >= 1:

                x_value = values[x_key]

                for x_unit in units[x_key]:
                    if len([k for k in x_unit if values[k] == x_value]) > 1:
                        for box in x_unit:
                            if len(values[box]) > 1 and values[box] != x_value:
                                for digit in x_value:
                                    values = assign_value(values, box, values[box].replace(digit, ''))

        post_solved_boxes = len([unit_key for unit_key in boxes if len(values[unit_key]) == 1])

        stalled = pre_solved_boxes == post_solved_boxes

    return values


def eliminate(values):
    """
        Eliminate values from peers of each box with a single value.
            Go through all the boxes, and whenever there is a box with a single value,
            eliminate this value from the set of values of all its peers.
        Args:
            values: Sudoku in dictionary form.
        Returns:
            Resulting Sudoku in dictionary form after eliminating values.
    """

    solved_values = [box for box in boxes if len(values[box]) == 1]

    for box in solved_values:

        box_value = values[box]

        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(box_value, ''))

    return values


def only_choice(values):
    """
        Finalize all values that are the only choice for a unit.
            Go through all the units, and whenever there is a unit with a value
            that only fits in one box, assign the value to this box.
        Args:
            values(dict) - Sudoku in dictionary form.
        Returns:
            Resulting Sudoku in dictionary form after filling in only choices.
    """

    stalled = False
    while not stalled:

        solved_boxes_before = len([unit_key for unit_key in boxes if len(values[unit_key]) == 1])

        for unit in unitlist:

            all_unit_digits = {unit_key: unit_value for (unit_key, unit_value) in values.items() if
                               unit_key in unit and len(unit_value)}

            all_unit_digits_str = ''.join(all_unit_digits.values())

            digit_counter = {digit_key for (digit_key, digit_count) in collections.Counter(all_unit_digits_str).items()
                             if digit_count == 1}

            for digit_key in digit_counter:
                unit_keys = []
                for unit_key in unit:

                    if len(values[unit_key]) > 1 and values[unit_key].find(digit_key) > -1:
                        unit_keys.append(unit_key)

                    for u in unit_keys:
                        values = assign_value(values, u, digit_key)

        solved_boxes_after = len([unit_key for unit_key in boxes if len(values[unit_key]) == 1])

        stalled = solved_boxes_before == solved_boxes_after

    return values


def reduce_puzzle(values):
    """
        Eliminate the most possibilities as possible from sudoku boxes.
        Args:
            values(dict) - Sudoku in dictionary form.
        Returns:
            Resulting Sudoku in dictionary form.
    """

    stalled = False
    while not stalled:

        # Check how many boxes have a determined value
        solved_values_before = len([box for box in boxes if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in boxes if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """
        Using depth-first search and propagation, create a search tree and solve the sudoku.
        Args:
            values(dict) - Sudoku in dictionary form.
        Returns:
            Resulting Sudoku in dictionary form or False if there is no further solutions to look at.
    """

    # before search technique, reducing sudoky puzzle to applied elimination with only choice
    values = reduce_puzzle(values)

    if values is False:
        return False;
    if all(len(values[s]) == 1 for s in boxes):
        return values

    # choosing min of unfilled squares
    box_val_len, box_key = min([(len(values[s]), s) for s in boxes if (len(values[s]) > 1)])

    # go through each box in unit and applied recursive search
    for digit in values[box_key]:

        new_sudoku = values.copy()
        new_sudoku[box_key] = digit

        values_new_sudoku = search(new_sudoku)

        if values_new_sudoku:
            return values_new_sudoku


def solve(grid):
    """
        Find the solution to a Sudoku grid.
            Try to find the solution considering the sudoku diagonal, if no solution is found,
            it is made an attempt with non-diagonal sudoku approach.
        Args:
            grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
            The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = grid_values(grid)
    values = search(values)

    if values is False:
        set_units_peers(False)

        values = grid_values(grid)
        values = search(values)

        set_units_peers(True)
    return values



if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))


    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
