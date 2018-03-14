import numpy as np
import math
from random import shuffle

#from pylab import *
#import matplotlib.pyplot as plt


fn_fake, fn_real = 'clean_fake.txt', 'clean_real.txt'


# Loads data into categorical sets for each class where each data is a list of words in a line.
def load_data(fn, class_label):
    # class_label is 0 for non-spam/real, and 1 for spam/fake
    
    train_ratio, test_ratio, validation_ratio = 0.70, 0.15, 0.15
    ratios = [train_ratio, test_ratio, validation_ratio]
    
    lines = [] 
    with open(fn, 'r') as f:
        lines = f.readlines()
        lines = np.array([line.split() for line in lines])
        f.close()
    
    num_lines = len(lines)
    sizes = [int(num_lines * ratio) for ratio in ratios]
    train_end_idx = sizes[0]
    test_end_idx = train_end_idx + sizes[1]
    validation_end_idx = test_end_idx + sizes[2]
    
    # separate data
    train_xs = lines[:train_end_idx]
    test_xs = lines[train_end_idx:test_end_idx]
    validation_xs = lines[test_end_idx:validation_end_idx]
    
    # build labels
    train_ys = np.empty(sizes[0])
    test_ys = np.empty(sizes[1])
    validation_ys = np.empty(sizes[2])
    train_ys.fill(class_label)
    test_ys.fill(class_label)
    validation_ys.fill(class_label)
    
    return train_xs, test_xs, validation_xs, train_ys, test_ys, validation_ys


def get_words_counts(data_real, data_fake):
    words_counts = {}

    for hl in data_real:
        for word in hl:
            if word not in words_counts:
                words_counts[word] = [1, 0]
            else:
                words_counts[word][0] += 1

    for hl in data_fake:
        for word in hl:
            if word not in words_counts:
                words_counts[word] = [0, 1]
            else:
                words_counts[word][1] += 1

    return words_counts


def get_prob_word_given_label(words_counts, label, num_labeled_data, m , p):
    # again, label is 0 for real and 1 for fake. This number refers to index
    # of words_counts[word] in which word count for that label is stored.
    P_w_l = {}
    for word, counts in words_counts.items():
        P_w_l[word] = (min(counts[label], num_labeled_data)  + m*p) / (num_labeled_data + m)         
        
    return P_w_l


def get_product_of_small_nums(small_nums):
    prod = 0
    
    for small_num in small_nums:
        try:
            prod += math.log(small_num)
        except ValueError:
            print(small_num)
    
    return math.exp(prod)


def get_prob_of_words_in_line(P_w_l, words_in_line):
    P_words_in_hl = np.empty([len(P_w_l)])
    i = 0
    for word, P_w in P_w_l.items():
        if word in words_in_line:
            P_words_in_hl[i] = P_w
        else:
            P_words_in_hl[i] = 1 - P_w
        i += 1
    
    return P_words_in_hl
    
    
def part1(train_real, train_fake):

    # get words count from each real and fake dataset
    words_counts = get_words_counts(train_real, train_fake)

    # # get the most common words in each dataset
    # real_common = []
    # fake_common = []
    #
    # for i in range(3):
    #     max_word_real = max(real_words, key=real_words.get)
    #     max_val_real = real_words.pop(max_word_real)
    #     real_common.append(tuple((max_word_real, max_val_real)))
    #     max_word_fake = max(fake_words, key=fake_words.get)
    #     max_val_fake = fake_words.pop(max_word_fake)
    #     fake_common.append(tuple((max_word_fake, max_val_fake)))

    # print real_common
    # print fake_common
    # print "'the' in real headlines: ", real_words['the']
    # print "'donald' in fake headlines: ", fake_words['donald']
    
    print "Word: 'trump'"
    print "# of appearances in real headlines: ", words_counts['trump'][0]
    print "# of appearances in fake headlines: ", words_counts['trump'][1]
    print "Word: 'donald'"
    print "# of appearances in real headlines: ", words_counts['donald'][0]
    print "# of appearances in fake headlines: ", words_counts['donald'][1]
    print "Word: 'the'"
    print "# of appearances in real headlines: ", words_counts['the'][0]
    print "# of appearances in fake headlines: ", words_counts['the'][1]


def part2(train_xs_r, train_xs_f, train_ys_r, train_ys_f, \
                           test_xs_r, test_xs_f, test_ys_r, test_ys_f):
    # Refer to page 18-23 in http://www.teach.cs.toronto.edu/~csc411h/winter/lec/week5/generative.pdf    
    words_counts = get_words_counts(train_xs_r, train_xs_f)
    
    num_real_data = len(train_ys_r)
    num_fake_data = len(train_ys_f)
    num_total_data = num_real_data + num_fake_data
    
    # m = 1
    # p = 0.1
    ms = [0.01, 0.1, 1, 10, 100]
    ps = [0.00001, 0.001, 0.1]
    print "Naive-Bayes classification (validation performance)\n"
    i = 1
    for m in ms:
        for p in ps:
            
            P_w_r = get_prob_word_given_label(words_counts, 0, num_real_data, m, p)
            P_w_f = get_prob_word_given_label(words_counts, 1, num_fake_data, m, p)
            
            # Prediction
            test_xs_all = np.concatenate((test_xs_f, test_xs_r))
            test_ys_all = np.concatenate((test_ys_f, test_ys_r))
                
            P_r = num_real_data / float(num_total_data)
            P_f = 1 - P_r
            P_hl_f = np.array([P_f * get_product_of_small_nums(get_prob_of_words_in_line(P_w_f, hl)) for hl in test_xs_all])
            P_hl_r = np.array([P_r * get_product_of_small_nums(get_prob_of_words_in_line(P_w_r, hl)) for hl in test_xs_all])
            predicted_ys = np.round(P_hl_f / (P_hl_f + P_hl_r))
            accuracy = np.sum(predicted_ys == test_ys_all) / float(len(test_ys_all))
            print "Test {}\n\nm: {}\np: {}\naccuracy: {}\n".format(i, m, p, accuracy)
            i += 1


def part3():
    #---------------------------------------------------------------------------
    # continue from here
    #---------------------------------------------------------------------------
    return

if __name__ == '__main__':
    train_xs_r, test_xs_r, validation_xs_r, train_ys_r, test_ys_r, validation_ys_r = load_data(fn_real, 0)
    train_xs_f, test_xs_f, validation_xs_f, train_ys_f, test_ys_f, validation_ys_f = load_data(fn_fake, 1)
    
    #part1(train_xs_r, train_xs_f)
    
    #part2(train_xs_r, train_xs_f, train_ys_r, train_ys_f, validation_xs_r, validation_xs_f, validation_ys_r, validation_ys_f)
    
    part3()
    
    

    
        