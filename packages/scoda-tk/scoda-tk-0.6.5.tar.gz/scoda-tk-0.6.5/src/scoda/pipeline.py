import time, os, copy, datetime, math, random, warnings
import numpy as np
import pandas as pd
import anndata
from contextlib import redirect_stdout, redirect_stderr
import logging, sys

SCANVPY = True
try:
    import scanpy as sc
except ImportError:
    print('WARNING: scanpy not installed.')
    SCANVPY = False

GSEAPY = True
try:
    import gseapy as gp
except ImportError:
    print('WARNING: gseapy not installed or not available. ')
    GSEAPY = False

def load_gmt_file(file):
    dct = {}
    with open(file, 'r') as f:
        for line in f:
            items = line.split('\t')
            dct[items[0]] = items[2:]
    return dct


from scoda.icnv import run_icnv, identify_tumor_cells
from scoda.cpdb import cpdb4_run, cpdb4_get_results, cpdb_plot, cpdb_get_gp_n_cp #, plot_circ
from scoda.gsea import select_samples, run_gsa, run_prerank
from scoda.deg import deg_multi, get_population, plot_population
from scoda.misc import plot_sankey_e, get_opt_files_path
from scoda.hicat import HiCAT

from scoda.hicat import HiCAT, get_markers_major_type
from scoda.hicat import get_markers_cell_type, get_markers_minor_type2, load_markers_all


def scoda_icnv_addon( adata_t, gtf_file, ref_types, 
                      ref_key, use_ref_only, 
                      clustering_algo, clustering_resolution, 
                      connectivity_threshold, n_cores, verbose, print_prefix, 
                      tumor_dec_margin, tumor_dec_th_max, N_loops,
                      net_search_mode, cmd_cutoff, gcm, 
                      N_cells_max_for_clustering, use_umap ):
    
    adata = adata_t[:,:]

    ref_types2 = ref_types
    ref_ind = None

    if ref_types is not None:
        if isinstance(ref_types, list):
            if len(ref_types) > 0:
                ref_types2 = list(set(ref_types).intersection(adata.obs[ref_key].unique()))
                ref_ind = adata.obs[ref_key].isin(ref_types)
    #'''
    if verbose: print('%sInferCNV .. ' % (print_prefix), flush = True)
        
    adata = run_icnv(adata, ref_key, ref_types2, gtf_file, 
                             resolution = 1, N_pca = 15, n_neighbors = 15,
                             cluster_key = 'cnv_leiden', umap = False, pca = False,
                             n_cores = n_cores, verbose = False )
    # if verbose: print('%sInferCNVpy .. done. ' % (print_prefix), flush = True)

    #'''
    if verbose: print('%sInferCNV addon .. ' % (print_prefix), flush = True)
    X_cnv = np.array(adata.obsm['X_cnv'].todense())
    pca = False
    df_res, summary, cobj, X_pca = identify_tumor_cells(X_cnv, ref_ind, pca = pca, clust = None, 
                           use_cnv_score = False, Clustering_algo = clustering_algo, 
                           Clustering_resolution = clustering_resolution, N_clusters = 30,
                           gmm_N_comp = 20, th_max = tumor_dec_th_max, refp_min = 0.9, p_exc = 0.1, 
                           dec_margin = tumor_dec_margin, n_neighbors = 10, cmd_cutoff = cmd_cutoff, N_loops = N_loops,
                           gcm = gcm, plot_stat = False, use_ref = use_ref_only, 
                           N_cells_max_for_clustering = N_cells_max_for_clustering,
                           connectivity_thresh = connectivity_threshold, net_search_mode = net_search_mode,
                           suffix = '', Data = None, n_cores = n_cores, verbose = False, use_umap = use_umap)
    # if verbose: print('%sInferCNV addon .. done. ' % (print_prefix), flush = True)
    
    if not pca: adata.obsm['X_cnv_pca'] = X_pca
        
    adata_t.obsm['X_cnv'] = adata.obsm['X_cnv']
    adata_t.obsm['X_cnv_pca'] = adata.obsm['X_cnv_pca']
    adata_t.uns['cnv'] = adata.uns['cnv']

    adata_t.obs['cnv_cluster'] = list(df_res['cnv_cluster'].astype(str))
    adata_t.obs['tumor_dec'] = list(df_res['tumor_dec'])
    adata_t.obs['tumor_score'] = list(df_res['tumor_score'])
    adata_t.obs['ref_ind'] = list(df_res['ref_ind_score'])
    
    '''
    if 'log_tumor_score' in list(df_res.columns.values):
        adata_t.obs['log_tumor_score'] = list(df_res['log_tumor_score'])
    if 'y_conf' in list(df_res.columns.values):
        adata_t.obs['y_conf'] = list(df_res['y_conf'])
    if 'y_conf_gmm' in list(df_res.columns.values):
        adata_t.obs['y_conf_gmm'] = list(df_res['y_conf_gmm'])
    #'''

    adata_t.uns['cnv_ref_celltypes'] = ref_types2
    # summary['clustering_obj'] = cobj
    adata_t.uns['cnv_addon_summary'] = summary

    lst1 = list(df_res.index.values)
    lst2 = list(adata_t.obs.index.values)
    rend = dict(zip(lst1, lst2))
    df_res.rename(index = rend, inplace = True)

    adata_t.obsm['cnv_addon_results'] = df_res 

    #'''
    adata_t.obs['celltype_minor_rev'] = adata_t.obs['celltype_minor'].copy(deep = True).astype(str)
    b = (adata_t.obs['tumor_dec'] == 'Tumor')
    if np.sum(b) > 0:
        if ref_types is not None:
            b = b & (~adata_t.obs['celltype_major'].isin(ref_types))
        adata_t.obs.loc[b, 'celltype_minor_rev'] = 'Tumor cell'
    #'''
    return df_res


