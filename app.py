import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import query

# 使用者資料儲存
user_data = {"user_name": None, "phone": None, "email": None}

# 頁面設定：我是業者 -> 我要租店面
plt.rcParams['font.family'] = ['Heiti TC']

# 每日平均人潮流動折線圖
def crowd_flow_spectrum():
    time_slots = ["00:00", "06:00", "12:00", "18:00", "24:00"]
    values = [10, 15, 70, 55, 45]

    df = pd.DataFrame({
        'time': time_slots,
        'values': values
    })

    norm = mcolors.Normalize(vmin=0, vmax=len(time_slots)-1)
    cmap = plt.get_cmap('viridis')

    df['color'] = [cmap(norm(i)) for i in range(len(df))]

    # 折線圖
    plt.figure(figsize=(10,6))
    plt.plot(df['time'], df['values'], marker='o', linestyle='-', color='tab:blue')

    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title('Time vs Values Spectrum')

    st.pyplot(plt)

# 住戶密度 & 收入水平分析
def income_density_chart():
    # 假資料
    density_values = [10, 50, 100]  # 住戶密度
    income_values = [10, 50, 100]  # 收入
    
    # 計算住戶密度和收入的平均值和中位數
    avg_density = np.mean(density_values)
    median_density = np.median(density_values)
    avg_income = np.mean(income_values)
    median_income = np.median(income_values)
    
    avg_density = round(avg_density)
    median_density = round(median_density)
    avg_income = round(avg_income)
    median_income = round(median_income)
    
    # X 軸為住戶密度，Y 軸為收入水平
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(density_values, income_values, c='blue', s=100, label='區域點')

    # 假資料
    location_density = 60
    location_income = 70

    # 標示該地點
    ax.scatter(location_density, location_income, c='red', s=100, label='該地點', edgecolor='black')

    # 標示 X 軸與 Y 軸的平均值與中位數
    ax.axvline(avg_density, color='green', linestyle='--', label=f'住戶密度平均值: {avg_density}')
    ax.axhline(avg_income, color='purple', linestyle='--', label=f'收入平均值: {avg_income}')
    ax.axvline(median_density, color='orange', linestyle=':', label=f'住戶密度中位數: {median_density}')
    ax.axhline(median_income, color='yellow', linestyle=':', label=f'收入中位數: {median_income}')

    ax.set_title("住戶密度與收入水平的關係圖")
    ax.set_xlabel("住戶密度")
    ax.set_ylabel("收入水平")
    ax.legend()

    st.pyplot(fig)

