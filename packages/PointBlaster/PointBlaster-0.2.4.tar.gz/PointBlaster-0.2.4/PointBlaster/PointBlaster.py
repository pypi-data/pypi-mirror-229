import os
import sys
import math
import argparse
import subprocess
import shutil
import pandas as pd
import random
import numpy as np
from Bio import SeqIO
from cvmblaster.blaster import Blaster


# from Bio.Blast import NCBIWWW
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast.Applications import NcbimakeblastdbCommandline


def args_parse():
    "Parse the input argument, use '-h' for help."
    parser = argparse.ArgumentParser(
        usage='PointBlaster -i <genome assemble directory> -s <species for point mutation detection> -o <output_directory> \n\nAuthor: Qingpo Cui(SZQ Lab, China Agricultural University)\n')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-i", help="<input_path>: the PATH to the directory of assembled genome files. Could not use with -f")
    group.add_argument(
        "-f", help="<input_file>: the PATH of assembled genome file. Could not use with -i")
    parser.add_argument("-o", help="<output_directory>: output PATH")
    parser.add_argument('-s', type=str, default='salmonella', choices=['salmonella', 'campylobacter'], help='<species>: optional var is [salmonella, campylobacter], other species will be supported soon')
    parser.add_argument('-minid', default=90,
                        help="<minimum threshold of identity>, default=90")
    parser.add_argument('-mincov', default=60,
                        help="<minimum threshold of coverage>, default=60")
    parser.add_argument('-list', action='store_true',
                        help='<show species list>')
    parser.add_argument(
        '-t', default=8, help='<number of threads>: default=8')
    # parser.add_argument("-store_arg_seq", default=False, action="store_true",
    #                     help='<save the nucleotide and amino acid sequence of find genes on genome>')
    # parser.add_argument("-p", default=True, help="True of False to process something",
    #                     type=lambda x: bool(strtobool(str(x).lower())))
    parser.add_argument('-v', '--version', action='version',
                        version='Version: ' + get_version("__init__.py"), help='<display version>')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-init', action='store_true',
                       help='<initialize the point mutationdatabase>')

    # group.add_argument('-updatedb', help="<add input fasta to BLAST database>")
    # group.add_argument('-init', action='store_true',
    #                    help='<initialize the reference database>')
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


def makeblastdb(file, name):
    cline = NcbimakeblastdbCommandline(
        dbtype="nucl", out=name, input_file=file)
    print(f'Making {name} database...')
    stdout, stderr = cline()
    print('Finish')


def get_sbjct_seq(ref_fasta, gene):
    """
    obtain gene sequence from reference fasta file of specific specie
    """
    for seq_record in SeqIO.parse(open(ref_fasta, mode='r'), 'fasta'):
        gene_name = seq_record.id.split('___')[0]
        if gene_name == gene:
            seq = str(seq_record.seq)
    return seq

    # seq_record.seq


