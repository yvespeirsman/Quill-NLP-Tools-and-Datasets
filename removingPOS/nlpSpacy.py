import re
import spacy
nlp = spacy.load('en')

'''
Important Notes:
POS = Part of Speech
Need to take into account words that have 's as is

TO-DO:
Put each main function into seperate file and import necessary files:
noun_remove
verd_remove
noun_verb_remove

For each newly created file start creating final text files:
First file output: original list of POS || updated list POS || words removed
Second file output to help people understand: Original sentence, word removed, updated sentence (everything as complete string)

Create a function that can turn a string of tuples into a list of tuples

Random but important:
take into account ,, and "  "
have to go through and update any 're ''s (etc.) that are actually verbs
'''

#turns string into a list of tuples, where each tuple contains a word, word depency, and word POS
def pos_tup_list(s):
    processed = nlp(s)
    tup_list = []
    for token in processed:
        tup_list.append((str(token),token.dep_,token.pos_))
    return tup_list

#changes a list of tuples to a string so that it can be printed
def tup_list_to_string(lst):
    return ', '.join('(' + ', '.join(i) + ')' for i in lst)

#turns a list of tuples into a sentence or words
def make_str(lst):
    s = ''
    for i in range(len(lst)):
        curr_word = lst[i][0]
        if lst[i][2] != 'PUNCT' and lst[i][1] != "case" and lst[i-1][0] != '-':
            s += ' ' + curr_word
        else:
            s += curr_word
    if s[0] == ' ':
        return s[1:]
    else:
        return s

#deletes a word from a sentence
def delete_words_string(sentence,s):
    #returns bool describing if matched word is in the beginning
    def word_at_beginning(sentence,s):
        regex = re.compile(s)
        match_span = regex.search(sentence).span()
        if match_span[0] == 0:
            return True
        else:
            return False

    regex1 = re.compile(s+"\'")
    if regex1.search(sentence) != None:
        return sentence.replace(s,"")
    elif word_at_beginning(sentence,s) == True:
        return sentence.replace(s+' ','')
    else:
        return sentence.replace(' '+s,'')

#returns true if a hypen is found in a sentence
def hypen_in_sentence(s):
    regex = re.compile(r'\-')
    match_bool = regex.search(s)
    if match_bool != None:
        return True
    else:
        return False

#this returns a list of tuples that are not in the second argument
def remove_tups_lst(ls_orig,ls_remove,removal_type):
    upd_tup_lst = []
    if removal_type == "noun":
        for i in range(len(ls_orig)):
            if i != ls_remove[0]:
                upd_tup_lst.append(ls_orig[i])
            else:
                ls_remove.pop(0)
    else:
        for tup in ls_orig:
            if tup not in ls_orig:
                upd_tup_lst.append(tup)
    return upd_tup_lst

#removes verbs from a sentence
def verb_removal(st):
    #returns a list of words that are consecutive verbs
    def consec_verb_list(lst):
        for i in range(len(lst)):
            if lst[i][2] == "VERB":
                verb_tup_lst = [lst[i]]
                indexes_mached = [i]
                for p in range(i+1,len(lst)):
                    if lst[p][2] == "VERB":
                        verb_tup_lst.append(lst[p])
                        indexes_mached.append(p)
                    else:
                        return (verb_tup_lst,indexes_mached)
        return []

    #returns a string with all the hypenated words removed
    def remove_hypens_words(st):
        #removes word duplicates in a list
        def remove_duplicates(lst):
            word_dict = {}
            for i in range(len(lst)):
                word = lst[i]
                if word_dict.get(word) == None:
                    word_dict[word] = word
            return list(word_dict.keys())

        regex = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        matches_lst = remove_duplicates(regex.findall(st)) #this is essential
        while matches_lst != []:
            word = matches_lst.pop()
            st = delete_words_string(st,word)
        return st

    def hypen_verb_removal(s):
        tup_sent_arr = pos_tup_list(s)
        st_wo_hypen_words = remove_hypens_words(s)
        tup_upd_st = pos_tup_list(st_wo_hypen_words)
        verb_list_found = consec_verb_list(tup_upd_st)
        if verb_list_found != []:
            verb = make_str(verb_list_found[0])
            sentence_wo_verb = delete_words_string(s,verb)
            return (sentence_wo_verb[0].upper()+sentence_wo_verb[1:],verb,tup_list_to_string(verb_list_found[0]),tup_list_to_string(tup_sent_arr))
        else:
            return ("ERROR",tup_list_to_string(tup_sent_arr))

    def normal_verb_removal(s):
        tup_sent_arr = pos_tup_list(s)
        verb_list_found = consec_verb_list(tup_sent_arr)
        if verb_list_found != []:
            verb = make_str(verb_list_found[0])
            sentence_wo_verb = delete_words_string(s,verb)
            return (sentence_wo_verb[0].upper()+sentence_wo_verb[1:],verb,tup_list_to_string(verb_list_found[0]),tup_list_to_string(tup_sent_arr))
        else:
            return ("ERROR",tup_list_to_string(tup_sent_arr))

    if hypen_in_sentence(st) == False:
        return normal_verb_removal(st)
    else:
        return hypen_verb_removal(st)

def noun_removal(s):
    #this function assumes that there is a hypen in the string and returns the span of the first hypen match
    def hypen_match_range(s):
        regex = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        check_found = regex.search(s)
        if check_found != None:
            return check_found.span()
        else:
            return None
    #returns true if the tuple is a noun
    def noun_bool(tup):
        word_pos = tup[2]
        word_dep = tup[1]
        if  word_pos == 'NOUN' or word_pos == 'PRON' or word_pos == 'PROPN' or word_dep == 'poss':
            return True
        else:
            return False

    #returns a list of the tuples that were removed that are of noun type
    def consec_noun_list(lst): #add case for numbers wehre noun before   ('On', 'prep', 'ADP') ('July', 'pobj', 'PROPN') ('21', 'nummod', 'NUM') ('the', 'det', 'DET')
        consec_lst = []
        indexes_lst = []
        for index in range(len(lst)):
            if noun_bool(lst[index]) == True:
                consec_lst.append(lst[index])
                indexes_lst.append(index)
                for i in range(index + 1, len(lst)):
                    if lst[i][0] == '.' and i != len(lst)-1: #making sure that the '.' found is not the period of the sentence
                        if noun_bool(lst[i+1]) == True:
                            consec_lst.append(lst[i])
                            indexes_lst.append(i)
                    elif lst[i][0][0] == "\'" and lst[i][2] != "VERB": #takes into account possesive nouns (Catherine's)
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    elif noun_bool(lst[i]) == True:
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    elif lst[i][2] == "NUM": #numbers are nouns
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    else:
                        return (consec_lst,indexes_lst)
        return []

    def normal_noun_removal(string): #here include hypen noun removal
        orig_sent_arr = pos_tup_list(string)
        noun_list_found = consec_noun_list(orig_sent_arr)
        if noun_list_found != []:
            noun = make_str(noun_list_found[0]) #just turn thing into string
            sentence_wo_noun = delete_words_string(string,noun)
            return (sentence_wo_noun[0].upper()+sentence_wo_noun[1:],noun,tup_list_to_string(noun_list_found[0]),tup_list_to_string(orig_sent_arr))
        else:
            return ("ERROR",tup_list_to_string(orig_sent_arr))

    #removes nouns from a string that contains hypens
    def hypen_noun_removal(s):
        orig_tup = pos_tup_list(s)
        hypen_match_ran = hypen_match_range(s)
        substring = s[:hypen_match_ran[0]-1] #substring before the hypen word. The space before the hypen match is not included in substring
        token_pos_lst = pos_tup_list(substring)
        last_token = token_pos_lst[len(token_pos_lst)-1]
        if hypen_match_ran[0] > len(s)/2: #meaning the hypen is at the very end, noun must be before this
            return normal_noun_removal(s)
        elif last_token[2] != 'NOUN' and last_token[2] != 'PRON' and last_token[2] != 'PROPN' and last_token[2] != "PUNCT" and last_token[1] != 'case' and last_token[1] != 'poss':
            substring_rem = normal_noun_removal(substring) #finding any nouns before the hypenated word
            if substring_rem[0] != 'ERROR':
                noun_removed = substring_rem[1]
                sentence_noun_removed = delete_words_string(s, noun_removed)
                return (sentence_noun_removed[0].upper()+sentence_noun_removed[1:],noun_removed,substring_rem[2],substring_rem[3])
            else:
                return ('ERROR',tup_list_to_string(orig_tup))
        else:
            return ('ERROR',tup_list_to_string(orig_tup))

    if hypen_in_sentence(s) == False:
        return normal_noun_removal(s)
    else:
        return hypen_noun_removal(s)

def noun_verb_removal(st):
    tup_lst = pos_tup_list(st)
    remove_noun_st = noun_removal(st) #i think this order is fine because also recognizes 're as verb
    remove_verb_st = verb_removal(st)
    if remove_noun_st[0] != "ERROR" and remove_verb_st[0] != "ERROR":
        noun_removed = remove_noun_st[1]
        verb_removed = remove_verb_st[1]
        st = delete_words_string(st,noun_removed)
        st = delete_words_string(st,verb_removed)
        return (st[0].upper()+st[1:], remove_noun_st[2]+' '+remove_verb_st[2],tup_list_to_string(tup_lst))
    else:
        return ("ERROR", tup_list_to_string(tup_lst))



