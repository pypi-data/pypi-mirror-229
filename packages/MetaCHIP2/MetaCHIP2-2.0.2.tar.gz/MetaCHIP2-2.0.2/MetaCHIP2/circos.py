import os
import Bio
import glob
import shutil
import platform
import warnings
import argparse
import itertools
import numpy as np
from ete3 import Tree
from time import sleep
import multiprocessing as mp
from datetime import datetime
from packaging import version
from reportlab.lib import colors
from reportlab.lib.units import cm
from string import ascii_uppercase
from distutils.spawn import find_executable
from Bio.Seq import Seq
from Bio import SeqIO, Phylo
from Bio.SeqRecord import SeqRecord
from Bio.Graphics import GenomeDiagram
from Bio.SeqFeature import FeatureLocation
from Bio.Graphics.GenomeDiagram import CrossLink
warnings.filterwarnings("ignore")


circos_usage = '''
======================================= circos example commands =======================================

MetaCHIP2 circos -h

=========================================================================================================
'''


def Get_circlize_plot(multi_level_detection, pwd_candidates_file_PG_normal_txt, genome_to_taxon_dict, circos_HGT_R, pwd_plot_circos, taxon_rank, pwd_MetaCHIP_op_folder):

    rank_abbre_dict              = {'d': 'domain',  'p': 'phylum', 'c': 'class',   'o': 'order',  'f': 'family',   'g': 'genus',  's': 'species', 'x': 'specified group'}
    pwd_cir_plot_t1              = '%s/HGTs_among_%s_t1.txt'                % (pwd_MetaCHIP_op_folder, rank_abbre_dict[taxon_rank])
    pwd_cir_plot_t1_sorted       = '%s/HGTs_among_%s_t1_sorted.txt'         % (pwd_MetaCHIP_op_folder, rank_abbre_dict[taxon_rank])
    pwd_cir_plot_t1_sorted_count = '%s/HGTs_among_%s_t1_sorted_count.txt'   % (pwd_MetaCHIP_op_folder, rank_abbre_dict[taxon_rank])
    pwd_cir_plot_matrix_filename = '%s/HGTs_among_%s.txt'                   % (pwd_MetaCHIP_op_folder, rank_abbre_dict[taxon_rank])

    name2taxon_dict = {}
    transfers = []
    for each in open(pwd_candidates_file_PG_normal_txt):
        if not each.startswith('Gene_1'):
            each_split  = each.strip().split('\t')
            Gene_1      = each_split[0]
            Gene_2      = each_split[1]
            Genome_1    = '_'.join(Gene_1.split('_')[:-1])
            Genome_2    = '_'.join(Gene_2.split('_')[:-1])

            if Genome_1 in genome_to_taxon_dict:
                Genome_1_taxon = '_'.join(genome_to_taxon_dict[Genome_1].split(' '))
            else:
                Genome_1_taxon = '%s_' % taxon_rank

            if Genome_2 in genome_to_taxon_dict:
                Genome_2_taxon = '_'.join(genome_to_taxon_dict[Genome_2].split(' '))
            else:
                Genome_2_taxon = '%s_' % taxon_rank

            Direction = each_split[5]
            if multi_level_detection == True:
                Direction = each_split[6]

            if '%)' in Direction:
                Direction = Direction.split('(')[0]

            if Genome_1 not in name2taxon_dict:
                name2taxon_dict[Genome_1] = Genome_1_taxon
            if Genome_2 not in name2taxon_dict:
                name2taxon_dict[Genome_2] = Genome_2_taxon
            transfers.append(Direction)

    tmp1 = open(pwd_cir_plot_t1, 'w')
    all_group_id = []
    for each_t in transfers:
        each_t_split    = each_t.split('-->')
        donor           = each_t_split[0]
        recipient       = each_t_split[1]
        donor_id        = name2taxon_dict[donor]
        recipient_id    = name2taxon_dict[recipient]
        if donor_id not in all_group_id:
            all_group_id.append(donor_id)
        if recipient_id not in all_group_id:
            all_group_id.append(recipient_id)
        tmp1.write('%s,%s\n' % (donor_id, recipient_id))
    tmp1.close()

    os.system('cat %s | sort > %s' % (pwd_cir_plot_t1, pwd_cir_plot_t1_sorted))

    tmp2 = open(pwd_cir_plot_t1_sorted_count, 'w')
    count = 0
    current_t = ''
    for each_t2 in open(pwd_cir_plot_t1_sorted):
        each_t2 = each_t2.strip()
        if current_t == '':
            current_t = each_t2
            count += 1
        elif current_t == each_t2:
            count += 1
        elif current_t != each_t2:
            tmp2.write('%s,%s\n' % (current_t, count))
            current_t = each_t2
            count = 1
    tmp2.write('%s,%s\n' % (current_t, count))
    tmp2.close()

    # read in count as dict
    transfer_count = {}
    for each_3 in open(pwd_cir_plot_t1_sorted_count):
        each_3_split = each_3.strip().split(',')
        key = '%s,%s' % (each_3_split[0], each_3_split[1])
        value = each_3_split[2]
        transfer_count[key] = value

    all_group_id = sorted(all_group_id)

    matrix_file = open(pwd_cir_plot_matrix_filename, 'w')
    matrix_file.write('\t' + '\t'.join(all_group_id) + '\n')
    for each_1 in all_group_id:
        row = [each_1]
        for each_2 in all_group_id:
            current_key = '%s,%s' % (each_2, each_1)
            if current_key not in transfer_count:
                row.append('0')
            else:
                row.append(transfer_count[current_key])
        matrix_file.write('\t'.join(row) + '\n')
    matrix_file.close()

    # get plot with R
    if len(all_group_id) == 1:
        print('Too less group (1), plot skipped')
    elif 1 < len(all_group_id) <= 200:
        os.system('Rscript %s -m %s -p %s' % (circos_HGT_R, pwd_cir_plot_matrix_filename, pwd_plot_circos))
    else:
        print('Too many groups (>200), plot skipped')

    # rm tmp files
    os.system('rm %s' % pwd_cir_plot_t1)
    os.system('rm %s' % pwd_cir_plot_t1_sorted)
    os.system('rm %s' % pwd_cir_plot_t1_sorted_count)


