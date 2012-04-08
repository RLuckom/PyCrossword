import filter

#master function for solving a given board

def solve_board(board):
	solution_list = [] #list of previously-tried boards as str representations
	x= 0 #keeps track of # of times through loop
	pos_list = [] #list of previous boards in which there was a choice of adding more than one letter
	test_output_frequency = 50 # Determines frequency of output for testing	
	while not board_solved(board):

		#deciding whether to print output
		if x%test_output_frequency == 0:
			print_tests(board, solution_list, x)
		
		#getting a list of possible letters and initializing an empty list
		#to collect the subset of possible letters that haven't already
		#been tried in this board position
		possible_letters = get_possible_letters(board)
		best_letters = []
		
		#go through the list of possible letters to see if they've already
		#been tried
		for letter in possible_letters:
			if hash_board_add_letter(board,letter) not in solution_list:
				best_letters.append(letter)

		#If there's more than one possible letter that hasn't been tried,
		#add the best letter to the board AND save this position in pos_list
		#so we can come back to it if we hit a dead end
		if len(best_letters) > 1:
			add_board_to_pos_list(board,pos_list)
			board_add_letter(board, best_letters[0])

		#If there's only one possible letter that hasn't been tried, just add
		#that letter to the board.
		elif len(best_letters) == 1:
			board_add_letter(board,best_letters[0])

		#If there are no possible letters that have not been tried, add this
		#board to the list of previously-tried boards and return the board to 
		#the last position in which there was a choice of more than one letter
		else:
			solution_list_add(board, solution_list)
			board = return_to_last_good_pos(board,pos_list,solution_list)
			del best_letters[:]
		
		#increment counter
		x+=1
	print_board(board)

#------------functions called directly by solve_board--------------------

#checks to see if the board is solved.

def board_solved(board):
	for row in board:
		if ' ' in row:
			return False
	return True

#prints the state of the board & other indicators.

def print_tests(board, solution_list, x):
	longest = ''
	y = 0
	for hsh in solution_list:
		if hsh.index(' ') > y:
			y = hsh.index(' ')
			longest = hsh
	#if x == 0:
		#print find_supernodes(board)
		#print check_against_word_list('  h   i')
	print 'iteration: ', x
	print 'longest so far: ',y
	print 'best board so far: ', longest
	print_board(board)


#wrapper function for returning a list of possible moves for a particular 
#board position in the form [a,b,c] such that the best letter is in position[0]

def get_possible_letters(board):
	
	#getting the coordinates of the active letter
	row_index,vert_index = get_coords(board)
	
	#getting the length of the horizontal word and any letters already 
	#chosen
	horiz_len, horiz_string = find_word(board[row_index],vert_index)
	
	#using get_column to return the active column as a list.
	column = get_column(board, vert_index)
	
	#using the column list to get the length of the vertical word
	#and any letters already chosen
	vert_len, vert_string = find_word(column, row_index)
	
	#passing the strings and target word lengths to the function
	#that finds the possible letters.
	return get_moves_list(vert_string,horiz_string,vert_len,horiz_len)


#returns a string representation of the board with letter added in 
#the first empty space. Used to check whether board + letter would result
#in a previously-tried board.

def hash_board_add_letter(board, letter):
	hsh = hash_board(board)
	indx = hsh.index(' ')
	hsh = hsh[:indx]+str(letter)+hsh[indx+1:]
	return hsh


#Adds the current board to the list of previous boards for 
#which there was a choice of more than one letter.

def add_board_to_pos_list(board, pos_list):
	container = []
	for row in board:
		container.append(row[:])
	pos_list.append(container)


#returns board with letter in next open space

def board_add_letter(board, letter):
	x,y = get_coords(board)
	board[x][y] = letter


#Adds the board to solution_list, which tracks boards that have been tried

def solution_list_add(board, solution_list):
	solution_list.append(hash_board(board))


#returns the last board configuration in which there was a choice 
#of more than one letter.

def return_to_last_good_pos(board,pos_list,solution_list):
	for pos in reversed(pos_list):
		if hash_board(pos) not in solution_list:
			return pos


#-------------functions to navigate and comprehend the board----------------

