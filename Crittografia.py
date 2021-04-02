def generating_coding_matrix(word, sentence):
    word_listed = list(word)
    sentence_listed = list(sentence)
    coded_matrix = []

    [coded_matrix.append([]) for _ in word_listed]

    c = 0
    for item in sentence_listed:
        if c == len(word):
            c = 0

        lis = coded_matrix[c]
        lis.append(item)
        coded_matrix[c] = lis
        c += 1

    [lists.append('*') for lists in coded_matrix if len(lists) < len(coded_matrix[0])]

    return coded_matrix


def encrypt(word, coded_matrix):
    word_listed = list(word)

    for i in range(len(word_listed)):
        for j in range(len(word_listed)):
            if word_listed[i] > word_listed[j]:
                word_listed[i], word_listed[j] = word_listed[j], word_listed[i]

    coded_sentence = ''

    for i in range(len(word_listed)):
        for item in coded_matrix[i]:
            coded_sentence += item

    return coded_sentence


def generating_decoding_matrix(word, coded_sentence):
    word_listed = list(word)
    sentence_listed = list(coded_sentence)
    coded_matrix = []

    [coded_matrix.append([]) for _ in range(len(sentence_listed) // len(word_listed))]

    c = 0
    for item in sentence_listed:
        if c == len(sentence_listed) // len(word_listed):
            c = 0

        lis = coded_matrix[c]
        lis.append(item)
        coded_matrix[c] = lis
        c += 1

    return coded_matrix


def decrypt(coded_matrix):
    decoded_sentence = ''

    for lis in coded_matrix:
        for item in lis:
            decoded_sentence += item

    if -1 != decoded_sentence.find('*'):
        decoded_sentence = decoded_sentence[0:decoded_sentence.find('*')]

    return decoded_sentence