# with open('./updatedSentences/nounSentences/testing.txt','w') as remov:
#     with open('./originalSentences/nounScreening.txt','r') as file:
#         for line in file:
#             # print(line)
#             n_sentence_rem = noun_removal(line)
#             if n_sentence_rem[0] != "ERROR":
#                 remov.write(line.rstrip('\n') + ' ||| ' + n_sentence_rem[2] + '\n' )

# with open('./updatedSentences/verbSentences/testing.txt','w') as remov:
#     with open('./originalSentences/verbScreening.txt','r') as file:
#         for line in file:
#             print(line)
#             v_sentence_rem = verb_removal(line)
#             if v_sentence_rem[0] != "ERROR":
#                 remov.write(line.rstrip('\n') + ' ||| ' + v_sentence_rem[2] + '\n' )

# with open('./updatedSentences/nounverbSentences/testing.txt','w') as remov:
#     with open('./originalSentences/nounverbScreening.txt','r') as file:
#         for line in file:
#             print(line)
#             nv_sentence_rem = noun_verb_removal(line)
#             if nv_sentence_rem[0] != "ERROR":
#                 remov.write(line.rstrip('\n') + ' ||| ' + nv_sentence_rem[2] + '\n' )


#THIS IS FOR NOUNS
# with open('./updatedSentences/nounSentences/nounErrorSentences.txt','w') as error_n:
#     with open('./updatedSentences/nounSentences/nounCompleteSentences.txt','w') as complete:
#         with open('./updatedSentences/nounSentences/nounRemovedSentences.txt','w') as remov:
#             with open('./updatedSentences/nounSentences/nounRemovedClean.txt','w') as remov_clean:
#                 with open('./originalSentences/nounScreening.txt','r') as file:
#                     for line in file:
#                         n_sentence_rem = noun_removal(line)
#                         if n_sentence_rem[0] != "ERROR":
#                             complete.write(line.rstrip('\n') + ' ||| ' + n_sentence_rem[1])
#                             remov.write(n_sentence_rem[0] + ' ||| ' +  n_sentence_rem[2].rstrip('\n') + ' ||| ' + line.rstrip('\n') + ' ||| ' + n_sentence_rem[3])
#                             remov_clean.write(n_sentence_rem[0]+"\n")
#                         else:
#                             error_n.write('ERROR ||| ' + line.rstrip('\n') + ' ||| ' + n_sentence_rem[1] + '\n')





#THIS IS FOR VERBS
# with open('./updatedSentences/verbSentences/verbErrorSentences.txt','w') as error_v:
#     with open('./updatedSentences/verbSentences/verbCompleteSentences.txt','w') as v_complete:
#         with open('./updatedSentences/verbSentences/verbRemovedSentences.txt','w') as v_remov:
#             with open('./updatedSentences/verbSentences/verbRemovedClean.txt','w') as v_remov_clean:
#                 with open('./originalSentences/verbScreening.txt','r') as f:
#                     for line in f:
#                         v_sentence_rem = verb_removal(line)
#                         if v_sentence_rem[0] != "ERROR":
#                             v_complete.write(line)
#                             v_remov.write(v_sentence_rem[0] + ' ||| ' +  v_sentence_rem[1] + ' ||| ' + line)
#                             v_remov_clean.write(v_sentence_rem[0])
#                         else:
#                             error_v.write('ERROR ||| ' + line.rstrip('\n') + ' ||| ' + v_sentence_rem[1] + '\n')
#
# # THIS IS FOR NOUNS AND VERBS
# with open('./updatedSentences//nounverbSentences/nounverbErrorSentences.txt','w') as error_nv:
#     with open('./updatedSentences/nounverbSentences/nounverbCompleteSentences.txt','w') as nv_complete:
#         with open('./updatedSentences/nounverbSentences/nounverbRemovedSentences.txt','w') as nv_remov:
#             with open('./updatedSentences/nounverbSentences/nounverbRemovedSentences.txt','w') as nv_remov_clean:
#                 with open('./originalSentences/nounverbScreening.txt','r') as fi:
#                     for line in fi:
#                         noun_verb_removed = noun_verb_removal(line)
#                         print(noun_verb_removed)
#                         if noun_verb_removed[0] != "ERROR":
#                             nv_complete.write(line)
#                             nv_remov.write(noun_verb_removed[0] + ' ||| ' + noun_verb_removed[1] + ' ||| ' + line)
#                             nv_remov_clean.write(noun_verb_removed[0])
#                         else:
#                             error_nv.write('ERROR ||| ' + line.rstrip('\n') + noun_verb_removed[1] +'\n')
#
# error_nv.close()
# nv_complete.close()
# nv_remov.close()
# nv_remov_clean.close()
# fi.close()