#returns tuple (x,y) of the coordinates of the first empty position on board.

def get_coords(board):
	for row in xrange(len(board)):
		try: return row, board[row].index(' ')
		except:pass


#returns a string representation of the board. Used for keeping track of boards 
#that have been tried.

def hash_board(board):
	hsh = ''
	for row in board:
		for letter in row:
			hsh += (str(letter))
	return hsh


#returns the length and string of the word so far from a list representing the 
#current column or row

def find_word(column_or_row, start_pos):
	word = ''
	for x in xrange(len(column_or_row)):
		if column_or_row[x] == '#' and x < start_pos:
			word = ''
		elif column_or_row[x] == '#' and x > start_pos:
			return len(word), word.strip(' ')
		else: 
			word += str(column_or_row[x])
	return len(word), word.strip(' ')

#prints board to stdout

def print_board(board):
	rowstring = ''
	for row in board:
		rowstring = '['
		for item in row:
			rowstring += " '"+str(item)+"' "
		rowstring += ']\n'
		print rowstring


#returns a list representing the column_number column

def get_column(board, column_number):
	#print 'board', board
	column = []
	for row in board:
		column.append(row[column_number])
	return column

#----------------------functions to choose letters--------------------------

#Checks to see whether this combo of strings and word lengths has been
#seen before. If yes, returns moves list from MOVES_LIST_DICT. If not, 
#adds it to MOVES_LIST_DICT and returns it.

def get_moves_list(vert_string, horiz_string, vert_len, horiz_len):
	try: return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]
	except KeyError:
		add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len)
		return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]


#Gets two dicts of letters(a-z):score representing the across and down word
#possibilities, returns a sorted list hopefully with the best letters first. 
#Needs work.

def add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len):
	vert_dict = score_letters(vert_string, vert_len)
	horiz_dict = score_letters(horiz_string, horiz_len)
	moves_list = []
	to_return = []
	for letter in vert_dict:
		if vert_dict[letter] * horiz_dict[letter] > 0:
			moves_list.append([vert_dict[letter] + horiz_dict[letter],letter])
	moves_list.sort(reverse=True)
	for move in moves_list:
		to_return.append(move[1])
	MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len] = to_return


#Checks to see whether this beginning word string and target word length
#is already in WORDS_SHORTCUT_DICT. If so, returns it; if not, calls add_
#to_words_shortcut_dict, then returns it

def score_letters(s, length):
	try: return WORDS_SHORTCUT_DICT[s,length]
	except KeyError: 
		add_to_words_shortcut_dict(s,length)
		return WORDS_SHORTCUT_DICT[s,length]


#adds a dict of letter(a-z):score to the WORDS_SHORTCUT_DICT for an 
#existing-string/word-length pair.

def add_to_words_shortcut_dict(s,length):
	words_of_length = WORD_LISTS_BY_LENGTH[length - 1]
	letter_scores = {}
	candidate = ''
	words = 0
	for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
		words = 0
		candidate = s + letter
		for word in words_of_length:
			if word[0:len(candidate)] == candidate:
				words += 1
		letter_scores[letter] = score_secret_sauce(words,length)
	WORDS_SHORTCUT_DICT[s,length] = letter_scores


#multiplies the score by proportion (total_words_of_length):(total_words) 
#Generally a function for testing scoring methods.

def score_secret_sauce(words_available, length):
	score = words_available * RARITY_FACTOR[length - 1]
	return score


#----------------helper functions for building word lists-----------------

#takes list of words, returns list of words_of_length_x from original list.

def get_words_of_length(x, word_list):
	words_of_length = []
	for word in word_list:
		if len(word) == x:
			words_of_length.append(word)
	return words_of_length


#Turns word_list into a list of lists of words of length 
#'#'-len(longest word)

def build_word_lists_by_length(word_list):
	word_lists_by_length = []
	longest_word_length = max(len(stn) for stn in word_list)
	for x in xrange(1,longest_word_length + 1):
		word_lists_by_length.append(get_words_of_length(x,word_list))
	return word_lists_by_length

#--------------------experimental function area--------------------------