def Get_circlize_plot_customized_grouping(multi_level_detection, pwd_candidates_file_PG_normal_txt, genome_to_group_dict, circos_HGT_R, pwd_plot_circos, pwd_MetaCHIP_op_folder):

    pwd_cir_plot_t1 =              '%s/cir_plot_t1.txt'              % pwd_MetaCHIP_op_folder
    pwd_cir_plot_t1_sorted =       '%s/cir_plot_t1_sorted.txt'       % pwd_MetaCHIP_op_folder
    pwd_cir_plot_t1_sorted_count = '%s/cir_plot_t1_sorted_count.txt' % pwd_MetaCHIP_op_folder
    pwd_cir_plot_matrix_filename = '%s/cir_plot_matrix.csv'          % pwd_MetaCHIP_op_folder

    transfers = []
    for each in open(pwd_candidates_file_PG_normal_txt):
        if not each.startswith('Gene_1'):
            each_split = each.strip().split('\t')
            Direction = each_split[5]
            if multi_level_detection == True:
                Direction = each_split[6]

            if '%)' in Direction:
                Direction = Direction.split('(')[0]

            transfers.append(Direction)

    tmp1 = open(pwd_cir_plot_t1, 'w')
    all_group_id = []
    for each_t in transfers:
        each_t_split    = each_t.split('-->')
        donor           = each_t_split[0]
        recipient       = each_t_split[1]
        donor_group     = genome_to_group_dict[donor]
        recipient_group = genome_to_group_dict[recipient]
        if donor_group not in all_group_id:
            all_group_id.append(donor_group)
        if recipient_group not in all_group_id:
            all_group_id.append(recipient_group)
        tmp1.write('%s,%s\n' % (donor_group, recipient_group))
    tmp1.close()

    os.system('cat %s | sort > %s' % (pwd_cir_plot_t1, pwd_cir_plot_t1_sorted))

    current_t = ''
    count = 0
    tmp2 = open(pwd_cir_plot_t1_sorted_count, 'w')
    for each_t2 in open(pwd_cir_plot_t1_sorted):
        each_t2 = each_t2.strip()
        if current_t == '':
            current_t = each_t2
            count += 1
        elif current_t == each_t2:
            count += 1
        elif current_t != each_t2:
            tmp2.write('%s,%s\n' % (current_t, count))
            current_t = each_t2
            count = 1
    tmp2.write('%s,%s\n' % (current_t, count))
    tmp2.close()

    # read in count as dict
    transfer_count = {}
    for each_3 in open(pwd_cir_plot_t1_sorted_count):
        each_3_split = each_3.strip().split(',')
        key = '%s,%s' % (each_3_split[0], each_3_split[1])
        value = each_3_split[2]
        transfer_count[key] = value

    all_group_id = sorted(all_group_id)

    matrix_file = open(pwd_cir_plot_matrix_filename, 'w')
    matrix_file.write('\t' + '\t'.join(all_group_id) + '\n')
    for each_1 in all_group_id:
        row = [each_1]
        for each_2 in all_group_id:
            current_key = '%s,%s' % (each_2, each_1)
            if current_key not in transfer_count:
                row.append('0')
            else:
                row.append(transfer_count[current_key])
        matrix_file.write('\t'.join(row) + '\n')
    matrix_file.close()

    # get plot with R
    if len(all_group_id) > 1:
        os.system('Rscript %s -m %s -p %s' % (circos_HGT_R, pwd_cir_plot_matrix_filename, pwd_plot_circos))

    # rm tmp files
    os.system('rm %s' % pwd_cir_plot_t1)
    os.system('rm %s' % pwd_cir_plot_t1_sorted)
    os.system('rm %s' % pwd_cir_plot_t1_sorted_count)


