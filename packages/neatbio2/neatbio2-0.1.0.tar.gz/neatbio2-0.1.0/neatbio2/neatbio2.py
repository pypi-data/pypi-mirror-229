import sys

CodonTable = {
    "TCA": "S",
    "TCC": "S",
    "TCG": "S",
    "TCT": "S",
    "AGC": "S",
    "AGT": "S",  # Serine
    "TTC": "F",
    "TTT": "F",  # Phenylalanine
    "TTA": "L",
    "TTG": "L",  # Leucine
    "TAC": "Y",
    "TAT": "Y",  # Tyrosine
    "TAA": "*",
    "TAG": "*",
    "TGA": "*",  # Stop
    "TGC": "C",
    "TGT": "C",  # Cysteine
    "TGG": "W",  # Tryptophan
    "CTA": "L",
    "CTC": "L",
    "CTG": "L",
    "CTT": "L",  # Leucine
    "CCA": "P",
    "CCC": "P",
    "CCG": "P",
    "CCT": "P",  # Proline
    "CAC": "H",
    "CAT": "H",  # Histidine
    "CAA": "Q",
    "CAG": "Q",  # Glutamine
    "CGA": "R",
    "CGC": "R",
    "CGG": "R",
    "CGT": "R",  # Arginine
    "ATA": "I",
    "ATC": "I",
    "ATT": "I",  # Isoleucine
    "ATG": "M",  # Methionine
    "ACA": "T",
    "ACC": "T",
    "ACG": "T",
    "ACT": "T",  # Threonine
    "AAC": "N",
    "AAT": "N",  # Asparagine
    "AAA": "K",
    "AAG": "K",  # Lysine
    "AGA": "R",
    "AGG": "R",  # Arginine
    "GTA": "V",
    "GTC": "V",
    "GTG": "V",
    "GTT": "V",  # Valine
    "GCA": "A",
    "GCC": "A",
    "GCG": "A",
    "GCT": "A",  # Alanine
    "GAC": "D",
    "GAT": "D",  # Aspartate
    "GAA": "E",
    "GAG": "E",  # Glutamate
    "GGA": "G",
    "GGC": "G",
    "GGG": "G",
    "GGT": "G",  # Glycine
}

CodonTable_lower = {
    "tca": "S",
    "tcc": "S",
    "tcg": "S",
    "tct": "S",
    "agc": "S",
    "agt": "S",  # Serine
    "ttc": "F",
    "ttt": "F",  # Phenylalanine
    "tta": "L",
    "ttg": "L",
    "cta": "L",
    "ctc": "L",
    "ctg": "L",
    "ctt": "L",  # Leucine
    "tac": "Y",
    "tat": "Y",  # tyrosine
    "taa": "*",
    "tag": "*",
    "tga": "*",  # stop
    "tgc": "C",
    "tgt": "C",  # Cysteine
    "tgg": "W",  # tryptophan
    "cca": "P",
    "ccc": "P",
    "ccg": "P",
    "cct": "P",  # proline
    "cac": "H",
    "cat": "H",  # histidine
    "caa": "Q",
    "cag": "Q",  # glutamine
    "cga": "R",
    "cgc": "R",
    "cgg": "R",
    "cgt": "R",
    "aga": "R",
    "agg": "R",  # arginine
    "ata": "I",
    "atc": "I",
    "att": "I",  # isoleucine
    "atg": "M",  # methionine
    "aca": "T",
    "acc": "T",
    "acg": "T",
    "act": "T",  # threonine
    "aac": "N",
    "aat": "N",  # asparagine
    "aaa": "K",
    "aag": "K",  # lysine
    "gta": "V",
    "gtc": "V",
    "gtg": "V",
    "gtt": "V",  # valine
    "gca": "A",
    "gcc": "A",
    "gcg": "A",
    "gct": "A",  # alanine
    "gac": "D",
    "gat": "D",  # aspartate
    "gaa": "E",
    "gag": "E",  # glutamate
    "gga": "G",
    "ggc": "G",
    "ggg": "G",
    "ggt": "G",  # glycine
}


