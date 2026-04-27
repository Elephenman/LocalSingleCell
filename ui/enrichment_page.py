import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from core import enrichment
from utils import exception_utils


def show():
    """
    基因富集分析页面
    """
    # 页面前置校验
    if not st.session_state.is_analysis_done:
        st.warning("请先完成分析流程")
        return
    
    st.title("基因富集分析")
    
    # 获取AnnData对象
    adata = st.session_state.anndata_obj
    
    # 基础配置区域
    st.markdown("## 基础配置")
    
    # 检测数据类型
    is_spatial = st.session_state.get('is_spatial_data', False)
    
    # 构建基因来源选项
    gene_source_options = ["所有聚类的显著差异基因", "指定聚类的差异基因", "自定义基因列表"]
    if is_spatial:
        gene_source_options.append("空间可变基因")
    
    # 选择基因来源
    gene_source = st.selectbox(
        "选择基因来源",
        gene_source_options,
        index=0
    )
    
    # 联动逻辑
    genes = []
    
    if gene_source == "指定聚类的差异基因":
        # 选择聚类
        cluster_key = 'leiden'
        clusters = sorted(adata.obs[cluster_key].unique())
        selected_cluster = st.selectbox("选择聚类", clusters, index=0)
        
        # 选择基因类型
        gene_type = st.multiselect(
            "选择基因类型",
            ["上调基因", "下调基因", "所有显著基因"],
            default=["所有显著基因"]
        )
        
        # 获取差异基因
        import scanpy as sc
        df = sc.get.rank_genes_groups_df(adata, group=str(selected_cluster))
        sig_genes = df[df['padj'] < 0.05]
        
        if "上调基因" in gene_type:
            up_genes = sig_genes[sig_genes['logfoldchanges'] > 0]['names'].tolist()
            genes.extend(up_genes)
        if "下调基因" in gene_type:
            down_genes = sig_genes[sig_genes['logfoldchanges'] < 0]['names'].tolist()
            genes.extend(down_genes)
        if "所有显著基因" in gene_type:
            all_genes = sig_genes['names'].tolist()
            genes = all_genes
    
    elif gene_source == "自定义基因列表":
        # 自定义基因输入
        custom_genes = st.text_area("输入基因列表（多个用逗号、空格或换行分隔）")
        if custom_genes:
            # 分割基因
            genes = [gene.strip() for gene in custom_genes.replace(',', ' ').split() if gene.strip()]
    
    elif gene_source == "空间可变基因":
        # 空间可变基因
        if 'moranI' in adata.uns:
            # 显示Top N空间可变基因选择滑块
            top_svg = st.slider("选择Top N空间可变基因", min_value=5, max_value=200, step=5, value=50)
            
            # 获取空间可变基因
            svg_df = adata.uns['moranI']
            # 按I值排序，取Top N
            top_genes = svg_df.sort_values('I', ascending=False).head(top_svg)['gene'].tolist()
            genes = top_genes
            
            st.info(f"已选择Top {top_svg}个空间可变基因")
        else:
            st.warning("未找到空间可变基因结果，请先运行空间可变基因分析")
            genes = []
    
    else:  # 所有聚类的显著差异基因
        import scanpy as sc
        all_genes = []
        cluster_key = 'leiden'
        clusters = sorted(adata.obs[cluster_key].unique())
        
        for cluster in clusters:
            df = sc.get.rank_genes_groups_df(adata, group=str(cluster))
            sig_genes = df[df['padj'] < 0.05]['names'].tolist()
            all_genes.extend(sig_genes)
        
        # 去重
        genes = list(set(all_genes))
    
    # 物种选择
    organism = st.selectbox(
        "物种选择",
        ["人（Human）", "小鼠（Mouse）", "大鼠（Rat）"],
        index=0
    )
    organism_map = {
        "人（Human）": "human",
        "小鼠（Mouse）": "mouse",
        "大鼠（Rat）": "rat"
    }
    organism_code = organism_map[organism]
    
    # 富集数据库选择
    databases = st.multiselect(
        "富集数据库选择",
        ["GO-BP（生物过程）", "GO-CC（细胞组分）", "GO-MF（分子功能）", "KEGG", "Reactome"],
        default=["GO-BP（生物过程）", "KEGG"]
    )
    db_map = {
        "GO-BP（生物过程）": "GO_BP",
        "GO-CC（细胞组分）": "GO_CC",
        "GO-MF（分子功能）": "GO_MF",
        "KEGG": "KEGG",
        "Reactome": "Reactome"
    }
    selected_dbs = [db_map[db] for db in databases]
    
    # 显著性阈值
    st.markdown("### 显著性阈值")
    p_adjust_cutoff = st.slider("调整后p值最大值（p.adjust）", min_value=0.001, max_value=0.1, step=0.001, value=0.05)
    min_gene_count = st.slider("最小富集基因数", min_value=1, max_value=10, step=1, value=3)
    
    # 展示的Top富集条目数量
    top_terms = st.slider("展示的Top富集条目数量", min_value=5, max_value=50, step=5, value=10)
    
    # 分析执行区域
    st.markdown("## 分析执行")
    
    if st.button("开始富集分析"):
        if not genes:
            st.error("未找到有效基因，请检查基因来源设置")
            return
        
        try:
            with st.spinner("正在执行富集分析..."):
                # 运行富集分析
                results = enrichment.run_enrichment(
                    gene_list=genes,
                    organism=organism_code,
                    databases=selected_dbs,
                    p_adjust_cutoff=p_adjust_cutoff,
                    min_gene_count=min_gene_count
                )
                
                # 更新全局状态
                st.session_state.enrichment_result = results
                
                st.success("富集分析完成！")
                
        except Exception as e:
            st.error(f"执行富集分析失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 结果展示区域
    if 'enrichment_result' in st.session_state and st.session_state.enrichment_result:
        st.markdown("## 结果展示")
        
        # 分标签页展示不同数据库的富集分析结果
        results = st.session_state.enrichment_result
        if results:
            db_tabs = st.tabs(databases)
            
            for i, db in enumerate(databases):
                with db_tabs[i]:
                    db_key = db_map[db]
                    result_df = results.get(db_key, pd.DataFrame())
                    
                    if result_df.empty:
                        st.info("无显著富集结果")
                    else:
                        # 显示结果表格
                        st.markdown("### 富集分析结果表格")
                        st.dataframe(result_df.head(top_terms))
                        
                        # 图表类型选择
                        chart_type = st.selectbox(
                            "选择图表类型",
                            ["富集气泡图", "富集柱状图"],
                            index=0,
                            key=f"chart_type_{db_key}"
                        )
                        
                        # 生成图表
                        st.markdown("### 富集分析图表")
                        if chart_type == "富集气泡图":
                            fig = enrichment.plot_enrichment_bubble(result_df.head(top_terms))
                        else:
                            fig = enrichment.plot_enrichment_bar(result_df.head(top_terms))
                        st.pyplot(fig)
                        plt.close()
    
    # 下载功能
    if 'enrichment_result' in st.session_state and st.session_state.enrichment_result:
        st.markdown("## 下载功能")
        
        # 下载富集分析完整结果
        if st.button("下载富集分析完整结果"):
            try:
                import io
                import xlsxwriter
                
                # 创建Excel文件
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    results = st.session_state.enrichment_result
                    for db, result_df in results.items():
                        if not result_df.empty:
                            # 将数据库名称转换为中文
                            db_name = {v: k for k, v in db_map.items()}.get(db, db)
                            result_df.to_excel(writer, sheet_name=db_name[:30], index=False)
                
                output.seek(0)
                
                # 提供下载
                st.download_button(
                    label="下载Excel文件",
                    data=output,
                    file_name="enrichment_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"下载失败: {exception_utils.get_user_friendly_error(e)}")