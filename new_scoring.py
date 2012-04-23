from new_crossword import *

def find_row_and_column_crossings(board):
	rows_and_columns_spaces = []
	for row in xrange(len(board)):
		if row == 0:
			for col in xrange(len(board[row])):
				column_number = 0
				column = get_column(board,col)
				for tile in column:
					if tile != '#':
						column_number += 1
				rows_and_columns_spaces.append((column_number, col, 'h'))
		row_number = 0
		for tile in board[row]:
			if tile != '#':
				row_number += 1
		rows_and_columns_spaces.append((row_number, row, 'v'))
	rows_and_columns_spaces.sort()
	return rows_and_columns_spaces

def get_coord_list_from_row_or_column(row_or_column, board):
	coords = []
	to_return = []
	position_of_constant_coord = 0
	position_of_changing_coord = 1
	split_row = board[row_or_column[0]]
	if row_or_column[1]=='h':
		position_of_constant_coord = 1
		position_of_changing_coord = 0
		split_row = get_column(board,row_or_column[0])
	for tile in xrange(len(split_row)):
		coords.append([0,0])
		coords[tile][position_of_constant_coord] = row_or_column[0]
		coords[tile][position_of_changing_coord] = tile
	for coord in coords:
		if board[coord[0]][coord[1]] != '#':
			to_return.append([(coord[0],coord[1]),row_or_column[1]])
	copy_of_first_coord = to_return[0][:]
	if copy_of_first_coord[1] == 'h':
		copy_of_first_coord[1] = 'v'
	else: copy_of_first_coord[1] = 'h'
	to_return.insert(0,copy_of_first_coord)
	return to_return

def solve_intersections(board,nodes_to_fill):
	pos_list = []  
	ctr = 0 #number of times through the loop
	through_else = 0 #number of times a word has not been found. Used only for debugging
	test_output_frequency = 1 #how often to print testing output
	current_coordinate = nodes_to_fill[0] #this gets managed inside the while loop later on
	best_words = []
	#Main loop
	while not board_solved(board):
		
		#forward is what determines whether to advance to the next coordinate upon completion.
		#the loop doesn't tightly control the order in which horizontal or vertical words 
		#get filled in, so forward is presumed to be False unless a test shows that the current
		#coordinate has valid horiz and vert words already
		forward = True


		#Some values we're going to need in a few places are the words associated with the coordinate
		#and the locations of the words in their row/column. The coord_to_words_and_ranges function gets
		#those values. 
		x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])

		#deciding whether to print output
		if ctr%test_output_frequency == 0:
			print_tests_new(board, ctr,forward,through_else,current_coordinate,'prime')


		#Each coordinate is in the form ((x-coord,y-coord), v-or-h) where the v or h indicates
		#whether to start with the vertical or horizontal word based on which is longer. I've written out
		#separate branches to fill in horizontal and vertical words, because
		#with vertical words the columns have to be arranged into lists.
		if current_coordinate[1] =='v':
			if y_word.find(' ') != -1:

				#if we're encountering this position for the first time, the best_words list will be empty
				#but if we're returning to this position we'll have the best_words list we generated last
				#time, with the next word to use at the end. This test determines whether to find the best
				#words for this position
				if best_words == []:
				

					#this gets a list of words that could be added to the current column without disturbing
					#any letters there already.
					y_possibilities = check_against_word_list(find_word_and_range(get_column(board, current_coordinate[0][1]),y_range[0])[0])
					

					#This is the current source of issues. I need to debug the functions meant to score 
					#the best_words list. The plan is to add the words to a
					#board and take the scores of the resulting several vertical/horizontal words
					#This has the disadvantage that, along with the complexity, it locks in the most 
					#important words on the board high up in the tree, where for large boards it will be
					#infeasible to expect to find better choices if the first ones don't work. However, by
					#forcing the program to fill in ALL the highly-connected nodes first, I hope that it will
					#minimize the number of letters per crash

					best_words = test_vert_letters(y_range,current_coordinate[0][1],board,y_possibilities)
				#If there's more than one possible word for this column that hasn't been tried,
				#add the best word to the column AND save this position and best_words list in pos_list
				#so we can come back to it if we hit a dead end
				if len(best_words) > 1:
					word_to_add = best_words.pop()
					add_board_and_coords_to_pos_list(board,pos_list,current_coordinate,best_words)
					board_add_vert_word(board, word_to_add,current_coordinate[0][1],y_range)
					x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
					del best_words[:]
					#print strings such as the following have as their last element an indication of which 
					#branch they come from, which is displayed for debugging.
					#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'y len > 1')

				#If there's only one possible word that hasn't been tried in this column, just add
				#that word to the column.
				elif len(best_words) == 1:
					word_to_add = best_words.pop()
					board_add_vert_word(board, word_to_add,current_coordinate[0][1],y_range)
					#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'y len == 1')
					x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
					del best_words[:]
				
				#If there are no possible words that have not been tried for this column, return the board 
				#and current_coordinate to the last position in which there was a choice of more than one 
				#word, and bring back the best_words list we had at that time.
				else:
					try:
						board, current_coordinate, best_words = pos_list.pop()
					except IndexError:
						return False
					x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
					forward = False
					through_else += 1

					#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'y-else')
				

		#This is the beginning of filling in the horizontal word.
		if current_coordinate[1] == 'h':
			if x_word.find(' ') != -1:
				#if we're encountering this position for the first time, the best_words list will be empty
				#but if we're returning to this position we'll have the best_words list we generated last
				#time, with the next word to use at the end. This test determines whether to find the best
				#words for this position
				if best_words == []:

					#finding words that could be placed in the current row without 
					#disturbing the letters already there.
					x_possibilities = check_against_word_list(find_word_and_range(board[current_coordinate[0][0]],x_range[0])[0])
			
			
					#This is the current source of issues. I need to debug the functions meant to score 
					#the best_words list. The plan is to add the words to a
					#board and take the scores of the resulting several vertical/horizontal words
					#This has the disadvantage that, along with the complexity, it locks in the most 
					#important words on the board high up in the tree, where for large boards it will be
					#infeasible to expect to find better choices if the first ones don't work. However, by
					#forcing the program to fill in ALL the highly-connected nodes first, I hope that it will
					#minimize the number of letters per crash
					best_words = test_horiz_letters(x_range,current_coordinate[0][0],board,x_possibilities)
				
				
				#If there's more than one possible word for this row that hasn't been tried,
				#add the best word to the column AND save this position and best_words list in pos_list
				#so we can come back to it if we hit a dead end
				if len(best_words) > 1:
					word_to_add = best_words.pop()
					add_board_and_coords_to_pos_list(board,pos_list,current_coordinate,best_words)
					board_add_horiz_word(board, word_to_add, current_coordinate[0][0], x_range)
					x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
					del best_words[:]
					#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'yx > 1')

				#If there's only one possible word that hasn't been tried in this row,
				#just add that letter to the board.
				elif len(best_words) == 1:
					word_to_add = best_words.pop()
					board_add_horiz_word(board, word_to_add, current_coordinate[0][0], x_range)
					del best_words[:]
					x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
					#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'yx =1')
				
				#If there are no possible words that have not been tried for this row, return the board 
				#and current_coordinate to the last position in which there was a choice of more than one 
				#word, and bring back the best_words list we had at that time.
				else:
					try:
						board, current_coordinate, best_words = pos_list.pop()
					except IndexError:
						return False
					x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
					forward = False
					through_else += 1

		
		ctr += 1
		#If somewhere in the last loop we completed the coordinate, we need to move to the next one
		if forward == True:
			try:
				current_coordinate = nodes_to_fill[nodes_to_fill.index(current_coordinate)+1] 
			except IndexError:
				return board
			x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])

