# Copyright 2020 Paul Lu
#--------------------------------------------
#   Name: Nikhil Nayyar
#   ID: 1614962
#   CMPUT 274, Fall 2020
#
#   Assignment #1: OO Classifier
#-------------------------------------------- 
import sys
import copy     # for deepcopy()

Debug = False   # Sometimes, print for debugging
InputFilename = "file.input.txt"
TargetWords = [
        'outside', 'today', 'weather', 'raining', 'nice', 'rain', 'snow',
        'day', 'winter', 'cold', 'warm', 'snowing', 'out', 'hope', 'boots',
        'sunny', 'windy', 'coming', 'perfect', 'need', 'sun', 'on', 'was',
        '-40', 'jackets', 'wish', 'fog', 'pretty', 'summer'
        ]

def open_file(filename=InputFilename):
    try:
        f = open(filename, "r")
        return(f)
    except FileNotFoundError:
        # FileNotFoundError is subclass of OSError
        if Debug:
            print("File Not Found")
        return(sys.stdin)
    except OSError:
        if Debug:
            print("Other OS Error")
        return(sys.stdin)

def safe_input(f=None, prompt=""):
    try:
        # Case:  Stdin
        if f is sys.stdin or f is None:
            line = input(prompt)
        # Case:  From file
        else:
            assert not (f is None)
            assert (f is not None)
            line = f.readline()
            if Debug:
                print("readline: ", line, end='')
            if line == "":  # Check EOF before strip()
                if Debug:
                    print("EOF")
                return("", False)
        return(line.strip(), True)
    except EOFError:
        return("", False)

class C274:
    def __init__(self):
        self.type = str(self.__class__)
        return

    def __str__(self):
        return(self.type)

    def __repr__(self):
        s = "<%d> %s" % (id(self), self.type)
        return(s)

