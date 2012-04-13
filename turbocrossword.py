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
the highest-connected part of the moard.

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
	solution_list = []  #list to keep hashes of previously-tried boards
	pos_list = []   #list of boards representing positions where there was a choice of adding several words
	ctr = 0 #number of times through the loop
	through_else = 0 #number of times a word has not been found. Used only for debugging
	test_output_frequency = 1 #how often to print testing output
	current_coordinate = nodes_in_order[0] #this gets managed inside the while loop later on
	#Main loop
	while not board_solved(board):
		
		#forward is what determines whether to advance to the next coordinate upon completion.
		#If we haven't found a word, we're going to move to an older coordinate as part of the
		#process of resetting the board, and we don't want to then advance one coordinate forward
		#when we get to the end of the loop, so forward gets set to False if we reset.
		forward = True


		#Some values we're going to need in a few places are the words associated with the coordinate
		#and the locations of the words in their row/column. The coord_to_words_and_ranges function gets
		#those values. 
		x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])

		#deciding whether to print output
		if ctr%test_output_frequency == 0:
			print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate,'prime')


		#Each coordinate is in the form ((x-coord,y-coord), v-or-h) where the v or h indicates
		#whether to start with the vertical or horizontal word based on which is longer. I've written out
		#two full branches to handle both cases. That might have been a terrible idea, as I have to remember to 
		#fix bugs in both places.
		if current_coordinate[1] =='v':


			#Initializing an empty list to hold the words that have not been tried
			best_words = []
			

			#this gets a list of words that could be added to the current column without disturbing
			#any letters there already.
			y_possibilities = check_against_word_list(find_word_and_range(get_column(board, current_coordinate[0][1]),y_range[0])[0])
			

			#looks through the possible words and adds those that haven't been tried 
			#to best_words
			for words in y_possibilities:
				if hash_board_add_vert_word(board, words,current_coordinate[0][1],y_range) not in solution_list:
					best_words.append(words)


			#This is the current source of issues. I need to debug the functions meant to sort 
			#the best_words list in place based on a scoring system. The plan is to add the words to a
			#board and take the scores of the resulting several vertical/horizontal words
			#This has the disadvantage that, along with the complexity, it locks in the most 
			#important words on the board high up in the tree, where for large boards it will be
			#infeasible to expect to find better choices if the first ones don't work. However, by
			#forcing the program to fill in ALL the highly-connected nodes first, I hope that it will
			#miniimize the number of letters per crash. Anyway, that should go here.
			#sort_best_vert_words_by_score(best_words,board,y_range,current_coordinate[0][1])
			best_words = test_vert_letters(y_range,current_coordinate[0][1],board,best_words)


			#If there's more than one possible word for this column that hasn't been tried,
			#add the best word to the column AND save this position in pos_list
			#so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_vert_word(board, best_words[0],current_coordinate[0][1],y_range)
			
			
			#print strings such as the following have as their last element an indication of which 
			#branch they come from, which is displayed for debugging.
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'y len > 1')

			#If there's only one possible word that hasn't been tried in this column, just add
			#that word to the column.
			elif len(best_words) == 1:
				board_add_vert_word(board, best_words[0],current_coordinate[0][1],y_range)
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'y len == 1')
			
			#If there are no possible words that have not been tried for this column, add this
			#board to the list of previously-tried boards and return the board and current_coordinate
			#to the last position in which there was a choice of more than one word.
			#AND set forward to False so we don't increment the coordinate list at 
			#the end of the loop.
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)
				forward = False
				through_else += 1
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])

				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'y-else')
			

			#This is the beginning of filling in the horizontal word. First we 
			#empty out the best_words list so we can use it again.
			del best_words [:]

			
			#finding words that could be placed in the current row without 
			#disturbing the letters already there.
			x_possibilities = check_against_word_list(find_word_and_range(board[current_coordinate[0][0]],x_range[0])[0])
			
			
			#Checking the words in the list of possibilities to see if they've
			#already been used.
			for words in x_possibilities:
				if hash_board_add_horiz_word(board, words, current_coordinate[0][0], x_range) not in solution_list:
					best_words.append(words)


			#Again, this is where someone paying more attention would've scored
			#the words.	
			#sort_best_horiz_words_by_score(best_words,board,x_range,current_coordinate[0][0])
			best_words = test_horiz_letters(x_range,current_coordinate[0][0],board,best_words)
			

			#If there's more than one possible word for this row that hasn't 
			#been tried, add the best word to the row AND save this position 
			#in pos_list so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_horiz_word(board, best_words[0],current_coordinate[0][0], x_range)


			#If there's only one possible word that hasn't been tried in this row,
			#just add that letter to the board.
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'yx > 1')
			elif len(best_words) == 1:
				board_add_horiz_word(board, best_words[0],current_coordinate[0][0], x_range)
		

			#If there are no possible words that have not been tried in this row, add this
			#board to the list of previously-tried boards and return the board to 
			#the last position in which there was a choice of more than one letter
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'yx =1')
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
				through_else += 1
				forward = False

				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'yx else')
			
			#Clear the best_words list again to prepare for the next time.
			#Not sure this is necessary, but I've seen lists do weird things
			#in loops.
			del best_words [:]

		
		#This is the beginning of the second possibility; that we should fill 
		#in the horizontal word first. It is hopefully exactly the same as the first
		#but in reverse.
		else:
			best_words = []


			#finding words that could be placed in the current row without 
			#disturbing the letters already there.
			x_possibilities = check_against_word_list(find_word_and_range(board[current_coordinate[0][0]],x_range[0])[0])
			
			#print x_possibilities
		#print current_coordinate
		#print x_word,x_range, y_word,y_range
			#Checking the words in the list of possibilities to see if they've
			#already been used.
			for words in x_possibilities:
				if hash_board_add_horiz_word(board, words, current_coordinate[0][0], x_range) not in solution_list:
					best_words.append(words)

		
			#print best_words
			#Again, this is where someone paying more attention would've scored
			#the words.
			best_words = test_horiz_letters(x_range,current_coordinate[0][0],board,best_words)
			#sort_best_horiz_words_by_score(best_words,board,x_range,current_coordinate[0][0])
			print best_words	

			#If there's more than one possible word for this row that hasn't 
			#been tried, add the best word to the row AND save this position 
			#in pos_list so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_horiz_word(board, best_words[0], current_coordinate[0][0], x_range)
				#print_board(board)

			#If there's only one possible word that hasn't been tried in this row,
			#just add that letter to the board.
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'yx > 1')
			elif len(best_words) == 1:
				board_add_horiz_word(board, best_words[0], current_coordinate[0][0], x_range)
			
			
			#If there are no possible words that have not been tried in this row, add this
			#board to the list of previously-tried boards and return the board to 
			#the last position in which there was a choice of more than one letter
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'yx =1')
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)

				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])
				through_else += 1
				forward = False

				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'yx else')
			
			#Clear the best_words list again to prepare for the next time.
			#Not sure this is necessary, but I've seen lists do weird things
			#in loops.
			del best_words [:]


			#this gets a list of words that could be added to the current column without disturbing
			#any letters there already.
			y_possibilities = check_against_word_list(find_word_and_range(get_column(board, current_coordinate[0][1]),y_range[0])[0])
			
			#print y_possibilities

			#looks through the possible words and adds those that haven't been tried 
			#to best_words
			for words in y_possibilities:
				if hash_board_add_vert_word(board, words,current_coordinate[0][1],y_range) not in solution_list:
					best_words.append(words)

			#print best_words
			#Observant humans might notice at this point that the words haven't actually
			#been scored yet. I bet I would've noticed that too, if I hadn't been rushing.
			#Anyway, that should go here.
			#sort_best_vert_words_by_score(best_words,board,y_range,current_coordinate[0][1])

			best_words = test_vert_letters(y_range,current_coordinate[0][1],board,best_words)
			#print best_words
			#If there's more than one possible word for this column that hasn't been tried,
			#add the best word to the column AND save this position in pos_list
			#so we can come back to it if we hit a dead end
			if len(best_words) > 1:
				add_board_and_coords_to_pos_list(board,pos_list,current_coordinate)
				board_add_vert_word(board, best_words[0],current_coordinate[0][1],y_range)
			
			#print strings such as the following have as their last element an indication of which 
			#branch they come from, which is displayed for debugging.
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'y len > 1')

			#If there's only one possible word that hasn't been tried in this column, just add
			#that word to the column.
			elif len(best_words) == 1:
				board_add_vert_word(board, best_words[0],current_coordinate[0][1],y_range)
			
			#If there are no possible words that have not been tried for this column, add this
			#board to the list of previously-tried boards and return the board and current_coordinate
			#to the last position in which there was a choice of more than one word.
			#AND sets forward to False so we don't increment the coordinate list at 
			#the end of the loop.
				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'y len == 1')
			else:
				solution_list_add(board, solution_list)
				board, current_coordinate = return_to_last_good_pos_and_coords(board,pos_list,solution_list)
				forward = False
				through_else += 1
				x_word,x_range,y_word,y_range = coord_to_words_and_ranges(board, current_coordinate[0])

				print_tests_new(board, solution_list,ctr,forward,through_else,current_coordinate, 'y-else')
			

			#This is the beginning of filling in the horizontal word. First we 
			#empty out the best_words list so we can use it again.
			del best_words [:]

		ctr += 1
		if forward == True:
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
				coordinate_values.append(((y_length + x_length),(row,column),directional))
	coordinate_values.sort(reverse=True)
	for element in xrange(len(coordinate_values)):
		coordinate_values[element] = coordinate_values[element][1],coordinate_values[element][2]
	return coordinate_values