#the next idea is to find the squares on the board where the longest words
#meet, and try to add those words first. find_supernodes returns a sorted
#list of the coordinates with the most important nodes first.

def find_supernodes(board):
	coordinate_values = []
	for row in xrange(len(board)):
		for column in xrange(len(board[row])):
			if board[row][column] != '#':
				current_column = get_column(board, column)
				current_row = board[row]
				y_length = find_word(current_column, row)[0]
				x_length =  find_word(current_row, column)[0]
				if y_length > x_length:
					directional = 'v'
				else: directional = 'h'
				coordinate_values.append(((y_length + x_length),(row,column),directional))
	coordinate_values.sort(reverse=True)
	for element in xrange(len(coordinate_values)):
		coordinate_values[element] = coordinate_values[element][1],coordinate_values[element][2]
	return coordinate_values



def solve_board_use_your_words(board):
	nodes_in_order = find_supernodes(board)
	times = 0
	solution_list = []
	pos_list = []
	ctr = 0
	through_else = 0
	test_output_frequency = 50
	current_coordinate = nodes_in_order[0]
	while not board_solved(board):
		forward = True
		#deciding whether to print output
		coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])
		if ctr%test_output_frequency == 0:
			print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'prime')

		#checking to see what the spin is
		if current_coordinate[1] =='v':
			y_possibilities = check_against_word_list(find_just_word(get_column(current_coordinate[0][1],board),board))
			best_words = []
			for words in y_possibilities:
				if hash_board_add_vert_word(board, word,coord_ranges[1]) not in solution_list:
					best_words.append(word)
			#If there's more than one possible letter that hasn't been tried,
			#add the best letter to the board AND save this position in pos_list
			#so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_vert_word(board, best_words[0],coord_ranges[1])

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'y len > 1')

			#If there's only one possible letter that hasn't been tried, just add
			#that letter to the board.
			elif len(best_words) == 1:
				board_add_vert_word(board, best_words[0],coord_ranges[1])
			#If there are no possible letters that have not been tried, add this
			#board to the list of previously-tried boards and return the board to 
			#the last position in which there was a choice of more than one letter

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'y len == 1')
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)
				forward = False
				through_else += 1
				coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'y-else')
			del best_words [:]
			x_possibilities = check_against_word_list(find_just_word(board[current_coordinate[0][0]]),board)
			#print x_possibilities
			for words in x_possibilities:
				if hash_board_add_horiz_word(board, word, coord_ranges[0]) not in solution_list:
					best_words.append(word)
			#If there's more than one possible letter that hasn't been tried,
			#add the best letter to the board AND save this position in pos_list
			#so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_horiz_word(board, x_possibilities[0],coord_ranges[0])

			#If there's only one possible letter that hasn't been tried, just add
			#that letter to the board.

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'yx > 1')
			elif len(best_words) == 1:
				board_add_vert_word(board, y_possibilities[0],coord_ranges[0])
			#If there are no possible letters that have not been tried, add this
			#board to the list of previously-tried boards and return the board to 
			#the last position in which there was a choice of more than one letter
			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'yx =1')
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)

				coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])
				through_else += 1
				forward = False
			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'yx else')
			del best_words [:]
		else:
			#print 'hi'
			best_words = []
			x_possibilities = check_against_word_list(find_just_word(board[current_coordinate[0][0]],coord_ranges[0][0][1][0])[0])
			#print board[current_coordinate[0][0]]
			#print x_possibilities
			#print coord_ranges[0][0][1][0]
			for words in x_possibilities:
				if hash_board_add_horiz_word(board, words, coord_ranges[0]) not in solution_list:
					best_words.append(words)
			#If there's more than one possible letter that hasn't been tried,
			#add the best letter to the board AND save this position in pos_list
			#so we can come back to it if we hit a dead end
			#if ctr ==1:
			#	print best_words
			#print_board(board)
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_horiz_word(board, best_words[0],coord_ranges[0])

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'x > 1')
			#If there's only one possible letter that hasn't been tried, just add
			#that letter to the board.
			elif len(best_words) == 1:
				board_add_horiz_word(board, best_words[0],coord_ranges[0])
			#If there are no possible letters that have not been tried, add this
			#board to the list of previously-tried boards and return the board to 
			#the last position in which there was a choice of more than one letter
			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'x = 1')
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)
				forward = False
				coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])
				through_else += 1
			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'x else')
			del best_words [:]
			y_possibilities = check_against_word_list(find_just_word(get_column(board, current_coordinate[0][1]),coord_ranges[0][0][1][0])[0])
			#print coord_ranges, 'c'
			#print get_column(board,current_coordinate[0][1])
			coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])
			best_words = []
			for words in y_possibilities:
				if hash_board_add_vert_word(board, words,coord_ranges[1]) not in solution_list:
					best_words.append(words)
			#If there's more than one possible letter that hasn't been tried,
			#add the best letter to the board AND save this position in pos_list
			#so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_vert_word(board, best_words[0],coord_ranges[1])

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'xy > 1')
			#If there's only one possible letter that hasn't been tried, just add
			#that letter to the board.
			elif len(best_words) == 1:
				board_add_vert_word(board, best_words[0],coord_ranges[1])
			#If there are no possible letters that have not been tried, add this
			#board to the list of previously-tried boards and return the board to 
			#the last position in which there was a choice of more than one letter

			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'xy =1')
			else:
				solution_list_add(board, solution_list)
				through_else += 1
				forward = False
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)
			#	print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,coord_ranges, 'xy else')
				coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])
			del best_words [:]
		ctr += 1
		if forward == True:
			current_coordinate = nodes_in_order[nodes_in_order.index(current_coordinate)+1] 
			coord_ranges = coord_to_words_and_ranges(board, current_coordinate[0])