class ClassifyByTarget(C274):
    def __init__(self, lw=[]):
        # FIXME:  Call superclass, here and for all classes
        self.type = str(self.__class__)
        self.allWords = 0
        self.theCount = 0
        self.nonTarget = []
        self.set_target_words(lw)
        self.initTF()
        return

    def initTF(self):
        self.TP = 0
        self.FP = 0
        self.TN = 0
        self.FN = 0
        return

    def get_TF(self):
        return(self.TP, self.FP, self.TN, self.FN)

    # FIXME:  Use Python properties
    #     https://www.python-course.eu/python3_properties.php
    def set_target_words(self, lw):
        # Could also do self.targetWords = lw.copy().  Thanks, TA Jason Cannon
        self.targetWords = copy.deepcopy(lw)
        return

    def get_target_words(self):
        return(self.targetWords)

    def get_allWords(self):
        return(self.allWords)

    def incr_allWords(self):
        self.allWords += 1
        return

    def get_theCount(self):
        return(self.theCount)

    def incr_theCount(self):
        self.theCount += 1
        return

    def get_nonTarget(self):
        return(self.nonTarget)

    def add_nonTarget(self, w):
        self.nonTarget.append(w)
        return

    def print_config(self):
        print("-------- Print Config --------")
        ln = len(self.get_target_words())
        print("TargetWords Hardcoded (%d): " % ln, end='')
        print(self.get_target_words())
        return

    def print_run_info(self):
        print("-------- Print Run Info --------")
        print("All words:%3s. " % self.get_allWords(), end='')
        print(" Target words:%3s" % self.get_theCount())
        print("Non-Target words (%d): " % len(self.get_nonTarget()), end='')
        print(self.get_nonTarget())
        return

    def print_confusion_matrix(self, targetLabel, doKey=False, tag=""):
        assert (self.TP + self.TP + self.FP + self.TN) > 0
        print(tag+"-------- Confusion Matrix --------")
        print(tag+"%10s | %13s" % ('Predict', 'Label'))
        print(tag+"-----------+----------------------")
        print(tag+"%10s | %10s %10s" % (' ', targetLabel, 'not'))
        if doKey:
            print(tag+"%10s | %10s %10s" % ('', 'TP   ', 'FP   '))
        print(tag+"%10s | %10d %10d" % (targetLabel, self.TP, self.FP))
        if doKey:
            print(tag+"%10s | %10s %10s" % ('', 'FN   ', 'TN   '))
        print(tag+"%10s | %10d %10d" % ('not', self.FN, self.TN))
        return

    def eval_training_set(self, tset, targetLabel):
        print("-------- Evaluate Training Set --------")
        self.initTF()
        z = zip(tset.get_instances(), tset.get_lines())
        for ti, w in z:
            lb = ti.get_label()
            cl = ti.get_class()
            if lb == targetLabel:
                if cl:
                    self.TP += 1
                    outcome = "TP"
                else:
                    self.FN += 1
                    outcome = "FN"
            else:
                if cl:
                    self.FP += 1
                    outcome = "FP"
                else:
                    self.TN += 1
                    outcome = "TN"
            explain = ti.get_explain()
            print("TW %s: ( %10s) %s" % (outcome, explain, w))
            if Debug:
                print("-->", ti.get_words())
        # self.print_confusion_matrix(targetLabel, tag="XY")
        self.print_confusion_matrix(targetLabel)
        return

    def classify_by_words(self, ti, update=False, tlabel="last"):
        inClass = False
        evidence = ''
        lw = ti.get_words()
        for w in lw:
            if update:
                self.incr_allWords()
            if w in self.get_target_words():    # FIXME Write predicate
                inClass = True
                if update:
                    self.incr_theCount()
                if evidence == '':
                    evidence = w            # FIXME Use first word, but change
            elif w != '':
                if update and (w not in self.get_nonTarget()):
                    self.add_nonTarget(w)
        if evidence == '':
            evidence = '#negative'
        if update:
            ti.set_class(inClass, tlabel, evidence)
        return(inClass, evidence)

    # Could use a decorator, but not now
    def classify(self, ti, update=False, tlabel="last"):
        cl, e = self.classify_by_words(ti, update, tlabel)
        return(cl, e)

    # NEW Lecture 15
    #   Compare with classify_all() in class TrainingSet
    def classify_all(self, ts, update=True, tlabel="classify_all"):
        for ti in ts.get_instances():
            cl, e = self.classify(ti, update=update, tlabel=tlabel)
        return

class ClassifyByTopN(ClassifyByTarget):
    def __init__(self, lw=[]):
        # assign attributes that help in finding word frequency
        self.type = str(self.__class__)
        super().__init__(lw)
        self.word_list = []
        self.freq_list = []
        self.words = dict()
        return

    def target_top_n(self, tset, num=5, label=""):
        self.find_words(tset)
        tw = []
        num += 1 # this is so when you remove the positve label, you still get 
        # the top n words
        
        # append the top n most frequent words into the new target words list
        for i in range(0, num):
            try:
                tw.append(self.word_list[i])
            except:
                pass

        # check if there is a tie for the last most frequent word, if there is
        # add the words that are tied also to the list of target words
        last_indx = i
        for j in range(i, len(self.freq_list)):
            try:
                if self.freq_list[j+1] == self.freq_list[last_indx]:
                    tw.append(self.word_list[j+1])
            except:
                pass
        
        self.set_target_words(tw)
        return
   
    def find_words(self, tset):
        # reset attributes to empty incase word frequency is needed again
        self.word_list = []
        self.freq_list = []
        self.words = dict()

        # get the lines from the training instances
        lines = []
        for ti in tset.get_instances():
            ti_words = ti.get_words()
            ti_words = " ".join(ti_words)
            lines.append(ti_words)

        # separate each line into list of words
        for i in range(0, len(lines)):
            oneline = lines[i].split()
            if oneline[0] == "#negative":
                pass
            else:
                # add each word as a key in dictionary, or increase the value
                # of a word if it appears more than once
                for j in range(0, len(oneline)):
                    if oneline[j] in self.words:
                        self.words[oneline[j]] += 1
                    else:
                        self.words[oneline[j]] = 1
        
        # sort the word list so that every element in the word list matches its 
        # word frequency in the frequecny word list
        sorted_word_list = sorted(self.words, key=self.words.get) # stack overflow thanks
        self.word_list = list(sorted_word_list)
        self.word_list = self.word_list[::-1]

        total = sum(self.words.values())
        self.freq_list = []

        # obtain the frequency of every word by getting the value from
        # the dictionary and dividing by total words
        for i in range(0, len(self.word_list)):
            num_of_word = self.words[self.word_list[i]]
            freq = num_of_word/total
            freq = round(freq, 3)
            self.freq_list.append(freq)

        # sort the frequency list so the elements of the frequency list match
        # the same indexed word in the word list
        self.freq_list.sort()
        self.freq_list = self.freq_list[::-1]
        return 

