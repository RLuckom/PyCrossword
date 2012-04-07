#unused early recursive version. Exceeds max recursion depth in most cases.

def solve_board_recursive(board, solution_list):
	if board_solved(board):
		return board
	elif tried_all(board, solution_list):
		#print solution_list
		return solve_board(board_decrement(board),solution_list_add(board,solution_list))
	else:
		return solve_board(board_increment(board,solution_list),solution_list)


#returns True or False depending on whether all possible letters have been 
#tried. Only used by deprecated recursive version.

def tried_all(board, solution_list,best_letters):
	have_not_tried = len(best_letters)
	for letter in best_letters:
		if hash_board_add_letter(board,letter) in solution_list:
			have_not_tried -= 1
	if have_not_tried <= 0:
		return True
	return False
	

#not currently used function for deleting the last added letter

def board_decrement(board):
	last_good_point = [0,0]
	alpha = 'abcdefghijklmnopqrstuvwxyz'
	for row in xrange(len(board)):
		for letter in xrange(len(board[row])):
			if board[row][letter] == ' ':
				board[last_good_point[0]][last_good_point[1]] = 0
				return board
			elif str(board[row][letter]) in alpha:
				last_good_point[0], last_good_point[1] = row,letter


#wrapper function for finding and adding the best letter to the board

def board_increment(board, solution_list,best_letters):
	for letter in best_letters:
		if hash_board_add_letter(board,letter) not in solution_list:
			return board_add_letter(board,letter)