def scoda_hicat(adata, mkr_db, print_prefix, verbose = False):
    
    X1 = adata.to_df()
    
    PNSH12 = '100000'
    target_tissues = []
    target_cell_types = []
    # target_cell_types = ['T cell', 'B cell', 'Myeloid cell', 'Fibroblast',
    #                      'Epithelial cell', 'Endothelial cell', 'Mast cell', 
    #                      'Smooth muscle cell', 'Granulocyte'] 
    to_exclude = [] 

    if verbose: print('%sCelltype annotation (using HiCAT) .. ' % (print_prefix), flush = True)
    df_pred, summary = \
        HiCAT( X1, mkr_db, log_transformed = False,
               target_tissues = target_tissues, target_cell_types = target_cell_types, 
               minor_types_to_exclude = to_exclude, mkr_selector = PNSH12, 
               N_neighbors_minor = 31, N_neighbors_subset = 1,  
               Clustering_algo = 'lv', Clustering_resolution = 1, 
               Clustering_base = 'pca', N_pca_components = 15, 
               cycling_cell = False, copy_X = False, verbose = 1, print_prefix = print_prefix + '   ',
               model = 'gmm', N_gmm_components = 20, cbc_cutoff = 0.01,
               Target_FPR = 0.05, pval_th = 0.05, pval_th_subset = 1, 
               pmaj = 0.7, pth_fit_pnt = 0.4, pth_min = 0.5, min_logP_diff = 1, 
               use_minor = True, minor_wgt = 0, use_union = False, use_union_major = True,
               use_markers_for_pca = False, comb_mkrs = False, 
               knn_type = 1, knn_pmaj = 0.3, N_max_to_ave = 2,
               thresholding_minor = False, thresholding_subset = False )
    if verbose: print('%sCelltype annotation (using HiCAT) .. done.  ' % (print_prefix), flush = True)

    adata.obs['celltype_major'] = df_pred['cell_type_major']
    adata.obs['celltype_minor'] = df_pred['cell_type_minor']
    adata.obs['celltype_subset'] = df_pred['cell_type_subset']

    adata.obsm['HiCAT_result'] = df_pred
    
    ## Store marker info.
    mkr_dict, mkr_dict_neg, mkr_dict_sec, major_dict, minor_dict = load_markers_all(mkr_db, target_cells = [], 
                                                                                 pnsh12 = '111000', 
                                                                                 comb_mkrs = False, to_upper = False)
    #'''
    mkr_dict, mkr_dict_neg = \
    get_markers_minor_type2(mkr_db, target_cells = [], 
                            pnsh12 = '100000', comb_mkrs = False, 
                            rem_common = False, verbose = False, to_upper = False)
    #'''

    mkr_info = {}
    if isinstance(mkr_db, pd.DataFrame):
        mkr_info['marker_db'] = mkr_db
    elif isinstance(mkr_db, str):
        mkr_info['marker_db'] = pd.read_csv(mkr_db, sep = '\t')
        
    mkr_info['subset_markers_dict'] = mkr_dict
    mkr_info['subset_to_major_map'] = major_dict
    mkr_info['subset_to_minor_map'] = minor_dict
    adata.uns['Celltype_marker_DB'] = mkr_info
    
    return # adata