def print_tests_new(board, solution_list, x,forward,through_else, current_coordinates,coord_ranges,sent_by):
#	if board[4][3]=='A':
	print sent_by
	print 'iteration: ', x
	print 'coords: ',current_coordinates
	print 'coord_ranges: ',coord_ranges
	print 'forward = ', forward
	print 'through_else: ',through_else
	print_board(board)
	#print_board(board)


def hash_board_add_horiz_word(board,word,x_range_and_y):
	board_copy = get_board_copy(board)
	board_add_horiz_word(board_copy, word,x_range_and_y)
	return hash_board(board_copy)

def hash_board_add_vert_word(board,word,x_and_range):
	board_copy = get_board_copy(board)
	board_add_vert_word(board_copy, word,x_and_range)
	return hash_board(board_copy)
				
#Adds the current board to the list of previous boards for 
#which there was a choice of more than one letter.

def get_board_copy(board):
	container = []
	for row in board:
		container.append(row[:])
	return container

def add_board_and_coords_to_pos_list(board,pos_list,current_coordinate):
	board_copy = get_board_copy(board)
	entry = [board_copy,current_coordinate]
	pos_list.append(entry)

def return_to_last_good_pos_and_coords(board,pos_list,solution_list):
	for pos in reversed(pos_list):
		if hash_board(pos[0]) not in solution_list:
			return pos

#pass in a board & coordinates, get back tuple in which both elements
#are suited to call find intersecting words function.

def coord_to_words_and_ranges(board, coord):
	x_range = find_just_word(board[coord[0]],coord[1])
	y_range = find_just_word(get_column(board, coord[1]),coord[0])
	return (x_range, coord[0]),(coord[1],y_range)

#tests the effect of adding a horizontal word to the board

def test_add_horiz_word(c_to_w_r_x, word, board):
	words = find_horiz_intersecting_words(c_to_w_r_x, board)
	index_to_add_at = c_to_w_r_x[1] 
	for test_word in words:
		test_word = test_word[:index_to_add_at] + word[index_to_add_at] + test_word[index_to_add_at+1:]
	return score_word_list(words)

#tests the effect of adding a vertical word to the board

def test_add_vert_word(c_to_w_r_y, word, board):
	words = find_vert_intersecting_words(c_to_w_r_y, board)
	index_to_add_at = c_to_w_r_y[0] 
	for test_word in words:
		test_word = test_word[:index_to_add_at] + word[index_to_add_at] + test_word[index_to_add_at+1:]
	return score_word_list(words)