def board_solved(board):
	"""checks to see if the board is solved."""
	for row in board:
		if ' ' in row:
			return False
	return True


def coord_to_words_and_ranges(board, coord):
	"""Takes a board and coord and returns x_word, x_range, y_word, y_range"""
	x_word, x_range = find_word_and_range(board[coord[0]],coord[1])
	y_word, y_range = find_word_and_range(get_column(board, coord[1]),coord[0])
	return x_word,x_range,y_word,y_range


def print_tests_new(board, solution_list, x,forward,through_else, current_coordinates,sent_by):
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


def hash_board_add_vert_word(board,word,column_number,range_within_column):
	"""adds a vertical word to a copy of the board using the 1st element of coord_ranges"""
	board_copy = get_board_copy(board)
	board_add_vert_word(board_copy, word,column_number,range_within_column)
	return hash_board(board_copy)


def hash_board_add_horiz_word(board,word,row_number,range_within_row):
	"""this function adds a horizontal word to a copy of the board using the 0th element of coord_ranges"""
	board_copy = get_board_copy(board)
	board_add_horiz_word(board_copy, word,row_number,range_within_row)
	return hash_board(board_copy)


def add_board_and_coords_to_pos_list(board,pos_list,current_coordinate):
	"""Adds the current board to the list of previous boards for which there was a choice of more than one letter."""
	board_copy = get_board_copy(board)
	entry = [board_copy,current_coordinate]
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


