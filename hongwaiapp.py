import streamlit as st
import pandas as pd
import os
import re

# ===== 0. 页面配置 =====
st.set_page_config(
    page_title="红外相机影像数据库",
    layout="wide",
    page_icon="📷",
    initial_sidebar_state="expanded"
)

# ===== 1. 数据逻辑 (保持不变) =====
REGION_MAP = {
    "1": "城西猫科动物栖息地",
    "2": "城西南鹅喉羚栖息地",
    "3": "古海区域",
    "4": "南新公园"
}


@st.cache_data
def load_data(folder_path, media_type):
    if not os.path.exists(folder_path):
        return pd.DataFrame()

    files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
    valid_exts = ('.mp4') if media_type == 'video' else ('.jpg', '.jpeg', '.png')
    files = [f for f in files if f.lower().endswith(valid_exts)]

    if not files:
        return pd.DataFrame()

    data_list = []
    for f in files:
        region_id = f[0]
        region_name = REGION_MAP.get(region_id)
        if region_name:
            clean_temp = re.sub(r'^[0-9]-', '', f)
            clean_temp = os.path.splitext(clean_temp)[0]
            species = re.sub(r'[\s\.-]*[0-9]+$', '', clean_temp)
            data_list.append({
                "FileName": f,
                "RegionName": region_name,
                "Species": species,
                "FilePath": os.path.join(folder_path, f)
            })
    return pd.DataFrame(data_list)


df_video = load_data("video", "video")
df_photo = load_data("photo", "photo")

# ===== 2. 🎨 CSS 深度美化 (这里是魔法) =====
st.markdown("""
<style>
    /* 全局字体优化 */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* 1. 顶部去白边 & 隐藏 Header */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    header {visibility: hidden !important;}
    footer {visibility: hidden;}

    /* 2. 背景颜色：使用高级深灰 */
    .stApp {
        background-color: #1a1a1a;
    }

    /* 3. 侧边栏美化 */
    [data-testid="stSidebar"] {
        background-color: #121212; /* 更深的侧边栏 */
        border-right: 1px solid #333;
    }
    /* 侧边栏标题样式 */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3 {
        color: #00bc8c !important; /* 绿色标题 */
        font-weight: 800;
        letter-spacing: 1px;
    }
    /* 侧边栏普通文字 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #cfcfcf !important;
    }

    /* 4. 输入组件美化 (圆角 + 深色背景) */
    .stSelectbox > div > div, .stRadio > div {
        background-color: #2b2b2b !important;
        color: white !important;
        border: 1px solid #444;
        border-radius: 8px;
    }
    /* 选中项的高亮颜色 */
    div[data-baseweb="select"] > div {
        background-color: #2b2b2b !important;
        color: white !important;
        border-color: #555 !important;
    }

    /* 5. 按钮高级样式 (悬浮发光) */
    .stButton > button {
        background: linear-gradient(135deg, #00bc8c 0%, #008f6b 100%);
        color: white;
        border: none;
        border-radius: 25px; /* 胶囊形状 */
        padding: 0.5rem 1rem;
        font-weight: bold;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 188, 140, 0.4); /* 绿色光晕 */
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* 6. 核心展示区卡片 (科技感黑盒) */
    .media-card {
        background-color: #000000;
        border: 1px solid #333;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6); /* 深度阴影 */
        text-align: center;
        margin-top: 15px;
        position: relative;
    }
    /* 给卡片加一个微弱的顶部绿条装饰 */
    .media-card::before {
        content: "";
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 30%;
        height: 3px;
        background: #00bc8c;
        border-radius: 0 0 4px 4px;
        box-shadow: 0 0 10px #00bc8c;
    }

    /* 状态徽章样式 */
    .status-badge {
        background-color: #2b2b2b;
        border-left: 4px solid #00bc8c;
        padding: 10px;
        border-radius: 4px;
        color: #fff;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ===== 3. 侧边栏布局 =====
with st.sidebar:
    st.markdown("### 📂 红外相机影像数据库")
    st.markdown("<div style='height: 2px; background: #333; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    media_type = st.radio("📊 数据库类型:", ["📸 照片库 (Photo)", "🎥 视频库 (Video)"])
    is_video_mode = "Video" in media_type

    current_df = df_video if is_video_mode else df_photo

    if current_df.empty:
        st.error(f"❌ 未找到文件，请检查 {media_type} 文件夹")
        st.stop()

    # 筛选区
    all_regions = sorted(current_df['RegionName'].unique())
    selected_region = st.selectbox("📍 区域筛选:", all_regions)

    species_in_region = sorted(current_df[current_df['RegionName'] == selected_region]['Species'].unique())
    selected_species = st.selectbox("🐾 物种筛选:", species_in_region)

    filtered_df = current_df[
        (current_df['RegionName'] == selected_region) &
        (current_df['Species'] == selected_species)
        ].reset_index(drop=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # 美化的状态显示
    st.markdown(f"""
    <div class="status-badge">
        <b>当前状态</b><br>
        ✅ 已加载: {len(filtered_df)} 个文件<br>
        🌏 区域: {selected_region}
    </div>
    """, unsafe_allow_html=True)

# ===== 4. 主展示区 =====

if filtered_df.empty:
    st.info("👋 请在左侧选择区域和物种以开始浏览。")
else:
    # 动态标题 (带图标)
    icon = '🎥' if is_video_mode else '📸'
    st.markdown(
        f"<h2 style='color: white; border-bottom: 2px solid #333; padding-bottom: 10px;'>{icon} {selected_species}</h2>",
        unsafe_allow_html=True)

    if is_video_mode:
        # === 视频模式 ===
        video_files = filtered_df['FileName'].tolist()
        display_names = [f.replace('.mp4', '') for f in video_files]

        selected_clip_name = st.selectbox("🎬 选择视频片段:", display_names)
        clip_row = filtered_df[filtered_df['FileName'].str.contains(selected_clip_name, regex=False)].iloc[0]

        # 黑色卡片容器
        st.markdown('<div class="media-card">', unsafe_allow_html=True)
        st.video(clip_row['FilePath'])
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # === 照片模式 ===
        if 'photo_index' not in st.session_state:
            st.session_state.photo_index = 0

        current_filter_hash = f"{selected_region}_{selected_species}"
        if 'last_filter' not in st.session_state or st.session_state.last_filter != current_filter_hash:
            st.session_state.photo_index = 0
            st.session_state.last_filter = current_filter_hash

        total_photos = len(filtered_df)
        st.session_state.photo_index = st.session_state.photo_index % total_photos
        current_idx = st.session_state.photo_index

        # 翻页按钮区 (使用列布局居中)
        c1, c2, c3 = st.columns([1, 6, 1])
        with c1:
            if st.button("⬅️ 上一张"):
                st.session_state.photo_index -= 1
                st.rerun()
        with c3:
            if st.button("下一张 ➡️"):
                st.session_state.photo_index += 1
                st.rerun()

        # 进度指示器
        st.markdown(f"""
        <div style="text-align: center; color: #888; font-size: 0.9rem; margin-top: -10px; margin-bottom: 10px;">
            第 <span style="color: #00bc8c; font-weight: bold; font-size: 1.2rem;">{current_idx + 1}</span> 张 
            <span style="margin: 0 5px;">/</span> 共 {total_photos} 张
        </div>
        """, unsafe_allow_html=True)

        # 黑色卡片容器
        current_photo_row = filtered_df.iloc[current_idx]
        st.markdown('<div class="media-card">', unsafe_allow_html=True)
        st.image(current_photo_row['FilePath'], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)