import turbocrossword

BOARD = [['S','C',' ','B','S'],['T','O',' ','A','L'],[' ',' ',' ',' ',' '],['R','O',' ','E','D'],['T','R',' ','S','S']]
horiz = turbocrossword.find_horiz_intersecting_words((0,4),2,BOARD)
vert = turbocrossword.find_vert_intersecting_words((0,4),2,BOARD)
print turbocrossword.test_vert_letters((0,4),2,BOARD,turbocrossword.WORD_LISTS_BY_LENGTH[4])
print turbocrossword.test_horiz_letters((0,4),2,BOARD,turbocrossword.WORD_LISTS_BY_LENGTH[4])
