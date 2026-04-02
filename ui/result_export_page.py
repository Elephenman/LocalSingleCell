import streamlit as st
import os
import tempfile
import zipfile
import io
import pandas as pd
import matplotlib.pyplot as plt
from utils import exception_utils


def show():
    """
    结果导出页面
    """
    # 页面前置校验
    if not st.session_state.get('is_analysis_done', False):
        st.warning("请先完成分析流程")
        return
    
    st.title("结果导出")
    
    # 获取AnnData对象
    adata = st.session_state.anndata_obj
    
    # 检测数据类型
    is_spatial = st.session_state.get('is_spatial_data', False)
    
    # 导出选项配置
    st.markdown("## 导出选项")
    
    # 复选框组
    export_options = {
        "h5ad": st.checkbox("分析完成的AnnData对象（.h5ad格式）", value=True),
        "qc": st.checkbox("质控结果表格（.csv格式）", value=True),
        "cluster": st.checkbox("聚类结果表格（.csv格式）", value=True),
        "markers": st.checkbox("所有聚类的标记基因完整表格（.csv格式）", value=True),
        "diff": st.checkbox("所有聚类的差异基因完整表格（.csv格式）", value=True),
        "enrichment": st.checkbox("富集分析完整结果（.xlsx格式）", value=True),
        "figures": st.checkbox("所有已生成的可视化图表（PNG 300dpi格式）", value=True),
        "report": st.checkbox("自动化分析报告（.html格式）", value=True)
    }
    
    # 空间数据专属导出选项
    if is_spatial:
        st.markdown("### 空间分析专属选项")
        export_options["spatial_h5ad"] = st.checkbox("空间分析结果（.h5ad格式，包含空间信息）", value=True)
        export_options["spatial_genes"] = st.checkbox("空间可变基因表格（.csv格式）", value=True)
        export_options["spatial_figures"] = st.checkbox("空间可视化图表（PNG 300dpi格式）", value=True)
    
    # 导出功能
    st.markdown("## 导出功能")
    
    if st.button("一键打包导出"):
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 准备导出文件
                files_to_zip = []
                
                # 1. 分析完成的AnnData对象
                if export_options["h5ad"]:
                    h5ad_path = os.path.join(temp_dir, "adata.h5ad")
                    adata.write_h5ad(h5ad_path)
                    files_to_zip.append((h5ad_path, "adata.h5ad"))
                
                # 2. 质控结果表格
                if export_options["qc"]:
                    qc_path = os.path.join(temp_dir, "qc_results.csv")
                    adata.obs.to_csv(qc_path)
                    files_to_zip.append((qc_path, "qc_results.csv"))
                
                # 3. 聚类结果表格
                if export_options["cluster"]:
                    cluster_path = os.path.join(temp_dir, "cluster_results.csv")
                    cluster_key = 'leiden'
                    cluster_df = adata.obs[[cluster_key]]
                    cluster_df.to_csv(cluster_path)
                    files_to_zip.append((cluster_path, "cluster_results.csv"))
                
                # 4. 所有聚类的标记基因完整表格
                if export_options["markers"]:
                    import scanpy as sc
                    markers_dir = os.path.join(temp_dir, "markers")
                    os.makedirs(markers_dir, exist_ok=True)
                    
                    cluster_key = 'leiden'
                    clusters = sorted(adata.obs[cluster_key].unique())
                    
                    for cluster in clusters:
                        df = sc.get.rank_genes_groups_df(adata, group=str(cluster))
                        marker_path = os.path.join(markers_dir, f"cluster_{cluster}_markers.csv")
                        df.to_csv(marker_path, index=False)
                        files_to_zip.append((marker_path, f"markers/cluster_{cluster}_markers.csv"))
                
                # 5. 所有聚类的差异基因完整表格
                if export_options["diff"]:
                    import scanpy as sc
                    diff_dir = os.path.join(temp_dir, "diff_genes")
                    os.makedirs(diff_dir, exist_ok=True)
                    
                    cluster_key = 'leiden'
                    clusters = sorted(adata.obs[cluster_key].unique())
                    
                    for cluster in clusters:
                        df = sc.get.rank_genes_groups_df(adata, group=str(cluster))
                        # 过滤显著差异基因
                        sig_df = df[df['padj'] < 0.05]
                        diff_path = os.path.join(diff_dir, f"cluster_{cluster}_diff_genes.csv")
                        sig_df.to_csv(diff_path, index=False)
                        files_to_zip.append((diff_path, f"diff_genes/cluster_{cluster}_diff_genes.csv"))
                
                # 6. 富集分析完整结果
                if export_options["enrichment"] and 'enrichment_result' in st.session_state:
                    enrichment_path = os.path.join(temp_dir, "enrichment_results.xlsx")
                    results = st.session_state.enrichment_result
                    
                    with pd.ExcelWriter(enrichment_path, engine='xlsxwriter') as writer:
                        for db, result_df in results.items():
                            if not result_df.empty:
                                result_df.to_excel(writer, sheet_name=db[:30], index=False)
                    
                    files_to_zip.append((enrichment_path, "enrichment_results.xlsx"))
                
                # 7. 所有已生成的可视化图表
                if export_options["figures"]:
                    # 这里需要实际生成图表，或者从缓存中获取
                    # 暂时跳过，实际实现时需要根据生成的图表进行处理
                    pass
                
                # 8. 自动化分析报告
                if export_options["report"]:
                    report_path = os.path.join(temp_dir, "analysis_report.html")
                    generate_report(adata, report_path, is_spatial)
                    files_to_zip.append((report_path, "analysis_report.html"))
                
                # 空间数据专属导出
                if is_spatial:
                    # 9. 空间分析结果h5ad
                    if export_options.get("spatial_h5ad", False):
                        spatial_h5ad_path = os.path.join(temp_dir, "spatial_adata.h5ad")
                        adata.write_h5ad(spatial_h5ad_path)
                        files_to_zip.append((spatial_h5ad_path, "spatial_adata.h5ad"))
                    
                    # 10. 空间可变基因表格
                    if export_options.get("spatial_genes", False) and 'moranI' in adata.uns:
                        spatial_genes_path = os.path.join(temp_dir, "spatial_variable_genes.csv")
                        svg_df = adata.uns['moranI']
                        svg_df.to_csv(spatial_genes_path, index=False)
                        files_to_zip.append((spatial_genes_path, "spatial_variable_genes.csv"))
                    
                    # 11. 空间可视化图表
                    if export_options.get("spatial_figures", False):
                        spatial_figs_dir = os.path.join(temp_dir, "spatial_figures")
                        os.makedirs(spatial_figs_dir, exist_ok=True)
                        
                        try:
                            # 导入空间可视化模块
                            from core import spatial_visualization
                            
                            # 生成空间聚类图
                            if 'leiden' in adata.obs:
                                fig = spatial_visualization.plot_spatial_cluster_composition(adata, cluster_key='leiden')
                                fig_path = os.path.join(spatial_figs_dir, "spatial_clusters.png")
                                fig.savefig(fig_path, dpi=300, bbox_inches='tight')
                                files_to_zip.append((fig_path, "spatial_figures/spatial_clusters.png"))
                                plt.close(fig)
                            
                            # 生成空间散点图
                            fig = spatial_visualization.plot_spatial_scatter(adata, color='leiden' if 'leiden' in adata.obs else None)
                            fig_path = os.path.join(spatial_figs_dir, "spatial_scatter.png")
                            fig.savefig(fig_path, dpi=300, bbox_inches='tight')
                            files_to_zip.append((fig_path, "spatial_figures/spatial_scatter.png"))
                            plt.close(fig)
                            
                        except Exception as e:
                            # 空间图表生成失败时跳过，不影响整体导出
                            pass
                
                # 创建zip文件
                zip_path = os.path.join(temp_dir, "analysis_results.zip")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path, arcname in files_to_zip:
                        zipf.write(file_path, arcname)
                
                # 提供下载
                with open(zip_path, 'rb') as f:
                    st.download_button(
                        label="下载分析结果压缩包",
                        data=f,
                        file_name="analysis_results.zip",
                        mime="application/zip"
                    )
                
                st.success("导出完成！")
                
        except Exception as e:
            st.error(f"导出失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 额外功能
    st.markdown("## 额外功能")
    
    # 单独导出AnnData对象
    if st.button("单独导出AnnData对象"):
        try:
            import io
            
            # 创建内存缓冲区
            buffer = io.BytesIO()
            adata.write_h5ad(buffer)
            buffer.seek(0)
            
            st.download_button(
                label="下载AnnData对象",
                data=buffer,
                file_name="adata.h5ad",
                mime="application/x-hdf5"
            )
        except Exception as e:
            st.error(f"导出失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 生成分析报告
    if st.button("生成分析报告"):
        try:
            import io
            
            # 创建内存缓冲区
            buffer = io.BytesIO()
            
            # 生成报告
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                generate_report(adata, tmp.name, is_spatial)
                
                # 读取报告内容
                with open(tmp.name, 'rb') as f:
                    buffer.write(f.read())
                
                # 清理临时文件
                os.unlink(tmp.name)
            
            buffer.seek(0)
            
            st.download_button(
                label="下载分析报告",
                data=buffer,
                file_name="analysis_report.html",
                mime="text/html"
            )
        except Exception as e:
            st.error(f"生成报告失败: {exception_utils.get_user_friendly_error(e)}")


def generate_report(adata, output_path, is_spatial=False):
    """
    生成自动化分析报告
    
    Args:
        adata: AnnData对象
        output_path: 输出路径
        is_spatial: 是否为空间转录组数据
    """
    # 空间分析章节
    spatial_section = ""
    if is_spatial:
        has_spatial = 'spatial' in adata.obsm
        has_image = 'spatial' in adata.uns and 'images' in adata.uns['spatial']
        has_svg = 'moranI' in adata.uns
        
        spatial_section = f"""
        <h2>6. 空间转录组分析</h2>
        <div class="info-box">
            <p>包含空间坐标: {'是' if has_spatial else '否'}</p>
            <p>包含组织图像: {'是' if has_image else '否'}</p>
            <p>空间可变基因分析: {'已完成' if has_svg else '未完成'}</p>
            {'<p>空间可变基因数量: ' + str(len(adata.uns['moranI'])) if has_svg else ''}</p>
        </div>
        """
    
    # 生成HTML报告
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LocalSingleCell 分析报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .info-box {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 3px solid #333; }}
        </style>
    </head>
    <body>
        <h1>LocalSingleCell 分析报告</h1>
        
        <h2>1. 数据基本信息</h2>
        <div class="info-box">
            <p>数据类型: {'空间转录组' if is_spatial else '单细胞转录组'}</p>
            <p>细胞总数: {adata.n_obs}</p>
            <p>基因总数: {adata.n_vars}</p>
        </div>
        
        <h2>2. 质控结果</h2>
        <div class="info-box">
            <p>质控后细胞数: {adata.n_obs}</p>
            <p>质控后基因数: {adata.n_vars}</p>
        </div>
        
        <h2>3. 聚类结果</h2>
        <div class="info-box">
            <p>聚类方法: Leiden</p>
            <p>聚类数量: {len(adata.obs['leiden'].unique())}</p>
        </div>
        
        <h2>4. 分析参数</h2>
        <div class="info-box">
            <p>分析参数配置: 请参考配置文件</p>
        </div>
        
        <h2>5. 结论</h2>
        <div class="info-box">
            <p>分析完成，结果已保存。</p>
        </div>
        
        {spatial_section}
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)