def get_align_seq(result_dict, ref_fasta):
    """
    convert the result from cvmblaster to gene list format like:
    [gene , sbjct_start, sbjct_string, query_string, coverage, identity]
    """
    gene_list = {}

    # need concatenate hits from same gene

    # check if multiple hits from same gene exist
    for item in result_dict.keys():
        gene = result_dict[item]['GENE']
        if gene not in gene_list.keys():

            sbjct_start = result_dict[item]['SBJSTART']
            sbjct_string = result_dict[item]['SBJCT_SEQ']
            query_string = result_dict[item]['QUERY_SEQ']
            # print(len(query_string))
            coverage = result_dict[item]['%COVERAGE']
            # print(coverage)
            identity = result_dict[item]['%IDENTITY']
            gene_list[gene] = (gene, sbjct_start, sbjct_string,
                               query_string, coverage, identity)
        else:
            new_sbjct_start = result_dict[item]['SBJSTART']
            new_sbjct_string = result_dict[item]['SBJCT_SEQ']
            new_query_string = result_dict[item]['QUERY_SEQ']

            # get reference sequence of gene
            raw_sbjct_seq = get_sbjct_seq(ref_fasta, gene)
            if new_sbjct_start < gene_list[gene][1]:
                sbjct_start = new_sbjct_start
                second_sbjct_start = gene_list[gene][1]
                first_sbjct = new_sbjct_string
                second_sbjct = gene_list[gene][2]
                first_query = new_query_string
                second_query = gene_list[gene][3]
            else:
                sbjct_start = gene_list[gene][1]
                second_sbjct_start = new_sbjct_start
                first_sbjct = gene_list[gene][2]
                second_sbjct = new_sbjct_string
                first_query = gene_list[gene][3]
                second_query = new_query_string
                # sbjct_string = raw_sbjct_seq[sbjct_start - 1:len(new_sbjct_string)] + raw_sbjct_seq[sbjct_start + len(
                #     new_sbjct_string) - 1:gene_list[gene][1] - 1 ] + gene_list[gene][2]
            if (sbjct_start + len(first_sbjct) - 1) <= second_sbjct_start:
                sbjct_string = first_sbjct + raw_sbjct_seq[sbjct_start + len(
                    first_sbjct) - 1:second_sbjct_start - 1] + second_sbjct
                query_string = first_query + raw_sbjct_seq[sbjct_start + len(
                    first_sbjct) - 1:second_sbjct_start - 1] + second_query
            else:
                sbjct_string = first_sbjct + second_sbjct[sbjct_start + len(
                    first_sbjct) - 1:]
                querey_string = first_query + second_query[sbjct_start + len(
                    first_query) - 1:]

            identity = compute_identity(query_string, sbjct_string)
            # print(gene)
            coverage = len(sbjct_string) * 100 / len(raw_sbjct_seq)
            # print(coverage)

            gene_list[gene] = (gene, sbjct_start, sbjct_string,
                               query_string, coverage, identity)

    return gene_list


def compute_identity(query_string, sbjct_string):
    a = 1
    # print(len(query_string))
    # print(len(sbjct_string))
    for i in range(0, len(query_string)):
        # print(i)
        # print(query_string[i])
        # print(sbjct_string[i])
        # print(i)
        if query_string[i] == sbjct_string[i]:
            a += 1
    identity = a * 100 / len(sbjct_string)
    # print(identity)
    return identity


def aa(codon):
    """
    This function converts a codon to an amino acid. If the codon is not
    valid an error message is given, or else, the amino acid is returned.
    """
    codon = codon.upper()
    aa = {"ATT": "I", "ATC": "I", "ATA": "I",
          "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L", "TTA": "L", "TTG": "L",
          "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
          "TTT": "F", "TTC": "F",
          "ATG": "M",
          "TGT": "C", "TGC": "C",
          "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
          "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
          "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
          "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
          "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S", "AGT": "S", "AGC": "S",
          "TAT": "Y", "TAC": "Y",
          "TGG": "W",
          "CAA": "Q", "CAG": "Q",
          "AAT": "N", "AAC": "N",
          "CAT": "H", "CAC": "H",
          "GAA": "E", "GAG": "E",
          "GAT": "D", "GAC": "D",
          "AAA": "K", "AAG": "K",
          "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R", "AGA": "R", "AGG": "R",
          "TAA": "*", "TAG": "*", "TGA": "*"}

    # Translate valid codon
    try:
        amino_a = aa[codon]
    except KeyError:
        amino_a = "?"
    return amino_a


def get_indel(gapped_seq, indel_seq):
    """
    This function finds the zone of gaps compared to the indel sequece.

    """
    insert_seq = indel_seq[0]
    for item in range(1, len(gapped_seq)):
        if gapped_seq[item] == '-':
            insert_seq += indel_seq[item]
        else:
            break
    return insert_seq


def get_substitution(sbjct_seq, substitution_seq):
    """
    This function find substitution zone
    """
    sub_seq = substitution_seq[0]
    for item in range(1, len(sbjct_seq)):
        if sbjct_seq[item] != substitution_seq[item]:
            sub_seq += substitution_seq[item]
        else:
            break
    return sub_seq


