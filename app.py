import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import query as q

# 使用者資料儲存
user_data = {"user_name": None, "phone": None, "email": None}

# 頁面設定：我是業者 -> 我要租店面
plt.rcParams['font.family'] = ['Heiti TC']

# 每日平均人潮流動折線圖
def crowd_flow_spectrum(case_id):
    df = q.get_shop_flow_data(case_id=case_id)

    if 'time_period' not in df.columns or 'avg_total_flow' not in df.columns:
        st.error("Required columns not found in the data.")
        return
    
    # data for plotting
    df['time_period'] = pd.Categorical(df['time_period'], ordered=True)
    df.sort_values('time_period', inplace=True)  # 按 time_period 排序
    df.reset_index(drop=True, inplace=True)
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['time_period'], df['avg_total_flow'], marker='o', linestyle='-', color='tab:blue')
    plt.xlabel('時刻(時)')
    plt.ylabel('平均流動人潮')
    plt.grid(True)

    plt.xticks(rotation=45)
    st.pyplot(plt)

# 住戶密度 & 收入水平分析
def income_density_chart(case_id, district):
    # 查詢該 case_id 所在 village 的資訊
    shop_flow_df = q.get_shop_flow_data(case_id=case_id)
    target_village = shop_flow_df['village'].iloc[0]
    
    # 查詢該區域所有 village 的資訊
    village_df = q.get_village_data(district=district)
    
    # 篩出目標 village 的數據
    target_data = village_df[village_df['village'] == target_village]
    location_density = target_data['household_count']
    location_income = target_data['avg_income']
    avg_income = int(target_data['nearby_avg_income'].iloc[0])
    avg_density = int(target_data['nearby_avg_density'].iloc[0])

    # 除目標 village 外其他 villages 的數據
    other_villages = village_df[village_df['village'] != target_village]
    density_values = other_villages['household_count'].tolist()
    income_values = other_villages['avg_income'].tolist()
    
    # 圖表
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 其他 village 的點 (藍色)
    ax.scatter(density_values, income_values, c='blue', s=100, label='其他村里')
    
    # 目標 village 的點 (紅色)
    ax.scatter(location_density, location_income, c='red', s=100, label=f"{target_village}", edgecolor='black')
    
    # X 軸與 Y 軸平均值
    ax.axhline(avg_income, color='purple', linestyle='--', label=f'收入平均值: {avg_income}')
    ax.axvline(avg_density, color='yellow', linestyle=':', label=f'人口密度平均值: {avg_density}')
    
    ax.set_title(f"{district} 各村里住戶密度與收入水平的關係圖")
    ax.set_xlabel("住戶密度")
    ax.set_ylabel("收入水平")
    ax.legend()
    
    st.pyplot(fig)