class TrainingInstance(C274):
    def __init__(self):
        self.type = str(self.__class__)
        self.inst = dict()
        # FIXME:  Get rid of dict, and use attributes
        self.inst["label"] = "N/A"      # Class, given by oracle
        self.inst["words"] = []         # Bag of words
        self.inst["class"] = ""         # Class, by classifier
        self.inst["explain"] = ""       # Explanation for classification
        self.inst["experiments"] = dict()   # Previous classifier runs
        return

    def get_label(self):
        return(self.inst["label"])

    def get_words(self):
        return(self.inst["words"])

    def get_proc_words(self):
        # This method was used to remove the positive label so it would not
        # get preprocessed, the implications of this are explained in the
        # README
        x = self.get_words()
        y = x.pop(0)
        return x, y

    def set_words(self, new_word_list):
        # updates the words after being preprocessed
        self.inst["words"] = new_word_list
        return

    def set_class(self, theClass, tlabel="last", explain=""):
        # tlabel = tag label
        self.inst["class"] = theClass
        self.inst["experiments"][tlabel] = theClass
        self.inst["explain"] = explain
        return

    def get_class_by_tag(self, tlabel):             # tlabel = tag label
        cl = self.inst["experiments"].get(tlabel)
        if cl is None:
            return("N/A")
        else:
            return(cl)

    def get_explain(self):
        cl = self.inst.get("explain")
        if cl is None:
            return("N/A")
        else:
            return(cl)

    def get_class(self):
        return self.inst["class"]

    def process_input_line(
                self, line, run=None,
                tlabel="read", inclLabel=True
            ):
        for w in line.split():
            if w[0] == "#":
                self.inst["label"] = w
                # FIXME: For testing only.  Compare to previous version.
                if inclLabel:
                    self.inst["words"].append(w)
            else:
                self.inst["words"].append(w)

        if not (run is None):
            cl, e = run.classify(self, update=True, tlabel=tlabel)
        return(self)

    def convert_lower(self):
        lower_words = []
        # change all the words in a list to lowercase and add them to new list
        for word in self.get_words():
            word = word.lower()
            lower_words.append(word)

        # set the words to the new lowercased words
        self.set_words(lower_words)
        return

    def remove_punc(self):
        spec_chars = "! @ # - $ % & ' ( ) * + , . / : ; < = > ? _ [ ] ^ ` { | } ~ '"
        spec_list = spec_chars.split(" ")
        no_punc_words = []

        wordList, label = self.get_proc_words()
        # check every character in every word in the list
        for word in wordList:
            new_word = ""
            for char in word:
                # if the characters are not symbols, add them to a new word
                if char not in spec_list:
                    new_word = new_word + char
            # add all the new words ridden of punctuation and sybols to a list
            no_punc_words.append(new_word)

        # if no mode was selected, the label would be reinserted here
        no_punc_words.insert(0, label)
        # set the words to the new removed punctuation words
        self.set_words(no_punc_words)
        return

    def remove_nums(self):
        nums = "0 1 2 3 4 5 6 7 8 9"
        num_list = nums.split(" ")
        no_num_words = []
        num_word = ""
        # check every character of every word in the list
        for word in self.get_words():
            new_word = ""
            no_num = 0
            for char in word:
                # if the character is not a number, add it to a new word
                if char not in num_list:
                    new_word = new_word + char
                    no_num = 1
                # if all the charcters are a number, keep it as all numbers
                elif char in num_list:
                    num_word = num_word + char
            # after checking each word, either add the number ridden word to a
            # list, or add the word that was comprised of only numbers
            if no_num == 1:
                no_num_words.append(new_word)
            else:
                no_num_words.append(num_word)
                num_word = ""
        
        # set the words to the new number ridden words
        self.set_words(no_num_words)
        return

    def remove_stop(self):
        stop_list = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
        "you","your","yours", "yourself", "yourselves", "he", "him", "his", 
        "himself", "she", "her","hers", "herself", "it", "its", "itself", 
        "they", "them", "their", "theirs","themselves", "what", "which","who",
        "whom", "this", "that", "these", "those","am", "is", "are", "was", 
        "were", "be","been", "being", "have", "has", "had","having", "do", 
        "does", "did", "doing", "a", "an","the", "and", "but", "if","or", 
        "because", "as", "until", "while", "of", "at", "by", "for", "with",
        "about", "against", "between", "into", "through", "during", "before",
        "after","above", "below", "to", "from", "up", "down", "in", "out", 
        "on", "off", "over","under", "again", "further", "then", "once", "here",
        "there", "when", "where","why", "how", "all", "any", "both", "each", 
        "few", "more", "most", "other","some", "such", "no", "nor", "not", 
        "only", "own", "same", "so", "than","too", "very", "s", "t", "can", 
        "will", "just", "don", "should", "now"]

        no_stop = []
        # check every word to see if its a stop word, and add only the words
        # that are not to a new list
        for word in self.get_words():
            if word not in stop_list:
                no_stop.append(word)

        # set the words to the new words without stops
        self.set_words(no_stop)
        return

    def preprocessing_words(self, mode=""):
        # Do all the preprocessing on the words, or keep certain characters
        # based on mode select
        self.convert_lower()
        if mode != "keep-symbols":
            self.remove_punc()
        if mode != "keep-digits":
            self.remove_nums()
        if mode != "keep-stops": # check mode types
            self.remove_stop()
        # this last if statement adds the label into the words in case
        # keep-stops mode was chosen
        if mode == "keep-stops":
            temp_words, label = self.get_proc_words()
            temp_list = []
            temp_list = self.get_words()
            temp_list.insert(0, label)
        return 

