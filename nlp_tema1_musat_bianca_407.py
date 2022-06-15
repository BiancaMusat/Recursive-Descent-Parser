# -*- coding: utf-8 -*-
"""NLP_Tema1_Musat_Bianca_407.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_UBSryD7BurSJt6iQcV9VggcKh6G6cIv

# Recursive descent parsing (top-down)

Name: Musat Bianca-Stefania

Group: 407, Artificial Intelligence

## Algorithm description:


Recursive descent parsing is a top-down approach to the parsing problem. It takes a grammar and a sentence and, starting from the start symbol of the grammar (usually S, generally the symbol that appears only in the left hand side of any rule) it expands the tree using the rules given by the grammar until it reaches the words in the sentence. In order to remember the subtrees that haven't been expanded yet, we will use a locations list, which is a list of lists containing the path (from the root to the leaf, as a list of symbols from the grammar that represent the value of each node from the path) of each subtree that hasn't been expanded. The locations list will be used as a stack, adding the new locations at the beggining of the list.

The recursive method has 4 big steps:

1. We check if we still have words to match and if the locations list is empty. In this case the parsing failed because we still have words to match, but we cannot expand the tree anymore.
2. We check if we covered all the words in the sentence and if the locations list is empty. In this case the parsing succeded and we can add the tree to the solutions.
3. We check the leaf corresponding to the first subtree in the locations list. If that leaf is a word and that word is the one we are currently trying to match, then we can consider that we mached it and continue with the next word, removing the subtree from the locations list.
4. If that leaf is not a word, but a rule that can be expanded, we retrieve from the grammar all the ways in which we can expand that terminal and add them to a list of rules. For each rule in that list, we create a subtree that has as root the terminal and as children the symbols in the rule. We then add that subtree to the initial tree and update the locations list, by removing the first element from it and adding at the beggining an updated location for each symbol in the rule. We than continue the recursive algorithm for each new tree.

Limitation:
  Unfortunatelly, the recursive descent parsing algorithm can result in an infinite loop if we have left-recursion in our grammar. That can be observed with both nltk algorithm and my implementation when testing on the example with the elephant. The algorithms manage to find both interpretations of the sentence "I shot an elephant in my pijamas", but after finding those it goes into an infinite loop while searching for more possible parsing solutions. On the other example, the one with the sentence "I am watching a show", both algorithms finish successfully, as there is no left-recursion in the grammar definition.
"""

!pip install nltk

import nltk

nltk.download('punkt')
nltk.download('wordnet')

import string
import copy

"""## Using NLTK RecursiveDescentParser as groundtruth

Using RecursiveDescentParser from nltk library to generate an output that will be compared against the output of my alorithm.

If we compare the output generated by the nltk implementation with the output generated by my implementation (see the end of this notebook) we can observe that they are identical (if we ignore the small differences in the style of the output).
"""

my_grammar = nltk.CFG.fromstring('''
S -> NP VP
S -> VP
NP -> DT NN
NP -> DT JJ NN
NP -> PRP
VP -> VBP NP
VP -> VBP VP
VP -> VBG NP
VP -> TO VP
VP -> VB
VP -> VB NP
NN -> "show" | "book"
PRP -> "I"
VBP -> "am"
VBG -> "watching"
VB -> "show"
DT -> "a" | "the"
MD -> "will"''')
sent = ['I', 'am', 'watching', 'a', 'show']
parser = nltk.parse.recursivedescent.RecursiveDescentParser(my_grammar, trace=0)
for tree in parser.parse(sent):
  print(tree)

my_grammar = nltk.CFG.fromstring('''
S -> NP VP
PP -> P NP
NP -> Det N | Det N PP | "I"
VP -> V NP | VP PP
Det -> "an" | "my"
N -> "elephant" | "pajamas"
V -> "shot"
P -> "in"''')
sent = ["I", "shot", "an", "elephant", "in", "my", "pajamas"]
parser = nltk.parse.recursivedescent.RecursiveDescentParser(my_grammar, trace=0)
for tree in parser.parse(sent):
  print(tree)

