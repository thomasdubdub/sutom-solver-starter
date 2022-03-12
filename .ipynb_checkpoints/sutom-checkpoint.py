from collections import defaultdict, Counter
from collections.abc import Set
from itertools import combinations

# SUTOM sizes
WORD_MIN_SIZE = 6
WORD_MAX_SIZE = 9

class Dictionary(Set):
    def __init__(self, words: set):
        self.words = set()
        for word in words:
            wd = word.strip().upper() 
            if (len(wd) >= WORD_MIN_SIZE) and (len(wd) <= WORD_MAX_SIZE):
                self.words.add(wd)
        
        self._init_variables()
        
    def _init_variables(self):
        self.words_by_len = defaultdict(set)
        self.sutom_words = defaultdict(
            lambda: defaultdict(set)
        )  # dictionary: key 1 = nb of letters key 2 = first letter
        self._d = defaultdict(
            lambda: defaultdict(set)
        )  # dictionary: key 1 = nb of letters key 2 = sorted letters
        self.letter_occurrences = defaultdict(int)
        self.min_size, self.max_size = (WORD_MAX_SIZE, WORD_MIN_SIZE) 
        
        self.counters = {}  
        self.sutom_counters = {} # without first letter
        alphabet_set = set()
        for wd in self.words:
            self.words_by_len[len(wd)].add(wd)
            self.sutom_words[len(wd)][wd[0]].add(wd)
            self._d[len(wd)]["".join(sorted(wd))].add(wd)
            self.counters[wd] = Counter(wd)
            self.sutom_counters[wd] = Counter(wd[1:])
            if len(wd) > self.max_size:
                self.max_size = len(wd)
            if len(wd) < self.min_size:
                self.min_size = len(wd)
            alphabet_set.update(wd)
            for l in wd:
                self.letter_occurrences[l] +=1
                
        self.alphabet = sorted(alphabet_set)
        self.max_letter_occurence = {k: max(v.values()) for k, v in self.counters.items()}
        self.sutom_max_letter_occurence = {k: max(v.values()) for k, v in self.sutom_counters.items()}
        self.letter_occurrences = dict(sorted(self.letter_occurrences.items(), key=lambda item: item[1], reverse= True))

    @classmethod
    def from_txt(cls, file_name: str, sep: str = " ") -> "Dictionary":
        file_set = set()
        with open(file_name, encoding="utf-8", mode="r") as f:
            for l in f.readlines():
                wd_list = l.strip().split(sep)
                for wd in wd_list:
                    wd = wd.strip()
                    if (len(wd) >= WORD_MIN_SIZE) and (len(wd) <= WORD_MAX_SIZE):
                        file_set.add(wd.upper())

        return cls(file_set)
    
    def __iter__(self):
        return iter(self.words)

    def __contains__(self, value: str):
        wd = value.strip().upper()
        return wd in self.words

    def __len__(self):
        return len(self.words)

    def __add__(self, other):
        return Dictionary(self.words | other.words)
        
    def __repr__(self) -> str:
        return f"Dictionary including {len(self)} words (size {self.min_size} to {self.max_size}) with alphabet of {len(self.alphabet)} letters"

    def save(self, output_file_name):
        with open(output_file_name, "w") as f:
            for wd in self.words:
                f.write(wd)
                f.write('\n')
    
    def wordlist(
        self,
        nb_letters=0,
        with_letters="",
        without_letters="",
        startswith="",
        endswith="",
    ):  # get list of all words with 'nb_letters' letters and including the letters 'letters'
        wds = self.words if nb_letters < 2 else self.words_by_len[nb_letters]

        l = []
        for wd in wds:
            with_letter = True
            for letter in set(with_letters):
                if wd.count(letter.upper()) < with_letters.count(letter):
                    with_letter = False
            without_letter = True
            for letter in without_letters:
                if wd.count(letter.upper()) > 0:
                    without_letter = False

            if all(
                [
                    with_letter,
                    without_letter,
                    (wd.startswith(startswith)),
                    (wd.endswith(endswith)),
                ]
            ):
                l.append(wd)
        return sorted(l)

    def subwords(self, wd: str) -> list:
        subwds = []
        for i in range(len(wd), 1, -1):
            lst = []
            for j in combinations(wd, i):
                swd = "".join(sorted(j))
                if swd in self._d[i].keys():
                    lst.extend(self._d[i][swd])
            subwds.extend(sorted(lst))
        return subwds

    def palindromes(self) -> list:
        pals = [wd for wd in self.words if wd[::-1] == wd]
        return sorted(pals)

    def anagram(
        self, letters: str
    ) -> list:  # get all valid words formed by all the letters in 'wd'
        o_letters = "".join(sorted(letters))
        wds = self._d[len(letters)].get(o_letters, set())
        wds.discard(letters)  # if input letters was a valid word
        return sorted(wds)

    def cousin(self, wd: str) -> list:
        # return list of cousins of word wd
        cousins = []
        for i in range(len(wd)):
            for letter in self.alphabet:
                c = wd[:i] + letter + wd[i + 1 :]
                if (c != wd) and (c in self.words):
                    cousins.append(c)
        return cousins

    def suffixes(self, wd: str):  # return list of suffixes
        suffixes = []
        for key in self._d.keys():
            if key > len(wd):
                for k, v in self._d[key].items():
                    if all(letter in k for letter in wd):
                        for word in self._d[key][k]:
                            if word[: len(wd)] == wd:
                                suffixes.append(word)
        return sorted(suffixes)

    def anagram_plus_one(
        self, wd: str
    ) -> dict:  # return dict letter - new word with only one different letter
        m = defaultdict(list)
        anagrams = []
        for letter in self.alphabet:
            wds = self.anagram(wd + letter)
            if len(wds) > 0:
                m[letter].extend(wds)
        return m
    
    def get_answer(self, candidate, target): # SUTOM answer
        rep =  ["*" for l in candidate]
        
        # Number of infos already given on each letter
        infos_right, infos_wrong = (defaultdict(int), defaultdict(int))
        remaining_indices = []
        
        for i,l in enumerate(candidate):
            if target[i]==l:
                rep[i] = "R" # ROUGE = right position
                infos_right[l] += 1
            else:
                remaining_indices.append(i)
                
        for i in remaining_indices:
            l = candidate[i]
            if self.counters[target][l] > infos_right[l] + infos_wrong[l]:
                    rep[i] = "J" # JAUNE = wrong position
                    infos_wrong[l] += 1    
        
        return ''.join(rep)
    
    def _right_spots_filter(self, wordlist, right_spots):
        filter_list = wordlist.copy()
        for i, l in right_spots.items():
            if i > 0: # first spot useless
                for wd in list(filter_list):
                    if wd[i] != l:
                        filter_list.discard(wd)
        return filter_list
    
    def _get_right_spots(self, sutom_answers):
        return {i:proposal[i] for proposal, answer in sutom_answers.items() for i, l in enumerate(answer) if l == "R"}
    
    def _wrong_spot_filter(self, wordlist, wrong_spots):
        filter_list = wordlist.copy()
        for i, l in wrong_spots.items():
            for wd in list(filter_list):
                if l not in wd[1:]:
                    filter_list.discard(wd)
                elif wd[i] == l: # should be "R"
                    filter_list.discard(wd)
        return filter_list
    
    def _get_wrong_spots(self, sutom_answers):
        return {i:proposal[i] for proposal, answer in sutom_answers.items() for i, l in enumerate(answer) if l == "J"}
    
    def _absent_letters_filter(self, wordlist, absent_letters):
        filter_list = wordlist.copy()
        for letter in absent_letters:
            for wd in list(filter_list):
                if letter in wd[1:]: # not the first letter
                    filter_list.discard(wd)
        return filter_list
    
    def _get_absent_letters(self, first_letter, sutom_answers, no_repetition=False):
        absent_letters = set()
        if no_repetition:
            return {l for (proposal,answer) in sutom_answers.items() for (i,l) in enumerate(proposal) if answer[i] == "*"}
        for proposal, answer in sutom_answers.items():
            for i, l in enumerate(proposal): # all letters incl. the first letter
                if answer[i] == "*":
                    if self.max_letter_occurence[proposal] == 1:
                        absent_letters.add(l)
                    elif self.counters[proposal][l] == 1:
                        absent_letters.add(l)
                    elif (self.counters[proposal][l] == 2) and (l == first_letter):
                        absent_letters.add(l)
        return absent_letters
    
    def solve_from_list(self, wordlist, sutom_answers):
        final_wordlist = wordlist.copy()
        for proposal, answer in sutom_answers.items():
            for wd in list(final_wordlist):
                if self.get_answer(proposal, wd) != answer:
                    final_wordlist.discard(wd)
        return final_wordlist
    
    def solve(self, nb_letters, first_letter, sutom_answers, no_repetition=False):
        initial_wordlist = self.sutom_words[nb_letters][first_letter]
        right_spots = self._get_right_spots(sutom_answers)
        wrong_spots = self._get_wrong_spots(sutom_answers)
        absent_letters = self._get_absent_letters(first_letter, sutom_answers, no_repetition=no_repetition)
        
        wdlist1 = self._right_spots_filter(initial_wordlist, right_spots)
        wdlist2 = self._wrong_spot_filter(wdlist1, wrong_spots)
        wdlist3 = self._absent_letters_filter(wdlist2, absent_letters)
        
        if no_repetition:
            return wdlist3
        return self.solve_from_list(wdlist3, sutom_answers)
        
    
  
        
            