class TrainingSet(C274):
    def __init__(self):
        self.type = str(self.__class__)
        self.inObjList = []     # Unparsed lines, from training set
        self.inObjHash = []     # Parsed lines, in dictionary/hash
        # NEW Lecture 15
        self.variable = dict()
        return

    def get_instances(self):
        return(self.inObjHash)      # FIXME Should protect this more

    def get_lines(self):
        return(self.inObjList)      # FIXME Should protect this more
    
    def set_instances(self, newInst):
        # used to update after preprocessing
        self.inObjHash = newInst
        return
    
    def set_lines(self, newLines):
        # used to update after preprocessing
        self.inObjList = newLines
        return

    def print_training_set(self):
        print("-------- Print Training Set --------")
        z = zip(self.inObjHash, self.inObjList)
        for ti, w in z:
            lb = ti.get_label()
            cl = ti.get_class_by_tag("last")     # Not used
            explain = ti.get_explain()
            print("( %s) (%s) %s" % (lb, explain, w))
            if Debug:
                print("-->", ti.get_words())
        return

    # NEW Lecture 15
    #    Compare with new method (from assignment):
    #        preprocess() in class TrainingSet
    #   Compare with classify_all() in class ClassifyByTarget
    def classify_all(self, run, update=True, tlabel="classify_all"):
        for ti in self.get_instances():
            cl, e = run.classify(ti, update=update, tlabel=tlabel)
        return

    # NEW Lecture 15
    def set_env_variable(self, k, v):
        self.variable[k] = v
        return

    # NEW Lecture 15
    def get_env_variable(self, k):
        if k in self.variable:
            return(self.variable[k])
        else:
            return ""

    # NEW Lecture 15
    def inspect_comment(self, line):
        if len(line) > 1 and line[1] != ' ':      # Might be variable
            v = line.split(maxsplit=1)
            self.set_env_variable(v[0][1:], v[1])
        return

    def process_input_stream(self, inFile, run=None):
        assert not (inFile is None), "Assume valid file object"
        cFlag = True
        while cFlag:
            line, cFlag = safe_input(inFile)
            if not cFlag:
                break
            assert cFlag, "Assume valid input hereafter"

            # Check for comments
            if line[0] == '%':  # Comments must start with %
                # NEW Lecture 15
                self.inspect_comment(line)
                continue
            
            # Save the training data input, by line
            self.inObjList.append(line)
            # Save the training data input, after parsing
            ti = TrainingInstance()
            ti.process_input_line(line, run=run)
            self.inObjHash.append(ti)
        return
   
    def preprocess(self, mode=""):
        # preprocess all the training instances in the training set using
        # preprocess_words in class TrainingInstance
        unparsedlines = self.get_lines()
        processed_inst = []
        for i in range(0,len(unparsedlines)):
            ti = TrainingInstance()
            ti.process_input_line(unparsedlines[i])
            ti.preprocessing_words(mode)
            unparsedlines[i] = " ".join(ti.get_words())
            processed_inst.append(ti)

        self.set_instances(processed_inst)
        return

    def return_nfolds(self, num=3):
        new_obj_list = []
        nfold_list = []
        tot_inst = self.get_instances()

        # make the amount of deepcopy objects based on the input parameter num
        for i in range(1, num+1):
            new_obj = copy.deepcopy(self)
            new_obj_list.append(new_obj)
            x = []
            nfold_list.append(x)

        # use the round robin technique to create the n folds
        j = 0
        for i in range(0, len(tot_inst)):
            try:
                nfold_list[j].append(tot_inst[i])
            except:
                pass

            if j + 1 >= len(nfold_list):
                j = 0
            else:
                j += 1

        # give each newly made object the nfolded instances
        for i in range(0, num):
            new_obj_list[i].set_instances(nfold_list[i])

        return new_obj_list

    def copy(self):
        # create a copy of a training set
        tsetcopy = copy.deepcopy(self)
        return tsetcopy

    def add_fold(self, tset):
        '''
        add new instances by getting the current instances and adding on
        the new ones. The new instances come via deepcopy, and the lines
        are also added via deepcopy for use in the method evaluate training
        set
        '''
        copied_obj = tset.copy()
        current_inst = self.get_instances()
        copied_inst = copied_obj.get_instances()
        tot_inst = current_inst + copied_inst
        copied_obj.set_instances(tot_inst)
        self.set_lines(copied_obj.get_lines())
        self.set_instances(copied_obj.get_instances())
        return

