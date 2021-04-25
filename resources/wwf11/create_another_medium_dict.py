import random

inpt_path = './old_dictionary.txt'
output_path = './dictionary.txt'
inpt = open(inpt_path, 'r')
output = open(output_path, 'w')

words = set()

for line in inpt:
    if len(line[:-1]) <= 3:
        words.add(line[:-1])

random_words = random.sample(words, 500)

for word in random_words:
    output.write(word + '\n')

inpt.close()
output.close()