def circos(args):

    circos_HGT_R     = args['circos_HGT_R']
    detected_hgt_txt = args['hgt']
    gnm_taxon_txt    = args['hgt']


    genome_to_taxon_dict = dict()
    genome_to_group_dict = dict()

    if grouping_file is not None:
        pwd_plot_circos = '%s/%s_x%s_HGTs_among_provided_groups.pdf' % (detect_wd, op_prefix, group_num)
        Get_circlize_plot_customized_grouping(multi_level_detection, detected_hgt_txt, genome_to_group_dict, circos_HGT_R, pwd_plot_circos, detect_wd)
    else:
        # for single level detection
        if len(detection_rank_list) == 1:
            pwd_plot_circos = '%s/detected_HGTs.pdf' % (detect_wd)
            Get_circlize_plot(multi_level_detection, detected_hgt_txt, genome_to_taxon_dict, circos_HGT_R, pwd_plot_circos, detection_rank_list, detect_wd)

        # for multiple level detection
        else:
            for detection_rank in detection_rank_list:
                if detection_rank not in ignored_rank_list:
                    Get_circlize_plot(multi_level_detection, detected_hgt_txt, genome_to_taxon_dict, circos_HGT_R, pwd_plot_circos, detection_rank, pwd_combined_prediction_folder)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-hgt',         required=True,                                          help='detected HGTs gbk folder')
    parser.add_argument('-taxon',       required=False,                                         help='taxonomic classification of input genomes')
    parser.add_argument('-r',           required=False,                         default=None,   help='grouping rank, e.g., p, c, o, f, g, pcofg, pco ...')
    parser.add_argument('-g',           required=False,                         default=None,   help='grouping file')
    parser.add_argument('-p',           required=True,                                          help='output prefix')
    parser.add_argument('-o',           required=False,                         default=None,   help='output folder (default: current working directory)')
    parser.add_argument('-quiet',       required=False, action="store_true",                    help='do not report progress')
    parser.add_argument('-f',           required=False, action="store_true",                    help='force overwrite previous results')
    args = vars(parser.parse_args())
    circos(args)