def find_mismatch(sbjct_start, sbjct_string, query_string, gene, genes_list):
    """
    This function find indel or substitution of query seq compared to sbjct seq and return
    mutation type, indel seq, mutation position.
    """
    mutations = []

    shift = 0
    seq_pos = sbjct_start
    for index in range(sbjct_start - 1, len(sbjct_string)):

        # Shift index according to gaps
        i = index + shift

        if i == len(sbjct_string):
            break

        sbjct_nuc = sbjct_string[i]
        query_nuc = query_string[i]

        mutation_type = ''

        if sbjct_nuc.upper() != query_nuc.upper():
            if sbjct_nuc == '-' or query_nuc == '-':

                # insert mutation

                if sbjct_nuc == '-':
                    mutation_type = 'ins'
                    mut_pos = i + 1
                    indel_start_pos = seq_pos
                    indel = get_indel(
                        sbjct_string[i:], query_string[i:])
                    indel_end_pos = seq_pos + len(indel) - 1

                # deletion mutation
                else:
                    mutation_type = 'del'
                    mut_pos = i + 1
                    indel_start_pos = seq_pos
                    indel = get_indel(query_string[i:], sbjct_string[i:])
                    indel_end_pos = indel_start_pos + len(indel) - 1

                # shift the index to the end of the gaps
                shift += len(indel) - 1

                # generate mutation name
                if len(indel) == 1 and mutation_type == 'del':
                    mutation_name = str(indel_start_pos) + 'del' + indel
                else:
                    mutation_name = str(indel_start_pos) + '_' + \
                        str(indel_end_pos) + mutation_type + indel

                mutations += [[mutation_type, mutation_name, indel_start_pos,
                               indel_end_pos, indel, indel]]

                # print(mutation_name)

            # substitute mutation
            # print(sbjct_nuc + '->' + query_nuc)
            else:
                mutation_type = 'sub'
                mut_pos = i + 1
                sub_start_pos = seq_pos
                sub_seq = get_substitution(sbjct_string[i:], query_string[i:])
                sub_end_pos = seq_pos + len(sub_seq) - 1
                shift = len(sub_seq) - 1

                # print(sub_start_pos, sub_seq, sub_end_pos)
                if gene in genes_list:
                    # calculate condon if gene is not RNA sequence
                    if seq_pos % 3 == 0:
                        if sub_end_pos % 3 != 0:
                            ref_seq = sbjct_string[i - 3 + 1: i +
                                                   len(sub_seq) - 1 + (3 - (sub_end_pos % 3)) + 1]

                            query_seq = query_string[i - 3 + 1: i +
                                                     len(sub_seq) - 1 + (3 - (sub_end_pos % 3)) + 1]
                        else:
                            ref_seq = sbjct_string[i -
                                                   3 + 1: i + len(sub_seq) - 1 + 1]
                            query_seq = query_string[i -
                                                     3 + 1: i + len(sub_seq) - 1 + 1]
                    elif seq_pos % 3 == 1:
                        if sub_end_pos % 3 != 0:
                            ref_seq = sbjct_string[i: i +
                                                   len(sub_seq) - 1 + (3 - (sub_end_pos % 3)) + 1]

                            query_seq = query_string[i: i +
                                                     len(sub_seq) - 1 + (3 - (sub_end_pos % 3)) + 1]
                        else:
                            ref_seq = sbjct_string[i: i + len(sub_seq)]
                            query_seq = query_string[i: i + len(sub_seq)]
                    else:
                        if sub_end_pos % 3 != 0:
                            ref_seq = sbjct_string[i - 1: i +
                                                   len(sub_seq) - 1 + (3 - (sub_end_pos % 3)) + 1]

                            query_seq = query_string[i - 1: i +
                                                     len(sub_seq) - 1 + (3 - (sub_end_pos % 3)) + 1]
                        else:
                            ref_seq = sbjct_string[i - 1: i + len(sub_seq)]
                            query_seq = query_string[i - 1: i + len(sub_seq)]
                else:
                    ref_seq = sbjct_nuc

                    query_seq = query_nuc

                # print(ref_seq, query_seq)
                if len(sub_seq) == 1:
                    mutation_name = str(seq_pos) + \
                        sbjct_nuc + '->' + query_nuc

                else:
                    mutation_name = str(seq_pos) + '_' + \
                        str(sub_end_pos) + ref_seq + '->' + query_seq

                mutations += [[mutation_type, mutation_name, sub_start_pos,
                               sub_end_pos, query_seq, ref_seq]]

        # increment seq_position
        if mutation_type != 'ins':
            seq_pos += 1
    # print(mutations)
    return mutations


