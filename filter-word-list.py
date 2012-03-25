def file_to_list():
	text = open('words.txt', 'r')
	word_list = []
	for line in text:
		word_list.append(line.strip('\n'))
	return word_list

def filter_words(word_list):
	fair_words = []
	for word in word_list:
		if word.isalpha():
			fair_words.append(word)
	return fair_words

def find_longest(word_list):
	x = 0
	longest_word = ''
	for word in word_list:
		if len(word) > x:
			x = len(word)
			longest_word = word
	return x,longest_word

def get_words_of_length(x, word_list):
	words_of_length = []
	for word in word_list:
		if len(word) == x:
			words_of_length.append(word)
	return words_of_length

def build_word_lists_by_length(word_list):
	word_lists_by_length = []
	for x in xrange(1,23):
		word_lists_by_length.append(get_words_of_length(x,word_list))
	return word_lists_by_length

def score_letters(s, words_of_length):
	letter_scores = {}
	candidate = ''
	words = 0
	for letter in 'abcdefghijklmnopqrstuvwxyz':
		words = 0
		candidate = s + letter
		for word in words_of_length:
			if word[0:len(candidate)] == candidate:
				words += 1
		letter_scores[letter] = words
	#if s == '':
		#print letter_scores
	return letter_scores

def get_moves_list(vert_string, horiz_string, vert_len, horiz_len):
	#print vert_string, horiz_string, vert_len, horiz_len
	vert_dict = score_letters(vert_string, WORD_LISTS_BY_LENGTH[vert_len -1])
	horiz_dict = score_letters(horiz_string, WORD_LISTS_BY_LENGTH[horiz_len -1])
	#if vert_string == '' or horiz_string == '':
		#print vert_dict, horiz_dict
	moves_list = []
	to_return = []
	for letter in vert_dict:
		if vert_dict[letter] * horiz_dict[letter] > 0:
			moves_list.append([score_secret_sauce(vert_dict[letter], vert_len, horiz_dict[letter], horiz_len), letter])
	moves_list.sort(reverse=True)
	for move in moves_list:
		to_return.append(move[1])
	return to_return

def score_secret_sauce(vert_dict_score, vert_len, horiz_dict_score, horiz_len):
	vert_factor = vert_dict_score * RARITY_FACTOR[vert_len - 1]
	horiz_factor = horiz_dict_score * RARITY_FACTOR[horiz_len - 1]
	return vert_factor + horiz_factor

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

def solve_board(board, solution_list):
	if board_solved(board):
		return board
	elif tried_all(board, solution_list):
		#print solution_list
		return solve_board(board_decrement(board),solution_list_add(board,solution_list))
	else:
		return solve_board(board_increment_optimized(board,solution_list),solution_list)

def solve_board_not_recursive(board):
	solution_list = []
	x= 0
	y = 0
	while not board_solved(board):
		if x%50 == 0:
			for entry in solution_list:
				if entry.index('0')>y:
					y = entry.index('0')
			print 'iteration: ', x,'\n','longest so far: ',y,'\n',board
		if tried_all(board,solution_list):
			solution_list = solution_list_add(board, solution_list)
			board = board_decrement(board)	
			#print 'tried all ',solution_list
		board_increment_optimized(board,solution_list)
		x+=1
	return board

def board_solved(board):
	for row in board:
		for letter in row:
			if letter == 0:
				return False
	return True

def get_coords(board):
	for row in xrange(len(board)):
		try: return row, board[row].index(0)
		except:pass

def tried_all(board, solution_list):
	letters = get_best_letters(board)
	have_not_tried = len(letters)
	for letter in letters:
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

def board_increment_optimized(board, solution_list):
	for letter in get_best_letters(board):
		if hash_board_add_letter(board,letter) not in solution_list:
			return board_add_letter(board,letter)

WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter_words(file_to_list()))

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

solution_list = []
board_prime = solve_board_not_recursive(BOARD[:])

print board_prime