# 年齡層分析
def age_distribution_page(case_id, district):
    # 流動人潮
    shop_flow_df = q.get_shop_flow_data(case_id=case_id)
    target_village = shop_flow_df['village'].iloc[0]
    
    # 查詢該區域所有 village 資訊
    village_df = q.get_village_data(district=district)
    
    # 篩出目標 village 數據
    target_data = village_df[village_df['village'] == target_village]
    
    # 計算年齡分布比例
    age_distribution = {
        "孩童": target_data['avg_0_9_ratio'].iloc[0] * 100,
        "青少年": target_data['avg_10_19_ratio'].iloc[0] * 100,
        "新鮮人": target_data['avg_20_29_ratio'].iloc[0] * 100,
        "壯年": target_data['avg_30_64_ratio'].iloc[0] * 100,
        "老年": target_data['avg_over_65_ratio'].iloc[0] * 100,
    }
    
    # 比較目標村里和周邊地區的年齡分布
    age_comparison = {
        "孩童": compare_ratios(target_data['avg_0_9_ratio'].iloc[0], target_data['nearby_0_9_ratio'].iloc[0]),
        "青少年": compare_ratios(target_data['avg_10_19_ratio'].iloc[0], target_data['nearby_10_19_ratio'].iloc[0]),
        "新鮮人": compare_ratios(target_data['avg_20_29_ratio'].iloc[0], target_data['nearby_20_29_ratio'].iloc[0]),
        "壯年": compare_ratios(target_data['avg_30_64_ratio'].iloc[0], target_data['nearby_30_64_ratio'].iloc[0]),
        "老年": compare_ratios(target_data['avg_over_65_ratio'].iloc[0], target_data['nearby_over_65_ratio'].iloc[0]),
    }
    
    age_groups = ["孩童", "青少年", "新鮮人", "壯年", "老年"]

    age_df = pd.DataFrame({
        'age_group': age_groups,
        'count': [age_distribution[group] for group in age_groups],
        'comparison': [age_comparison[group] for group in age_groups]
    })

    # 顯示年齡層人口數
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="孩童 (0~9 歲)", value=f"{age_df.loc[0, 'count']:.1f}%", delta=age_df.loc[0, 'comparison'])
    with col2:
        st.metric(label="青少年 (10~19 歲)", value=f"{age_df.loc[1, 'count']:.1f}%", delta=age_df.loc[1, 'comparison'])
    with col3:
        st.metric(label="新鮮人 (20~29 歲)", value=f"{age_df.loc[2, 'count']:.1f}%", delta=age_df.loc[2, 'comparison'])

    col4, col5 = st.columns(2)
    with col4:
        st.metric(label="壯年 (30~64 歲)", value=f"{age_df.loc[3, 'count']:.1f}%", delta=age_df.loc[3, 'comparison'])
    with col5:
        st.metric(label="老年 (65 歲以上)", value=f"{age_df.loc[4, 'count']:.1f}%", delta=age_df.loc[4, 'comparison'])

def compare_ratios(target_ratio, nearby_ratio):
    """比較目標村莊和附近地區的比例，返回對應的描述。"""
    if target_ratio > nearby_ratio:
        return "客群高於附近其他地區"
    elif target_ratio == nearby_ratio:
        return "客群量與附近地區一致"
    else:
        return "客群量低於附近其他地區"

# 性別比例
def gender_distribution_page(case_id, district):
    shop_flow_df = q.get_shop_flow_data(case_id=case_id)
    target_village = shop_flow_df['village'].iloc[0]
    # 查詢該區域所有 village 資訊
    village_df = q.get_village_data(district=district)
    target_data = village_df[village_df['village'] == target_village]
    male = target_data['male_population_ratio'].iloc[0]*100
    female = target_data['female_population_ratio'].iloc[0]*100
    gender_distribution = {"男": male, "女": female}
    colors = ['#66b3ff', '#ff66b3']

    fig, ax = plt.subplots()
    ax.pie(gender_distribution.values(), labels=gender_distribution.keys(), autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops={'edgecolor': 'black'})
    ax.axis('equal')
    st.pyplot(fig)

# 商機分析
def opportunity_analysis_page():
    if "selected_rental" in st.session_state:
        rental = st.session_state.selected_rental
        case_id = rental["case_id"]
    if "selected_districts" in st.session_state:
        selected_districts = st.session_state.selected_districts

    # 人潮流量光譜：早到晚
    st.subheader("人潮流量光譜")
    crowd_flow_spectrum(case_id=case_id)

    # 住戶密度&人潮流動光譜
    st.subheader("住戶密度光譜")
    income_density_chart(case_id=case_id, district=selected_districts)
    
    col1, col2 = st.columns([5, 3])

    with col1:
        st.subheader("年齡層分佈")
        age_distribution_page(case_id=case_id, district=selected_districts)

    with col2:
        st.subheader("性別分布")
        gender_distribution_page(case_id=case_id, district=selected_districts)

