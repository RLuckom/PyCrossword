def file_to_list():
	'''opens the file 'words.txt' in containing folder and makes a list of the lines.'''
	text = open('words.txt', 'r')
	word_list = []
	for line in text:
		word_list.append(line.strip('\n'))
	return word_list

def filter_words(word_list):
	'''removes words including punctuation, numerals &c from word list.'''
	fair_words = []
	for word in word_list:
		if word.isalpha():
			fair_words.append(word)
	return fair_words

def get_words_of_length(x, word_list):
	'''takes list of words, returns list of words of length x from original list.'''
	words_of_length = []
	for word in word_list:
		if len(word) == x:
			words_of_length.append(word)
	return words_of_length

def build_word_lists_by_length(word_list):
	'''Turns word_list into a list of lists of words of length '#'-len(longest word)'''
	word_lists_by_length = []
	longest_word_length = max(len(stn) for stn in word_list)
	print longest_word_length
	for x in xrange(1,longest_word_length + 1):
		word_lists_by_length.append(get_words_of_length(x,word_list))
	return word_lists_by_length

def score_letters(s, length):
	'''takes a string and scores each letter a-z on how many words of arg length can be made by adding the letter to the string. returns dict of letter:score for a-z.'''
	try: return WORDS_SHORTCUT_DICT[s,length]
	except KeyError: 
		add_to_dict(s,length)
		return WORDS_SHORTCUT_DICT[s,length]

def add_to_dict(s,length):
	'''adds a dict of letter(a-z):score to the WORDS_SHORTCUT_DICT for an existing-string/word-length pair.'''
	words_of_length = WORD_LISTS_BY_LENGTH[length - 1]
	letter_scores = {}
	candidate = ''
	words = 0
	for letter in 'abcdefghijklmnopqrstuvwxyz':
		words = 0
		candidate = s + letter
		for word in words_of_length:
			if word[0:len(candidate)] == candidate:
				words += 1
		letter_scores[letter] = score_secret_sauce(words,length)
	WORDS_SHORTCUT_DICT[s,length] = letter_scores

def get_moves_list(vert_string, horiz_string, vert_len, horiz_len):
	'''Checks to see whether this combo of strings and word lengths has been seen before. If yes, returns moves list from MOVES_LIST_DICT. If not, adds it to MOVES_LIST_DICT and returns it.'''
	try: return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]
	except KeyError:
		add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len)
		return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]

def add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len):
	'''gets two dicts of letters(a-z):score representing the across and down words, returns a sorted list hopefully with the best letters first. Needs work.'''
	vert_dict = score_letters(vert_string, vert_len)
	horiz_dict = score_letters(horiz_string, horiz_len)
	#if vert_string == '' or horiz_string == '':
		#print vert_dict, horiz_dict
	moves_list = []
	to_return = []
	for letter in vert_dict:
		if vert_dict[letter] * horiz_dict[letter] > 0:
			moves_list.append([vert_dict[letter] + horiz_dict[letter],letter])
	moves_list.sort(reverse=True)
	for move in moves_list:
		to_return.append(move[1])
	MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len] = to_return

def score_secret_sauce(words_available, length):
	'''multiplies the score by proportion (total_words_of_length):(total_words) Generally a function for testing scoring methods.'''
	score = words_available * RARITY_FACTOR[length - 1]
	return score

def find_word(column_or_row, start_pos):
	'''returns the current word from a one-dimensional list of the current column or row'''
	word = ''
	for x in xrange(len(column_or_row)):
		if column_or_row[x] == '#' and x < start_pos:
			word = ''
		elif column_or_row[x] == '#' and x > start_pos:
			return len(word), word.strip(' ')
		else: 
			word += str(column_or_row[x])
	return len(word), word.strip(' ')

def get_best_letters(board):
	'''wrapper function for returning possible moves for a particular board position'''
	row_index,vert_index = get_coords(board)
	horiz_len, horiz_string = find_word(board[row_index],vert_index)
	column = []
	for row in board:
		column.append(row[vert_index])
	vert_len, vert_string = find_word(column, row_index)
	return get_moves_list(vert_string,horiz_string,vert_len,horiz_len)

def solve_board_recursive(board, solution_list):
	'''unused early recursive version. Exceeds max recursion depth in most cases.'''
	if board_solved(board):
		return board
	elif tried_all(board, solution_list):
		#print solution_list
		return solve_board(board_decrement(board),solution_list_add(board,solution_list))
	else:
		return solve_board(board_increment_optimized(board,solution_list),solution_list)

