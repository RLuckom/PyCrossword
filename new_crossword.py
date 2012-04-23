#--------------------------import statements-------------------------

import filter
#----------------------------Description----------------------------
'''
I've started thinking a new way about this problem. Before, I was 
scoring individual letters, moving through the problem space a tiny bit
at a time. I was trying a lot of words, but I wasn't trying a very wide
variety of boards; instead, I was trying a lot of different boards
that had the same first and second lines. For each letter I put down early,
I spent a lot of time before I changed it, without any way fix it if 
it became a problem.

This time, I want to focus on eliminating as wide a variety of potential 
boards as I can with as few letters as possible. That way I'll hopefully
move across the problem space more quickly, and only explore solutions
if they have a chance of success. 

To do that, I've started out by prioritizing the squares on the board 
based on the raw number of other blank squares in their horizontal
and vertical words. It turns out that there are many ties (usually 
multiples of four) but I haven't worried about that yet, because groups
of four nodes with like scores tend to be situated on groups of four
words arranged in a square at the center of the board, which is usually
the highest-connected part of the board.

Basically, the idea is to take the nodes in order of 'importance' and 
fill in their entire vertical and horizontal words, scoring them based on
their effect on the board, as measured by the number of possible attaching
words they leave open. Obviously, if the introduction of any word would
make it impossible to form a valid attaching word, we can retreat from
that position. My hope is that this scoring method, and the fact of the
order of the nodes from highest importance to lowest importance, will
tend to generate crashes for boards that would not have worked much more
quickly than the previous algorithm.
'''
#--------------------------master function--------------------------

def solve_board_use_your_words(board):
	nodes_in_order = find_supernodes(board) #order in which to try to complete coords
	#nodes_in_order = get_nodes_in_order(board)
	#list of boards representing positions where there was a choice of adding several words, 
	#as well as the specific coordinate that was being solved(including whether it was working 
	#on the vertical or horizontal word) and the list of words left to try
	pos_list = []  
	
	ctr = 0 #number of times through the loop
	through_else = 0 #number of times a word has not been found. Used only for debugging
	test_output_frequency = 1 #how often to print testing output
	current_coordinate = nodes_in_order[0] #this gets managed inside the while loop later on
	best_words = []
	#Main loop
	while not board_solved(board):
		
		#forward is what determines whether to advance to the next coordinate upon completion.
		#the loop doesn't tightly control the order in which horizontal or vertical words 
		#get filled in, so forward is presumed to be False unless a test shows that the current
		#coordinate has valid horiz and vert words already
		forward = False


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
				board, current_coordinate, best_words = pos_list.pop()
				through_else += 1
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
				#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'y-else')
			

		#check to see if the coordinate is all filled out. If so, we set forward to True.
		#Note that this doesn't prevent it filling in the horiz word--but because that 
		#is already a valid word, the function will just replace it with itself
		#This is an opportunity for some optimization, but shouldn't introduce problems.
		if is_filled(board,x_word,y_word):
			forward = True
		
		
		#This is the beginning of filling in the horizontal word.
		if current_coordinate[1] == 'h':
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
				current_coordinate[1] = 'v'
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
				del best_words[:]
				#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'yx > 1')

			#If there's only one possible word that hasn't been tried in this row,
			#just add that letter to the board.
			elif len(best_words) == 1:
				word_to_add = best_words.pop()
				board_add_horiz_word(board, word_to_add, current_coordinate[0][0], x_range)
				current_coordinate[1] = 'v'
				del best_words[:]
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
				#print_tests_new(board, ctr,forward,through_else,current_coordinate, 'yx =1')
			
			#If there are no possible words that have not been tried for this row, return the board 
			#and current_coordinate to the last position in which there was a choice of more than one 
			#word, and bring back the best_words list we had at that time.
			else:
				board, current_coordinate, best_words = pos_list.pop()
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
				through_else += 1

		#check to see if the coordinate is completed
		if is_filled(board,x_word,y_word):
			forward = True

		
		ctr += 1
		#If somewhere in the last loop we completed the coordinate, we need to move to the next one
		if forward == True:
			try:
				current_coordinate = nodes_in_order[nodes_in_order.index(current_coordinate)+1] 
			except ValueError:
				if current_coordinate[1] == 'h':
					current_coordinate[1] = 'v'
				elif current_coordinate[1] == 'v':
					current_coordinate[1] ='h'
				current_coordinate = nodes_in_order[nodes_in_order.index(current_coordinate)+1] 
			x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
	print_board(board)


#------------------functions called directly by master----------------



