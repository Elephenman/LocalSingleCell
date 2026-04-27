import gseapy as gp
import pandas as pd
import numpy as np


def run_enrichment(gene_list, organism='human', databases=['GO_BP', 'KEGG'], p_adjust_cutoff=0.05, min_gene_count=3):
    """
    运行基因富集分析
    
    Args:
        gene_list: 基因列表
        organism: 物种，可选 'human', 'mouse', 'rat'
        databases: 富集数据库列表
        p_adjust_cutoff: 调整后p值阈值
        min_gene_count: 最小富集基因数
    
    Returns:
        dict: 各数据库的富集分析结果
    """
    results = {}
    
    # 物种映射
    organism_map = {
        'human': 'hsapiens',
        'mouse': 'mmusculus',
        'rat': 'rnorvegicus'
    }
    
    if organism not in organism_map:
        raise Exception(f"不支持的物种: {organism}")
    
    organism_code = organism_map[organism]
    
    # 对每个数据库运行富集分析
    for db in databases:
        try:
            # 运行富集分析
            enr = gp.enrichr(
                gene_list=gene_list,
                gene_sets=db,
                organism=organism_code,
                outdir=None,
                cutoff=p_adjust_cutoff
            )
            
            # 获取结果
            result_df = enr.results
            
            # 过滤结果
            filtered_result = result_df[
                (result_df['Adjusted P-value'] < p_adjust_cutoff) & 
                (result_df['Overlap'].apply(lambda x: int(x.split('/')[0]) >= min_gene_count))
            ]
            
            # 按调整后p值排序
            filtered_result = filtered_result.sort_values('Adjusted P-value')
            
            results[db] = filtered_result
        except Exception as e:
            results[db] = pd.DataFrame()
            print(f"{db} 富集分析失败: {str(e)}")
    
    return results


def get_marker_genes(adata, cluster, top_n=10):
    """
    获取指定聚类的标记基因
    
    Args:
        adata: AnnData对象
        cluster: 聚类编号
        top_n: 前N个标记基因
    
    Returns:
        list: 标记基因列表
    """
    try:
        # 提取指定聚类的标记基因
        cluster_key = 'leiden'
        
        # 使用scanpy的内置函数获取标记基因
        import scanpy as sc
        marker_genes = sc.get.rank_genes_groups_df(adata, group=str(cluster))
        
        # 过滤显著差异基因
        significant_genes = marker_genes[marker_genes['padj'] < 0.05]
        
        # 按log2FC排序，取前top_n个
        top_genes = significant_genes.sort_values('logfoldchanges', ascending=False).head(top_n)
        
        return top_genes['names'].tolist()
    except Exception as e:
        raise Exception(f"获取标记基因失败: {str(e)}")


def plot_enrichment_bubble(result_df, save_path=None):
    """
    绘制富集分析气泡图
    
    Args:
        result_df: 富集分析结果DataFrame
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    if result_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, '无显著富集结果', ha='center', va='center')
        return fig
    
    # 计算富集因子
    result_df['Enrichment Factor'] = result_df['Overlap'].apply(lambda x: int(x.split('/')[0]) / int(x.split('/')[1]))
    
    # 取前20个结果
    top_result = result_df.head(20)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制气泡图
    sns.scatterplot(
        x='Enrichment Factor',
        y='Term',
        size='Combined Score',
        hue='Adjusted P-value',
        data=top_result,
        ax=ax,
        sizes=(50, 500),
        palette='viridis_r'
    )
    
    ax.set_title('基因富集分析气泡图')
    ax.set_xlabel('富集因子')
    ax.set_ylabel('富集条目')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_enrichment_bar(result_df, save_path=None):
    """
    绘制富集分析柱状图
    
    Args:
        result_df: 富集分析结果DataFrame
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    if result_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, '无显著富集结果', ha='center', va='center')
        return fig
    
    # 取前20个结果
    top_result = result_df.head(20)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制柱状图
    sns.barplot(
        x='Combined Score',
        y='Term',
        data=top_result,
        ax=ax,
        palette='viridis'
    )
    
    ax.set_title('基因富集分析柱状图')
    ax.set_xlabel('综合得分')
    ax.set_ylabel('富集条目')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig