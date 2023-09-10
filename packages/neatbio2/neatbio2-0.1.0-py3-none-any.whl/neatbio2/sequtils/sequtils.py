# export PATH="$PATH:$HOME/.local/bin"

#!/urs/bin/env
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

# Translation
CodonTable = {
    'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S', 'AGC': 'S', 'AGT': 'S', # Serine
    'TTC': 'F', 'TTT': 'F',  # Phenylalanine
    'TTA': 'L', 'TTG': 'L',  # Leucine
    'TAC': 'Y', 'TAT': 'Y',  # Tyrosine
    'TAA': '*', 'TAG': '*', 'TGA': '*',  # Stop
    'TGC': 'C', 'TGT': 'C',   # Cysteine
    'TGG': 'W',    # Tryptophan
    'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L', # Leucine
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P', # Proline
    'CAC': 'H', 'CAT': 'H',   # Histidine
    'CAA': 'Q', 'CAG': 'Q',   # Glutamine
    'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R', # Arginine
    'ATA': 'I', 'ATC': 'I', 'ATT': 'I',  # Isoleucine
    'ATG': 'M',    # Methionine
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T', # Threonine
    'AAC': 'N', 'AAT': 'N',  # Asparagine
    'AAA': 'K', 'AAG': 'K',   # Lysine
    'AGA': 'R', 'AGG': 'R',   # Arginine
    'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V', # Valine
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A', # Alanine
    'GAC': 'D', 'GAT': 'D',   # Aspartate
    'GAA': 'E', 'GAG': 'E',   # Glutamate
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G' # Glycine
}

CodonTable_lower = {
    'tca': 'S', 'tcc': 'S', 'tcg': 'S', 'tct': 'S', 'agc': 'S', 'agt': 'S',  # Serine
    'ttc': 'F', 'ttt': 'F',  # Phenylalanine
    'tta': 'L', 'ttg': 'L', 'cta': 'L', 'ctc': 'L', 'ctg': 'L', 'ctt': 'L',  # Leucine
    'tac': 'Y', 'tat': 'Y',  # tyrosine
    'taa': '*', 'tag': '*', 'tga': '*',  # stop
    'tgc': 'C', 'tgt': 'C',  # Cysteine
    'tgg': 'W',    # tryptophan
    'cca': 'P', 'ccc': 'P', 'ccg': 'P', 'cct': 'P', # proline
    'cac': 'H', 'cat': 'H',   # histidine
    'caa': 'Q', 'cag': 'Q',   # glutamine
    'cga': 'R', 'cgc': 'R', 'cgg': 'R', 'cgt': 'R', 'aga': 'R', 'agg': 'R',  # arginine
    'ata': 'I', 'atc': 'I', 'att': 'I',  # isoleucine
    'atg': 'M',    # methionine
    'aca': 'T', 'acc': 'T', 'acg': 'T', 'act': 'T', # threonine
    'aac': 'N', 'aat': 'N',  # asparagine
    'aaa': 'K', 'aag': 'K',   # lysine
    'gta': 'V', 'gtc': 'V', 'gtg': 'V', 'gtt': 'V', # valine
    'gca': 'A', 'gcc': 'A', 'gcg': 'A', 'gct': 'A', # alanine
    'gac': 'D', 'gat': 'D',   # aspartate
    'gaa': 'E', 'gag': 'E',   # glutamate
    'gga': 'G', 'ggc': 'G', 'ggg': 'G', 'ggt': 'G' # glycine
}

# Amino acid keys
full_amino_acid_name = {
    'Alanine': 'Ala',
    'Cysteine': 'Cys',
    'Aspartic Acid': 'Asp',
    'Glutamic Acid': 'Glu',
    'Phenylalanine': 'Phe',
    'Glycine': 'Gly',
    'Histidine': 'His',
    'Isoleucine': 'Ile',
    'Lysine': 'Lys',
    'Leucine': 'Leu',
    'Methionine': 'Met',
    'Asparagine': 'Asn',
    'Proline': 'Pro',
    'Glutamine': 'Gln',
    'Arginine': 'Arg',
    'Serine': 'Ser',
    'Threonine': 'Thr',
    'Valine': 'Val',
    'Tryptophan': 'Trp',
    'Tyrosine': 'Tyr'
}

aa_3to1_dict = {
    'Ala': 'A',
    'Cys': 'C',
    'Asp': 'D',
    'Glu': 'E',
    'Phe': 'F',
    'Gly': 'G',
    'His': 'H',
    'Ile': 'I',
    'Lys': 'K',
    'Leu': 'L',
    'Met': 'M',
    'Asn': 'N',
    'Pro': 'P',
    'Gln': 'Q',
    'Arg': 'R',
    'Ser': 'S',
    'Thr': 'T',
    'Val': 'V',
    'Trp': 'W',
    'Tyr': 'Y'
}

