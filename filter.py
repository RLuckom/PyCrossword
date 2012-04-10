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
			if word.islower():
				fair_words.append(word.upper())
	return fair_words

