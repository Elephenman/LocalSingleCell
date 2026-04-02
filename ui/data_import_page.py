import streamlit as st
import os
import tempfile
from core import data_loader, sra_processor, spatial_loader
from utils import validator_utils, exception_utils


def show():
    """
    数据导入页面
    """
    st.title("📁 数据导入")
    
    # 欢迎提示
    st.info("👋 欢迎使用数据导入功能！请选择适合您数据格式的导入方式。")
    
    # 示例数据快速加载
    st.markdown("---")
    st.subheader("🎯 快速开始：加载示例数据")
    st.info("如果您没有自己的数据，可以先使用示例数据体验功能！")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📊 加载 PBMC3k 示例数据", type="primary", use_container_width=True):
            try:
                import scanpy as sc
                with st.spinner("正在加载示例数据..."):
                    adata = sc.datasets.pbmc3k_processed()
                    
                    st.session_state.anndata_obj = adata
                    st.session_state.is_data_loaded = True
                    st.session_state.is_spatial_data = False
                    
                    st.success("✅ PBMC3k示例数据加载成功！")
                    st.markdown("### 数据基本信息")
                    st.info(f"细胞总数: {adata.n_obs}")
                    st.info(f"基因总数: {adata.n_vars}")
                    st.info(f"数据描述: 外周血单个核细胞（PBMC）3k数据集，已完成预处理")
                    
            except Exception as e:
                st.error(f"加载示例数据失败: {str(e)}")
    
    with col2:
        st.info("💡 更多示例数据即将上线！")
        st.caption("（包括空间转录组示例数据）")
    
    st.markdown("---")
    
    # 快速提示
    with st.expander("💡 如何选择导入方式？", expanded=False):
        st.markdown("""
        ### 不同数据格式对应的导入方式：
        
        | 数据格式 | 推荐导入方式 |
        |---------|------------|
        | `.h5ad` 文件（单细胞） | 📁 本地h5ad文件导入 |
        | 10x Genomics 输出（filtered_feature_bc_matrix） | 📂 10x单细胞标准输出导入 |
        | SRA 数据库编号（如 SRR1234567） | 🔗 SRA号数据导入 |
        | `.h5ad` 文件（空间转录组） | 🧬 空间转录组h5ad导入 |
        | 10x Visium 空间转录组输出 | 🧫 10x Visium空间转录组导入 |
        
        ### 没有示例数据？
        如果您没有自己的数据，可以从以下资源下载公开数据集：
        - 10x Genomics 公开数据集：https://www.10xgenomics.com/resources/datasets
        - GEO 数据库：https://www.ncbi.nlm.nih.gov/geo/
        - ArrayExpress：https://www.ebi.ac.uk/arrayexpress/
        """)
    
    st.markdown("---")
    
    # 标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📁 本地h5ad文件导入", 
        "📂 10x单细胞标准输出导入", 
        "🔗 SRA号数据导入",
        "🧬 空间转录组h5ad导入",
        "🧫 10x Visium空间转录组导入"
    ])
    
    # 标签页1：本地h5ad文件导入
    with tab1:
        st.subheader("📁 本地h5ad文件导入")
        st.info("""
        h5ad是AnnData格式的标准文件格式，是单细胞数据分析最常用的格式。
        
        **文件要求：**
        - 扩展名：`.h5ad`
        - 包含表达矩阵、细胞信息和基因信息
        """)
        h5ad_file = st.file_uploader("上传h5ad文件", type=["h5ad"], help="支持单个h5ad文件，最大1GB")
        
        if h5ad_file is not None:
            try:
                # 保存临时文件
                with tempfile.NamedTemporaryFile(suffix=".h5ad", delete=False) as tmp:
                    tmp.write(h5ad_file.getvalue())
                    tmp_path = tmp.name
                
                # 读取文件
                adata = data_loader.read_h5ad(tmp_path)
                
                # 更新全局状态
                st.session_state.anndata_obj = adata
                st.session_state.is_data_loaded = True
                
                # 显示数据信息
                st.success("数据加载成功！")
                st.markdown("### 数据基本信息")
                st.info(f"细胞总数: {adata.n_obs}")
                st.info(f"基因总数: {adata.n_vars}")
                
                # 重新上传按钮
                if st.button("重新上传文件"):
                    st.session_state.anndata_obj = None
                    st.session_state.is_data_loaded = False
                    st.rerun()
                
            except Exception as e:
                st.error(f"文件读取失败: {exception_utils.get_user_friendly_error(e)}")
            finally:
                # 清理临时文件
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # 标签页2：10x标准输出导入
    with tab2:
        st.subheader("📂 10x单细胞标准输出导入")
        st.info("""
        导入10x Genomics Cell Ranger的输出结果。
        
        **文件结构要求：**
        ```
        filtered_feature_bc_matrix/
        ├── barcodes.tsv.gz
        ├── features.tsv.gz (或 genes.tsv.gz)
        └── matrix.mtx.gz
        ```
        
        请将整个文件夹打包为zip文件上传。
        """)
        zip_file = st.file_uploader("上传10x标准输出zip包", type=["zip"], help="请将filtered_feature_bc_matrix文件夹打包为zip文件")
        
        if zip_file is not None:
            try:
                # 保存临时文件
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    tmp.write(zip_file.getvalue())
                    tmp_path = tmp.name
                
                # 创建临时解压目录
                extract_dir = tempfile.mkdtemp()
                
                # 解压文件
                data_loader.extract_zip(tmp_path, extract_dir)
                
                # 查找filtered_feature_bc_matrix目录
                matrix_dir = None
                for root, dirs, files in os.walk(extract_dir):
                    if 'filtered_feature_bc_matrix' in dirs:
                        matrix_dir = os.path.join(root, 'filtered_feature_bc_matrix')
                        break
                
                if matrix_dir is None:
                    # 直接检查当前目录
                    if data_loader.check_10x_structure(extract_dir):
                        matrix_dir = extract_dir
                
                if matrix_dir is None:
                    raise Exception("未找到符合10x标准的矩阵目录")
                
                # 读取数据
                adata = data_loader.read_10x_mtx(matrix_dir)
                
                # 更新全局状态
                st.session_state.anndata_obj = adata
                st.session_state.is_data_loaded = True
                
                # 显示数据信息
                st.success("数据加载成功！")
                st.markdown("### 数据基本信息")
                st.info(f"细胞总数: {adata.n_obs}")
                st.info(f"基因总数: {adata.n_vars}")
                
                # 重新上传按钮
                if st.button("重新上传文件", key="reupload_10x"):
                    st.session_state.anndata_obj = None
                    st.session_state.is_data_loaded = False
                    st.rerun()
                
            except Exception as e:
                st.error(f"文件读取失败: {exception_utils.get_user_friendly_error(e)}")
            finally:
                # 清理临时文件
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                if 'extract_dir' in locals() and os.path.exists(extract_dir):
                    import shutil
                    shutil.rmtree(extract_dir)
    
    # 标签页3：SRA号数据导入
    with tab3:
        st.subheader("🔗 SRA号数据导入")
        st.warning("""
        ⚠️ 此功能需要安装额外的工具：
        - SRA Toolkit (prefetch, fasterq-dump)
        - STAR 比对工具
        - 基因组索引文件
        
        如果您没有配置这些工具，建议使用其他导入方式。
        """)
        sra_ids = st.text_input("输入SRA号（多个用逗号或空格分隔）", placeholder="例如：SRR1234567, SRR1234568")
        
        if sra_ids:
            # 分割SRA号
            sra_id_list = [sra.strip() for sra in sra_ids.replace(',', ' ').split() if sra.strip()]
            
            # 校验SRA号格式
            valid_sra_ids = []
            invalid_sra_ids = []
            
            for sra_id in sra_id_list:
                if validator_utils.validate_sra_id(sra_id):
                    valid_sra_ids.append(sra_id)
                else:
                    invalid_sra_ids.append(sra_id)
            
            if invalid_sra_ids:
                st.error(f"以下SRA号格式无效: {', '.join(invalid_sra_ids)}")
            
            if valid_sra_ids:
                st.success(f"有效的SRA号: {', '.join(valid_sra_ids)}")
                
                # 开始下载与定量按钮
                if st.button("开始下载与定量"):
                    try:
                        # 检查工具是否安装
                        if not sra_processor.check_tool_installed('prefetch'):
                            st.error("未安装SRA Toolkit，请先安装")
                        elif not sra_processor.check_tool_installed('fasterq-dump'):
                            st.error("未安装SRA Toolkit，请先安装")
                        elif not sra_processor.check_tool_installed('STAR'):
                            st.error("未安装STAR，请先安装")
                        else:
                            # 这里需要提供基因组索引路径，暂时使用占位符
                            # 实际使用时应该让用户选择或提供默认索引
                            genome_index = st.text_input("请输入基因组索引路径")
                            
                            if genome_index and os.path.exists(genome_index):
                                # 创建临时目录
                                temp_dir = tempfile.mkdtemp()
                                
                                # 处理第一个SRA号（暂时只处理一个）
                                sra_id = valid_sra_ids[0]
                                
                                # 显示进度
                                with st.spinner(f"正在处理 {sra_id}..."):
                                    # 处理SRA数据
                                    adata = sra_processor.process_sra(sra_id, temp_dir, genome_index)
                                    
                                    # 更新全局状态
                                    st.session_state.anndata_obj = adata
                                    st.session_state.is_data_loaded = True
                                    
                                    # 显示数据信息
                                    st.success("数据加载成功！")
                                    st.markdown("### 数据基本信息")
                                    st.info(f"细胞总数: {adata.n_obs}")
                                    st.info(f"基因总数: {adata.n_vars}")
                            else:
                                st.error("请输入有效的基因组索引路径")
                    except Exception as e:
                        st.error(f"处理SRA数据失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页4：空间转录组h5ad导入
    with tab4:
        st.subheader("🧬 空间转录组h5ad导入")
        st.info("""
        导入带有空间信息的h5ad文件。
        
        **文件要求：**
        - 扩展名：`.h5ad`
        - 包含空间坐标信息（adata.obsm['spatial']）
        - 可选：包含组织图像（adata.uns['spatial']）
        """)
        spatial_h5ad_file = st.file_uploader("上传空间转录组h5ad文件", type=["h5ad"], help="支持包含空间信息的h5ad文件")
        
        if spatial_h5ad_file is not None:
            try:
                # 保存临时文件
                with tempfile.NamedTemporaryFile(suffix=".h5ad", delete=False) as tmp:
                    tmp.write(spatial_h5ad_file.getvalue())
                    tmp_path = tmp.name
                
                # 读取空间转录组文件
                adata = spatial_loader.read_spatial_h5ad(tmp_path)
                
                # 验证空间数据完整性
                is_valid, issues = spatial_loader.validate_spatial_data(adata)
                
                if not is_valid:
                    st.warning("数据验证发现以下问题：")
                    for issue in issues:
                        st.warning(f"- {issue}")
                
                # 更新全局状态
                st.session_state.anndata_obj = adata
                st.session_state.is_data_loaded = True
                st.session_state.is_spatial_data = True
                
                # 显示数据信息
                st.success("空间转录组数据加载成功！")
                st.markdown("### 数据基本信息")
                
                info = spatial_loader.get_spatial_data_info(adata)
                st.info(f"细胞总数: {info['n_cells']}")
                st.info(f"基因总数: {info['n_genes']}")
                st.info(f"包含空间坐标: {'是' if info['has_spatial'] else '否'}")
                st.info(f"包含组织图像: {'是' if info['has_image'] else '否'}")
                
                if info['has_image']:
                    st.info(f"图像类型: {', '.join(info['image_types'])}")
                
                # 重新上传按钮
                if st.button("重新上传文件", key="reupload_spatial_h5ad"):
                    st.session_state.anndata_obj = None
                    st.session_state.is_data_loaded = False
                    st.session_state.is_spatial_data = False
                    st.rerun()
                
            except Exception as e:
                st.error(f"文件读取失败: {exception_utils.get_user_friendly_error(e)}")
            finally:
                # 清理临时文件
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # 标签页5：10x Visium空间转录组导入
    with tab5:
        st.subheader("🧫 10x Visium空间转录组导入")
        st.info("""
        导入10x Genomics Visium空间转录组的输出结果。
        
        **文件结构要求：**
        - 包含 filtered_feature_bc_matrix 文件夹
        - 包含 spatial 文件夹（包含坐标文件和组织图像）
        
        请将整个输出文件夹打包为zip文件上传。
        """)
        visium_zip_file = st.file_uploader("上传10x Visium标准输出zip包", type=["zip"], help="请将10x Visium输出文件夹打包为zip文件")
        
        if visium_zip_file is not None:
            try:
                # 保存临时文件
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    tmp.write(visium_zip_file.getvalue())
                    tmp_path = tmp.name
                
                # 读取Visium数据
                adata = spatial_loader.read_visium_zip(tmp_path)
                
                # 验证空间数据完整性
                is_valid, issues = spatial_loader.validate_spatial_data(adata)
                
                if not is_valid:
                    st.warning("数据验证发现以下问题：")
                    for issue in issues:
                        st.warning(f"- {issue}")
                
                # 更新全局状态
                st.session_state.anndata_obj = adata
                st.session_state.is_data_loaded = True
                st.session_state.is_spatial_data = True
                
                # 显示数据信息
                st.success("10x Visium空间转录组数据加载成功！")
                st.markdown("### 数据基本信息")
                
                info = spatial_loader.get_spatial_data_info(adata)
                st.info(f"细胞总数: {info['n_cells']}")
                st.info(f"基因总数: {info['n_genes']}")
                st.info(f"包含空间坐标: {'是' if info['has_spatial'] else '否'}")
                st.info(f"包含组织图像: {'是' if info['has_image'] else '否'}")
                
                if info['has_image']:
                    st.info(f"图像类型: {', '.join(info['image_types'])}")
                
                # 重新上传按钮
                if st.button("重新上传文件", key="reupload_visium"):
                    st.session_state.anndata_obj = None
                    st.session_state.is_data_loaded = False
                    st.session_state.is_spatial_data = False
                    st.rerun()
                
            except Exception as e:
                st.error(f"文件读取失败: {exception_utils.get_user_friendly_error(e)}")
            finally:
                # 清理临时文件
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # 数据加载成功后，显示下一步按钮
    if st.session_state.is_data_loaded:
        st.markdown("---")
        # 根据数据类型决定下一步
        if st.session_state.get('is_spatial_data', False):
            if st.button("下一步：去配置空间分析参数"):
                st.session_state.page = "空间分析流程配置"
                st.rerun()
        else:
            if st.button("下一步：去配置分析参数"):
                st.session_state.page = "分析流程配置"
                st.rerun()