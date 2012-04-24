#--------------------------import statements-------------------------
import filter
#----------------------------Description----------------------------
'''
This solution is designed to break the board into smaller sub-boards
that can be solved concurrently.

The basic idea is to pick the row or column with the fewest white spaces,
solve the words that cross those white spaces perpendicularly to the row
or column, and then split the board at that row or column. So in the board:

[' ',' ',' ',' ',' ',' ']

[' ',' ',' ',' ',' ',' ']

[' ',' ',' ',' ',' ',' ']

['#','#','#','#','#','#']

[' ',' ',' ',' ',' ',' ']

[' ',' ',' ',' ',' ',' ']

It is obviously trivial to solve the top and bottom half separately. But
in the board

[' ',' ',' ',' ',' ',' ']

[' ',' ',' ',' ',' ',' ']

[' ',' ',' ',' ',' ',' ']

['#','#',' ','#','#','#']

[' ',' ',' ',' ',' ',' ']

[' ',' ',' ',' ',' ',' ']

it is still possible to split the halves apart after solving the one 
'down' word that connects them; we can insert

[' ',' ','F',' ',' ',' ']

[' ',' ','R',' ',' ',' ']

[' ',' ','A',' ',' ',' ']

['#','#','M','#','#','#']

[' ',' ','E',' ',' ',' ']

[' ',' ','S',' ',' ',' ']

and then solve the boards:

[' ',' ','F',' ',' ',' ']

[' ',' ','R',' ',' ',' ']

[' ',' ','A',' ',' ',' ']

and 

['#','#','M','#','#','#']

[' ',' ','E',' ',' ',' ']

[' ',' ','S',' ',' ',' ']

because there's no communication between those boards that hasn't already
been settled. We just need to figure out whether one of those boards is
unsolvable, because if it is we need to redo the connecting word and re-solve
both of them (unless there's a way to change only the part of the connecting
word that enters into one territory or the other while keeping it a valid word,
which is something I'm still thinking about).

Another property of this method is that in a board without any black tiles,
solving the words necessary to break the board in half means filling in the entire
board. Therefore it is not necessary to have any 'fill in the rest' step--the
entire board will be filled in just by recursively trying to break it down into 
smaller boards, then recombining them when they are solved.

The idea is to try to break the board down into sub-boards and allow those boards
to more-or-less-intelligently 'report' back to the subprocess controlling the 
intersection. Ideally, it would be possible for a subprocess to request a change 
only to the part of the intersection that was on its territory, so for instance
in the boards:

[' ',' ','F',' ',' ',' ']

[' ',' ','R',' ',' ',' ']

[' ',' ','A',' ',' ',' ']

and 

['#','#','M','#','#','#']

[' ',' ','E',' ',' ',' ']

[' ',' ','S',' ',' ',' ']

if the first board turned out to be unsolvable, it could ask the higher-level process
for a new word, and become:

[' ',' ','B',' ',' ',' ']

[' ',' ','L',' ',' ',' ']

[' ',' ','A',' ',' ',' ']

without requiring that the other sub-board be changed. Obviously this would be more
and more difficult with boards involving more intersecting and interdependent words.

TODO:

What is still needed is a strategy for controlling the solution-in-progress, facilitating
communication between the sub-boards and controlling the areas of the board shared by more
than one sub-process such that we don't waste work by throwing out too much progress
when one sub-board fails, but also that we don't keep working on a solution after any
sub-board has found a fatal flaw.

Finally, some potential issues:

The biggest issue I've found so far is that I have had to modify the word-scoring
algorithms as they deal with existing letters. You can see that in one of
the sub-boards above, the "word" 'FRA' appears. To avoid errors, it is necessary
to rewrite the scoring function so that if it encounters a word with no
blank spaces, it treats that word as valid without looking it up in the word list.
I am relatively confident that I haven't screwed anything up, but there's always
a chance. Those changes are in the test_horiz_letters and test_vert_letters functions.

Another issue concerns the changes that I made to the original solving algorithm, now
called solve_intersections. Extensive changes were necessary to get it to solve
only the words on a single line and then return the board. I do not consider this
worth too much effort, because I anticipate rewriting the whole function as part of 
a more intelligent way to control the subprocesses responsible for solving the sub-boards 
at each step.
'''
#--------------------------master functions-------------------------------
def solve_board_recursive(board):
	"""Not an actual working recursion--just used to test the functionality of the helper functions. It has no way to deal with boards that cannot be solved, and instead returns False all the way up the recursion when it hits a dead end."""
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


#------------------functions called directly by master--------------------
def board_solved(board):
	"""checks to see if the board has no empty spaces. Does not validate words."""
	for row in board:
		if ' ' in row:
			return False
	return True

def coord_to_words_and_ranges(board, coord):
	"""Takes a board and coord and returns x_word, x_range, y_word, y_range"""
	x_word, x_range = find_word_and_range(board[coord[0]],coord[1])
	y_word, y_range = find_word_and_range(get_column(board, coord[1]),coord[0])
	return x_word,x_range,y_word,y_range


