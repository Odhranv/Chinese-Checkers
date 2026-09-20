from typing import Dict, List, NamedTuple, Tuple
import random

'''
Helper Class to contain the results
'''

class GameResult(NamedTuple):
    status: str
    winners: List[int]
    tied_players: List[int]
    losers: List[int]

'''
Initial board states for 1v1v1v1 and 1v1
'''
initial_pos: List[List[int]] = [
    [1,1,0,2,2],
    [1,0,0,0,2],
    [0,0,0,0,0],
    [4,0,0,0,3],
    [4,4,0,3,3]
]

initial_pos_1v1: List[List[int]] = [
    [1,1,0,0,0],
    [1,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,2],
    [0,0,0,2,2]
]


'''
Win cells per player for 1v1v1v1 and 1v1
'''
win_cells_all: Dict[int, List[Tuple[int, int]]] = {
    1: [(3, 4), (4, 3), (4, 4)],  # E4, D5, E5
    2: [(3, 0), (4, 0), (4, 1)],  # A4, A5, B5
    3: [(0, 0), (0, 1), (1, 0)],  # A1, B1, A2
    4: [(0, 3), (0, 4), (1, 4)]   # D1, E1, E2
}


win_cells_1v1: Dict[int, List[Tuple[int, int]]] = {
    1: [(3, 4), (4, 3), (4, 4)],  # E4, D5, E5
    2: [(0, 0), (0, 1), (1, 0)]   # A1, B1, A2
}

'''
Utility function to parse input string and transform it into Tuple
'''
def parse_position(position: str) -> Tuple[int, int]:
    position = position.strip().lower()

    if len(position) != 2:
        raise ValueError(
            f"Invalid position '{position}'. Expected something like 'a4'."
        )

    column_character: str = position[0]
    row_character: str = position[1]

    if column_character not in "abcde":
        raise ValueError("Column must be between 'a' and 'e'.")

    if row_character not in "12345":
        raise ValueError("Row must be between 1 and 5.")

    column: int = ord(column_character) - ord("a")
    row: int = int(row_character) - 1

    return row, column

'''
This function detects if the move is legal according to the rulles specified in the assignment
'''
def check_legal_move(
    board: List[List[int]],
    oldPos: Tuple[int, int],
    newPos: Tuple[int, int]
) -> bool:
    
    rest: Tuple[int, int] = tuple(
        map(lambda i, j: abs(i - j), oldPos, newPos)
    )

    # Only one piece may occupy a square.
    if board[newPos[0]][newPos[1]] != 0:
        return False

    # Move one square horizontally or vertically.
    if rest in [(0, 1), (1, 0)]:
        return True

    # Jump exactly two squares horizontally or vertically.
    if rest in [(0, 2), (2, 0)]:
        middlePos: Tuple[int, int] = (
            (oldPos[0] + newPos[0]) // 2,
            (oldPos[1] + newPos[1]) // 2
        )

        # Any piece, including an opponent's piece, may be jumped over.
        if board[middlePos[0]][middlePos[1]] != 0:
            return True

    return False

'''
This function executes the move, if it has been executed it will return True, if not False
'''
def move(
    board: List[List[int]],
    oldPos: Tuple[int, int],
    newPos: Tuple[int, int],
    player: int
) -> bool:
    try:
        assert player in [1, 2, 3, 4], \
            f"Player {player} is not a valid player"

        assert len(board) > 0 and len(board[0]) > 0, \
            "The board is empty"

        assert (
            0 <= oldPos[0] < len(board)
            and 0 <= oldPos[1] < len(board[oldPos[0]])
        ), "Old position is out of bounds"

        assert (
            0 <= newPos[0] < len(board)
            and 0 <= newPos[1] < len(board[newPos[0]])
        ), "New position is out of bounds"

        assert board[oldPos[0]][oldPos[1]] == player, \
            f"Player {player} selected a cell containing " \
            f"{board[oldPos[0]][oldPos[1]]}"

    except AssertionError as e:
        print(e)
        return False

    legal: bool = check_legal_move(board, oldPos, newPos)

    if not legal:
        return False

    board[newPos[0]][newPos[1]] = player
    board[oldPos[0]][oldPos[1]] = 0

    return True