def get_db_mutations(mut_db_path):
    """
    transform the table of resistance_overview.txt to dict format
    """
    try:
        drugfile = open(mut_db_path, 'r')
    except:
        sys.exit('Could not found database: %s' % (mut_db_path))

    # Initiate a empty dict
    mutation_dict = {}
    # Go throug mutation file line by line
    for line in drugfile:
        # Ignore headers and check where the indel section starts
        if line.startswith("#"):
            # print(line)
            if "indel" in line.lower():
                indelflag = True
            elif "stop codon" in line.lower():
                stopcodonflag = True
            else:
                stopcodonflag = False
            continue
        # Ignore empty lines
        elif line.strip() == "":
            continue
        else:

            # Strip data entries
            mutation = [data.strip() for data in line.strip().split("\t")]
            # print(mutation)

            # Extract all info on the line (even though it is not all used)
            gene_ID = mutation[0]
            if gene_ID not in mutation_dict.keys():
                mutation_dict[gene_ID] = [{'gene_name': mutation[1], 'mut_pos': int(mutation[2]), 'ref_codon': mutation[3], 'ref_aa': mutation[4], 'alt_aa': mutation[5].split(
                    ","), 'res_drug': mutation[6].replace("\t", " "), 'pmid': mutation[7].split(",")}]
            else:
                mutation_dict[gene_ID] += [{'gene_name': mutation[1], 'mut_pos': int(mutation[2]), 'ref_codon': mutation[3], 'ref_aa': mutation[4], 'alt_aa': mutation[5].split(
                    ","), 'res_drug': mutation[6].replace("\t", " "), 'pmid': mutation[7].split(",")}]

    return mutation_dict


# print(find_mismatch(1,  'AAATCAGATATAC', 'AAATCAGGATAAC'))
# print(find_mismatch(1,  'AT-GGATC', 'ATCGGATC'))
# print(find_mismatch(1,  'ATCGGATC', 'AT-GGATC'))
# print(find_mismatch(1,  'ATCGAATC', 'ATCAAATC'))


def get_gene_list(species):
    """
    This function return gene list from point_mutation database using species parameter.

    """
    genes_file = os.path.join(
        os.path.dirname(__file__), f'db/point_mutation/{species}/genes.txt')
    RNA_genes_file = os.path.join(
        os.path.dirname(__file__), f'db/point_mutation/{species}/RNA_genes.txt')
    genes = []
    RNA_genes = []
    with open(genes_file, 'r') as f1:
        for i in f1.readlines():
            if i != '':
                genes.append(i.strip())
    with open(RNA_genes_file, 'r') as f2:
        for i in f2.readlines():
            if i != '':
                RNA_genes.append(i.strip())
    for item in RNA_genes:
        if item in genes:
            genes.remove(item)
    return genes, RNA_genes


# print(get_gene_list('salmonella'))


def find_mutations(gene_list_result, genes_list):
    """
    find mutations from gene_list
    gene_list = [(gene, sbjct_start, sbjct_string,
                           query_string, coverage, identity)]

    """
    mutation_result = {}
    for item in gene_list_result:
        coverage = float(item[4])
        identity = float(item[5])
        if (coverage == 100.00) or (identity != 100):
            mutation_result[item[0]] = find_mismatch(
                item[1], item[2], item[3], item[0], genes_list)

    return mutation_result


def get_aa_seq(ref_seq, query_seq):
    """
    switch dna sequence to amino acid sequence.

    string = 'ATCATG'
    for i in np.arange(0, 6, 3):
        print(i)
        print(string[i:i + 3])

    """
    aa_ref = ''
    aa_alt = ''

    for i in np.arange(0, len(ref_seq), 3):
        aa_ref += aa(ref_seq[i:i + 3])
        aa_alt += aa(query_seq[i:i + 3])
    return aa_ref, aa_alt