# 競爭市場
def competitive_market_page(case_id, district):
    # 目標村里
    shop_flow_df = q.get_shop_flow_data(case_id=case_id)
    target_village = shop_flow_df['village'].iloc[0]
    
    # 根據條件選擇查詢方式
    if "selected_business_type" in st.session_state:
        selected_type = st.session_state["selected_business_type"]
        subtype_df = q.get_competitive_data(district=district, village=target_village, type=selected_type)
    else:
        subtype_df = q.get_top5_subtype_data(district=district, village=target_village)
    
    # 如果查無資料，顯示提示
    if subtype_df.empty:
        st.write("### 無競爭市場數據")
        st.write("目前該地區沒有相關的營業資料。")
        return
    
    # 變更欄位名稱
    subtype_df = subtype_df.rename(columns={
        "business_sub_type": "營業項目",
        "shop_cnt": "店舖數量",
        "avg_capital": "平均資本額"
    })
    
    # 單位：資本額(元) -> 資本額(萬元)
    subtype_df["平均資本額"] = subtype_df["平均資本額"] // 10000
    
    # 按照店舖數量排序
    subtype_df = subtype_df.sort_values(by="店舖數量", ascending=False)

    # 市場資料顯示
    st.write("### 競爭市場概覽：")
    col1, col2, col3 = st.columns([3, 3, 3])
    col1.markdown("**營業項目**")
    col2.markdown("**店舖數量**")
    col3.markdown("**平均資本額 (萬元)**")

    for _, row in subtype_df.iterrows():
        col1, col2, col3 = st.columns([3, 3, 3])
        col1.write(row["營業項目"])
        col2.write(row["店舖數量"])
        col3.write(row["平均資本額"])

    # 顯示每個營業項目的 Top 5 店鋪
    for business in subtype_df["營業項目"]:
        st.write(f"### {business} 的 Top 5 資本額店鋪")
        store_df = q.get_business_data(business, district, target_village)
        filtered_stores = store_df.nlargest(5, "capital")

        col1, col2, col3, col4 = st.columns([2, 5, 3, 3])
        col1.markdown("**店名**")
        col2.markdown("**地址**")
        col3.markdown("**資本額 (萬元)**")
        col4.markdown("**地圖**")

        for _, row in filtered_stores.iterrows():
            col1, col2, col3, col4 = st.columns([2, 5, 3, 3])
            col1.write(row["business_name"])
            col2.write(row["address"])
            col3.write(row["capital"])
            col4.markdown(f"[Google 地圖連結](https://www.google.com/maps?q={row['latitude']},{row['longitude']})", unsafe_allow_html=True)

def filter_stores_by_business(business_type, store_df):
    if business_type == "零售業":
        return store_df[store_df["店名"].isin(["店鋪A", "店鋪B", "店鋪C"])]
    elif business_type == "餐飲業":
        return store_df[store_df["店名"].isin(["店鋪D", "店鋪E", "店鋪F"])]
    else:
        return pd.DataFrame()