def print_tests_new(board, x,forward,through_else, current_coordinates,sent_by):
	"""prints args for debugging"""
	print sent_by
	print 'iteration: ', x
	print 'coords: ',current_coordinates
	print 'coord_ranges: '
	print 'forward = ', forward
	print 'through_else: ',through_else
	print_board(board)

def check_against_word_list(word):
	"""takes a word-string, including whitespace, and returns a list of words that it could become."""
	valid_words = []
	num_letters = len(word)
	for mot in WORD_LISTS_BY_LENGTH[len(word)-1]:
		same = True
		for letter in xrange(num_letters):
			if word[letter] != ' ':
				if mot[letter] != word[letter]:
					same = False
		if same == True:
			valid_words.append(mot)
	return valid_words

def find_word_and_range(column_or_row, start_pos): 
	"""returns the whole word, including whitespace, and its start and end positions in the row or column."""
	word = ''
	word_start = 0
	word_end = len(column_or_row)-1
	for x in xrange(len(column_or_row)):
		if column_or_row[x] == '#' and x < start_pos:
			word = ''
			word_start = x+1
		elif column_or_row[x] == '#' and x > start_pos:
			word_end = x-1
			return word, (word_start, word_end)
		else: 
			word += str(column_or_row[x])
	
	#print column_or_row, [word], (word_start, word_end)
	return word, (word_start, word_end)

def get_column(board, column_number):
	"""returns a list representing the column_number column"""
	#print 'board', board
	column = []
	for row in board:
		column.append(row[column_number])
	return column

def add_board_and_coords_to_pos_list(board,pos_list,current_coordinate,best_words):
	"""Adds the current board to the list of previous boards for which there was a choice of more than one letter."""
	board_copy = get_board_copy(board)
	best_words_copy = best_words[:]
	current_coordinate_copy = current_coordinate[:]
	entry = [board_copy,current_coordinate_copy,best_words_copy]
	pos_list.append(entry)

def board_add_horiz_word(board, word,y_coord,x_range):	
	"""adds a horizontal word to the board"""
	indx = 0
	for letter in xrange(x_range[0],x_range[1]+1):
		#print letter
		#print word
		#print indx
		#print x_range
		board[y_coord][letter] = word[indx]
		indx += 1

def board_add_vert_word(board, word,x,y_range):
	"""adds a vertical word to the board"""
	indx = 0
	for letter in xrange(y_range[0],y_range[1]+1):
		board[letter][x] = word[indx]
		indx += 1

def get_coord_list_from_row_or_column(row_or_column, board):
	"""takes a board and a row_or_column identifier tuple in the format that comes from find_row_and_column_crossings and returns a list of coords that can be solved in order by solve_intersections to prepare the board to be split"""
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
	#This next part basically says: first, solve the word that lies
	#ALONG (as opposed to across) the row or column to split. My idea
	#in writing it was that it might be easier to control the overall 
	#solution to the intersection by controlling that word, and on
	#the test board it had the effect of increasing speed (could easily
	#be an artifact though). I am overall skeptical of whether this is a 
	#good idea.
	copy_of_first_coord = to_return[0][:]
	if copy_of_first_coord[1] == 'h':
		copy_of_first_coord[1] = 'v'
	else: copy_of_first_coord[1] = 'h'
	to_return.insert(0,copy_of_first_coord)
	#End of potentially problematic code
	return to_return

def split_board(board,row_or_column):
	"""splits the board into sub-boards along the row or column identified by the row_or_column identifier. boards are returned in a list of two elements."""
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

def find_row_and_column_crossings(board):
	"""takes a board, and returns a list of rows and columns to break it at, with each entry in the format (score, row_or_column_number, h_or_v) where h represents a column and v represents a row because rows get solved as vertical words and columns get solved as horizontal words"""
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

def stitch_boards(boards,v_or_h):
	"""Takes two boards and the last element from the row_or_column identifier used to split them and recombines them into a single board"""
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


#---------------functions to navigate & comprehend the board--------------

def print_board(board):
	"""prints board to stdout"""
	rowstring = ''
	for row in board:
		rowstring = '['
		for item in row:
			rowstring += " '"+str(item)+"' "
		rowstring += ']\n'
		print rowstring


def find_word(column_or_row, start_pos):
	"""returns the length and string of the word so far from a list representing the current column or row word"""
	word = ''
	for x in xrange(len(column_or_row)):
		if column_or_row[x] == '#' and x < start_pos:
			word = ''
		elif column_or_row[x] == '#' and x > start_pos:
			return len(word), word.strip(' ')
		else: 
			word += str(column_or_row[x])
	return len(word), word.strip(' ')


def get_board_copy(board):
	"""returns a copy of the board to functions that have side effects"""
	container = []
	for row in board:
		container.append(row[:])
	return container


#----------------helper functions for building word lists-----------------