def solve_board(board):
	'''master function for solving a given board'''
	solution_list = []
	x= 0
	y = 0
	pos_list = []
	while not board_solved(board):
		if x%50 == 0: # following lines are output for testing
			print 'iteration: ', x
			for hsh in solution_list:
				if hsh.index(' ') > y:
					y = hsh.index(' ')
			print 'longest so far: ',y
			print_board(board)# end of section for printing output for testing
		possible_letters = get_best_letters(board)
		best_letters = []
		for letter in possible_letters:
			if hash_board_add_letter(board,letter) not in solution_list:
				best_letters.append(letter)
		if len(best_letters) > 1:
			pos_list = add_board_to_pos_list(board,pos_list)
			board_add_letter(board, best_letters[0])
		elif len(best_letters) == 1:
			board = board_add_letter(board,best_letters[0])
		else:
			solution_list = solution_list_add(board, solution_list)
			board = last_good_pos(board,pos_list,solution_list)
			del best_letters[:]
		x+=1
	print_board(board)

def last_good_pos(board,pos_list,solution_list):
	'''returns the last board configuration in which there was a choice of more than one letter'''
	for pos in reversed(pos_list):
		if hash_board(pos) not in solution_list:
			return pos

def add_board_to_pos_list(board, pos_list):
	'''Adds the current board to the list of previous boards.'''
	container = []
	for row in board:
		container.append(row[:])
	pos_list.append(container)
	return pos_list

def board_solved(board):
	'''checks to see if the board is solved'''
	for row in board:
		if ' ' in row:
			return False
	return True

def get_coords(board):
	'''returns tuple (x,y) of the coordinates of the first empty position on board.'''
	for row in xrange(len(board)):
		try: return row, board[row].index(' ')
		except:pass

def tried_all(board, solution_list,best_letters):
	'''returns True or False depending on whether all possible letters have been tried'''
	have_not_tried = len(best_letters)
	for letter in best_letters:
		if hash_board_add_letter(board,letter) in solution_list:
			have_not_tried -= 1
	if have_not_tried <= 0:
		return True
	return False
		
def board_decrement(board):
	'''not currently used function for deleting the last added letter'''
	last_good_point = [0,0]
	alpha = 'abcdefghijklmnopqrstuvwxyz'
	for row in xrange(len(board)):
		for letter in xrange(len(board[row])):
			if board[row][letter] == ' ':
				board[last_good_point[0]][last_good_point[1]] = 0
				return board
			elif str(board[row][letter]) in alpha:
				last_good_point[0], last_good_point[1] = row,letter

def solution_list_add(board, solution_list):
	'''adds the board to solution_list, which tracks boards that have been tried'''
	solution_list.append(hash_board(board))
	return solution_list

def hash_board(board):
	'''returns a string representation of the board'''
	hsh = ''
	for row in board:
		for letter in row:
			hsh += (str(letter))
	return hsh

def hash_board_add_letter(board, letter):
	'''returns a string representation of the board with letter added in the first empty space.'''
	hsh = hash_board(board)
	indx = hsh.index(' ')
	hsh = hsh[:indx]+str(letter)+hsh[indx+1:]
	return hsh

def board_add_letter(board, letter):
	'''adds letter to the first empty space on board'''
	x,y = get_coords(board)
	board[x][y] = letter
	return board

def board_increment_optimized(board, solution_list,best_letters):
	'''wrapper function for finding and adding the best letter to the board'''
	for letter in best_letters:
		if hash_board_add_letter(board,letter) not in solution_list:
			return board_add_letter(board,letter)

def print_board(board):
	'''prints board to stdout'''
	rowstring = ''
	for row in board:
		rowstring = '['
		for item in row:
			rowstring += " '"+str(item)+"' "
		rowstring += ']'
		print rowstring

WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter_words(file_to_list()))

WORDS_SHORTCUT_DICT = {}
MOVES_LIST_DICT = {}
del WORD_LISTS_BY_LENGTH[0][:]
WORD_LISTS_BY_LENGTH[0] = ['a','i','o']
WORD_TOTAL = 0
WORDS_PER_LENGTH = []
for lst in WORD_LISTS_BY_LENGTH:
	WORDS_PER_LENGTH.append(len(lst))
	WORD_TOTAL += len(lst)
 
RARITY_FACTOR = []

for total in WORDS_PER_LENGTH:
	RARITY_FACTOR.append(float(total)/float(WORD_TOTAL))

BOARD = [[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ',' ',' ','#','#','#'],[' ',' ',' ','#',' ',' ',' ','#',' ',' ',' '],['#','#','#',' ',' ',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]
BOARDO = [[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' '],['#',' ',' ',' ','#',' '],[' ','#',' ',' ',' ','#'],[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' ']]

BOARDL = [[' ','a',' ',' '],['e',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' ']]
#print WORD_LISTS_BY_LENGTH[' ']
#print 'htoe' in WORD_LISTS_BY_LENGTH[3]
TEST_LIST = []
TEST = []
solution_list = []
board_prime = solve_board(BOARD)

print board_prime



