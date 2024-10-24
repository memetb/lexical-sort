from typing import Tuple, List
import random
import string
import gzip
import json

words = []
valid_words = json.load(open("ox3000.json"))

def show(x):
	print("\n".join([" ".join(y) for y in x]))

def generate_alphabetical_order_recall_words(difficulty_range : Tuple[int], count : int , tuple_size : int =2) -> List[Tuple[str]]:
	"""
	Generates word tuples focusing on alphabetical order recall.

	Parameters:
	- difficulty_range (tuple): A tuple (min_distance, max_distance) specifying the range of distances between starting letters.
	- count (int): Number of word tuples to generate.
	- tuple_size (int): Number of words in each tuple.

	Returns:
	- List[Tuple[str]]: A list of word tuples.
	"""

	word_tuples = []

	# Ensure valid difficulty_range
	min_distance, max_distance = difficulty_range
	min_distance = max(1, min_distance)
	max_distance = min(25, max_distance)  # Max possible distance between letters is 25
	if min_distance > max_distance:
		min_distance, max_distance = max_distance, min_distance	 # Swap if min > max

	# Create a mapping from starting letters to words
	letter_to_words = {}
	for word in valid_words:
		if word:  # Ensure the word is not empty
			letter = word[0].lower()
			if letter in string.ascii_lowercase:
				letter_to_words.setdefault(letter, []).append(word)

	letters = sorted(letter_to_words.keys())

	for _ in range(count):
		# Select a starting letter index
		start_letter = random.choice(letters)
		start_index = string.ascii_lowercase.index(start_letter)

		words_in_tuple = []
		used_letters = set()

		# Add the first word starting with the start_letter
		first_word = random.choice(letter_to_words[start_letter])
		words_in_tuple.append(first_word)
		used_letters.add(start_letter)

		# Generate the rest of the letters based on distances
		for _ in range(tuple_size - 1):
			# Randomly select a distance within the min-max range
			distance = random.randint(min_distance, max_distance)

			# Calculate the new letter index
			new_index = (start_index + distance) % 26
			new_letter = string.ascii_lowercase[new_index]

			# Avoid duplicates and ensure the new_letter has words
			attempts = 0
			while (new_letter in used_letters or new_letter not in letter_to_words) and attempts < 26:
				# Try a different distance
				distance = random.randint(min_distance, max_distance)
				new_index = (start_index + distance) % 26
				new_letter = string.ascii_lowercase[new_index]
				attempts += 1

			if attempts >= 26:
				# Unable to find a suitable letter, break out
				break

			# Select a word starting with the new_letter
			word = random.choice(letter_to_words[new_letter])
			words_in_tuple.append(word)
			used_letters.add(new_letter)

		if len(words_in_tuple) == tuple_size:
			word_tuple = tuple(words_in_tuple)
			word_tuples.append(word_tuple)
		else:
			# If unable to form a complete tuple, try again
			continue

	return word_tuples


def generate_sorting_algorithm_words(rank : int, count : int, tuple_size : int = 2, min_prefix_length : int = 2) -> List[Tuple[str]]:
	"""
	Generates word tuples focusing on the sorting algorithm (comparing letters at different positions).

	Parameters:
	- rank (int): Controls at which position the words differ.
	- count (int): Number of word tuples to generate.
	- tuple_size (int): Number of words in each tuple.
	- min_prefix_length (int): the shortest stem allowable
	(computed as rank - prefix_length)

	Returns:
	- List[Tuple[str]]: A list of word tuples.
	"""
	word_tuples = []
	if not valid_words:
		return word_tuples	# Return empty list if no valid words

	diff_position = rank	# 0-based index

	# Filter words that are at least as long as diff_position + 1
	#words_list = [word for word in valid_words if len(word) > diff_position]

	prefixes = set()
	for word in valid_words:
		prefix = word[:diff_position].lower()
		prefixes.add(prefix)

	# Group words by their prefixes up to the differing character position
	prefix_to_words = {}
	for word in valid_words:
#		prefix = word[:diff_position].lower()
#		prefix_to_words.setdefault(prefix, []).append(word)
		word_lower = word.lower()
		if len(word_lower) >= diff_position:
			prefix = word_lower[:diff_position]
			prefix_to_words.setdefault(prefix, []).append(word)
		elif len(word_lower) > min_prefix_length:
			for prefix in prefixes:
				if prefix.startswith(word_lower):
					prefix_to_words.setdefault(prefix, []).append(word)

	prefixes = list(prefix_to_words.keys())

	for _ in range(count):
		# Select a common prefix
		if not prefixes:
			break  # No prefixes available
		prefix = random.choice(prefixes)
		words_with_prefix = prefix_to_words[prefix]

		# Ensure enough words to form a tuple
		if len(words_with_prefix) < tuple_size:
			continue

		# Select words that differ at diff_position
		words_in_tuple = random.sample(words_with_prefix, k=tuple_size)
		word_tuple = tuple(words_in_tuple)
		word_tuples.append(word_tuple)

	return word_tuples


def generate_word_tuples(count, tuple_size=2, probability_goal1=0.5, probability_goal2=0.5, difficulty1=13, difficulty2=3):
	"""
	Creates a list of word tuples, each tuple generated by either of the two generator functions.

	Parameters:
	- count (int): Total number of word tuples to generate.
	- tuple_size (int): Number of words in each tuple.
	- probability_goal1 (float): Probability of generating a tuple focusing on alphabetical order recall.
	- probability_goal2 (float): Probability of generating a tuple focusing on the sorting algorithm.
	- difficulty1 (int): Difficulty parameter for alphabetical order recall.
	- difficulty2 (int): Difficulty parameter for sorting algorithm.

	Returns:
	- List[Tuple[str]]: A list of word tuples.
	"""
	import random

	word_tuples = []
	total_probability = probability_goal1 + probability_goal2

	for _ in range(count):
		r = random.uniform(0, total_probability)
		if r < probability_goal1:
			tuples = generate_alphabetical_order_recall_words(difficulty1, 1, tuple_size=tuple_size)
			word_tuples.extend(tuples)
		else:
			tuples = generate_sorting_algorithm_words(difficulty2, 1, tuple_size=tuple_size)
			if tuples:
				word_tuples.extend(tuples)
			else:
				# Fallback to the other generator if no tuples were produced
				tuples = generate_alphabetical_order_recall_words(difficulty1, 1, tuple_size=tuple_size)
				word_tuples.extend(tuples)

	return word_tuples