def basemain():
    tset = TrainingSet()
    run1 = ClassifyByTarget(TargetWords)
    print(run1)     # Just to show __str__
    lr = [run1]
    print(lr)       # Just to show __repr__

    argc = len(sys.argv)
    if argc == 1:   # Use stdin, or default filename
        inFile = open_file()
        assert not (inFile is None), "Assume valid file object"
        tset.process_input_stream(inFile, run1)
        inFile.close()
    else:
        for f in sys.argv[1:]:
            inFile = open_file(f)
            assert not (inFile is None), "Assume valid file object"
            tset.process_input_stream(inFile, run1)
            inFile.close()

    if Debug:
        tset.print_training_set()
    run1.print_config()
    run1.print_run_info()
    run1.eval_training_set(tset, '#weather')

    return

def base3main():
    tset = TrainingSet()
    run1 = ClassifyByTopN()       # NEW No default target words
    argc = len(sys.argv)
    if argc == 1:   # Use stdin, or default filename
        inFile = open_file()
        assert not (inFile is None), "Assume valid file object"
        tset.process_input_stream(inFile, run1)
        inFile.close()
    else:
        for f in sys.argv[1:]:
            inFile = open_file(f)
            assert not (inFile is None), "Assume valid file object"
            tset.process_input_stream(inFile, run1)
            inFile.close()

    print("********************************************")
    pfeatures = tset.get_env_variable("pos-features")
    print("pos-features: ", pfeatures)
    plabel = tset.get_env_variable("pos-label")
    print("pos-label: ", plabel)
    print("********************************************")
  
    tsetOrig = tset.copy()

    ##--- Original Classification --##
    run1.set_target_words(pfeatures.strip().split())
    run1.classify_all(tset)     # See classify_all() in class TrainingSet
    run1.print_config()
    run1.eval_training_set(tset, plabel)

    # *********************************************
    # *** Look here *** for Task 1 and 2
    # *********************************************
    tset.preprocess()           # Call to new Task I method
    run1.target_top_n(tset, 3, plabel)
  
    tw = run1.get_target_words()
    if plabel in tw:     # Remove (once) a word, if also label
        tw.remove(plabel)
    run1.set_target_words(tw)

    run1.classify_all(tset)     # Redo the classification
    run1.print_config()         # Print New config and evaluation
    run1.eval_training_set(tset, plabel)

    ## --- N folds --- ##
    ts_3 = tset.return_nfolds()
    # FOLD 0
    train0 = TrainingSet()
    test0 = TrainingSet()
    test0.add_fold(ts_3[0])
    train0.add_fold(ts_3[1])
    train0.add_fold(ts_3[2])

    run1.target_top_n(train0, num=3, label=plabel)
    tw = run1.get_target_words()
    if plabel in tw:     # Remove (once) a word, if also label
        tw.remove(plabel)
    run1.set_target_words(tw)

    run1.classify_all(test0)
    run1.print_config()
    run1.eval_training_set(test0, plabel)

    ## FOLD 1
    test1 = TrainingSet()
    train1 = TrainingSet()
    train1.add_fold(ts_3[0])
    test1.add_fold(ts_3[1])
    train1.add_fold(ts_3[2])

    run1.target_top_n(train1, num=3, label=plabel)
    tw = run1.get_target_words()
    if plabel in tw:     # Remove (once) a word, if also label
        tw.remove(plabel)
    run1.set_target_words(tw)
    run1.classify_all(test1)
    run1.print_config()
    run1.eval_training_set(test1, plabel)

    # FOLD 2
    test2 = TrainingSet()
    train2 = TrainingSet()
    train2.add_fold(ts_3[0])
    train2.add_fold(ts_3[1])
    test2.add_fold(ts_3[2])

    run1.target_top_n(train2, num=3, label=plabel)
    tw = run1.get_target_words()
    if plabel in tw:     # Remove (once) a word, if also label
        tw.remove(plabel)
    run1.set_target_words(tw)
    run1.classify_all(test2)
    run1.print_config()
    run1.eval_training_set(test2, plabel)
    
    tp, fp, tn, fn = run1.get_TF()
    precision = float(tp) / float( tp + fp )
    recall = float(tp) / float( tp + fn )
    accuracy = float( tp + tn ) / float( tp + tn + fp + fn )
    print("Accuracy:  %3.2g = " % accuracy, end='')
    print("(%d + %d) / (%d + %d + %d + %d)" % (tp, tn, tp, tn, fp, fn) )
    print("Precision: %3.2g = " % precision, end='')
    print("%d / (%d + %d)" % (tp, tp, fp))
    print("Recall:    %3.2g = " % recall, end='' )
    print("%d / (%d + %d)" % (tp, tp, fn))
    
    
    return


if __name__ == "__main__":
    base3main()