def solution_list_add(board, solution_list):
	"""Adds the board to solution_list, which tracks boards that have been tried"""
	solution_list.append(hash_board(board))


def return_to_last_good_pos_and_coords(board,pos_list,solution_list):
	"""returns the (board,current_coordinate) from the last position in which there was a choice of more than one word."""
	for pos in reversed(pos_list):
		if hash_board(pos[0]) not in solution_list:
			return pos


#---------------functions to navigate & comprehend the board-------------



def hash_board(board):
	"""returns a string representation of the board. Used for keeping track of boards that have been tried."""
	hsh = ''
	for row in board:
		for letter in row:
			hsh += (str(letter))
	return hsh



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

#--------------------experimental function area--------------------------

def sort_best_horiz_words_by_score(best_words, board, x_range, y):
	"""filters and sorts the best_words list in place"""
	words = []
	#print best_words
	for word in best_words:
		print 'word: ', word, 'score: ', test_add_horiz_word(x_range,y,word,board)
		words.append([test_add_horiz_word(x_range,y,word,board),word])
		if words[-1][0] == 0:
			words.pop()
	words.sort(reverse=True)
	print words
	del best_words[:]
	for x in words:
		best_words.append(x[1])
	#print best_words


def sort_best_vert_words_by_score(best_words, board, y_range, x):
	"""filters and sorts the best_words list in place"""
	words = []	
	for word in best_words:
		words.append([test_add_vert_word(y_range,x,word,board),word])
		if words[-1][0] == 0:
			words.pop()
	words.sort(reverse=True)
	del best_words[:]
	for x in words:
		best_words.append(x[1])