def __get_key(val,my_dict):
    for key,value in my_dict.items():
        if val == value:
            return key

def __get_value(val,my_dict):
    for key,value in my_dict.items():
        if val == key:
            return value


# GC and AT content
def gc_content(seq):
    """Get the GC Content"""
    result = float(str(seq).count('G') + str(seq).count('C')) / len(seq) * 100
    return result

def at_content(seq):
    """Get the AT Content"""
    result = float(str(seq).count('A') + str(seq).count('T')) / len(seq) * 100
    return result

def gc_content_lower(seq):
    """Get the GC Content - lowercase seq"""
    result = float(str(seq).count('g') + str(seq).count('c')) / len(seq) * 100
    return result

def at_content_lower(seq):
    """Get the AT Content - lowercase seq"""
    result = float(str(seq).count('a') + str(seq).count('t')) / len(seq) * 100
    return result


# Converting amino acid names 3 to 1 and vice versa
def convert1to3(seq):
    term_list = []
    for i in seq:
        result = __get_key(i,aa_3to1_dict)
        term_list.append(result)
    return "".join(term_list)

def __kmers(seq,k=2):
    pair_list = []
    for i in range(0,len(seq),k):
        pair_list.append(seq[i:i+k])
    return pair_list

def convert3to1(seq):
    term_list = []
    for i in __kmers(seq,k=3):
        result = __get_value(i,aa_3to1_dict)
        term_list.append(result)
    return ''.join(term_list)

# k-mers 
def get_kmers(seq,k=2):
    pair_list = []
    for i in range(0,len(seq),k):
        pair_list.append(seq[i:i+k])
    return pair_list

# Sequence alignment/similarity
def hamming_distance(lhs,rhs):
    return len([(x,y) for x,y in zip(lhs,rhs) if x != y])

def occurance(main_seq,sub_seq):
    start = 0
    indices = []
    while True:
        start = main_seq.find(sub_seq,start)
        if start > 0:
            indices.append(start)
        else:
            break
        start += 1
    return indices

# Produce a dotplot of sequence alignment between 2 seqs
def delta(x,y):
    return 0 if x == y else 1
def M(seq1, seq2, i, j, k):
    slice1 = seq1[i:i+k]
    slice2 = seq2[j:j+k]

    # Check if the slices are empty
    if not slice1 or not slice2:
        return 0

    return sum(delta(x, y) for x, y in zip(slice1, slice2))
def makeMatrix(seq1,seq2,k):
    n = len(seq1)
    m = len(seq2)
    return [[M(seq1,seq2,i,j,k) for j in range(m-k+1)] for i in range(n-k+1)]
def plotMatrix(M, t, seq1, seq2, nonblank=chr(0x25A0), blank=' '):
    print(' |' + seq2)
    print('-' * (2 + len(seq2)))
    for label, row in zip(seq1, M):
        line = ''.join(nonblank if s < t else blank for s in row)
        print(label + '|' + line)
def dotplot(seq1,seq2,k = 1,t = 1):
    M = makeMatrix(seq1,seq2,k)
    plotMatrix(M, t, seq1,seq2) #experiment with character choice
    dotplot=plt.imshow(np.array(makeMatrix(seq1,seq2,1)))
    xt=plt.xticks(np.arange(len(list(seq1))),list(seq2))
    yt=plt.yticks(np.arange(len(list(seq1))),list(seq2))
    plt.show()

# seq1 and seq2 must be converted to a str first
# Got above code from: https://stackoverflow.com/questions/40822400/how-to-create-a-dotplot-of-two-dna-sequence-in-python

def get_aa_name(seq):
    """Returns the Full Name of a 3 Letter Amino Acid
    
    example: get_aa_name("Ala")
    >>> ""Alanine"
     
    """
    term_list = []
    for i in __kmers(seq,k=3):
        res = __get_key(i,full_amino_acid_name)
        term_list.append(res)
    return ''.join(term_list)

# Codon Frequency
def codon_frequency(seq, aminoacid):
    """Provides the frequency of each codon encoding a given amino acid in a DNA sequence"""
    tmpList = []
    for i in range(0, len(seq) - 2, 3):
        if CodonTable[seq[i:i + 3]] == aminoacid:
            tmpList.append(seq[i:i + 3])

    freqDict = dict(Counter(tmpList))
    totalScore = sum(freqDict.values())
    for seq in freqDict:
        freqDict[seq] = round(freqDict[seq] / totalScore, 2)
    return freqDict


