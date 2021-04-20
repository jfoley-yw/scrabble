import random

inpt_path = './resources/wwf11/old_dictionary.txt'
output_path = './resources/wwf11/dictionary.txt'
inpt = open(inpt_path, 'r')
output = open(output_path, 'w')

words = set()

for line in inpt:
    if len(line[:-1]) <= 5:
        words.add(line[:-1])

random_words = random.sample(words, 10000)

for word in random_words:
    output.write(word + '\n')

inpt.close()
output.close()