def scoda_cci( adata_t, cpdb_path, cond_col, sample_col, 
               cci_base, unit_of_cci_run, min_n_cells_for_cci, 
               data_dir, pval_max, mean_min, Rth, n_cores,
               print_prefix, verbose = False):
    
    if verbose: print('%sCellphoneDB .. ' % (print_prefix), flush = True)
    if cci_base in list(adata_t.obs.columns.values):
        celltype_col = cci_base
    else:
        celltype_col = 'celltype_minor'

    if cond_col not in list(adata_t.obs.columns.values):
        adata_t.obs[cond_col] = 'Not specified'
        if verbose: 
            print('%s   \'condition\' column not specified. Will be set as \'unspecied\'' % print_prefix)        
    cond_lst = list(adata_t.obs[cond_col].unique())
    
    if sample_col not in list(adata_t.obs.columns.values):
        adata_t.obs[sample_col] = 'Not specified'
        if verbose: 
            print('%s   \'sample\' column not specified. Will be set as \'unspecied\'' % print_prefix)
    sample_lst = list(adata_t.obs[sample_col].unique())

    # print(cond_lst)
    # print(sample_lst)
    t_col = cond_col
    t_lst = cond_lst
    
    if unit_of_cci_run == 'sample':
        t_col = sample_col
        t_lst = sample_lst
    else:
        if verbose: print('%s   Unit of CCI RUN is \'condition\'' % print_prefix)        
        
    df_cnt, df_pct= get_population( adata_t.obs[t_col], 
                                    adata_t.obs[celltype_col], sort_by = [] )

    ## Filter celltype with its number is below the minimum value
    N_cells_min = min_n_cells_for_cci
    
    ## Set output dir
    cpdb_dir = data_dir + '/cpdb'
    if not os.path.isdir(cpdb_dir):
        os.mkdir(cpdb_dir)

    dfv_dct = {}
    for k, s in enumerate(t_lst):

        if verbose: print('%s   %2i/%2i - %s' % (print_prefix, k+1, len(t_lst), s))

        out_dir = cpdb_dir + '/CPDB_res_%s' % (s)

        celltype_all = df_cnt.columns.values
        b = df_cnt.loc[s,:] >= N_cells_min
        celltype_lst = list(celltype_all[b])
        
        b1 = adata_t.obs[t_col] == s
        b2 = adata_t.obs[celltype_col].isin(celltype_lst)
        b = b1 & b2
        adata_s = adata_t[b,:]
        celltype = adata_s.obs[celltype_col]

        df_mn, df_pv = cpdb4_run( adata_s, celltype, db = cpdb_path,
                                  out_dir = out_dir, n_cores = n_cores,
                                  threshold = 0.05, gene_id_type = 'gene_name', 
                                  verbose = False )

        dfi, dfp, dfm, dfv = cpdb4_get_results( df_pv, df_mn, 
                                                pval_max = pval_max, mean_min = mean_min )

        dfv_dct[s] = dfv
    ## End for
        
    if unit_of_cci_run == cond_col:
        
        adata_t.uns['CCI'] = dfv_dct
        
    else: 
        
        s2c_map = {}
        group_lst = []
        for k, s in enumerate(sample_lst):
            b = adata_t.obs[sample_col] == s
            cond = list(adata_t.obs.loc[b, cond_col])[0]
            s2c_map[s] = cond
            group_lst.append(cond)

        ## Load CPDB results, convert them to suitable format
        dfv_per_group = {}
        for s, g in zip(sample_lst, group_lst):
            
            dfv = dfv_dct[s]            
            if g in dfv_per_group.keys():
                dfv_per_group[g].append(dfv)
            else:
                dfv_per_group[g] = [dfv]    
                
        ## Filter CCIs
        ## Get all gg--cc indices: idx_lst_all

        rth = Rth

        idx_lst_all = []
        idx_dct = {}
        df_dct = {}

        for g in dfv_per_group.keys():
            lst = dfv_per_group[g]

            ## Get list of gg--cc indices (idx_lst) that meets the requirement
            idx_lst = []
            for df in lst:
                idx_lst = idx_lst + list(df.index.values)
                
            idx_lst = list(set(idx_lst))
            # print(len(idx_lst))
            idx_lst.sort()

            ## For each gg--cc index, 
            ## Get # of samples where gg--cc interaction detected
            ps = pd.Series(0, index = idx_lst)

            for df in lst:
                ps[df.index.values] += 1

            ## Get Union of gg--cc indices from all groups
            b = ps >= len(lst)*rth
            idxs = list(ps.index.values[b])
            idx_dct[g] = idxs
            idx_lst_all = idx_lst_all + idxs

            if verbose: print('%sGroup: %s (Ns = %i) - N_valid_interactions: %i among %i.' % (print_prefix, g, len(lst), np.sum(b), len(b)))

            ## Get combined dfv
            ## pval = max(pvals)
            ## mean = mean(means)

            dfv = pd.DataFrame(index = idxs, columns = df.columns)
            dfv['pval'] = 0
            dfv['mean'] = 0
            for k, df in enumerate(lst):

                idxt = list(set(idxs).intersection(list(df.index.values)))
                cols = list(df.columns.values[:-2])
                dfv.loc[idxt, cols] = df.loc[idxt, cols]
                dfv.loc[idxt, 'mean'] = dfv.loc[idxt, 'mean'] + df.loc[idxt, 'mean']
                dft = pd.DataFrame(index = idxt)
                dft['pv1'] = dfv.loc[idxt, 'pval']
                dft['pv2'] = df.loc[idxt, 'pval']
                dfv.loc[idxt, 'pval'] = dft.max(axis = 1)

            dfv['mean'] = dfv['mean']/len(lst) 
            df_dct[g] = dfv

        idx_lst_all = list(set(idx_lst_all))
        if verbose: print('%sNumber of common Interactions: ' % print_prefix, len(idx_lst_all))    
        
        adata_t.uns['CCI'] = df_dct
    # if verbose: print('%sCellphoneDB .. done. ' % (print_prefix), flush = True)
        
    return


