from collections import Counter
import re
import nltk
from nltk.stem import PorterStemmer
import json
import time
import math
from IPython.display import clear_output
from sys import stdout

def all_lower(my_list): #from https://blog.finxter.com/python-convert-string-list-to-lowercase/#:~:text=The%20most%20Pythonic%20way%20to,new%20string%20list%2C%20all%20lowercase.
    return [x.lower() for x in my_list]
def removeField(discarded_fields,file_path):
    # Ask the user for the output file name
    output_file_path = f"{file_path}{discarded_fields}FieldRemoved.txt"
    try:
        with open(file_path, 'r') as file, open(output_file_path, 'w') as output_file:
            xStop = False
            for line in file:
                line = line.strip()
                line2 = line.split()
                if line2[0] in discarded_fields:
                    xStop = True
                if ".I" in line2:
                    xStop = False
                if not xStop:
                    output_file.write(line + '\n')
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return output_file_path

def stopwords(stopwordfile):
    #read stopwords.txt
    try:
        with open(stopwordfile,'r') as wordfile:
            stopwords_set = all_lower(list(wordfile.read().splitlines()))
    except FileNotFoundError:
        print(f"The file {stopwordfile} does not exist.")
        exit(1)
    return stopwords_set
    
def dictionaryCreate(wordList, dictionaryFile,currentID,document_list = []):
    already_added = False
    for word in wordList:
        word = word.lower()
        if word in document_list:
            already_added = True
        else:
            document_list.append(word)
            already_added = False
        if already_added == False:
            if word in dictionaryFile:
                dictionaryFile[word] += 1
            else:
                dictionaryFile[word] = 1
    return dictionaryFile, document_list
def postingPosList(wordList, currentDocId, filePath,line_number, line,posting_frequency, completed_article = bool, old_posting_frequency ={}, new_posting_frequency ={}):
    wordOccurrences = posting_frequency 
    postings_list = {}
    wordList = {k.lower(): v for k, v in wordList.items()}
    if completed_article and not old_posting_frequency:
        for word in posting_frequency.keys():
            word = word.lower()
            the_set = [(currentDocId,wordList[word],posting_frequency[word])]
            
            if word in postings_list:
                postings_list[word].extend(the_set)
            else:
                postings_list[word] = the_set
        return postings_list
    if completed_article and old_posting_frequency:
        for word in posting_frequency.keys():
            if word in old_posting_frequency:
                old_posting_frequency[word].extend(new_posting_frequency[word])
            else:
                old_posting_frequency[word] = new_posting_frequency[word]
        #print(old_posting_frequency)
        return old_posting_frequency
                
    for word in wordList.keys():
        word = word.lower()
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        matches = pattern.finditer(str(line))
        positions = [(line_number,match.start()+1) for match in matches]
        word = str(word)
        if positions:
            if word in wordOccurrences:
                wordOccurrences[word].extend(positions)
            else:
                wordOccurrences[word] = positions
    return wordOccurrences
      