"""## Input description

The 2 grammar files that I will test the implementation on have the following content:

grammar:
  ```
  S -> NP VP
  S -> VP
  NP -> DT NN
  NP -> DT JJ NN
  NP -> PRP
  VP -> VBP NP
  VP -> VBP VP
  VP -> VBG NP
  VP -> TO VP
  VP -> VB
  VP -> VB NP
  NN -> "show" | "book"
  PRP -> "I"
  VBP -> "am"
  VBG -> "watching"
  VB -> "show"
  DT -> "a" | "the"
  MD -> "will"

  ```
grammar2:
  ```
  S -> NP VP
  PP -> P NP
  NP -> Det N | Det N PP | "I"
  VP -> V NP | VP PP
  Det -> "an" | "my"
  N -> "elephant" | "pajamas"
  V -> "shot"
  P -> "in"
```
The sentence for the first grammar: "I am watching a show."

The sentence for the second grammar: "I shot an elephant in my pajamas."

## Recursive descent parsing implementation
"""

def recursiveDescentWrapper(grammar_file, sentence):
    """
    Gets the grammar file that we want to use and a sentence that we want to parse using
    that grammar and transforms the grammar into a dictionary and the sentence into a
    list of tokens in order to be used by the recursiveDescent algorithm.

    Parameters
    ----------
    grammar_file : str
        The grammar file to be used
    sentence : str
        The sentece that we want to parse

    Returns
    -------
    cfg: dict
        A dictionary whose keys are the left hand side of each rule, 
        and the values are represented by a list of lists, contating the right hand side of each rule
    sentence: list of str
        The tokenized sentence (with the punctuation removed).
    """
    # read grammar from file
    with open(grammar_file) as f:
        grammar = f.read()

    # tokenize and remove punctuation from the input sentence
    tokenized_sentence = nltk.word_tokenize(sentence)
    tokenized_sentence = [t for t in tokenized_sentence if t not in string.punctuation]
    
    # transform the grammar into a dictionary
    split_grammar = grammar.split('\n')
    cfg = {}
    for rule in split_grammar:
        components = rule.split(' ')
        if len(components) >= 3:
            head = components[0]  # this is the lhs of each rule
            all_symbols_list = []  # this will be the list of rules that mach the lhs
            l = []  # this is an individual rule that mach the lhs
            for i in range(2, len(components)):
                if components[i] == '|':
                    all_symbols_list.append(l)
                    l = []
                else:
                    l.append(components[i])
            all_symbols_list.append(l)

            # add the rules that corespond to the head (lhs) in the dictionary
            for ent in all_symbols_list:
                if head in cfg:
                    cfg[head].append(ent)
                else:
                    cfg[head] = [ent]
    return cfg, tokenized_sentence

class TreeNode:
    """
    A class used to represent a node in a tree

    Attributes
    ----------
    val : str
        The value associated with the node
    children : list of nodes
        The list of children of each node
    """

    def __init__(self, val, children=[]):
        self.val = val
        self.children = children
    def __repr__(self):
        return "Self implementation of a tree"

def append(tree, location, node):
    """
    Gets a tree and a location in the tree (list of nodes' values) and traverse the tree from root,
    going on the path of that child node that has the associated value in the list. Once it reaches
    the final node in the locations list, it adds the 'node' children as its children.

    Parameters
    ----------
    tree : TreeNode
        The root of a tree
    location : list of str
        A list of nodes' values (eg. ['S', 'NP', 'DT'] -> will go from the root which has the value S, to
        its child node with the value NP; then, it will search through the children of the node with the value NP
        that child that has the value DT)
    node : TreeNode
        Node to be appended to the tree, at the location given by the location parameter

    Returns
    -------
    head : TreeNode
        The root of the new tree
    """

    new_tree = copy.deepcopy(tree)
    head = new_tree
    for l in location:
        for ch in new_tree.children:
            if ch.val == l:
                new_tree = ch
                break
    new_tree.children = []
    for ch in node.children:
        new_tree.children.append(ch)
    return head

def printTree(node):
    """
    Gets the root of the tree and returns a string contating the visual representation of the whole tree.

    Parameters
    ----------
    node : TreeNode
        The root of a tree
        
    Returns
    -------
    pr : str
        The visual (string) representation of the whole tree.
    """

    pr = " (" + str(node.val)
    for ch in node.children:
        pr += printTree(ch)
    pr += " )"
    return pr

