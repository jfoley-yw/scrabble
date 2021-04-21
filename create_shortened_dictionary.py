import random

inpt_path = './resources/wwf11/old_dictionary.txt'
output_path = './resources/wwf5/dictionary.txt'
inpt = open(inpt_path, 'r')
output = open(output_path, 'w')

words = set()

for line in inpt:
    if len(line[:-1]) <= 3:
        words.add(line[:-1])

random_words = random.sample(words, 100)

for word in random_words:
    output.write(word + '\n')

inpt.close()
output.close()