stemmingOn = False
stopwordsOn = False     
def invert():
    # The variables
    global stemmingOn, stopwordsOn
    file_path = "cacm.all"
    #file_path_old = file_path
    #file_path = removeField(['.B','.A','.N','.X'],file_path)
    stopwords_file_path = "stopwords.txt"
    stopwords_set = stopwords(stopwords_file_path)
    try:
        stemmingON = input("Do you wish to turn stemming on?(Press 1 for yes, anything else for no): ")
        stopwordsON = input("Do you wish to remove stopwords?(Press 1 for yes, anything else for no): ")
        if stemmingON == '1':
            stemmingOn = True
        if stopwordsON == '1':
            stopwordsOn = True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    try: 
        documentID_counter=[]
        documentID = 0
        startIndexing = False
        dictionaryFile = {}
        postingFile = {}
        postingFreq ={}
        old_postingFile = {}
        line_counter = 0
        line_reset_at_new_id = 0
        #examplecounter = 0
        with open(file_path, 'r') as file:
            #text = file.read()
            words = []
            for line in file:
                line_counter +=1
                line_reset_at_new_id +=1
                line = line.strip()
                if ".I" in line:
                    line_reset_at_new_id=0
                    startIndexing = False
                    if line_counter >= 2:
                        
                        postingFile = postingPosList(word_frequencies, documentID, file_path, line_reset_at_new_id-1,line.lower(),postingFreq,True)
                        if not old_postingFile:
                            old_postingFile = dict(postingFile)
                        else:
                            postingFile = postingPosList(word_frequencies, documentID, file_path, line_reset_at_new_id-1,line.lower(),postingFreq,True, old_postingFile, postingFile)
                            
                    documentID = line.split()[1]
                    document_counter = []
                    words =[]
                    postingFreq ={}
                if ".T" in line:
                    startIndexing = True
                if startIndexing:
                    line = re.sub(r'(?<![0-9])\W+(?![0-9])', ' ', line)
                    line = re.sub(r'[()]', '', line)
                    line = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', line)
                    #line = re.sub(r'[\'"]', '', line)
                    if stemmingOn:#from a site
                        stemmer = PorterStemmer()
                        linewords = nltk.word_tokenize(line)
                        stemmed_words = [stemmer.stem(word) for word in linewords]
                        line = ' '.join(stemmed_words)  
                    word = line.split()
                    words.extend(word)
                    if stopwordsOn == True:
                        filtered_words = [word for word in words if word.lower() not in stopwords_set]
                        words = filtered_words
                    word_frequencies = Counter(words)
                    postingFreq = postingPosList(word_frequencies, documentID, file_path, line_reset_at_new_id-1,line.lower(),postingFreq,False)
                    dictionaryFile, document_counter = dictionaryCreate((word_frequencies.keys()), dictionaryFile,documentID,document_counter)
                    
                    #examplecounter +=1
                    #if examplecounter == 500:
                        #print("exit")
                        #exit(1)
        posting_file_name = "PostingsFile.txt"
        dictionary_file_name = "dictionaryFile.txt"
        json.dump(sorted(dictionaryFile.items()), open("dictionaryFile.txt",'w'))
        json.dump(sorted(postingFile.items()), open("PostingsFile.txt",'w'))
        return [file_path,dictionary_file_name,posting_file_name,documentID]
        """
        with open('dictionaryFile.txt','w') as dictionary_file_output, open('PostingsFile.txt','w') as postings_file_output:
            dictionary_file_output.write("(Term,Document Appearances)"+ '\n')
            postings_file_output.write("(Term, [(DocumentID, Frequency in Document, [(Row#, Column#),*Other occurrences*]),*Other Documents*])"+ '\n')
        with open('dictionaryFile.txt','a') as dictionary_file_output, open('PostingsFile.txt','a') as postings_file_output:
            for i in sorted(dictionaryFile.items()):
                dictionary_file_output.write(str(i) + '\n') 
            for i in sorted(postingFile.items()):
                postings_file_output.write(str(i) + '\n')
        """
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def search(files,query,k=10,evaluation=False):
    dictionary_file = files[1]
    N = int(files[3])
    posting_file = files[2]
    user_query = sorted(query[1].items())#sets where (term,freq)
    query_weights = [0]*len(user_query)
    doc_weights_dictionary = {}
    try:
        dictionary_doc= dict(json.load(open(dictionary_file)))
        posting_doc = dict(json.load(open(posting_file)))
        #print("check 1")
        #start IDF calculations
        idf_scores = {}
        for term in dictionary_doc.keys():
            df = int(dictionary_doc[term])
            idf_scores[term] = math.log(N/df,10)
        #json.dump(idf_scores, open("idf_scores.txt",'w'))
        # end IDF calculations
        #print("check 2")
        # find documents
        #print(user_query)
        for index, term_freq in enumerate(user_query):
            #print(term_freq)
            
            
            #print(f"check 3, {term_freq}")
            if term_freq[0] in dictionary_doc:
                #query_weights[index] = (1 + math.log(term_freq[1],10))*(idf_scores[term_freq[0]])
                if idf_scores[term_freq[0]] >= 0.6:
                    query_weights[index] = (1 + math.log(term_freq[1],10))*(idf_scores[term_freq[0]])
                else:
                    query_weights[index] = (1 + math.log(term_freq[1],10))*(0)
                for docID in posting_doc[term_freq[0]]:
                    doc_id = docID[0]
                    word_freq = int(docID[1])
                    tf = 1 + math.log(word_freq,10)
                    idf = idf_scores[term_freq[0]]
                    #if idf < 1.0:
                        #idf = 0
                    w = tf * idf
                    if doc_id in doc_weights_dictionary:
                        doc_weights_dictionary[doc_id][index] = w
                    else:
                        doc_weights_dictionary[doc_id] = [0]*len(user_query)
                        doc_weights_dictionary[doc_id][index] = w
        sim_score_dictionary = simScore(doc_weights_dictionary,query_weights)
        sorted_sim_score_dictionary = sorted(sim_score_dictionary.items(), key=lambda item: (-item[1], item[0]))
        #print(query_weights)
        #print(query_weights)
        #print(doc_weights_dictionary['1350'])
        #print(doc_weights_dictionary['1134'])
        #print(sorted_sim_score_dictionary)
        if len(sorted_sim_score_dictionary)>9:
            top_k = sorted_sim_score_dictionary[:k]
        else:
            top_k = sorted_sim_score_dictionary
        #print(top_k)
        top_k_dic_id = [doc[0] for doc in top_k]
        #print(top_k_dic_id)
        original_doc = files[0]

        begin_copy = False
        with open(original_doc,'r') as f:
            counter=0
            for line in f:
                line = line.strip().split()
                if ".I" in line:  
                    if line[1] in top_k_dic_id:
                        index = top_k_dic_id.index(line[1])
                        begin_copy = True
                        title = []
                        author = []
                        author_section = False
                        title_section = False
                    else:
                        begin_copy = False
                        author_section = False
                        title_section = False
                        continue
                if any(element == ".B" or element == ".W" or element == ".N" or element == ".X" or element == ".K" or element == ".C"for element in line):
                    title_section = False
                    author_section = False
                if ".T" in line and begin_copy:
                    title_section = True
                    author_section = False
                    continue 
                if ".A" in line and begin_copy:
                    author_section = True
                    title_section = False
                    continue
                if begin_copy and title_section:
                    title.extend(line)
                    continue
                if author_section and begin_copy:
                    if len(author) > 1:
                        author.append(",")
                    author.extend(line)
                        
                    continue
                if ".X" in line and begin_copy:
                    top_k_dic_id[index] = " ".join(title) + " by: " + " ".join(author)  
        #print(top_k_dic_id)       
        json.dump(top_k, open("TopK.txt",'w')) #[[documentID, relevance scores]] 
        if evaluation == False:   
            for rank,items in enumerate(top_k_dic_id):
                print(f"___________________________________________________________________________\nRank {rank+1}:\n{items}")
        
    except FileNotFoundError:
        print(f"The file '{files[0]}' or '{files[1]}' or '{files[2]}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    
    return top_k

def simScore(doc_weights, query_weights):
    sqrt_weights = {}
    sim_score_dict = {}

    query_weights_squared = [num ** 2 for num in query_weights]

    sqrt_weights["Q"] = math.sqrt(sum(query_weights_squared))

    for index,weight in enumerate(doc_weights):
        squared_weights = [num ** 2 for num in doc_weights[weight]]#square each element
        #squared_weights = [num * 0 if num < 0.3 else num ** 2 for num in doc_weights[weight]]
        sum_of_weights = sum(squared_weights)#sum of entire list
        sqrt_weights[weight] = math.sqrt(sum_of_weights)#square root of sum
        #calculate simScore
        result = [a * b for a, b in zip(doc_weights[weight], query_weights)]#produces a list of final results after multiplying element by element from 1 list to another
        if sqrt_weights["Q"] == 0:
            continue
        sim_score_dict[weight] = sum(result)/(sqrt_weights[weight]*sqrt_weights["Q"])
    
    #print("cleared simscore")
    return sim_score_dict
def userQuery():
    list_of_eclipsed_time = []
    global stemmingOn, stopwordsOn
    
    #ask for query
    while True:
        user_input = input("Please enter the query you wish to search for (Enter ZZEND to end program): ").lower().strip()
        if len(user_input) < 1:
            continue
        user_input = re.sub(r'(\d)([A-Za-z])', r'\1 \2', user_input)
        user_input = re.sub(r'[!@#$%^&*()+\-_=\[\]{}|;:"\'<>,.?/\\`~]', '', user_input)
        if user_input == 'zzend':
            return False
        user_input = user_input.split()
        #print(user_input)
        if stopwordsOn:
            stopwords_set = stopwords("stopwords.txt")
            user_input = [word for word in user_input if word.lower() not in stopwords_set]
            user_input = " ".join(user_input)
        if len(user_input) == 0:
            continue
        user_input_non_stemmed=user_input
        if stemmingOn:
            stemmer = PorterStemmer()
            linewords = nltk.word_tokenize(user_input)
            user_input = [stemmer.stem(word) for word in linewords]
            user_input = ' '.join(user_input)
            user_input = user_input.strip()
        if stemmingOn or stopwordsOn:
            user_input = user_input.split()
        
        return [stemmingOn,Counter(user_input),Counter(user_input_non_stemmed),user_input_non_stemmed]
    
def userQueryEval(input):
    #list_of_eclipsed_time = []
    global stemmingOn, stopwordsOn
    
    #ask for query
    user_input = input
    user_input = re.sub(r'(\d)([A-Za-z])', r'\1 \2', user_input)
    user_input = re.sub(r'[!@#$%^&*()+\-_=\[\]{}|;:"\'<>,.?/\\`~]', '', user_input)
    if len(user_input) < 1:
            return False
    user_input = user_input.split()
    #print(user_input)
    if stopwordsOn:
        stopwords_set = stopwords("stopwords.txt")
        user_input = [word for word in user_input if word.lower() not in stopwords_set]
        user_input = " ".join(user_input)
    if len(user_input) < 1:
            False
    user_input_non_stemmed=user_input
    if stemmingOn:
        stemmer = PorterStemmer()
        linewords = nltk.word_tokenize(user_input)
        user_input = [stemmer.stem(word) for word in linewords]
        user_input = ' '.join(user_input)
        user_input = user_input.strip()
    if stemmingOn or stopwordsOn:
        user_input = user_input.split()
    
    return [stemmingOn,Counter(user_input),Counter(user_input_non_stemmed),user_input_non_stemmed]

def averagePrecision(rel, ret, sumAP):
    pList = []
    counter=0
    for index,id in enumerate(ret):
        if id in rel:
            counter += 1
            p = counter/(index+1)
            pList.append(p)
    #print(len(rel), pList)
    
    sumAP+=sum(pList)/len(rel)
    
    return sumAP
def rPrecision(rel, ret, sumRP):
    counter = 0
    for index,id in enumerate(ret):
        if id in rel:
            counter += 1
        if index + 1 == len(rel):
            break
    sumRP += counter/len(rel)
    
    return sumRP
def eval(files):
    RET_DOC = 'query.text'
    REL_DOC = 'qrels.text'
    rel_dict = {}
    ret_list = {}
    file_names_list = files
    with open(REL_DOC, 'r') as REL_FILE:
        for line in REL_FILE:
            line = line.strip().split()
            #print(line)
            if int(line[0]) in rel_dict:
                rel_dict[int(line[0])].append(line[1])
            else:
                rel_dict[int(line[0])] = [line[1]]
        #print(len(rel_dict))
    with open(RET_DOC, 'r') as RET_FILE:
        counter = 0
        start_recording = False
        query_eval = ""
        sumAp = 0
        sumRp = 0
        for line in RET_FILE:
            line = line.strip().split()
            if ".I" in line:
                doc_id = int(line[1])
                continue
            if ".W" in line:
                #counter+=1
                start_recording = True
                query_eval = ""
                continue
            if start_recording:
                query_eval += ' '.join(line) + " "
            if ".A" in line:
                start_recording = False
            if ".N" in line:
                start_recording = False
                query_eval = query_eval.strip()
                query = userQueryEval(query_eval)
                if query == False:
                    continue
                #clear_output(wait=True)
                #k = len(rel_dict[doc_id])
                ret_list = search(file_names_list, query,10, True)
                ret_list = [id[0] for id in ret_list]
                #print(ret_list)
                #print(rel_dict[doc_id])
                if doc_id in rel_dict:
                    sumAp = averagePrecision(rel_dict[doc_id],ret_list,sumAp)
                    #print(apList)
                    sumRp = rPrecision(rel_dict[doc_id],ret_list,sumRp)
                    counter+=1
                    #print(len(rel_dict[doc_id]))
                
            #if counter == 5:
                #break
        #print(counter)
        MAP = sumAp/counter
        RPRECISION = sumRp/counter
        print(f"MAP = {MAP}, Average R-Precision = {RPRECISION}")
        
    
    
    return
def main():
    file_names_list = invert()
    #file_names_list = ['cacm.all', 'dictionaryFile.txt', 'PostingsFile.txt', '3204']
    while True:
        query = userQuery() #returns a list of [bool, Counter(user_input),Counter(user_input_non_stemmed)]
        if query == False:
            break
        stdout.flush() 
        search(file_names_list, query)
        #time.sleep(10)
        #clear_output(wait=True)
         
    
    evaluate = input("Do you wish to run the evaluation program? (y/n): ").lower().strip()
    if evaluate == 'y':
        eval(file_names_list)
    return
main()