def check_lex_symbol(symbol):
    """
    Gets a symbol from the grammar and checks if it is a lexical symbol (an actual word).

    Parameters
    ----------
    symbol : str
        The symbol
        
    Returns
    -------
    bool
        True value if the symbol is lexical; False otherwise
    """

    if symbol[0] == "\"":
          return True
    return False

def get_start_symbol(cfg):
    """
    Gets the start symbol of the grammar (the symbol that appears only in lhs of the rules).

    Parameters
    ----------
    cfg : dict
        The grammar
        
    Returns
    -------
    k : str
        The start symbol
    """

    keys = cfg.keys()
    values = cfg.values()
    for k in keys:
        if k not in values:
              return k

def rec(cfg, sentence, tree, locations):
    """
    Gets the grammar, the sentence to be parsed, the current tree and the locations and
    recursively construct the tree corresponding to the sentence parsing.

    Parameters
    ----------
    cfg : dict
        The grammar
    sentence : list of str
        The sentence to be parsed
    tree : TreeNode
        The head of the current tree
    locations : list of lists of str
        The list of tree locations

    Returns
    -------
    list of TreeNode
        The tree or trees resulted after the parsing has been completed
    """

    # if we still have words that haven't been covered, but the locations is empty, the parsing failed as we cannot expand the tree anymore
    if len(sentence) > 0 and len(locations) == 0:
        return

    # if we don't have any more words to cover and the locations is empty, it means we found a correct parsing of the sentence
    elif len(sentence) == 0 and len(locations) == 0:
        yield tree

    # if the terminal (leaf) corresponding to the first location list in the locations is a word
    # and it corresponds to the word that we are currently trying to match, it means we found
    # a correct parsing for this word and we can move on to the next word in the sentence
    elif len(locations[0]) > 0 and str(locations[0][-1])[0] == "\"":  # check if the last symbol in the first location list is a word
        terminal = locations[0][-1]
        if len(sentence) > 0 and terminal[1:-1] == sentence[0]:  # check if that word corresponds to the word in sentence that we are currently trying to match
          yield from rec(cfg, sentence[1:], tree, locations[1:])  # continue the parsing for the rest of the words

    # else, it means we need to expand the terminal (leaf)
    else:
        rules = []  # will conatin all grammar rules that have as the lhs symbol the terminal
        for k in cfg:
            if len(locations[0]) > 0 and k == str(locations[0][-1]):
                rules = cfg[k]
                break
            if len(locations[0]) == 0 and k == get_start_symbol(cfg):  # if we've just started the parsing and the tree has only the start symbol, expand the start symbol
                rules = cfg[k]
                break

        # for each matching rule, make a TreeNode corresponding to the expanding of the lch (terminal) with that rule
        # and generate the new tree; the locations must be updated with a new location list for every added symbol in each rule
        for rule in rules:
            children = []
            for r in rule:
                children.append(TreeNode(r, []))
            sub_tree = TreeNode(k, children)
            new_tree = append(tree, locations[0], sub_tree)
            new_locations = [locations[0] + [i,] for i in rule]
            yield from rec(cfg, sentence, new_tree, new_locations + locations[1:])

def recursiveDescent(cfg, sentence):
    """
    Gets the grammar and the sentence to be parsed and calls the rec algorithm that does the parsing.
    The parsing will start from the start symbol (usually S) and with locations consisting of an empty list.

    Parameters
    ----------
    cfg : dict
        The grammar
    sentence : list of str
        The sentence to be parsed

    Returns
    -------
    TreeNode
        The tree(s) resulted after the parsing has been completed
    """

    root = TreeNode(get_start_symbol(cfg), [])  # first node of the tree, contating the start symbol and an empty list of children
    locations = [[]]
    return rec(cfg, sentence, root, locations)

sentence = "I am watching a show."
cfg, tokenized_sentence = recursiveDescentWrapper('grammar.txt', sentence)
for tree in recursiveDescent(cfg, tokenized_sentence):
    print(printTree(tree))

sentence = "I shot an elephant in my pajamas."
cfg, tokenized_sentence = recursiveDescentWrapper('grammar2.txt', sentence)
for tree in recursiveDescent(cfg, tokenized_sentence):
    print(printTree(tree))