def find_supernodes(board):
	"""returns a sorted list of the coordinates with the most important nodes first and an 'h' or 'v' next to indicate whether the longer word off the node is the horizontal or vertical one. defaults to h in a tie."""
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
				coordinate_values.append([(y_length + x_length),(row,column),directional])
	coordinate_values.sort(reverse=True)
	for element in xrange(len(coordinate_values)):
		coordinate_values[element] = [coordinate_values[element][1],coordinate_values[element][2]]
	return coordinate_values


def get_nodes_in_order(board):
	nodes = []
	for row in xrange(len(board)):
		for letter in xrange(len(board[row])):
			if board[row][letter] != '#':
				nodes.append([(row,letter),'h'])
				nodes.append([(row,letter),'v'])
	return nodes

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
#	if board[4][3]=='A':
	print sent_by
	print 'iteration: ', x
	print 'coords: ',current_coordinates
	print 'coord_ranges: '
	print 'forward = ', forward
	print 'through_else: ',through_else
	print_board(board)

def check_against_word_list(word):
	"""takes a word-string, including whitespace, and returns a list of words that it could become."""
	#print 'word ', word
	valid_words = []
	num_letters = len(word)
	#print len(word), word
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


#---------------functions to navigate & comprehend the board-------------

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

#--------------------------scoring functions----------------------------

def is_filled(board, x_word, y_word):
	"""checks to see if the vert and horiz words associated with a coord are filled already"""
	return False if x_word not in WORD_LISTS_BY_LENGTH[len(x_word)-1] or y_word not in WORD_LISTS_BY_LENGTH[len(y_word)-1] else True

def test_horiz_letters(x_range,y,board,best_words):
	"""likely a source of problems. Takes a board and target word-space, and identifies and ranks the words that could go there based on how many intersecting words they would leave open. Returns a list of those words with the best word last, for use with list.pop()"""
	list_of_letters_dicts = []
	board_copy = (get_board_copy(board))
	word_list_in_order  = []
	to_return = []
	for space in xrange(x_range[0],x_range[1]+1):
		new_dict = {}
		if board[y][space] != ' ':
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				new_dict[letter] = 0
			new_dict[board[y][space]] = 1
		else:
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				board_copy[y][space] = letter
				new_dict[letter] = len(check_against_word_list(find_word_and_range(get_column(board_copy,space),y)[0]))
		list_of_letters_dicts.append(new_dict)
	for word in best_words:
		word_score = 0
		#print word
		for letter in xrange(len(word)):
			letter_score = list_of_letters_dicts[letter][word[letter]]
			if letter_score == 0:
				word_score = 0
				break
			else:
				word_score += letter_score
		word_list_in_order.append([word_score,word])
		#print 'word: ',word,'word score: ',word_score#,'letter: ',letter
	#print word_list_in_order
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
		if board[space][x] != ' ':
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				new_dict[letter] = 0
			new_dict[board[space][x]] = 1
		else:
			for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
				board_copy[space][x] = letter
				new_dict[letter] = len(check_against_word_list(find_word_and_range(board_copy[space],x)[0]))
		list_of_letters_dicts.append(new_dict)
	#print 'board copy: ', print_board(board_copy), list_of_letters_dicts 
	for word in best_words:
		word_score = 0
		#print word
		for letter in xrange(len(word)):
			letter_score = list_of_letters_dicts[letter][word[letter]]
			if letter_score == 0:
				word_score = 0
				break
			else:
				word_score += letter_score
		word_list_in_order.append([word_score,word])
	word_list_in_order.sort()
	#print word_list_in_order
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



#----------------global variable declarations-----------------------

#List of lists of words such that WORD_LISTS_BY_LENGTH[0] consists of words of 
#length 1, [1] consists of words of length 2, etc.

WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter.filter_words(filter.file_to_list()))
del WORD_LISTS_BY_LENGTH[0][:] #the word list initially includes all single letters as words
WORD_LISTS_BY_LENGTH[0] = ['A','I','O']#replacing with just valid single-letter words.

#several test boards. the board currently named BOARD is the board used
words = 0
for word_list in WORD_LISTS_BY_LENGTH:
	words += len(word_list)

BOARD = [[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ','#',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ',' ',' ','#','#','#'],[' ',' ',' ','#',' ',' ',' ','#',' ',' ',' '],['#','#','#',' ',' ',' ',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ','#',' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],[' ',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]

BOARDO = [[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' '],['#',' ',' ',' ','#',' '],[' ','#',' ',' ',' ','#'],[' ',' ',' ','#',' ',' '],[' ',' ','#',' ',' ',' ']]

BOARDO = [[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' ']]

#-------------------end global variable declarations-------------------

if __name__ =="__main__":
	print "I have ",words,"words."
	print "I have ",len(WORD_LISTS_BY_LENGTH[7]),"eight-letter words."
	board_prime = solve_board_use_your_words(BOARD)