#specialized version of find_word that returns the whole word, including 
#whitespace, and its start and end positions in the row or column.

def find_just_word(column_or_row, start_pos): 
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
	return word, (word_start, word_end)


#takes a word-string, including whitespace, and returns a list of
#words that it could become.

def check_against_word_list(word):
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


#returns all the words that intersect a horizontal word

def find_horiz_intersecting_words(x_range,y, board):
	words = []
	for letter in xrange(x_range[0],x_range[1]+1):
		words.append(find_just_word(get_column(board, letter))[0],y)
	return words


#returns all the words that intersect a vertical word

def find_vert_intersecting_words(x, y_range, board):
	words = []
	for letter in xrange(y_range[0],y_range[1]+1):
		words.append(find_just_word(board[letter],x)[0])
	return words


#returns a cumulative score of the number of potential words that 
#could be made from a list of partially-completed words. Returns 
#zero if any of the partially-completed words cannot be made into words

def score_word_list(word_list):
	score = 0
	for word in word_list:
		pos_words =  len(check_against_word_list(word))
		if pos_words == 0:
			return 0
		score += pos_words
	return score


#adds a horizontal word to the board

def board_add_horiz_word(board, word,x_range_and_y):	
	y = x_range_and_y[1]
	x_range = x_range_and_y[0][1]
#	print 'y',y, 'x-range',x_range
	indx = 0
	for letter in xrange(x_range[0],x_range[1]+1):
		#print letter
		#print word
		board[y][letter] = word[indx]
		indx += 1

#adds a vertical word to the board

def board_add_vert_word(board, word,x_and_range):
	x = x_and_range[0]
	y_range = x_and_range[1][1]
	#print 'real', x_and_range
	indx = 0
	for letter in xrange(y_range[0],y_range[1]+1):
		board[letter][x] = word[indx]
		indx += 1



#----------------global variable declarations-----------------------

#List of lists of words such that WORD_LISTS_BY_LENGTH[0] consists of words of 
#length 1, [1] consists of words of length 2, etc.

WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter.filter_words(filter.file_to_list()))
del WORD_LISTS_BY_LENGTH[0][:] #the word list initially includes all single letters as words
WORD_LISTS_BY_LENGTH[0] = ['a','i','o']#replacing with just valid single-letter words.


#dict with entries in the form 
#[beginning_of_word_str, target_word_length]:{letters a-z:scores of letters}
#scores of letters should represent the usefulness of adding those letters to
#beginning_of_word_string when trying to end up with a word of target_word_length

WORDS_SHORTCUT_DICT = {}


#dict with entries in the form
#[vert_beginning_word_str, horiz_beginning_word_str, vert_target_word_length, horiz_target_word_length]:
#{letters_a-z:scores_of_letters}
#similar to WORDS_SHORTCUT_DICT, but keeps track of combinations of across and vertical
#strings/word lengths

MOVES_LIST_DICT = {}


#collecting some info about the distribution of words by length to make decisions
#about priority later on.

WORD_TOTAL = 0
WORDS_PER_LENGTH = []
for lst in WORD_LISTS_BY_LENGTH:
	WORDS_PER_LENGTH.append(len(lst))
	WORD_TOTAL += len(lst)


#calculating the reciprocal of words_of_length_x/total_words. So if 10%
#of total words are 7 letters, and 30% are 5 letters, letters that contribute
#to 7-letter words are scored higher than letters that contribute to 5-letter words.

RARITY_FACTOR = []
for total in WORDS_PER_LENGTH:
	RARITY_FACTOR.append(1-(float(total)/float(WORD_TOTAL)))

#several test boards. the board currently named BOARD is the board used

BOARD = [[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ',' ',' ','#','#','#'],[' ',' ',' ','#',' ',' ',' ','#',' ',' ',' '],['#','#','#',' ',' ',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]
BOARDO = [[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' '],['#',' ',' ',' ','#',' '],[' ','#',' ',' ',' ','#'],[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' ']]

BOARDO = [[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' ']]

#-------------------end global variable declarations-------------------

if __name__ =="__main__":
	board_prime = solve_board(BOARD)
