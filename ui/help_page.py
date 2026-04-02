import streamlit as st


def show():
    """
    帮助文档页面
    """
    st.title("❓ 帮助文档")
    
    st.markdown("---")
    
    # 快速导航
    st.markdown("## 📋 快速导航")
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("🚀 快速上手", use_container_width=True):
            st.session_state.help_section = "quickstart"
    with nav_col2:
        if st.button("⚙️ 参数说明", use_container_width=True):
            st.session_state.help_section = "parameters"
    with nav_col3:
        if st.button("❓ 常见问题", use_container_width=True):
            st.session_state.help_section = "faq"
    with nav_col4:
        if st.button("📞 反馈与贡献", use_container_width=True):
            st.session_state.help_section = "feedback"
    
    st.markdown("---")
    
    # 获取当前显示的章节
    current_section = st.session_state.get('help_section', 'quickstart')
    
    # 快速上手教程
    if current_section == 'quickstart':
        st.header("📖 快速上手教程")
        
        st.markdown("### 1. 安装依赖")
        st.code("cd LocalSingleCell\npip install -r requirements.txt", language="bash")
        
        st.markdown("### 2. 启动程序")
        st.code("streamlit run app.py --server.headless true --browser.gatherUsageStats false", language="bash")
        
        st.markdown("### 3. 导入数据")
        st.info("👈 点击左侧导航栏「🏡 首页」查看详细的导入说明")
        st.markdown("""
        - **方式1**：📁 上传本地h5ad文件（推荐）
        - **方式2**：📂 上传10x Genomics输出的zip包
        - **方式3**：🧬 上传空间转录组h5ad文件
        - **方式4**：🧫 上传10x Visium输出的zip包
        """)
        
        st.markdown("### 4. 配置分析参数")
        st.markdown("""
        **选项A：使用AI自然语言分析（推荐新手）**
        1. 进入「🤖 AI自然语言分析」页面
        2. 选择示例需求或用中文描述您的需求
        3. 点击「🔍 解析需求」查看生成的参数
        4. 确认无误后点击「🚀 一键执行分析」
        
        **选项B：手动配置参数（推荐高级用户）**
        1. 进入「⚙️ 分析流程配置」页面
        2. 根据需要调整各项参数
        3. 点击「📊 预览质控结果」查看过滤效果
        4. 点击「▶️ 保存配置并执行分析」
        """)
        
        st.markdown("### 5. 查看结果可视化")
        st.markdown("""
        分析完成后，进入「📊 结果可视化」页面：
        - 选择不同类型的图表进行查看
        - 调整图表参数（如配色、尺寸等）
        - 点击下载按钮保存图表
        """)
        
        st.markdown("### 6. 进行基因富集分析")
        st.markdown("""
        1. 进入「🔬 基因富集分析」页面
        2. 选择基因来源（差异基因或自定义基因列表）
        3. 选择物种和富集数据库（GO、KEGG、Reactome）
        4. 点击「▶️ 执行富集分析」
        5. 查看富集结果表格和气泡图
        """)
        
        st.markdown("### 7. 导出结果")
        st.markdown("""
        1. 进入「💾 结果导出」页面
        2. 勾选要导出的内容
        3. 点击「📦 一键打包导出」
        4. 下载分析结果压缩包
        """)
        
        st.markdown("---")
        
        st.markdown("### 🎯 典型分析流程图")
        st.graphviz_chart("""
        digraph G {
            rankdir=TB;
            node [shape=box, style=filled, fillcolor="#e3f2fd"];
            
            start [label="开始", fillcolor="#c8e6c9"];
            import_data [label="导入数据"];
            choose_method [label="选择分析方式", shape=diamond, fillcolor="#fff9c4"];
            ai_analysis [label="AI自然语言分析"];
            manual_config [label="手动配置参数"];
            run_analysis [label="执行分析", fillcolor="#bbdefb"];
            visualize [label="查看可视化"];
            enrichment [label="基因富集分析"];
            export [label="导出结果"];
            end [label="完成", fillcolor="#c8e6c9"];
            
            start -> import_data;
            import_data -> choose_method;
            choose_method -> ai_analysis [label="推荐"];
            choose_method -> manual_config [label="高级"];
            ai_analysis -> run_analysis;
            manual_config -> run_analysis;
            run_analysis -> visualize;
            visualize -> enrichment;
            enrichment -> export;
            export -> end;
        }
        """)
    
    # 参数详细说明
    elif current_section == 'parameters':
        st.header("⚙️ 参数详细说明")
        
        with st.expander("🔬 质控与过滤参数", expanded=True):
            st.markdown("""
            ### 基因过滤
            - **过滤在少于N个细胞中表达的基因**：默认3个细胞。去除在极少数细胞中表达的基因，可以减少噪音。
            
            ### 细胞过滤
            - **每个细胞最少基因数**：默认200。过滤基因数过少的低质量细胞。
            - **每个细胞最多基因数**：默认6000。过滤基因数异常多的细胞（可能是 doublets）。
            - **每个细胞最少UMI数**：默认500。过滤UMI数过少的低质量细胞。
            - **每个细胞最多UMI数**：默认20000。过滤UMI数异常多的细胞。
            
            ### 线粒体基因过滤
            - **过滤线粒体基因比例过高的细胞**：默认启用。
            - **线粒体基因前缀**：默认"MT-"（人类），小鼠为"mt-"。
            - **最大线粒体基因比例**：默认20%。比例过高通常表示细胞凋亡。
            
            ### 核糖体基因过滤
            - **过滤核糖体基因比例过高的细胞**：默认禁用。
            - **核糖体基因前缀**：默认"RP[SL]"。
            - **最大核糖体基因比例**：默认50%。
            """)
        
        with st.expander("📊 归一化与高变基因筛选参数", expanded=False):
            st.markdown("""
            ### 归一化
            - **归一化方法**：
              - Scanpy标准归一化（推荐）：将每个细胞的总计数归一化到目标值
              - CPM归一化：Counts Per Million
            - **目标总计数**：默认10000。
            
            ### 高变基因筛选
            - **筛选高变基因**：默认启用。高变基因对细胞类型鉴定更有信息量。
            - **筛选方法**：
              - Seurat_v3（推荐）：适合大数据集
              - Seurat：经典方法
              - Cell Ranger：10x Genomics方法
            - **高变基因数量**：默认2000个。
            
            ### 数据标准化
            - **对数据进行z-score标准化**：默认启用。使每个基因均值为0，方差为1。
            - **最大绝对值**：默认10。截断过大的值，减少异常值影响。
            """)
        
        with st.expander("📉 降维分析参数", expanded=False):
            st.markdown("""
            ### PCA分析
            - **PCA主成分数量**：默认50。
            - **使用高变基因进行PCA分析**：默认启用。减少计算量，提高效果。
            
            ### UMAP降维
            - **执行UMAP降维**：默认启用。UMAP是目前最常用的可视化方法。
            - **UMAP邻居数**：默认15。较小的值保留局部结构，较大的值保留全局结构。
            - **UMAP最小距离**：默认0.5。较小的值使点更聚集，较大的值使点更分散。
            
            ### tSNE降维
            - **执行tSNE降维**：默认禁用。tSNE计算较慢，通常UMAP效果更好。
            - **tSNE困惑度**：默认30。通常设置为细胞数的平方根。
            """)
        
        with st.expander("🎯 细胞聚类分析参数", expanded=False):
            st.markdown("""
            ### 聚类参数
            - **构建邻居图使用的PCA主成分数量**：默认30。
            - **邻居数量**：默认15。
            - **聚类算法**：
              - Leiden（推荐）：改进的Louvain，更稳定
              - Louvain：经典算法
            - **聚类分辨率**：默认0.5。
              - 分辨率越大，聚类数量越多
              - 分辨率越小，聚类数量越少
              - 推荐范围：0.1-2.0
            """)
        
        with st.expander("🔬 差异基因分析参数", expanded=False):
            st.markdown("""
            ### 差异分析
            - **执行聚类差异基因分析**：默认启用。
            - **差异检验方法**：
              - Wilcoxon秩和检验（推荐）：非参数检验，稳健
              - t-test：参数检验
              - Logistic回归
            - **调整后p值最大值**：默认0.05。显著性阈值。
            - **最小log2倍变化**：默认0.25。表达变化阈值。
            - **仅保留在至少N%的细胞中表达的基因**：默认25%。过滤低表达基因。
            """)
    
    # 常见问题FAQ
    elif current_section == 'faq':
        st.header("❓ 常见问题FAQ")
        
        with st.expander("💻 安装与启动问题", expanded=True):
            st.markdown("""
            **Q: Python版本有什么要求？**
            A: 需要Python 3.10或更高版本。
            
            **Q: 依赖安装失败怎么办？**
            A: 
            - 确保使用Python 3.10+
            - 尝试使用虚拟环境：`python -m venv venv` 然后激活虚拟环境
            - 检查网络连接，某些包可能需要从国外服务器下载
            - 对于Windows用户，可能需要安装 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
            
            **Q: 程序启动报错怎么办？**
            A: 
            - 检查依赖是否安装成功：`pip list` 查看所有已安装的包
            - 检查Streamlit版本是否符合要求（1.30+）
            - 检查端口8501是否被占用，可以使用 `--server.port 8502` 指定其他端口
            - 查看错误信息中的详细堆栈跟踪
            
            **Q: Streamlit提示无法访问配置目录？**
            A: 程序已创建项目本地的.streamlit目录，应该不会出现此问题。如果仍有问题，请检查项目目录的读写权限。
            """)
        
        with st.expander("📁 数据导入问题", expanded=False):
            st.markdown("""
            **Q: 支持哪些数据格式？**
            A: 
            - h5ad文件（AnnData格式）
            - 10x Genomics Cell Ranger输出（filtered_feature_bc_matrix）
            - 10x Visium空间转录组输出
            - SRA号（需要额外配置工具）
            
            **Q: 从哪里可以获取示例数据？**
            A: 可以从以下资源下载公开数据集：
            - 10x Genomics 公开数据集：https://www.10xgenomics.com/resources/datasets
            - GEO 数据库：https://www.ncbi.nlm.nih.gov/geo/
            - ArrayExpress：https://www.ebi.ac.uk/arrayexpress/
            - Scanpy内置数据集：可以使用scanpy.datasets模块下载
            
            **Q: 数据读取失败怎么办？**
            A: 
            - 确保文件格式正确
            - 对于h5ad文件，确保使用兼容的Anndata版本创建
            - 对于10x数据，确保zip包包含正确的文件结构（filtered_feature_bc_matrix文件夹）
            - 检查文件是否损坏
            
            **Q: 文件太大上传失败怎么办？**
            A: Streamlit默认文件大小限制是200MB。对于大文件：
            - 可以先将文件放到项目目录中，然后修改代码直接读取
            - 或者在.streamlit/config.toml中增加maxUploadSize配置
            """)
        
        with st.expander("🧠 内存与性能问题", expanded=False):
            st.markdown("""
            **Q: 内存不足怎么办？**
            A: 
            - 对于大数据集，可以考虑使用subset功能（后续版本支持）
            - 关闭其他占用内存的程序
            - 增加电脑物理内存
            - 使用64位Python版本
            
            **Q: 分析速度很慢怎么办？**
            A: 
            - UMAP和tSNE是最耗时的步骤，可以考虑只运行UMAP
            - 减少PCA主成分数量
            - 减少高变基因数量
            - 使用更快的聚类算法（Leiden比Louvain快）
            
            **Q: 电脑配置较低能使用吗？**
            A: 
            - 最低配置：8GB RAM，可以分析中小规模数据集（<10,000细胞）
            - 推荐配置：16GB+ RAM，可以分析大多数数据集
            - 对于超大数据集（>100,000细胞），建议使用高配置服务器
            """)
        
        with st.expander("🎨 可视化问题", expanded=False):
            st.markdown("""
            **Q: 中文显示乱码怎么办？**
            A: 程序已内置中文字体配置，应该不会出现乱码。若仍出现乱码：
            - 检查系统是否安装了中文字体（SimHei、Microsoft YaHei等）
            - 在utils/visual_utils.py中修改字体配置
            
            **Q: 图表显示不全或变形怎么办？**
            A: 
            - 尝试调整图表尺寸参数
            - 尝试不同的保存格式（PNG、SVG、PDF）
            - 增加DPI参数提高分辨率
            
            **Q: 如何保存高质量的图表？**
            A: 
            - 使用SVG或PDF格式，这些是矢量格式，可以无限缩放
            - 提高DPI参数（默认300，最高可以600）
            - 对于出版物，推荐使用PDF格式
            """)
        
        with st.expander("🤖 AI分析问题", expanded=False):
            st.markdown("""
            **Q: AI分析需要联网吗？**
            A: 不需要！本项目的AI分析功能使用内置的规则解析器，所有解析都在本地完成，无数据上传到云端。
            
            **Q: AI解析结果不准确怎么办？**
            A: 
            - 尝试用更明确的语言重新描述您的需求
            - 先使用示例需求，然后在输入框中进行修改
            - 如果需要更精细的控制，可以点击「✏️ 手动调整参数」跳转到参数配置页面
            
            **Q: 可以使用真正的LLM（如GPT、Claude）吗？**
            A: 可以！配置文件中预留了LLM接口，您可以：
            - 配置使用本地Ollama模型
            - 或配置使用云端API（需要联网）
            - 修改config.yaml中的ai_analysis配置即可
            
            **Q: AI分析支持哪些语言？**
            A: 目前主要支持中文。后续版本会增加英文支持。
            """)
    
    # 反馈与贡献
    elif current_section == 'feedback':
        st.header("📞 反馈与贡献")
        
        st.markdown("### 🐛 问题反馈")
        st.info("""
        如果您在使用过程中遇到任何问题：
        
        1. 首先查看「❓ 常见问题FAQ」是否有解决方案
        2. 查看logs目录下的日志文件，获取详细错误信息
        3. 记录您的操作步骤和错误信息
        
        **建议的反馈格式：**
        ```
        问题描述：（简要描述您遇到的问题）
        复现步骤：1. ... 2. ... 3. ...
        预期结果：（您期望的结果）
        实际结果：（实际发生的情况）
        错误信息：（如果有，请粘贴完整的错误信息）
        系统信息：Windows/Linux/macOS, Python版本, 浏览器版本
        ```
        """)
        
        st.markdown("---")
        
        st.markdown("### 💡 功能建议")
        st.success("""
        欢迎提出新功能建议！您可以建议：
        
        - 新的分析方法
        - 新的可视化图表
        - 用户体验改进
        - 文档改进
        - 任何其他想法
        
        请尽可能详细地描述您的想法，包括：
        - 这个功能解决什么问题？
        - 您期望的使用方式是什么？
        - 如果有参考的其他工具，也请提及
        """)
        
        st.markdown("---")
        
        st.markdown("### 👨‍💻 贡献代码")
        st.markdown("""
        欢迎贡献代码！如果您想参与开发：
        
        1. Fork本项目仓库
        2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
        3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
        4. 推送到分支 (`git push origin feature/AmazingFeature`)
        5. 开启一个Pull Request
        
        **代码规范：**
        - 遵循PEP 8代码风格
        - 添加函数级文档字符串
        - 保持中文界面和提示
        - 添加必要的异常处理
        - 更新相关文档
        
        **可以贡献的方向：**
        - 修复Bug
        - 优化性能
        - 增加新功能
        - 改进文档
        - 编写测试
        """)
        
        st.markdown("---")
        
        st.markdown("### 📚 学习资源")
        st.markdown("""
        如果您想学习单细胞和空间转录组分析：
        
        **单细胞分析入门：**
        - Scanpy官方文档：https://scanpy.readthedocs.io/
        - "Single-cell RNA-seq data analysis course"（EMBL）
        - 《单细胞数据分析指南》
        
        **空间转录组分析入门：**
        - Squidpy官方文档：https://squidpy.readthedocs.io/
        - 10x Genomics空间转录组指南
        - Nature Reviews Genetics相关综述
        
        **Python生信分析：**
        - Python for Data Analysis（Wes McKinney）
        - Biopython官方教程
        """)
        
        st.markdown("---")
        
        st.markdown("### 📄 许可证与免责声明")
        st.warning("""
        **许可证：**
        本项目为开源项目，仅供学习和研究使用。
        
        **免责声明：**
        - 本工具仅供科研使用，不用于临床诊断
        - 开发者不对使用本工具产生的任何后果负责
        - 请在使用前备份您的数据
        """)
        
        st.markdown("---")
        
        st.markdown("### 🙏 致谢")
        st.markdown("""
        本项目基于以下优秀的开源工具：
        
        - [Streamlit](https://streamlit.io/) - 低代码UI框架
        - [Scanpy](https://scanpy.readthedocs.io/) - 单细胞分析
        - [Squidpy](https://squidpy.readthedocs.io/) - 空间转录组分析
        - [GSEApy](https://gseapy.readthedocs.io/) - 富集分析
        - [Matplotlib](https://matplotlib.org/), [Seaborn](https://seaborn.pydata.org/), [Plotly](https://plotly.com/) - 可视化
        
        感谢所有开源社区的贡献者！
        """)
