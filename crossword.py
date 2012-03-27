def file_to_list():
	'''
	opens file 'words.txt' in containing folder and makes a list of the lines.
	'''
	text = open('words_new.txt', 'r')
	word_list = []
	for line in text:
		word_list.append(line.strip('\n'))
	return word_list

def filter_words(word_list):
	'''
	removes words including punctuation, numerals &c from word list.
	'''
	fair_words = []
	for word in word_list:
		if word.isalpha():
			fair_words.append(word)
	return fair_words

def get_words_of_length(x, word_list):
	'''
	takes list of words, returns list of words of length x from original list.
	'''
	words_of_length = []
	for word in word_list:
		if len(word) == x:
			words_of_length.append(word)
	return words_of_length

def build_word_lists_by_length(word_list):
	'''
	Turns word_list into a list of lists of words of length 1-len(longest word)
	'''
	word_lists_by_length = []
	longest_word_length = max(len(stn) for stn in word_list)
	print longest_word_length
	for x in xrange(1,longest_word_length + 1):
		word_lists_by_length.append(get_words_of_length(x,word_list))
	return word_lists_by_length

def score_letters(s, length):
	'''
	takes a string and scores each letter a-z on how many words of arg length can be made by adding the letter to the string. returns dict of letter:score for a-z.
	'''
	try: return WORDS_SHORTCUT_DICT[s,length]
	except KeyError: 
		add_to_dict(s,length)
		return WORDS_SHORTCUT_DICT[s,length]

def add_to_dict(s,length):
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
	try: return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]
	except KeyError:
		add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len)
		return MOVES_LIST_DICT[vert_string, horiz_string, vert_len, horiz_len]

def add_to_moves_list_dict(vert_string, horiz_string, vert_len, horiz_len):
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
	score = words_available * RARITY_FACTOR[length - 1]
	return score

def find_word(column_or_row, start_pos):
	word = ''
	for x in xrange(len(column_or_row)):
		if column_or_row[x] == 1 and x < start_pos:
			word = ''
		elif column_or_row[x] == 1 and x > start_pos:
			return len(word), word.strip('0')
		else: 
			word += str(column_or_row[x])
	return len(word), word.strip('0')

def get_best_letters(board):
	row_index,vert_index = get_coords(board)
	horiz_len, horiz_string = find_word(board[row_index],vert_index)
	column = []
	for row in board:
		column.append(row[vert_index])
	vert_len, vert_string = find_word(column, row_index)
	return get_moves_list(vert_string,horiz_string,vert_len,horiz_len)

def solve_board_recursive(board, solution_list):
	if board_solved(board):
		return board
	elif tried_all(board, solution_list):
		#print solution_list
		return solve_board(board_decrement(board),solution_list_add(board,solution_list))
	else:
		return solve_board(board_increment_optimized(board,solution_list),solution_list)

def solve_board(board):
	solution_list = []
	x= 0
	while not board_solved(board):
		if x%50 == 0:
			print 'iteration: ', x 
			print_board(board)
		if tried_all(board,solution_list, get_best_letters(board)):
			solution_list = solution_list_add(board, solution_list)
			board = board_decrement(board)	
			#print 'tried all ',solution_list
		board_increment_optimized(board,solution_list,get_best_letters(board))
		x+=1
	return board

def board_solved(board):
	for row in board:
		if 0 in row:
			return False
	return True

def get_coords(board):
	for row in xrange(len(board)):
		try: return row, board[row].index(0)
		except:pass

def tried_all(board, solution_list,best_letters):
	have_not_tried = len(best_letters)
	for letter in best_letters:
		if hash_board_add_letter(board,letter) in solution_list:
			have_not_tried -= 1
	if have_not_tried <= 0:
		return True
	return False
		
def board_decrement(board):
	last_good_point = [0,0]
	alpha = 'abcdefghijklmnopqrstuvwxyz'
	for row in xrange(len(board)):
		for letter in xrange(len(board[row])):
			if board[row][letter] == 0:
				board[last_good_point[0]][last_good_point[1]] = 0
				return board
			elif str(board[row][letter]) in alpha:
				last_good_point[0], last_good_point[1] = row,letter

def solution_list_add(board, solution_list):
	solution_list.append(hash_board(board))
	return solution_list

def hash_board(board):
	hsh = ''
	for row in board:
		for letter in row:
			hsh += (str(letter))
	return hsh

def hash_board_add_letter(board, letter):
	hsh = hash_board(board)
	indx = hsh.index('0')
	hsh = hsh[:indx]+str(letter)+hsh[indx+1:]
	return hsh

def board_add_letter(board, letter):
	x,y = get_coords(board)
	board[x][y] = letter
	return board

def board_increment_optimized(board, solution_list,best_letters):
	for letter in best_letters:
		if hash_board_add_letter(board,letter) not in solution_list:
			return board_add_letter(board,letter)

def print_board(board):
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

WORDS_PER_LENGTH = []
for lst in WORD_LISTS_BY_LENGTH:
	WORDS_PER_LENGTH.append(len(lst))
 
RARITY_FACTOR = []

for total in WORDS_PER_LENGTH:
	RARITY_FACTOR.append(int(20000/total))

BOARD = [[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,1,1,1],[0,0,0,1,0,0,0,1,0,0,0],[1,1,1,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0]]
BOARDO = [[0,0,0,1,0,0],[0,0,1,0,0,0],[1,0,0,0,1,0],[0,1,0,0,0,1],[0,0,0,1,0,0],[0,0,1,0,0,0]]

BOARDL = [['k',0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
#print WORD_LISTS_BY_LENGTH[0]
#print 'htoe' in WORD_LISTS_BY_LENGTH[3]
TEST_LIST = []
TEST = []
solution_list = []
board_prime = solve_board(BOARD)

print board_prime