def split_board(board,row_or_column):
	boards_to_return = [[],[]]
	if row_or_column[1] == 'h':
		new_board = []
		unrotated_board = [[],[]]
		for column in xrange(len(board[0])):
			new_board.append(get_column(board,column))
		unrotated_board[0] = list(new_board[:row_or_column[0]])
		unrotated_board[1] = list(new_board[row_or_column[0]:])
		for b in xrange(len(unrotated_board)):
			for column in xrange(len(unrotated_board[b][0])):
				boards_to_return[b].append(get_column(unrotated_board[b],column))
	else:
		boards_to_return[0] = list(board[:row_or_column[0]])
		boards_to_return[1] = list(board[row_or_column[0]:])
	for b in boards_to_return:
		print 'a board: '
		print_board(b)
	return boards_to_return

def stitch_boards(boards,v_or_h):
	for board in boards:
		if board == False:
			return False
	stitched_board = []
	if v_or_h == 'v':
		for row in boards[0]:
			stitched_board.append(row)
		for row in boards[1]:
			stitched_board.append(row)
		return stitched_board
	else:
		for row in xrange(len(boards[0])):
			stitched_board.append([])
			for tile in boards[0][row]:
				stitched_board[row].append(tile)
			for tile in boards[1][row]:
				stitched_board[row].append(tile)
	return stitched_board

def solve_board_recursive(board):
	if board_solved(board):
		return board
	else:
		split_lines = find_row_and_column_crossings(board)
		for line in split_lines:
			if line[1] != 0:
				split_line = line
				break
		row_or_column = (split_line[1],split_line[2])
		coords_to_fill = get_coord_list_from_row_or_column(row_or_column,board)
		board = solve_intersections(board, coords_to_fill)
		if not board:
			return False
		else:
			new_boards = split_board(board,row_or_column)
			return stitch_boards((solve_board_recursive(new_boards[0]),solve_board_recursive(new_boards[1])),row_or_column[1])

if __name__ == '__main__':
	#BOARD = [['S','C',' ','B','S'],['T','O',' ','A','L'],[' ',' ',' ',' ',' '],['R','O',' ','E','D'],['T','R',' ','S','S']]
	BOARD = [[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ',' ',' ','#','#','#'],[' ',' ',' ','#',' ',' ',' ','#',' ',' ',' '],['#','#','#',' ',' ',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]

	print solve_board_recursive(BOARD)
#	first = find_row_and_column_crossings(BOARD)[0]
#	row_or_column = (first[1],first[2])
#	row_or_column = (4,'v')
#	coords_to_fill = get_coord_list_from_row_or_column(row_or_column,BOARD)
#	print coords_to_fill
#	#board = solve_intersections(BOARD,coords_to_fill)
#	second = []
#	second_coords_to_fill = [[],[]]
#	new_boards = split_board(BOARD,row_or_column)
#	print_board(stitch_boards(new_boards,row_or_column[1]))
#	for b in new_boards:
#		print 'a board:\n'
#		print_board(b)
#		second.append(find_row_and_column_crossings(b)[0])
#	print second
#	for entry in xrange(len(second)):
#		second_coords_to_fill[entry] = get_coord_list_from_row_or_column((second[entry][1], second[entry][2]),new_boards[entry])
#	for b in xrange(len(new_boards)):
#		print_board(solve_intersections(new_boards[b],second_coords_to_fill[b]))