def test_add_horiz_word(x_range,y, word, board):
	"""Takes a word, adds it (in a horizontal word) to a copy of the board, finds the strings representing vertical intersecting words, and checks to see how many valid words those could be made into. score_word_list returns 0 if any of the intersecting strings cannot be turned into valid words."""
	words = find_horiz_intersecting_words(x_range,y, board)
	index_to_add_at = y
	to_score = []
	for test_word in xrange(len(words)):
		#print words[test_word], word, word[test_word]
		words[test_word][index_to_add_at] = word[test_word]
	for test_word in words:
		to_score.append(find_word_and_range(test_word,y)[0])
	#print words
	return score_word_list(to_score)

def test_horiz_letters(x_range,y,board,best_words):
	list_of_letters_dicts = []
	board_copy = (get_board_copy(board))
	word_list_in_order  = []
	to_return = []
	for space in xrange(x_range[0],x_range[1]+1):
		new_dict = {}
		for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
			board_copy[y][space] = letter
			new_dict[letter] = len(check_against_word_list(find_word_and_range(get_column(board_copy,x_range[0]),y)[0]))
		list_of_letters_dicts.append(new_dict)
	for word in best_words:
		word_score = 0
		#print word
		for letter in xrange(len(word)):
			#print letter, list_of_letters_dicts[letter]
			letter_score = list_of_letters_dicts[letter][word[letter]]
			if letter_score == 0:
				word_score = 0
				break
			word_score += list_of_letters_dicts[letter][word[letter]]
		word_list_in_order.append([word_score,word])
	word_list_in_order.sort(reverse=True)
	for elem in word_list_in_order:
		if elem[0] != 0:
			to_return.append(elem[1])
	return to_return

def test_vert_letters(y_range,x,board,best_words):
	list_of_letters_dicts = []
	board_copy = (get_board_copy(board))
	word_list_in_order  = []
	to_return = []
	for space in xrange(y_range[0],y_range[1]+1):
		new_dict = {}
		for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
			board_copy[space][x] = letter
			new_dict[letter] = len(check_against_word_list(find_word_and_range(board_copy[space],x)[0]))
		list_of_letters_dicts.append(new_dict)
	for word in best_words:
		word_score = 0
		#print word
		for letter in xrange(len(word)):
			letter_score = list_of_letters_dicts[letter][word[letter]]
			if letter_score == 0:
				word_score = 0
				break
			#print letter, list_of_letters_dicts[letter]
			word_score += list_of_letters_dicts[letter][word[letter]]
		word_list_in_order.append([word_score,word])
	word_list_in_order.sort(reverse=True)
	for elem in word_list_in_order:
		if elem[0] != 0:
			to_return.append(elem[1])
	return to_return



def test_add_vert_word(y_range,x, word, board):
	"""Takes a word, adds it (in a vertical word)to a copy of the board, finds the strings representing vertical intersecting words, and checks to see how many valid words those could be made into. score_word_list returns 0 if any of the intersecting strings cannot be turned into valid words."""
	words = find_vert_intersecting_words(y_range,x, board)
	index_to_add_at = x
	to_score = []
	for test_word in xrange(len(words)):
	#print words[test_word], word, word[test_word]
		words[test_word][index_to_add_at] = word[test_word]
	for test_word in words:
		to_score.append(find_word_and_range(test_word,x)[0])
	return score_word_list(to_score)


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
	board_prime = solve_board_use_your_words(BOARD)
