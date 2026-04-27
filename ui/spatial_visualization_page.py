import streamlit as st
import matplotlib.pyplot as plt
from core import spatial_visualization
from utils import exception_utils


def show():
    """
    空间转录组结果可视化页面
    """
    # 页面前置校验
    if not st.session_state.is_analysis_done or not st.session_state.get('is_spatial_data', False):
        st.warning("请先完成空间转录组分析流程")
        return
    
    st.title("空间转录组结果可视化")
    
    # 获取AnnData对象
    adata = st.session_state.anndata_obj
    
    # 标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ 组织切片空间分布图", 
        "🧬 基因表达空间图", 
        "📊 空间聚类可视化", 
        "🔬 空间可变基因",
        "📍 共定位分析"
    ])
    
    # 标签页1：组织切片空间分布图
    with tab1:
        st.subheader("组织切片空间分布图")
        
        # 基础配置
        st.markdown("#### 基础配置")
        
        # 选择颜色分组依据
        color_options = list(adata.obs.columns)
        color_by = st.selectbox("颜色分组依据", color_options, index=color_options.index('leiden') if 'leiden' in color_options else 0)
        
        # 图表配置
        st.markdown("#### 图表配置")
        spot_size = st.slider("点大小", min_value=1, max_value=50, step=1, value=10)
        alpha = st.slider("透明度", min_value=0.1, max_value=1.0, step=0.1, value=1.0)
        show_image = st.checkbox("显示组织切片图像", value=True)
        
        if show_image:
            img_alpha = st.slider("图像透明度", min_value=0.1, max_value=1.0, step=0.1, value=0.5)
            # 获取可用的图像类型
            image_types = []
            if 'spatial' in adata.uns and 'images' in adata.uns['spatial']:
                image_types = list(adata.uns['spatial']['images'].keys())
            if image_types:
                image_key = st.selectbox("选择图像", image_types, index=0)
            else:
                image_key = 'hires'
        else:
            img_alpha = 0.5
            image_key = 'hires'
        
        # 生成图表按钮
        if st.button("生成图表", key="spatial_plot"):
            try:
                st.markdown("### 组织切片空间分布图")
                if show_image:
                    fig = spatial_visualization.plot_image_with_overlay(
                        adata,
                        color=color_by,
                        image_key=image_key,
                        alpha=img_alpha
                    )
                else:
                    fig = spatial_visualization.plot_spatial_scatter(
                        adata,
                        color=color_by,
                        spot_size=spot_size,
                        alpha=alpha
                    )
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页2：基因表达空间图
    with tab2:
        st.subheader("基因表达空间图")
        
        # 基础配置
        st.markdown("#### 基础配置")
        
        # 基因输入
        custom_genes = st.text_input("输入基因名（多个用逗号分隔）")
        ncols = st.slider("每行显示的图表数", min_value=1, max_value=4, step=1, value=2)
        
        # 图表配置
        st.markdown("#### 图表配置")
        spot_size_gene = st.slider("点大小", min_value=1, max_value=50, step=1, value=10, key="spot_size_gene")
        show_image_gene = st.checkbox("显示组织切片图像", value=True, key="show_image_gene")
        
        if show_image_gene:
            img_alpha_gene = st.slider("图像透明度", min_value=0.1, max_value=1.0, step=0.1, value=0.5, key="img_alpha_gene")
        else:
            img_alpha_gene = 0.5
        
        # 生成图表按钮
        if st.button("生成图表", key="gene_spatial_plot"):
            if custom_genes:
                try:
                    # 处理基因列表
                    gene_list = [gene.strip() for gene in custom_genes.split(',') if gene.strip()]
                    
                    if gene_list:
                        st.markdown("### 基因表达空间图")
                        
                        # 验证基因是否存在
                        valid_genes = [gene for gene in gene_list if gene in adata.var_names]
                        invalid_genes = [gene for gene in gene_list if gene not in adata.var_names]
                        
                        if invalid_genes:
                            st.warning(f"以下基因不存在: {', '.join(invalid_genes)}")
                        
                        if valid_genes:
                            fig = spatial_visualization.plot_genes_spatial(
                                adata,
                                genes=valid_genes,
                                ncols=ncols,
                                spot_size=spot_size_gene,
                                img=show_image_gene,
                                img_alpha=img_alpha_gene
                            )
                            st.pyplot(fig)
                            plt.close()
                    else:
                        st.warning("未输入有效基因")
                except Exception as e:
                    st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
            else:
                st.warning("请输入基因名")
    
    # 标签页3：空间聚类可视化
    with tab3:
        st.subheader("空间聚类可视化")
        
        # 生成图表按钮
        if st.button("生成空间聚类图", key="spatial_cluster_plot"):
            try:
                st.markdown("### 空间聚类分布")
                fig = spatial_visualization.plot_spatial_cluster_composition(
                    adata,
                    cluster_key='leiden'
                )
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页4：空间可变基因
    with tab4:
        st.subheader("空间可变基因")
        
        # 基础配置
        st.markdown("#### 基础配置")
        n_top = st.slider("显示的Top基因数量", min_value=5, max_value=20, step=1, value=10)
        
        # 生成图表按钮
        if st.button("显示空间可变基因", key="svg_plot"):
            try:
                st.markdown("### 空间可变基因")
                fig = spatial_visualization.plot_spatial_variable_genes(
                    adata,
                    n_top=n_top
                )
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页5：共定位分析
    with tab5:
        st.subheader("共定位分析")
        
        # 生成图表按钮
        if st.button("显示共定位分析结果", key="colocalization_plot"):
            try:
                st.markdown("### 细胞类型共定位分析")
                fig = spatial_visualization.plot_co_occurrence(
                    adata,
                    cluster_key='leiden'
                )
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