def rent_store_page():
    st.title("🔍 我要租店面")

    # 初始化 session_state
    if "trade_area_details" not in st.session_state:
        st.session_state.trade_area_details = None
    if "rental_details" not in st.session_state:
        st.session_state.rental_details = None

    # 輸入理想開店地點 - 必填項目
    st.subheader("請至少輸入一個心目中的理想開店地點後，按 “進行查詢”")

    # 1. 選擇具體的地點
    districts = [
        "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區",
        "內湖區", "南港區", "文山區"
    ]
    selected_districts = st.selectbox(
        "選擇區域別",
        options=districts,
        help="選擇您理想開店的區域"
    )
    st.session_state.selected_districts = selected_districts
    # 2. 空間大小
    ping = st.slider(
        "選擇空間大小（坪）",
        min_value=0,
        max_value=10000,
        value=(20, 100),
        step=5,
        help="選擇您的店面空間需求"
    )

    # 3. 租金預算
    rent_budget = st.slider(
        "選擇租金預算（每月）",
        min_value=10000,
        max_value=1000000,
        value=(20000, 50000),
        step=5000,
        help="選擇您的租金預算範圍"
    )

    # 4. 營業項目
    business_type = st.selectbox(
        "選擇營業項目",
        options=[
            "農、林、漁、牧業", "礦業及土石採取業", "製造業", "電力及燃氣供應業", "用水供應及污染整治業",
            "營建工程業", "批發及零售業", "運輸及倉儲業", "住宿及餐飲業", "出版影音及資通訊業",
            "金融及保險業", "不動產業", "專業、科學及技術服務業", "支援服務業", "公共行政及國防",
            "教育業", "醫療保健及社會工作服務業", "藝術、娛樂及休閒服務業", "其他服務業"
        ],
        help="選擇您的營業項目"
    )
    st.session_state.selected_business_type = business_type

    # 查詢按鈕
    if st.button("進行查詢"):
        organization_data_df = q.get_organization_data(district=selected_districts)
        st.session_state.trade_area_details = organization_data_df.to_dict(orient='records')
        st.session_state.selected_trade_area = None

    # 分頁: 商圈資訊 和 出租案件
    if st.session_state.trade_area_details:
        tabs = st.tabs(["商圈資訊", "出租案件"])

        # Tab 1: 商圈資訊
        with tabs[0]:
            st.subheader("商圈資訊")
            for area in st.session_state.trade_area_details:
                with st.expander(f"{area['name']} - 周邊平均租金 $ {int(area['average_monthly_rent'])}/月"):
                    st.write(f"**地址**: {area['district']}")
                    st.write(f"**類型**: {area['tag']}")
                    st.write(f"**距離最近的捷運站**: {area['station_name']}")

        # Tab 2: 出租案件
        with tabs[1]:
            st.subheader("出租案件")
            rentals_df = q.get_filtered_shop_rentals(district=selected_districts,
                min_rent=rent_budget[0], max_rent=rent_budget[1],
                min_area=ping[0], max_area=ping[1]
            )
            rentals = rentals_df.to_dict(orient='records')

            cols = st.columns(2)
            for i, rental in enumerate(rentals):
                case_id = rental["case_id"]
                col = cols[i % 2]
                with col:
                    st.write(f"### {rental['case_name']}")
                    st.write(f"**地址**: {rental['address']} ({rental['village']})")
                    st.write(f"**租金**: $ {rental['monthly_rent']}/月 ({int(rental['monthly_rent_per_ping'])}/坪)")
                    st.write(f"**坪數**: {rental['area_ping']}")
                    st.write(f"**樓層/總樓層**: {rental['shop_floor']}/{rental['total_floor']}")
                    st.write(f"**押金**: $ {rental['deposit']}")

                    # 建 button
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"聯絡房仲", key=f"contact_{rental['address']}_{rental['area_ping']}_{rental['phone']}"):
                            # landlord = rental.get('landlord', {})
                            st.write(f"聯絡人: {rental['name']}")
                            st.write(f"電話: {rental['phone']}")
                    with btn_col2:
                        if st.button(f"適不適合我開店", key=f"check_{rental['address']}_{rental['area_ping']}_{rental['phone']}"):
                            st.session_state.selected_rental = rental
                            st.session_state.page = "analysis_page"

    # 進行分析
    if st.session_state.get("page", None) == "analysis_page":
        st.session_state.page = None
        analysis_tabs = st.tabs(["商機分析", "競爭市場"])
        with analysis_tabs[0]:
            opportunity_analysis_page()
        with analysis_tabs[1]:
            if "selected_districts" in st.session_state:
                selected_districts = st.session_state.selected_districts
            competitive_market_page(case_id=case_id, district=selected_districts)

locations_data = {
    "地點": ["A區", "B區", "C區", "D區", "E區"],
    "每日平均流動人潮": [1000, 5000, 3000, 1500, 4500],
    "熱門時段": [
        ["10:00-12:00", "18:00-20:00"],
        ["09:00-11:00", "14:00-16:00"],
        ["08:00-10:00", "20:00-22:00"],
        ["11:00-13:00", "17:00-19:00"],
        ["12:00-14:00", "19:00-21:00"]
    ]
}

locations_df = pd.DataFrame(locations_data)

