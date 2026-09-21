from halma import *
from treelib import Tree
from PIL import Image, ImageDraw, ImageFont

def AI_Player_Team12(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:
    if player not in [1, 2, 3, 4]:
        raise ValueError(f"Player {player} is not a valid player")

    if len(board) != 5 or any(len(row) != 5 for row in board):
        raise ValueError("Board must be 5 by 5")

    def evaluate_position(board):
        # We use manhattan distance for this 
        scores = []
        for player in range(1, 5):
            target_cells = win_cells_all.get(player, [])
                
            player_score = 0
            for r in range(len(board)):
                for c in range(len(board[r])):
                    if board[r][c] == player:
                        min_dist = float('inf')
                        for target_r, target_c in target_cells:
                            dist = abs(r - target_r) + abs(c - target_c)
                            if dist < min_dist:
                                min_dist = dist
                        player_score -= min_dist
            scores.append(player_score)
        
        return tuple(scores)

    def get_all_legal_moves(local_board, local_player):
        legal_moves = []
        for row in range(5):
                for column in range(5):
                    if local_board[row][column] != local_player:
                        continue
        
                    oldPos: Tuple[int, int] = (row, column)
        
                    for new_row in range(5):
                        for new_column in range(5):
                            newPos: Tuple[int, int] = (new_row, new_column)
        
                            if check_legal_move(local_board, oldPos, newPos):
                                legal_moves.append((oldPos, newPos))
        return legal_moves

    def rank_potential_moves(position_board, current_player, moves):
        scored_moves = []
        for old_position, new_position in moves:
            temp_board = [row[:] for row in position_board]
            move(temp_board, old_position, new_position, current_player)
            scored_moves.append((evaluate_position(temp_board)[current_player - 1], (old_position, new_position)))

        scored_moves.sort(key=lambda item: item[0], reverse=True)
        return [m for _, m in scored_moves]

    # Every visited position is recorded as a node so the search tree can be printed afterwards.
    def new_tree_node(potential_move, moving_player):
        return {
            "move": potential_move,   # the move that leads to this node (None for the root)
            "player": moving_player,  # the player who made that move
            "scores": None,           # the (P1, P2, P3, P4) value backed up to this node
            "children": [],           # list of children nodes
            "best_child": None,       # the child whose value was chosen at this node
            "cached": False,          # True if the value was reused from tree_dict instead of searched
        }

    tree_dict = {}
    def max_n_algorithm(board, player, moves, depth, node):
        if not moves or depth == 0:
            node["scores"] = evaluate_position(board)
            return node["scores"]

        board_key = tuple(map(tuple, board))
        if (board_key, player, depth) in tree_dict:
            node["scores"] = tree_dict[(board_key, player, depth)]
            node["cached"] = True
            return node["scores"]

        best_scores = float("-inf"), float("-inf"), float("-inf"), float("-inf")

        next_player = player % 4 + 1
        
        for potential_move in moves:
            temp_board = [row[:] for row in board]
            move(temp_board, potential_move[0], potential_move[1], player)
            next_moves = get_all_legal_moves(temp_board, next_player)

            child = new_tree_node(potential_move, player)
            node["children"].append(child)
            scores = max_n_algorithm(temp_board, next_player, next_moves, depth - 1, child)

            if scores[player - 1] > best_scores[player - 1]:
                best_scores = scores
                node["best_child"] = child

        tree_dict[(board_key, player, depth)] = best_scores
        node["scores"] = best_scores
        return best_scores

    def format_move(potential_move):
        (old_row, old_column), (new_row, new_column) = potential_move
        return (
            chr(ord("A") + old_column) + str(old_row + 1)
            + "->"
            + chr(ord("A") + new_column) + str(new_row + 1)
        )

    def format_scores(scores):
        return "(" + ", ".join(f"{score:g}" for score in scores) + ")"

    tree_stats = {"nodes": 0, "leaves": 0, "cached": 0}
    def add_children_to_tree(node, tree, parent_id):
        # Copies the children of a search node into the treelib tree, one labelled treelib node each.
        for child in node["children"]:
            marker = "*" if child is node["best_child"] else " "
            tag = f"{marker} P{child['player']} {format_move(child['move'])}  {format_scores(child['scores'])}"

            tree_stats["nodes"] += 1
            if child["cached"]:
                tree_stats["cached"] += 1
                tag += "  [cached]"
            elif not child["children"]:
                tree_stats["leaves"] += 1

            tree_node = tree.create_node(tag, parent=parent_id)
            add_children_to_tree(child, tree, tree_node.identifier)
            
    def save_lines_as_png(lines, path):
        # The branches only line up in a monospace font; try the usual ones on macOS, Windows and Linux.
        font = None
        for font_name in ["Menlo.ttc", "Consolas.ttf", "DejaVuSansMono.ttf", "Courier New.ttf", "cour.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 15)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()

        text = "\n".join(lines)
        margin = 20
        line_spacing = 4
        measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        _, _, width, height = measure.multiline_textbbox((0, 0), text, font=font, spacing=line_spacing)

        image = Image.new("RGB", (width + 2 * margin, height + 2 * margin), "white")
        ImageDraw.Draw(image).multiline_text((margin, margin), text, font=font, fill="black", spacing=line_spacing)
        image.save(path)
    
    legal_moves = get_all_legal_moves(board, player)
    if not legal_moves:
        raise ValueError(f"Player {player} has no legal moves")
    ordered_legal_moves = rank_potential_moves(board, player, legal_moves)
    best_move = legal_moves[0]
    best_score = float("-inf")

    root = new_tree_node(None, None)
    root["scores"] = float("-inf"), float("-inf"), float("-inf"), float("-inf")

    search_depth = 2

    for potential_move in ordered_legal_moves:
        temp_board = [row[:] for row in board]
        move(temp_board, potential_move[0], potential_move[1], player)
        child = new_tree_node(potential_move, player)
        root["children"].append(child)
        next_player = player % 4 + 1
        candidate_score = max_n_algorithm(temp_board, next_player, get_all_legal_moves(temp_board, next_player), search_depth, child)[player - 1]

        if candidate_score > best_score:
            best_move = potential_move
            best_score = candidate_score
            root["best_child"] = child
            root["scores"] = child["scores"]

    oldPos, newPos = best_move

    if visualize_tree:
        tree = Tree()
        tree_root = tree.create_node(f"root  {format_scores(root['scores'])}")
        add_children_to_tree(root, tree, tree_root.identifier)

        lines = [
            f"=== Search tree: player {player} to move (max-n, {search_depth + 1} plies) ===",
            "Legend: 'P2 E5->D4' = player 2 moves E5 to D4, (a, b, c, d) = value for players 1-4,",
            "* = branch chosen by the player above it, [cached] = value reused from an earlier identical position",
            "",
        ]
        # sorting=False keeps the moves in search order instead of treelib's default alphabetical order.
        lines += tree.show(stdout=False, line_type="ascii", sorting=False).rstrip("\n").split("\n")
        lines += [
            "",
            f"Searched {tree_stats['nodes']} nodes ({tree_stats['leaves']} leaves, {tree_stats['cached']} cached). "
            f"Chosen move: P{player} {format_move(best_move)}",
        ]

        tree_png_path = "Team12_tree.png"
        save_lines_as_png(lines, tree_png_path)
        print(f"Search tree written to {tree_png_path}")

    old_reference: str = chr(ord("A") + oldPos[1]) + str(oldPos[0] + 1)
    new_reference: str = chr(ord("A") + newPos[1]) + str(newPos[0] + 1)

    return old_reference, new_reference