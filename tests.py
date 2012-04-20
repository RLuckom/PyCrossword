from turbocrossword import *
import filter

def test_find_supernodes():
	if find_supernodes([['#',' ','#'],[' ',' ',' '],['#',' ','#']])[0][0] == (1,1):
		return 'PASS' 
	return 'FAIL'

def test_board_solved():
	if board_solved([['j','i','m'],['b','o','b'],['j','e','n']]) and not board_solved([[' ','i','m'],['b',' ','b'],['j','e','n']]):
		return 'PASS'
	return 'FAIL'

def test_coord_to_words_and_ranges():
	board = [[' ',' ',' '],[' ',' ',' '],['#',' ','#']]
	coord = (0,0)
	if coord_to_words_and_ranges(board, coord) == ('   ',(0,2),'  ',(0,1)):
		return 'PASS'
	return 'FAIL'

def test_check_against_word_list():
	if check_against_word_list('  TP') != []:
		print  check_against_word_list('  tp')
		return 'FAIL'
	if check_against_word_list('WORD') != ['WORD']:
		print  'word: ',check_against_word_list('WORD')
		return 'FAIL'
	return 'PASS'

def test_find_word_and_range():
	board = [[' ',' ',' '],[' ',' ',' '],['#',' ','#']]
	coord = (0,0)
	if find_word_and_range(board[0], coord[0]) == ('   ',(0,2)):
		return 'PASS'
	return 'FAIL'

def test_get_column():
	board = [[' ',' ',' '],[' ',' ',' '],['#',' ','#']]
	return 'PASS' if get_column(board,0) == [' ',' ','#'] else 'FAIL'
	
WORD_LISTS_BY_LENGTH = build_word_lists_by_length(filter.filter_words(filter.file_to_list()))
if __name__ =="__main__":
	print 'find_supernodes: ',test_find_supernodes()
	print 'board_solved: ',test_board_solved()
	print 'coord_to_words_and_ranges: ',test_coord_to_words_and_ranges()
	print 'check_against_word_list: ',test_check_against_word_list()
	print 'find_word_and_range: ',test_find_word_and_range()
	print 'get_column: ',test_get_column()
	