# 頁面設定：我是業者 -> 我要找熱點
def find_hotspot_page():
    st.title("📍我要找熱點")

    # 用戶輸入條件
    st.subheader("請輸入理想條件")

    # 每日平均流動人潮
    avg_traffic = st.slider("每日平均流動人潮 >= ", min_value=0, max_value=10)

    # 熱門時段（多選）
    popular_times = st.multiselect(
        "熱門時段",
        ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00",
         "17:00-19:00", "18:00-20:00", "20:00-22:00"]
    )

    # 篩選符合條件的地點
    filtered_df = locations_df
    # [
    #     (locations_df["每日平均流動人潮"] >= avg_traffic) &
    #     (locations_df["熱門時段"].apply(lambda x: any(time in popular_times for time in x)))
    # ]

    # 顯示符合條件的前五個地點
    st.subheader("符合條件的前 5 個地點：")

    # 假設 filtered_df 已經篩選完成，並包含所需資料
    top_locations = filtered_df.head(5)

    # 顯示表頭
    col1, col2, col3, col4 = st.columns([3, 4, 4, 3])
    col1.markdown("**地點**")
    col2.markdown("**每日平均流動人潮**")
    col3.markdown("**熱門時段**")
    col4.markdown("**操作**")

    # 一列一列寫入資料並附加按鈕
    for _, row in top_locations.iterrows():
        col1, col2, col3, col4 = st.columns([3, 4, 4, 3])
        col1.write(row['地點'])
        col2.write(f"{row['每日平均流動人潮']:,}")
        col3.write(", ".join(row['熱門時段']))
        
        # 添加按鈕，使用地點作為鍵以保證唯一性
        if col4.button(f"查看 {row['地點']} 附近店面出租資訊", key=row['地點']):
            # 呼叫對應的函式來顯示店面出租資訊
            show_rental_info(row['地點'])

# 顯示出租資訊
def show_rental_info(location):
    st.subheader(f"在 {location} 附近的店面出租資訊")

    # 假資訊
    rental_info = {
        "店面名稱": ["店面A", "店面B", "店面C"],
        "租金": ["50000元/月", "60000元/月", "55000元/月"],
        "面積": ["30㎡", "40㎡", "35㎡"],
        "聯絡房仲": ["胡先生", "洪小姐", "馮先生"],
        "聯絡方式": ["0922-xxxxxx", "0933-xxxxxx", "0911-xxxxxx"]
    }

    rental_df = pd.DataFrame(rental_info)

    # 顯示表頭
    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 3, 3])
    col1.markdown("**店面名稱**")
    col2.markdown("**租金**")
    col3.markdown("**面積**")
    col4.markdown("**聯絡房仲**")
    col5.markdown("**聯絡方式**")

    # 一列一列顯示資訊
    for idx, row in rental_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 2])
        col1.write(row['店面名稱'])
        col2.write(row['租金'])
        col3.write(row['面積'])
        col4.write(row['聯絡房仲'])
        col5.write(row['聯絡方式'])

# 房東新增出租 case
def add_case():
    st.subheader("請填寫出租店面的資料：")

    if 'address' not in st.session_state:
        st.session_state.address = ''
    if 'area' not in st.session_state:
        st.session_state.area = ''
    if 'floor' not in st.session_state:
        st.session_state.floor = ''
    if 'rent' not in st.session_state:
        st.session_state.rent = ''

    # required fields
    st.session_state.address = st.text_input("地址 (必填)", value=st.session_state.address)
    st.session_state.area = st.text_input("坪數 (必填)", placeholder="例如：30坪", value=st.session_state.area)
    st.session_state.floor = st.text_input("樓層 (必填)", placeholder="例如：1樓", value=st.session_state.floor)
    st.session_state.rent = st.text_input("理想租金 (必填)", placeholder="例如：30000元/月", value=st.session_state.rent)

    # 確定交出資料 button
    if st.button("提交表單"):
        if not st.session_state.address or not st.session_state.area or not st.session_state.floor or not st.session_state.rent or st.session_state.shop_type == "請選擇":
            st.error("請確保所有必填欄位已填寫完整！")
        else:
            st.success("表單已提交！以下是您輸入的資料：")
            st.write(f"**地址**: {st.session_state.address}")
            st.write(f"**坪數**: {st.session_state.area}")
            st.write(f"**樓層**: {st.session_state.floor}")
            st.write(f"**理想租金**: {st.session_state.rent}")

