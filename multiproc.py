import multiprocessing
import multi_crossword
BOARD = [[' ',' ',' ',' ',' '],[' ',' ',' ',' ',' '],[' ',' ',' ',' ',' '],[' ',' ',' ',' ',' '],[' ',' ',' ',' ',' ']]

def try_crosswords():
	"""creates individual processes to try boards with letters A-Z in the first position of the second row in the board. Processes seem to throw typerrors for impossible boards"""
	crosswords = []
	q = multiprocessing.JoinableQueue()
	for letter in 'a bcdefghijklmnopqrstuvwyz'.upper():
		BOARD[1][0] = letter
		crosswords.append(multiprocessing.Process(name=(letter+'-board'),target=multi_crossword.solve_board,args=(board_copy(BOARD),q)).start())
	solved = []
	while len(solved) < 2:
		solved.append(q.get())
		for item in solved:
			multi_crossword.print_board(item)

def return_from_process(fun_x):
	"""test function to start processes with a queue, collect the queue to a list, and print the list when it gets long enough"""
	q = multiprocessing.JoinableQueue() #I need to learn about how JoinableQueue is different from Queue
	procs = [] #list to collect the processes
	for n in xrange(10):
		#adds Process objects to the list and starts them as they are added
		procs.append(multiprocessing.Process(target=fun_x, args=(n,q),).start())
	solved = []
	while len(solved) < 7:
		solved.append(q.get())
	print solved

def board_copy(board):
	copy = []
	for row in board:
		copy.append(row[:])
	return copy

def test_process(x,output_q):
	test_list = []
	for n in xrange(x):
		test_list.append(n)
	output_q.put(test_list)
	return

if __name__ == '__main__':
	#return_from_process(test_process)
	try_crosswords()