'''
This Function checks for the win or tie conditions
'''
def check_win_condition(
    board: List[List[int]],
    move_count: int,
    maximum_move_limit: int,
    all_players: bool
) -> GameResult:
    if maximum_move_limit <= 0:
        raise ValueError("Maximum move limit must be greater than zero")

    if move_count < 0:
        raise ValueError("Move count cannot be negative")

    if all_players:
        win_cells: Dict[int, List[Tuple[int, int]]] = win_cells_all
    else:
        win_cells = win_cells_1v1

    active_players: List[int] = list(win_cells.keys())
    winners: List[int] = []

    # First check whether any player has reached their end zone.
    for player in active_players:
        player_has_won: bool = all(
            board[row][column] == player
            for row, column in win_cells[player]
        )

        if player_has_won:
            winners.append(player)

    if winners:
        return GameResult(
            status="winner",
            winners=winners,
            tied_players=[],
            losers=[
                player
                for player in active_players
                if player not in winners
            ]
        )

    # The game continues while the move limit has not been reached.
    if move_count < maximum_move_limit:
        return GameResult(
            status="ongoing",
            winners=[],
            tied_players=[],
            losers=[]
        )

    # The move limit has been reached.
    losers: List[int] = []

    for player in active_players:
        is_blocking: bool = False

        for other_player in active_players:
            if player == other_player:
                continue

            for row, column in win_cells[other_player]:
                if board[row][column] == player:
                    is_blocking = True
                    break

            if is_blocking:
                break

        if is_blocking:
            losers.append(player)

    tied_players: List[int] = [
        player
        for player in active_players
        if player not in losers
    ]

    return GameResult(
        status="move_limit",
        winners=[],
        tied_players=tied_players,
        losers=losers
    )
    

def random_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:
    if player not in [1, 2, 3, 4]:
        raise ValueError(f"Player {player} is not a valid player")

    if len(board) != 5 or any(len(row) != 5 for row in board):
        raise ValueError("Board must be 5 by 5")

    legal_moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

    for row in range(5):
        for column in range(5):
            if board[row][column] != player:
                continue

            oldPos: Tuple[int, int] = (row, column)

            for new_row in range(5):
                for new_column in range(5):
                    newPos: Tuple[int, int] = (new_row, new_column)

                    if check_legal_move(board, oldPos, newPos):
                        legal_moves.append((oldPos, newPos))

    if not legal_moves:
        raise ValueError(f"Player {player} has no legal moves")

    oldPos, newPos = random.choice(legal_moves)

    if visualize_tree:
        print("Random bot: no minimax search tree to visualize.")

    old_reference: str = chr(ord("A") + oldPos[1]) + str(oldPos[0] + 1)
    new_reference: str = chr(ord("A") + newPos[1]) + str(newPos[0] + 1)

    return old_reference, new_reference