# 編輯/更新頁面
def edit_case(case):
    """Displays a form to edit the selected case details."""
    st.subheader(f"編輯出租案件：{case['case_id']}")

    if 'address' not in st.session_state:
        st.session_state.address = case['address']
    if 'size' not in st.session_state:
        st.session_state.size = case['size']
    if 'floor' not in st.session_state:
        st.session_state.floor = case['floor']
    if 'rent' not in st.session_state:
        st.session_state.rent = case['ideal_rent']

    st.session_state.address = st.text_input("地址", value=st.session_state.address)
    st.session_state.size = st.text_input("坪數 (坪)", value=st.session_state.size)
    st.session_state.floor = st.text_input("樓層", value=st.session_state.floor)
    st.session_state.rent = st.text_input("理想租金 (元)", value=st.session_state.rent)

    # status update
    st.markdown("### 更新狀態")
    status = st.radio(
        "選擇新的狀態:",    
        ("尚未出租", "撤回案件", "已出租", "洽談中"),
        index=["尚未出租", "已下架", "已出租", "洽談中"].index(case['status'])
    )

    # submit button
    if st.button("OK"):
        # case update
        st.success("案件已成功更新！")
        st.write({
            "地址": st.session_state.address,
            "坪數": st.session_state.size,
            "樓層": st.session_state.floor,
            "理想租金": st.session_state.rent,
            "狀態": status
        })

# 頁面設定：我是房東
def landlord_page():
    st.title("房東管理頁面")

    # "我要出租店面" button
    with st.sidebar:
        if st.button("我要出租店面"):
            add_case()

    # 假資料
    landlord_cases = [
        {
            "case_id": "C001",
            "address": "台北市信義區松仁路123號",
            "size": 50,
            "floor": "1樓",
            "ideal_rent": 50000,
            "status": "已出租"
        },
        {
            "case_id": "C002",
            "address": "台北市中正區公園路30-1號",
            "size": 30,
            "floor": "2樓",
            "ideal_rent": 30000,
            "status": "尚未出租"
        },
        {
            "case_id": "C003",
            "address": "台北市大安區新生南路三段88之2號",
            "size": 100,
            "floor": "1樓",
            "ideal_rent": 80000,
            "status": "已下架"
        },
    ]

    st.subheader("既有出租案件")
    col1, col2 = st.columns(2)
    for idx, case in enumerate(landlord_cases):
        with (col1 if idx % 2 == 0 else col2):
            # 顯示每一筆出租案件的資訊
            st.write(f"### 案件編號: {case['case_id']}")
            st.write(f"地址: {case['address']}")
            st.write(f"坪數: {case['size']} 坪")
            st.write(f"樓層: {case['floor']}")
            st.write(f"理想租金: {case['ideal_rent']} 元/月")
            st.write(f"交易狀態: {case['status']}")

            # 編輯/更新按鈕
            if st.button("編輯/更新", key=case['case_id']):
                edit_case(case)
            
            st.divider()

# 房東登入頁面函式
def login_page():
    st.title("房東登入")
    phone_number = st.text_input("請輸入您的電話號碼")
    if st.button("登入"):
        if phone_number:
            st.success("登入成功！")
            st.session_state.logged_in = True
        else:
            st.error("請輸入電話號碼！")

def business_page():
    st.title("我是業者")
    tab1, tab2 = st.tabs(["我要租店面", "我要找熱點"])
    
    with tab1:
        rent_store_page()
    
    with tab2:
        find_hotspot_page()

def main():
    st.title("🏢 Welcome to SmartRent")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 選擇角色
    if "role" not in st.session_state:
        st.session_state.role = None
    
    if st.session_state.role is None:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            if st.button("🙋‍♂️ 我是業者", key="business_button"):
                st.session_state.role = "business"
        with col3:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            if st.button("💁‍♂️ 我是房仲", key="landlord_button"):
                st.session_state.role = "landlord"
    
    # 如果是業者
    if st.session_state.role == "business":
        business_page()
    
    # 如果是房東
    elif st.session_state.role == "landlord":
        if not st.session_state.logged_in:
            login_page()
        else:
            landlord_page()

if __name__ == "__main__":
    main()