def match_mut_indb(db_mutations, gene_name, aa_pos, aa_ref, aa_alt):
    """
    """
    save_check = 0
    resistance_phenotype = ''
    gene = ''
    gene_mut_list = db_mutations[gene_name]

    for single_mut_dict in gene_mut_list:

        if (aa_pos == single_mut_dict['mut_pos']) and (aa_alt in single_mut_dict['alt_aa']) and (aa_ref == single_mut_dict['ref_aa']):
            save_check = 1
            gene = single_mut_dict['gene_name']
            resistance_phenotype = single_mut_dict['res_drug']
            # print(save_check, gene, aa_pos, resistance_phenotype)
        else:
            next

    return save_check, gene, resistance_phenotype


def get_rna_change(ref_seq, query_seq, sub_position):
    """
    find substitution nuc in the zone of substitution of rna gene sequence

    """
    sub_nuc_index = sub_position % 3 - 1
    ref_nuc = ref_seq[sub_nuc_index]
    query_nuc = query_seq[sub_nuc_index]
    return ref_nuc, query_nuc


def filter_result(mutation_dict, db_mutations, pm_db_list):
    result = ''
    for key in mutation_dict.keys():
        gene_name = key
        # print(key)
        if key in pm_db_list:
            for item in mutation_dict[key]:
                # print(key)
                if item[0] == 'sub':
                    sub_start_pos = item[2]
                    aa_pos = math.ceil(sub_start_pos / 3)
                    aa_ref, aa_alt = get_aa_seq(item[5], item[4])
                    # print(item[2], item[5], aa_ref, aa_alt)
                    # print(item)
                    save, gene, res_pheno = match_mut_indb(
                        db_mutations, gene_name, aa_pos, aa_ref, aa_alt)
                    # print(save, gene, res_pheno)
                if save:
                        # print(gene_name)
                    result += f'{gene}\t{aa_ref}{aa_pos}{aa_alt}\t{item[5]} -> {item[4]}\t{aa_ref} -> {aa_alt}\t{res_pheno}\n'
                    # print('begin')
                    # print(result)
                    # print('end')

                    # print(aa_pos)
                    # print(aa_ref, aa_alt)
        else:
            for item in mutation_dict[key]:
                if item[0] == 'sub':
                    sub_start_pos = item[2]
                    ref_seq = item[5]
                    alt_seq = item[4]
                    # nuc_ref, nuc_alt = get_rna_change(
                    #     ref_seq, alt_seq, sub_start_pos)
                    # xxx
                    aa_ref = ref_seq
                    aa_alt = alt_seq
                    aa_pos = sub_start_pos
                    save, gene, res_pheno = match_mut_indb(
                        db_mutations, gene_name, aa_pos, aa_ref, aa_alt)
                    # print('RNA')
                    # print(save, gene, res_pheno)
                if save:
                    # print(gene_name)
                    result += f'{gene}\t{aa_ref}{aa_pos}{aa_alt}\t{item[5]} -> {item[4]}\t{aa_ref} -> {aa_alt}\t{res_pheno}\n'
                    # print('begin')
                    # print(result)
                    # print(end)

    return result


def show_db_list():
    print('Datbase of point mutation')
    db_path = os.path.join(os.path.dirname(__file__), 'db/point_mutation')
    for file in os.listdir(db_path):
        if os.path.isdir(os.path.join(db_path, file)):
            print(file)


def initialize_db():
    database_path = os.path.join(
        os.path.dirname(__file__), f'db/point_mutation')
    for point_db in os.listdir(database_path):
        point_db_path = os.path.join(database_path, point_db)

        if os.path.isdir(point_db_path):

            for file in os.listdir(point_db_path):
                if file.endswith('.fsa') and os.path.splitext(file)[0] == point_db:
                    file_path = os.path.join(database_path, point_db, file)
                    out_path = os.path.join(database_path, point_db, point_db)
                    print(f'Making {point_db} point mutation database...')
                    Blaster.makeblastdb(file_path, out_path)


