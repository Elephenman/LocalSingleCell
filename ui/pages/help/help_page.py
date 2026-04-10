import streamlit as st


def show():
    """帮助页面"""
    st.tabs_help = st.tabs(["📖 使用指南", "❓ 常见问题", "📞 反馈"])
    
    # 使用指南
    st.tabs_help[0].markdown("""
    ## 🔬 LocalSingleCell 使用指南
    
    ### 一分钟快速入门
    
    1. **导入数据** → 选择 h5ad 或 10x 格式文件
    2. **配置分析** → 调整参数或使用默认值
    3. **执行分析** → 等待自动完成
    4. **查看结果** → 在可视化页面查看图表
    """)
    
    # 数据格式说明
    with st.expander("📁 支持的数据格式"):        
        st.markdown("""
        | 格式 | 说明 | 扩展名 |
        |------|------|--------|
        | h5ad | AnnData 标准化格式 | .h5ad |
        | 10x MTX | 10x Cell Ranger输出 | mtx/ |
        | SRA | 公共数据库下载 | SRR号 |
        
        **h5ad文件要求：**
        - obs: 包含细胞ID
        - var: 包含基因名
        - X: 表达矩阵（稀疏或密集）
        """)
    
    # 常见问题
    with st.tabs_help[1].markdown("""
    ## ❓ 常见问题
    
    ### Q: 质控过滤后细胞数减少太多？
    - A: 调整线粒体基因比例阈值，15%是推荐值
    
    ### Q: 聚类数目太少/太多？
    - A: 调整聚类分辨率(Resolution)，值越大分得越细
    
    ### Q: 分析运行很慢？
    - A: 减少细胞数量或使用降采样功能
    
    ### Q: 导入h5ad时报错？
    - A: 确保是AnnData格式v0.7+，检查文件完整性
    """)
    
    # 反馈
    with st.tabs_help[2].markdown("""
    ## 📮 反馈与支持
    
    遇到问题？请通过以下方式获取帮助：
    - 📧 提交Issue: GitHub项目页面
    - 💬 加入讨论群
    """)