def AI_Player_Team12(board: List[List[int]],
    player: int,
    visualize_tree: bool) -> Tuple[str, str]:
    if player not in [1, 2, 3, 4]:
        raise ValueError(f"Player {player} is not a valid player")

    if len(board) != 5 or any(len(row) != 5 for row in board):
        raise ValueError("Board must be 5 by 5")

    def evaluate_position(board: List[List[int]], player: int) -> int:
        #TODO: Noah, implement an evaluation function for the board state.
        # I just need this to return a number that represents how good the board state is for the given player.
        pass

    # We find all the legal moves (This is a copy of the algo for random_bot, but we put it inside a nested function)
    def get_legal_moves(
        position_board: List[List[int]],
        position_player: int
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        legal_moves = []
        for row in range(5):
                for column in range(5):
                    if board[row][column] != player:
                        continue
        
                    oldPos: Tuple[int, int] = (row, column)
        
                    for new_row in range(5):
                        for new_column in range(5):
                            newPos: Tuple[int, int] = (new_row, new_column)
        
                            if check_legal_move(board, oldPos, newPos):
                                legal_moves.append((oldPos, newPos))
        return legal_moves

    def order_moves(
        position_board: List[List[int]],
        position_player: int,
        moves: List[Tuple[Tuple[int, int], Tuple[int, int]]],
        root_player: int,
        maximizing: bool
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        scored_moves = []
        for old_position, new_position in moves:
            child_board = [row[:] for row in position_board]
            move(child_board, old_position, new_position, position_player)
            scored_moves.append((
                evaluate_position(child_board, root_player),
                (old_position, new_position)
            ))

        scored_moves.sort(key=lambda item: item[0], reverse=maximizing)
        return [move_item for _, move_item in scored_moves]

    transposition_table: Dict[
        Tuple[Tuple[Tuple[int, ...], ...], int, int, int], float
    ] = {}

    def max_n(
        position_board: List[List[int]],
        current_player: int,
        remaining_depth: int,
        moves: List[Tuple[Tuple[int, int], Tuple[int, int]]],
        root_player: int,
        alpha: float,
        beta: float
    ) -> float:
        if remaining_depth == 0 or not moves:
            return evaluate_position(position_board, root_player)

        position_key = (
            tuple(tuple(row) for row in position_board),
            current_player,
            remaining_depth,
            root_player,
        )
        cached_score = transposition_table.get(position_key)
        if cached_score is not None:
            return cached_score

        next_player = current_player % 4 + 1
        maximizing = current_player == root_player
        best_score = float("-inf") if maximizing else float("inf")
        fully_searched = True

        ordered_moves = order_moves(
            position_board,
            current_player,
            moves,
            root_player,
            maximizing
        )

        for old_position, new_position in ordered_moves:
            child_board = [row[:] for row in position_board]
            move(child_board, old_position, new_position, current_player)

            score = max_n(
                child_board,
                next_player,
                remaining_depth - 1,
                get_legal_moves(child_board, next_player),
                root_player,
                alpha,
                beta
            )

            if maximizing:
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
            else:
                best_score = min(best_score, score)
                beta = min(beta, best_score)

            if alpha >= beta:
                fully_searched = False
                break

        if fully_searched:
            transposition_table[position_key] = best_score

        return best_score

    legal_moves = get_legal_moves(board, player)
    if not legal_moves:
        raise ValueError(f"Player {player} has no legal moves")

    best_move = legal_moves[0]
    best_score = float("-inf")

    ordered_legal_moves = order_moves(
        board,
        player,
        legal_moves,
        player,
        True
    )

    for candidate_move in ordered_legal_moves:
        child_board = [row[:] for row in board]
        move(child_board, candidate_move[0], candidate_move[1], player)
        candidate_score = max_n(
            child_board,
            player % 4 + 1,
            search_depth - 1,
            get_legal_moves(child_board, player % 4 + 1),
            player,
            best_score,
            float("inf")
        )

        if candidate_score > best_score:
            best_move = candidate_move
            best_score = candidate_score

    oldPos, newPos = best_move

    if visualize_tree:
        pass #TODO: Noah, implement minimax search tree visualization here.

    old_reference: str = chr(ord("A") + oldPos[1]) + str(oldPos[0] + 1)
    new_reference: str = chr(ord("A") + newPos[1]) + str(newPos[0] + 1)

    return old_reference, new_reference
    

def illegal_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:
    if player not in [1, 2, 3, 4]:
        raise ValueError(f"Player {player} is not valid")

    for row in range(5):
        for column in range(5):
            if board[row][column] == player:
                position: str = (
                    chr(ord("A") + column)
                    + str(row + 1)
                )

                if visualize_tree:
                    print(
                        f"Illegal bot attempts: "
                        f"{position} -> {position}"
                    )

                return position, position

    raise ValueError(f"Player {player} has no pieces")