def main():
    # df_all = pd.DataFrame()
    args = args_parse()
    if args.list:
        show_db_list()
        sys.exit(1)
    elif args.init:
        initialize_db()
        sys.exit(1)
    else:
        # threads
        threads = args.t
        # print(threads)

        minid = args.minid
        mincov = args.mincov

        # get the input path

        files = []
        if args.i is not None:
            # get the input path
            files = os.listdir(os.path.abspath(args.i))
            input_path = os.path.abspath(args.i)
        else:
            files.append(os.path.abspath(args.f))
            input_path = os.path.dirname(os.path.abspath(args.f))

        # check if the output directory exists
        if not os.path.exists(args.o):
            os.mkdir(args.o)

        output_path = os.path.abspath(args.o)

        # check if -species var exist
        species_list = ['salmonella', 'campylobacter']
        if args.s is not None:
            if args.s in species_list:
                blastdb = os.path.join(os.path.dirname(
                    __file__), f'db/point_mutation/{args.s}/{args.s}')
                db_mutations_path = os.path.join(os.path.dirname(
                    __file__), f'db/point_mutation/{args.s}/resistens-overview.txt')
                ref_fasta = os.path.join(os.path.dirname(
                    __file__), f'db/point_mutation/{args.s}/{args.s}.fsa')
            else:
                print(
                    "Please input the right species in species_list, the supported species are")
                print(species_list)
                sys.exit(1)
        else:
            sys.exit(1)
        df_final = pd.DataFrame()

        for file in files:
            file_base = str(os.path.basename(os.path.splitext(file)[0]))
            output_filename = file_base + '_tab.txt'
            # file_base = str(os.path.splitext(file)[0])
            # output_filename = file_base + '_tab.txt'
            outfile = os.path.join(output_path, output_filename)
            # print(file_base)
            file_path = os.path.join(input_path, file)
            with open(outfile, 'a') as f:
                f.write(
                    f'Gene\tMutation\tNucleotide change\tAmino Acid change\tResistance\n')
                if os.path.isfile(file_path):
                    # print("TRUE")
                    if Blaster.is_fasta(file_path):
                        print(f'Processing {file}')

                        # lower the blast coverage in order to find 23S point mutaiton
                        df, result_dict = Blaster(file_path, blastdb,
                                                  output_path, threads, minid, 20).biopython_blast()
                        # print(result_dict)
                        # print(result_dict)
                        # print(df)
                        db_mutations = get_db_mutations(db_mutations_path)
                        # print(db_mutations)
                        genes, RNA_genes = get_gene_list(args.s)

                        gene_dict_result = get_align_seq(
                            result_dict, ref_fasta)
                        # print(gene_list_result)
                        # print(gene_dict_result)

                        # parse gene_dict_result
                        gene_list_result = []
                        for key in gene_dict_result.keys():
                            if float(gene_dict_result[key][4]) >= float(mincov):
                                gene_list_result.append(gene_dict_result[key])
                        # print(gene_list_result)

                        mutation_result = find_mutations(
                            gene_list_result, genes)
                        # print(mutation_result)
                        # print(mutation_result)

                        # print(test)
                        # print(gene_list_result)
                        f.write(filter_result(
                            mutation_result, db_mutations, genes))

                        print(
                            f"Finishing process {file}: writing results to " + str(outfile))
            f.close()
            df_tmp = pd.read_csv(outfile, sep='\t')
            # print(df_tmp)
            df_tmp['File'] = file_base
            df_tmp['Value'] = 1
            df_final = pd.concat([df_final, df_tmp])
            # print(df_final)

    df_pivot = df_final.pivot_table(index='File',
                                    columns='Gene', values='Mutation', aggfunc=lambda x: ','.join(map(str, x)))
    # print(df_pivot)
    summary_file = os.path.join(output_path, 'PointMutation_Summary.csv')

    df_pivot.to_csv(summary_file)


if __name__ == '__main__':
    main()