# 年齡層分析
def age_distribution_page():
    # 假資料
    age_distribution = {
        "孩童": 10,
        "青少年": 50,
        "新鮮人": 120,
        "壯年": 200,
        "老年": 30
    }

    # 假設年齡層的人口數相較於其他地區的指標（+/- 表示多或少）
    age_comparison = {
        "孩童": "少",
        "青少年": "多",
        "新鮮人": "多",
        "壯年": "少",
        "老年": "少"
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
        st.metric(label="孩童 (0~9)", value=age_df.loc[0, 'count'], delta=age_df.loc[0, 'comparison'])
    with col2:
        st.metric(label="青少年 (10~19)", value=age_df.loc[1, 'count'], delta=age_df.loc[1, 'comparison'])
    with col3:
        st.metric(label="新鮮人 (20~29)", value=age_df.loc[2, 'count'], delta=age_df.loc[2, 'comparison'])

    col4, col5 = st.columns(2)
    with col4:
        st.metric(label="壯年 (30~64)", value=age_df.loc[3, 'count'], delta=age_df.loc[3, 'comparison'])
    with col5:
        st.metric(label="老年 (65 以上)", value=age_df.loc[4, 'count'], delta=age_df.loc[4, 'comparison'])
# 性別比例
def gender_distribution_page():
    gender_distribution = {"男": 60, "女": 40}
    gender_df = pd.DataFrame({
        'gender': gender_distribution.keys(),
        'percentage': gender_distribution.values()
    })
    colors = ['#66b3ff', '#ff66b3']

    fig, ax = plt.subplots()
    ax.pie(gender_distribution.values(), labels=gender_distribution.keys(), autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops={'edgecolor': 'black'})
    ax.axis('equal')
    st.pyplot(fig)

# 商機分析
def opportunity_analysis_page():
    # 人潮流量光譜：早到晚
    st.subheader("人潮流量光譜")
    crowd_flow_spectrum()

    # 住戶密度&人潮流動光譜
    st.subheader("住戶密度光譜")
    income_density_chart()
    
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("年齡層分佈")
        age_distribution_page()

    with col2:
        st.subheader("性別分布")
        gender_distribution_page()

# 競爭市場
def competitive_market_page():
    # 市場資料
    market_data = [
        {"營業項目": "零售業", "店鋪數量": 5, "平均資本額": 500000},
        {"營業項目": "餐飲業", "店舖數量": 3, "平均資本額": 600000},
    ]

    # 店鋪假資料
    store_data = [
        {"店名": "店鋪A", "營業項目": "零售業", "地址": "台北市信義區松仁路123號", "資本額": 1000000, "經度": 121.5654, "緯度": 25.0330},
        {"店名": "店鋪B", "營業項目": "零售業", "地址": "台北市中正區公園路30-1號", "資本額": 800000, "經度": 121.5070, "緯度": 25.0320},
        {"店名": "店鋪C", "營業項目": "零售業", "地址": "台北市大安區新生南路三段88之2號", "資本額": 1200000, "經度": 121.5351, "緯度": 25.0270},
        {"店名": "店鋪D", "營業項目": "餐飲業", "地址": "台北市南港區經貿二路10號", "資本額": 950000, "經度": 121.6035, "緯度": 25.0240},
        {"店名": "店鋪E", "營業項目": "餐飲業", "地址": "台北市北投區光明路35號", "資本額": 700000, "經度": 121.5121, "緯度": 25.1505},
    ]

    # 轉換單位：資本額(元) -> 資本額(萬元)
    for data in market_data:
        data["平均資本額"] = data["平均資本額"] // 10000

    for store in store_data:
        store["資本額"] = store["資本額"] // 10000

    # 按照店舖數量排序
    market_df = pd.DataFrame(market_data).sort_values(by="店舖數量", ascending=False)

    # 市場資料顯示
    st.write("### 競爭市場概覽：")
    col1, col2, col3 = st.columns([3, 3, 3])
    col1.markdown("**營業項目**")
    col2.markdown("**店舖數量**")
    col3.markdown("**平均資本額 (萬元)**")

    for _, row in market_df.iterrows():
        col1, col2, col3 = st.columns([3, 3, 3])
        col1.write(row["營業項目"])
        col2.write(row["店舖數量"])
        col3.write(row["平均資本額"])

    # 顯示每個營業項目的 Top 5 店鋪
    store_df = pd.DataFrame(store_data)
    for business in market_df["營業項目"]:
        st.write(f"### {business} 的 Top 5 資本額店鋪")
        filtered_stores = store_df[store_df["營業項目"] == business].nlargest(5, "資本額")

        col1, col2, col3, col4 = st.columns([2, 5, 3, 3])
        col1.markdown("**店名**")
        col2.markdown("**地址**")
        col3.markdown("**資本額 (萬元)**")
        col4.markdown("**地圖**")

        for _, row in filtered_stores.iterrows():
            col1, col2, col3, col4 = st.columns([2, 5, 3, 3])
            col1.write(row["店名"])
            col2.write(row["地址"])
            col3.write(row["資本額"])
            col4.markdown(f"[Google 地圖連結](https://www.google.com/maps?q={row['緯度']},{row['經度']})", unsafe_allow_html=True)

def filter_stores_by_business(business_type, store_df):
    if business_type == "零售業":
        return store_df[store_df["店名"].isin(["店鋪A", "店鋪B", "店鋪C"])]
    elif business_type == "餐飲業":
        return store_df[store_df["店名"].isin(["店鋪D", "店鋪E", "店鋪F"])]
    else:
        return pd.DataFrame()

def rent_store_page():
    st.title("🔍 我要租店面")

    if "trade_area_details" not in st.session_state:
        st.session_state.trade_area_details = None
    if "rental_details" not in st.session_state:
        st.session_state.rental_details = None
    if "sidebar_view" not in st.session_state:
        st.session_state.sidebar_view = None

    # 輸入理想開店地點 - 必填項目
    st.subheader("請至少輸入一個心目中的理想開店地點後，按 “進行查詢”")

    # 1. 選擇具體的地點
    districts = [
        "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區",
        "內湖區", "南港區", "文山區"
    ]

    selected_districts = st.multiselect(
            "選擇區域別",
            options=districts,
            help="選擇您理想開店的區域"
        )

    # 2. 租金預算
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
        max_value=2000000,
        value=(20000, 50000),
        step=5000,
        help="選擇您的租金預算範圍"
    )

    # 4. 營業項目
    business_type = st.multiselect(
        "選擇營業項目",
        options=[
            "農、林、漁、牧業", "礦業及土石採取業", "製造業", "電力及燃氣供應業", "用水供應及污染整治業",
            "營建工程業", "批發及零售業", "運輸及倉儲業", "住宿及餐飲業", "出版影音及資通訊業",
            "金融及保險業", "不動產業", "專業、科學及技術服務業", "支援服務業", "公共行政及國防",
            "教育業", "醫療保健及社會工作服務業", "藝術、娛樂及休閒服務業", "其他服務業"
        ],
        help="選擇您的營業項目"
    )

    # 進行查詢 button
    if st.button("進行查詢"):
        # 商圈資料
        st.session_state.trade_area_details = [
            {
                "name": "商圈 A",
                "type": "玩",
                "address": "地址 A",
                "rent": "93,000/月",
                "rentals": [
                    {"address": "出租地址 1", "rent": "73,000/月", "rent_ping": "2,433/坪", "size": "30 坪", "landlord": {"name": "章先生", "phone": "0927464741"}},
                    {"address": "出租地址 2", "rent": "85,000/月", "rent_ping": "1,700/坪", "size": "50 坪", "landlord": {"name": "洪小姐", "phone": "0998876232"}},
                ],
            },
            {
                "name": "商圈 B",
                "type": "吃",
                "address": "地址 B",
                "rent": "76,000/月",
                "rentals": [
                    {"address": "出租地址 3", "rent": "95,000/月", "rent_ping": "1,900/坪", "size": "50 坪", "landlord": {"name": "林先生", "phone": "0911234567"}},
                    {"address": "出租地址 4", "rent": "78,000/月", "rent_ping": "2,600/坪", "size": "30 坪", "landlord": {"name": "張小姐", "phone": "0987654321"}},
                ],
            },
        ]
        st.session_state.selected_trade_area = None

    # 查詢結果
    if "trade_area_details" in st.session_state:
        st.subheader("商圈資訊")
        for idx, area in enumerate(st.session_state.trade_area_details):
            # 商圈資訊
            with st.expander(f"{area['name']} - 周邊平均租金 {area['rent']}"):
                st.write(f"**地址**: {area['address']}")
                st.write(f"**類型**: {area['type']}")

                # 建 button -- 顯示該商圈的店面出租資訊
                if st.button(f"顯示 {area['name']} 附近店面出租資訊", key=f"show_rentals_{idx}"):
                    st.session_state.selected_trade_area = area

    # 店面出租資訊
    if "selected_trade_area" in st.session_state and st.session_state.selected_trade_area:
        area = st.session_state.selected_trade_area
        st.subheader(f"{area['name']} 附近店面出租資訊")
        rentals = area["rentals"]

        # 分成兩個 column 顯示
        cols = st.columns(2)
        for i, rental in enumerate(rentals):
            col = cols[i % 2]
            with col:
                st.write(f"### {rental['address']} - {rental['rent']}")
                st.write(f"**地址**: {rental['address']}")
                st.write(f"**租金**: {rental['rent']} ({rental['rent_ping']})")
                st.write(f"**坪數**: {rental['size']}")

                # 建兩個 button
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(f"聯絡房仲", key=f"contact_{rental['address']}"):
                        landlord = rental['landlord']
                        st.write(f"聯絡人: {landlord['name']}")
                        st.write(f"電話: {landlord['phone']}")
                with btn_col2:
                    if st.button(f"適不適合我開店", key=f"check_{rental['address']}"):
                        st.session_state.selected_rental = rental
                        st.session_state.page = "analysis_page"

    if st.session_state.get("page", None) == "analysis_page":
        st.session_state.page = None
        # 兩個 tab
        tabs = st.tabs(["商機分析", "競爭市場"])
        with tabs[0]:
            opportunity_analysis_page()
        with tabs[1]:
            competitive_market_page()

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
    avg_traffic = st.slider("每日平均流動人潮 >= ", min_value=0, max_value=10, value=(0,5))

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