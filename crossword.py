import filter


def solve_board(board):
	"""Takes a crossword board (a list of lists, each list representing a row, each element of each list being either ' ', a blank, or '#', a blocked square) and tries to return a board filled in with valid words. Takes an exceptionally long time for boards > ~7 square"""
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


def board_solved(board):
	"""checks to see if the board is solved."""
	for row in board:
		if ' ' in row:
			return False
	return True


def print_tests(board, solution_list, x):
	"""prints the state of the board & other indicators."""
	longest = ''
	y = 0
	for hsh in solution_list:
		if hsh.index(' ') > y:
			y = hsh.index(' ')
			longest = hsh
	print 'iteration: ', x
	print 'longest so far: ',y
	print 'best board so far: ', longest
	print_board(board)



def get_possible_letters(board):
	"""wrapper function for returning a list of possible moves for a particular board position in the form [a,b,c] such that the best letter is in position[0]"""
	
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



def hash_board_add_letter(board, letter):
	"""returns a string representation of the board with letter added in the first empty space. Used to check whether board + letter would result in a previously-tried board."""
	hsh = hash_board(board)
	indx = hsh.index(' ')
	hsh = hsh[:indx]+str(letter)+hsh[indx+1:]
	return hsh



def add_board_to_pos_list(board, pos_list):
	"""Adds the current board to the list of previous boards for which there was a choice of more than one letter."""
	container = []
	for row in board:
		container.append(row[:])
	pos_list.append(container)



def board_add_letter(board, letter):
	"""returns board with letter in next open space"""
	x,y = get_coords(board)
	board[x][y] = letter



def solution_list_add(board, solution_list):
	"""Adds the board to solution_list, which tracks boards that have been tried"""
	solution_list.append(hash_board(board))



def return_to_last_good_pos(board,pos_list,solution_list):
	"""returns the last board configuration in which there was a choice 
	of more than one letter."""
	for pos in reversed(pos_list):
		if hash_board(pos) not in solution_list:
			return pos


#-------------functions to navigate and comprehend the board----------------


def get_coords(board):
	"""returns tuple (x,y) of the coordinates of the first empty position on board."""
	for row in xrange(len(board)):
		try: return row, board[row].index(' ')
		except:pass



def hash_board(board):
	"""returns a string representation of the board. Used for keeping track of boards that have been tried."""
	hsh = ''
	for row in board:
		for letter in row:
			hsh += (str(letter))
	return hsh



def find_word(column_or_row, start_pos):
	"""returns the length and string of the word so far from a list representing the current column or row"""
	word = ''
	for x in xrange(len(column_or_row)):
		if column_or_row[x] == '#' and x < start_pos:
			word = ''
		elif column_or_row[x] == '#' and x > start_pos:
			return len(word), word.strip(' ')
		else: 
			word += str(column_or_row[x])
	return len(word), word.strip(' ')


def print_board(board):
	"""prints board to stdout"""
	rowstring = ''
	for row in board:
		rowstring = '['
		for item in row:
			rowstring += " '"+str(item)+"' "
		rowstring += ']\n'
		print rowstring



def get_column(board, column_number):
	"""returns a list representing the column_number column"""
	#print 'board', board
	column = []
	for row in board:
		column.append(row[column_number])
	return column

#----------------------functions to choose letters--------------------------


def get_moves_list(vert_string, horiz_string, vert_len, horiz_len):
	"""Checks to see whether this combo of strings and word lengths has been seen before. If yes, returns moves list from MOVES_LIST_DICT. If not, adds it to MOVES_LIST_DICT and returns it."""
	try: return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]
	except KeyError:
		add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len)
		return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]



def add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len):
	"""Gets two dicts of letters(a-z):score representing the across and down word possibilities, returns a sorted list hopefully with the best letters first. Needs work."""
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



def score_letters(s, length):
	"""Checks to see whether this beginning word string and target word length is already in WORDS_SHORTCUT_DICT. If so, returns it; if not, calls add_to_words_shortcut_dict, then returns it"""
	try: return WORDS_SHORTCUT_DICT[s,length]
	except KeyError: 
		add_to_words_shortcut_dict(s,length)
		return WORDS_SHORTCUT_DICT[s,length]



def add_to_words_shortcut_dict(s,length):
	"""adds a dict of letter(a-z):score to the WORDS_SHORTCUT_DICT for an existing-string/word-length pair."""
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



def score_secret_sauce(words_available, length):
	"""multiplies the score by proportion (total_words_of_length):(total_words) Generally a function for testing scoring methods."""
	score = words_available * RARITY_FACTOR[length - 1]
	return score


#----------------helper functions for building word lists-----------------


def get_words_of_length(x, word_list):
	"""takes list of words, returns list of words_of_length_x from original list."""
	words_of_length = []
	for word in word_list:
		if len(word) == x:
			words_of_length.append(word)
	return words_of_length



def build_word_lists_by_length(word_list):
	"""Turns word_list into a list of lists of words of length 
	'#'-len(longest word)"""
	word_lists_by_length = []
	longest_word_length = max(len(stn) for stn in word_list)
	for x in xrange(1,longest_word_length + 1):
		word_lists_by_length.append(get_words_of_length(x,word_list))
	return word_lists_by_length


#--------------------experimental function area--------------------------

#----------------global variable declarations-----------------------

#List of lists of words such that WORD_LISTS_BY_LENGTH[0] consists of words of 
#length 1, [1] consists of words of length 2, etc.

WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter.filter_words(filter.file_to_list()))
#del WORD_LISTS_BY_LENGTH[0][:] #the word list initially includes all single letters as words
WORD_LISTS_BY_LENGTH[0] = ['A','I','O']#replacing with just valid single-letter words.


#dict with entries in the form 
#[beginning_of_word_str, target_word_length]:{letters a-z:scores of letters}
#scores of letters should represent the usefulness of adding those letters to
#beginning_of_word_string when trying to end up with a word of target_word_length

WORDS_SHORTCUT_DICT = {}


#dict with entries in the form:
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

BOARDO = [[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ',' ',' ','#','#','#'],[' ',' ',' ','#',' ',' ',' ','#',' ',' ',' '],['#','#','#',' ',' ',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]
BOARDO = [[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' '],['#',' ',' ',' ','#',' '],[' ','#',' ',' ',' ','#'],[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' ']]

BOARD = [[' ',' ',' ',' ',' ',' '],['A',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ']]
BOARDO = [[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' ']]

#-------------------end global variable declarations-------------------

if __name__ =="__main__":
	board_prime = solve_board(BOARD)
