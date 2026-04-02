import streamlit as st

st.set_page_config(
    page_title="LocalSingleCell - 测试",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 LocalSingleCell 测试页面")
st.markdown("如果您能看到这个页面，说明Streamlit正常运行！")

st.sidebar.title("导航")
page = st.sidebar.radio(
    "选择页面",
    ["首页", "测试页面"]
)

if page == "首页":
    st.header("🏠 首页")
    st.info("这是首页内容")
elif page == "测试页面":
    st.header("🧪 测试页面")
    st.success("测试页面正常！")