def get_words_of_length(x, word_list):
	"""takes list of words, returns list of words_of_length_x from original list."""
	words_of_length = []
	for word in word_list:
		if len(word) == x:
			words_of_length.append(word)
	return words_of_length


def build_word_lists_by_length(word_list):
	"""Turns word_list into a list of lists of words of length '#'-len(longest word)"""
	word_lists_by_length = []
	longest_word_length = max(len(stn) for stn in word_list)
	for x in xrange(1,longest_word_length + 1):
		word_lists_by_length.append(get_words_of_length(x,word_list))
	return word_lists_by_length

#--------------------------scoring functions------------------------------

def test_horiz_letters(x_range,y,board,best_words):
	"""likely a source of problems. Takes a board and target word-space, and identifies and ranks the words that could go there based on how many intersecting words they would leave open. Returns a list of those words with the best word last, for use with list.pop()"""
	list_of_letters_dicts = []
	board_copy = (get_board_copy(board))
	word_list_in_order  = []
	to_return = []
	for space in xrange(x_range[0],x_range[1]+1):
		new_dict = {}
		#This is what I added to account for the fact that certain letters will
		#be found on the board that are already part of partial-words not found 
		#in the word list. If those spaces had scores of zero, the board would
		#treat that as a dead end. This solution causes the board to treat any letter
		#already on the board as a correct letter that cannot be replaced by
		#any other letter.
		if board[y][space] != ' ':
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				new_dict[letter] = 0
			new_dict[board[y][space]] = 1
		#This is the beginning of the regular code for assigning values to the letters
		#for each space
		else:
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				board_copy[y][space] = letter
				new_dict[letter] = len(check_against_word_list(find_word_and_range(get_column(board_copy,space),y)[0]))
		list_of_letters_dicts.append(new_dict)
	for word in best_words:
		word_score = 0
		for letter in xrange(len(word)):
			letter_score = list_of_letters_dicts[letter][word[letter]]
			if letter_score == 0:
				word_score = 0
				break
			else:
				word_score += letter_score
		word_list_in_order.append([word_score,word])
	word_list_in_order.sort()
	for elem in word_list_in_order:
		if elem[0] != 0:
			to_return.append(elem[1])
	return to_return

def test_vert_letters(y_range,x,board,best_words):
	"""likely a source of problems. Takes a board and target word-space, and identifies and ranks the words that could go there based on how many intersecting words they would leave open. Returns a list of those words with the best word last, for use with list.pop()"""
	list_of_letters_dicts = []
	board_copy = (get_board_copy(board))
	word_list_in_order  = []
	to_return = []
	for space in xrange(y_range[0],y_range[1]+1):
		new_dict = {}
		#This is analogous to the commented portion of the test_horiz_letters function
		if board[space][x] != ' ':
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				new_dict[letter] = 0
			new_dict[board[space][x]] = 1
		#End modified code
		else:
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				board_copy[space][x] = letter
				new_dict[letter] = len(check_against_word_list(find_word_and_range(board_copy[space],x)[0]))
		list_of_letters_dicts.append(new_dict)
	for word in best_words:
		word_score = 0
		for letter in xrange(len(word)):
			letter_score = list_of_letters_dicts[letter][word[letter]]
			if letter_score == 0:
				word_score = 0
				break
			else:
				word_score += letter_score
		word_list_in_order.append([word_score,word])
	word_list_in_order.sort()
	for elem in word_list_in_order:
		if elem[0] != 0:
			to_return.append(elem[1])
	return to_return

def find_horiz_intersecting_words(x_range,y, board):
	"""returns all the words that intersect a horizontal word."""
	words = []
	for letter in xrange(x_range[0],x_range[1]+1):
		words.append(get_column(board, letter))
	return words


def find_vert_intersecting_words(y_range, x, board):
	"""returns all the words that intersect a vertical word."""
	words = []
	for letter in xrange(y_range[0],y_range[1]+1):
		words.append(board[letter])
	return words


def score_word_list(word_list):
	"""returns a cumulative score of the number of potential words that could be made from a list of partially-completed words. Returns zero if any of the partially-completed words cannot be made into words."""
	score = 0
	for word in word_list:
		pos_words =  len(check_against_word_list(word))
		if pos_words == 0:
		#print word, check_against_word_list(word)
			return 0
		score += pos_words
	return score


#-------------------------Start function-------------------------

if __name__ == '__main__':
	#BOARD = [['S','C',' ','B','S'],['T','O',' ','A','L'],[' ',' ',' ',' ',' '],['R','O',' ','E','D'],['T','R',' ','S','S']]
	BOARD = [[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ',' ',' ','#','#','#'],[' ',' ',' ','#',' ',' ',' ','#',' ',' ',' '],['#','#','#',' ',' ',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]
	WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter.filter_words(filter.file_to_list()))
	del WORD_LISTS_BY_LENGTH[0][:] #the word list initially includes all single letters as words
	WORD_LISTS_BY_LENGTH[0] = ['A','I','O']#replacing with just valid single-letter words.
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