def scoda_deg_gsea( adata_t, pw_db, 
                    cond_col, sample_col, 
                    deg_base, ref_group, deg_pval_cutoff,
                    gsea_pval_cutoff, N_cells_min_per_sample, 
                    N_cells_min_per_condition, n_cores, 
                    print_prefix, verbose = False): 
        
    # ref_group_for_deg = ref_group
    ref_group_for_deg = None
    if ref_group is not None:
        if ref_group in list(adata_t.obs[cond_col].unique()):
            ref_group_for_deg = ref_group    
    
    # test_method = 't-test' # 't-test', 'wilcoxon'
    pw_db_sel = pw_db
    R_max = 2
    min_size = 5
    max_size = 1000                
    log_fc_col = 'log2_FC'
    gene_col = 'gene'

    if deg_base in list(adata_t.obs.columns.values):
        celltype_col = deg_base
    else:
        celltype_col = 'celltype_minor'

    if cond_col not in list(adata_t.obs.columns.values):
        adata_t.obs[cond_col] = 'Not specified'
    cond_lst = list(adata_t.obs[cond_col].unique())
    
    if sample_col not in list(adata_t.obs.columns.values):
        adata_t.obs[sample_col] = 'Not specified'
    sample_lst = list(adata_t.obs[sample_col].unique())
    
    if len(cond_lst) <= 1:
        if verbose: print('%sDEG analysis not performed.' % print_prefix)
        if verbose: print('%s(might be single sample or no sample condition provided.)' % print_prefix)
    else:
        if verbose: print('%sDEG/GSA analysis .. ' % (print_prefix), flush = True)
        pass
        
        ## Normalize and log-transform
        adata = adata_t[:,:]
        # if not tumor_identification:    
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

        cond_lst = list(adata.obs[cond_col].unique())
        celltype_lst = list(adata.obs[celltype_col].unique()) 
        genes_all = list(adata.var.index.values)

        df_dct_dct_n_cells = {}
        df_dct_dct_deg = {}
        df_dct_dct_enr = {}
        df_dct_dct_enr_up = {}
        df_dct_dct_enr_dn = {}
        df_dct_dct_pr = {}
        
        if 'unassigned' in celltype_lst:
            celltype_lst = list(set(celltype_lst) - {'unassigned'})
        celltype_lst.sort()
        
        if ref_group_for_deg is not None:
            if ref_group_for_deg not in list(adata_s.obs[cond_col].unique()):
                if verbose: 
                    print('%s   WARNING: Ref group %s not present -> will be performed in one-against-the-rest.' \
                       % (print_prefix, ref_group_for_deg))
                ref_group_for_deg = None
                
        for ct in celltype_lst:
            
            b = adata.obs[celltype_col] == ct
            adata_sel = adata[b,:]

            adata_s = select_samples( adata_sel, sample_col, 
                                      N_min = N_cells_min_per_sample, R_max = R_max )

            pcnt = adata_s.obs[cond_col].value_counts()
            s = ''
            for i in pcnt.index.values:
                s = s + '%i(%s), ' % (pcnt[i], i)
            s = s[:-2]

            if ((pcnt.min() < N_cells_min_per_condition) or pcnt.shape[0] <= 1):
                if verbose: 
                    print('%s   %s: %s -> insufficient # of cells -> DEG skipped.' \
                           % (print_prefix, ct, s), flush = True)
            else:
                if verbose: print('%s   %s: %s' % (print_prefix, ct, s), flush = True)

                df_cbyg_in = adata_s.to_df()
                groups_in = adata_s.obs[cond_col]
                samples_in = adata_s.obs.index.values

                df_lst, nc_lst = deg_multi( df_cbyg_in, groups_in, ref_group = ref_group_for_deg, 
                                    samples_in = samples_in, min_exp_frac = 0.05, 
                                    exp_only = False, min_frac = 0.05 )
                df_dct_dct_deg[ct] = df_lst
                df_dct_dct_n_cells[ct] = nc_lst

                '''
                '''
                ## Run gseapy.prerank
                df_lst_enrichr = {}
                df_lst_enrichr_up = {}
                df_lst_enrichr_dn = {}
                df_lst_prerank = {}
                #'''
                for c in df_lst.keys():
                    
                    gene_rank = df_lst[c].copy(deep = True)
                    b = gene_rank['pval'] <= deg_pval_cutoff

                    # print(np.sum(b), gene_rank.shape)
                    if np.sum(b) > 1:
                        gene_rank = gene_rank.loc[b,:]              
                        gene_rank[gene_col] = list(gene_rank.index.values)

                        ## Run gseapy.enrichr
                        df_res_enr_pos = None
                        b = gene_rank[log_fc_col] > 0
                        if np.sum(b) > 0:
                            df_res_enr_pos = run_gsa(gene_rank.loc[b,gene_col], pw_db_sel, genes_all, 
                                                     pval_max = gsea_pval_cutoff, min_size = min_size)
                            df_res_enr_pos['Ind'] = 1
                            # if verbose: print('  Num. of selected pathways in Enrichr (+): ', df_res_enr_pos.shape[0])

                        df_res_enr_neg = None
                        b = gene_rank[log_fc_col] < 0
                        if np.sum(b) > 0:
                            df_res_enr_neg = run_gsa(gene_rank.loc[b,gene_col], pw_db_sel, genes_all, 
                                                     pval_max = gsea_pval_cutoff, min_size = min_size)
                            df_res_enr_neg['Ind'] = -1
                            # if verbose: print('  Num. of selected pathways in Enrichr (-): ', df_res_enr_neg.shape[0])

                        if (df_res_enr_pos is not None) & (df_res_enr_neg is not None):
                            df_res_enr = pd.concat([df_res_enr_pos, df_res_enr_neg], axis = 0)
                        elif (df_res_enr_pos is not None):
                            df_res_enr = df_res_enr_pos
                        elif (df_res_enr_neg is not None):
                            df_res_enr = df_res_enr_neg
                        else:
                            df_res_enr = None

                        if df_res_enr is not None:
                            df_lst_enrichr[c] = df_res_enr

                        if df_res_enr_pos is not None:
                            df_lst_enrichr_up[c] = df_res_enr_pos
                        if df_res_enr_neg is not None:
                            df_lst_enrichr_dn[c] = df_res_enr_neg

                        ## Run gseapy.prerank
                        logfc = gene_rank[[log_fc_col]] ## index must be gene name
                        df_res_pr, pr_res = run_prerank(logfc, pw_db_sel, pval_max = gsea_pval_cutoff,
                                        min_size = min_size, max_size = max_size, n_cores = n_cores )

                        # df_res_pr.drop(columns = ['Tag %', 'Gene %'], inplace = True)
                        if df_res_pr.shape[0] > 0:
                            df_res_pr[['ES', 'NES', 'NOM p-val', 'FDR q-val', 'FWER p-val']] = \
                                df_res_pr[['ES', 'NES', 'NOM p-val', 'FDR q-val', 'FWER p-val']].astype(float)
                            df_lst_prerank[c] = df_res_pr                        

                df_dct_dct_enr_up[ct] = df_lst_enrichr_up
                df_dct_dct_enr_dn[ct] = df_lst_enrichr_dn
                df_dct_dct_enr[ct] = df_lst_enrichr
                df_dct_dct_pr[ct] = df_lst_prerank
                # '''

        adata_t.uns['DEG_stat'] = df_dct_dct_n_cells
        adata_t.uns['DEG'] = df_dct_dct_deg
        # adata_t.uns['GSA'] = df_dct_dct_enr
        adata_t.uns['GSA_up'] = df_dct_dct_enr_up
        adata_t.uns['GSA_down'] = df_dct_dct_enr_dn
        adata_t.uns['GSEA'] = df_dct_dct_pr
        
    # if verbose: print('%sDEG/GSA analysis .. done. ' % (print_prefix), flush = True)
    
    return