class Sequence(object):
    """Create a Valid Sequence for DNA,RNA

    example: seq1 = Sequence('ATGC')

    """

    def __init__(self, seq=None):
        super(Sequence, self).__init__()
        self.seq = seq

        # to enforce a string storage
        if not isinstance(self.__validate_seq(seq), str):
            raise TypeError(
                "The sequence data given to a Sequence object should"
                "be a string(not another Sequence object)"
                "nor a Non Valid Nucleotide [A,T,G,C,U]"
            )

    def __repr__(self):
        return "Sequence(seq='{}')".format(self.seq)

    def __str__(self):
        return self.seq

    def __validate_seq(self, seq):
        base_nt = ["A", "T", "C", "G", "U", "a", "t", "c", "g", "u"]
        real_seq = seq.upper()
        for base in real_seq:
            if base not in base_nt:
                return False
        return real_seq

    def __len__(self):
        return len(self.seq)

    def __contains__(self, sub_char):
        return sub_char in str(self)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.seq[index]

    # Basic fxn
    # Count, find, index
    def count(self, subseq, start=0, end=sys.maxsize):
        return str(self).count(subseq, start, end)
        """Return the Count of the Number of Nucleotides in a Sequence"""

    def find(self, subseq, start=0, end=sys.maxsize):
        return str(self).find(subseq, start, end)
        """Find the Position of a Nucleotide in a Sequence"""

    def rfind(self, subseq, start=0, end=sys.maxsize):
        return str(self).rfind(subseq, start, end)
        """Find the Position of a Nucleotide in a Sequence From the Right"""

    def index(self, subseq, start=0, end=sys.maxsize):
        return str(self).index(subseq, start, end)
        """Find the Index/Position of a Nucleotide in a Sequence"""

    def rindex(self, subseq, start=0, end=sys.maxsize):
        return str(self).rindex(subseq, start, end)
        """Find the Index/Position of a Nucleotide in a Sequence From the Right"""

    ### Main Fxns
    def get_symbol_frequency(self):
        """Get the Frequency of a Nucleotide in A Sequence"""
        base_dict = {"A": 0, "T": 0, "C": 0, "G": 0, "a": 0, "t": 0, "c": 0, "g": 0}
        for base in self.seq:
            if self.__validate_seq(base) != False:
                base_dict[base] += 1
            else:
                return "NucleotideError: {} not a nucleotide ['A,T,C,G']".format(base)
        return base_dict

    @property
    def gc(self):
        """Get the GC Content"""
        result = (
            float(str(self.seq).count("G") + str(self.seq).count("C"))
            / len(self.seq)
            * 100
        )
        return result

    @property
    def gc_lower(self):
        """Get the GC Content - lowercase seq"""
        result = (
            float(str(self.seq).count("g") + str(self.seq).count("c"))
            / len(self.seq)
            * 100
        )
        return result

    @property
    def at(self):
        """Get the AT Content"""
        result = (
            float(str(self.seq).count("A") + str(self.seq).count("T"))
            / len(self.seq)
            * 100
        )
        return result

    @property
    def at_lower(self):
        """Get the AT Content - lowercase seq"""
        result = (
            float(str(self.seq).count("a") + str(self.seq).count("t"))
            / len(self.seq)
            * 100
        )
        return result

    def complement(self):
        """Return the Complement of a Sequence"""
        base_pairs = {
            "A": "T",
            "T": "A",
            "G": "C",
            "C": "G",
            "a": "t",
            "t": "a",
            "g": "c",
            "c": "g",
        }
        comp_pairs = [base_pairs[a] for a in self.seq if a in base_pairs.keys()]
        return "".join(comp_pairs)

    def reverse_complement(self):
        """Return the Reverse Complement of a Sequence"""
        base_pairs = {
            "A": "T",
            "T": "A",
            "G": "C",
            "C": "G",
            "a": "t",
            "t": "a",
            "g": "c",
            "c": "g",
        }
        comp_pairs = [base_pairs[a] for a in self.seq if a in base_pairs.keys()]
        reverse_pairs = "".join(comp_pairs)[::-1]
        return reverse_pairs

    def transcribe(self):
        """Transcribe DNA Sequence into mRNA"""
        mRNA_result = self.seq.replace("T", "U")
        return mRNA_result

    def translate(self, start_pos=0):
        """Translate mRNA Sequence into a Protein/Amino Acids"""
        amino_acids_list = [
            CodonTable[self.seq[pos : pos + 3]]
            for pos in range(start_pos, len(self.seq) - 2, 3)
        ]
        return "".join(amino_acids_list)

    def lower_translate(self, start_pos=0):
        """Translate lowercase mRNA Sequence into a Protein/Amino Acids"""
        amino_acids_list = [
            CodonTable_lower[self.seq[pos : pos + 3]]
            for pos in range(start_pos, len(self.seq) - 2, 3)
        ]
        return "".join(amino_acids_list)
