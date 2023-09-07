from Bio import SeqIO


grouping_file    = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/gnm_clade_v1.txt'
detected_hgt_txt = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/demo_MetaCHIP_wd/detected_HGTs.txt'
recipient_ffn    = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/demo_MetaCHIP_wd/recipient.ffn'


grouping_file    = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/gnm_clade_v2.txt'
detected_hgt_txt = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/demo_v2_MetaCHIP_wd/detected_HGTs.txt'
recipient_ffn    = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/demo_v2_MetaCHIP_wd/recipient.ffn'


gnm_to_group_dict = dict()
for each_genome in open(grouping_file):
    each_genome_split = each_genome.strip().split(',')
    group_id = each_genome_split[0]
    genome_name = each_genome_split[1]
    gnm_to_group_dict[genome_name] = group_id
print(gnm_to_group_dict)


gnm_to_hgt_num_dict = dict()
grp_to_hgt_num_dict = dict()
for each_hgt in open(detected_hgt_txt):
    if not each_hgt.startswith('Gene_1\tGene_2\tIdentity'):

        each_hgt_split = each_hgt.strip().split('\t')
        recipient_gnm = each_hgt_split[-1].split('-->')[-1]
        recipient_grp = gnm_to_group_dict[recipient_gnm]

        if recipient_gnm not in gnm_to_hgt_num_dict:
            gnm_to_hgt_num_dict[recipient_gnm] = 1
        else:
            gnm_to_hgt_num_dict[recipient_gnm] += 1

        if recipient_grp not in grp_to_hgt_num_dict:
            grp_to_hgt_num_dict[recipient_grp] = 1
        else:
            grp_to_hgt_num_dict[recipient_grp] += 1

print(gnm_to_hgt_num_dict)
print(grp_to_hgt_num_dict)

grp_to_gc_content_dict = dict()
grp_to_gc_num_dict = dict()
grp_to_total_len_dict = dict()
for each_seq in SeqIO.parse(recipient_ffn, 'fasta'):
    recipient_gnm = '_'.join(each_seq.id.split('_')[:-1])
    recipient_grp = gnm_to_group_dict[recipient_gnm]
    gc_num = str(each_seq.seq).count('G') + str(each_seq.seq).count('C')
    gc_content = gc_num*100/len(each_seq.seq)
    gc_content = float("{0:.2f}".format(gc_content))
    if recipient_grp not in grp_to_gc_content_dict:
        grp_to_gc_content_dict[recipient_grp] = [gc_content]
        grp_to_gc_num_dict[recipient_grp] = gc_num
        grp_to_total_len_dict[recipient_grp] = len(each_seq.seq)
    else:
        grp_to_gc_content_dict[recipient_grp].append(gc_content)
        grp_to_gc_num_dict[recipient_grp] += gc_num
        grp_to_total_len_dict[recipient_grp] += len(each_seq.seq)


print(grp_to_gc_content_dict)

def Average(lst):
    return sum(lst) / len(lst)

for each_grp in sorted(list(grp_to_gc_content_dict.keys())):
    gc_list = grp_to_gc_content_dict[each_grp]
    mean_gc = Average(gc_list)
    print('%s\t%s\t%s' % (each_grp, mean_gc, gc_list))

print()
for each_grp in sorted(list(grp_to_gc_content_dict.keys())):
    total_gc = grp_to_gc_num_dict[each_grp]/grp_to_total_len_dict[each_grp]
    print('%s\t%s' % (each_grp,total_gc))

