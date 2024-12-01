import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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
    cmap = plt.get_cmap('viridis')  # 可以選擇不同的顏色映射

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
        "嬰兒": 10,
        "青少年": 50,
        "新鮮人": 120,
        "壯年": 200,
        "老年": 30
    }

    # 假設年齡層的人口數相較於其他地區的指標（+/- 表示多或少）
    age_comparison = {
        "嬰兒": "少",
        "青少年": "多",
        "新鮮人": "多",
        "壯年": "少",
        "老年": "少"
    }

    age_groups = ["嬰兒", "青少年", "新鮮人", "壯年", "老年"]

    age_df = pd.DataFrame({
        'age_group': age_groups,
        'count': [age_distribution[group] for group in age_groups],
        'comparison': [age_comparison[group] for group in age_groups]
    })

   # 顯示年齡層人口數
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="嬰兒", value=age_df.loc[0, 'count'], delta=age_df.loc[0, 'comparison'])
    with col2:
        st.metric(label="青少年", value=age_df.loc[1, 'count'], delta=age_df.loc[1, 'comparison'])
    with col3:
        st.metric(label="新鮮人", value=age_df.loc[2, 'count'], delta=age_df.loc[2, 'comparison'])

    col4, col5 = st.columns(2)
    with col4:
        st.metric(label="壯年", value=age_df.loc[3, 'count'], delta=age_df.loc[3, 'comparison'])
    with col5:
        st.metric(label="老年", value=age_df.loc[4, 'count'], delta=age_df.loc[4, 'comparison'])
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

# 競爭市場頁面
def competitive_market_page():
    market_data = [
        {"業務項目": "零售業", "店鋪數量": 5, "平均資本額": 500000},
        {"業務項目": "餐飲業", "店鋪數量": 3, "平均資本額": 600000},
    ]

    market_df = pd.DataFrame(market_data)

    st.write("### 競爭市場概覽：")
    st.table(market_df)

    # 假資料
    store_data = [
        {"店名": "店鋪A", "地址": "台北市信義區松仁路123號", "資本額": 1000000, "經度": 121.5654, "緯度": 25.0330},
        {"店名": "店鋪B", "地址": "台北市中正區公園路30-1號", "資本額": 800000, "經度": 121.5070, "緯度": 25.0320},
        {"店名": "店鋪C", "地址": "台北市大安區新生南路三段88之2號", "資本額": 1200000, "經度": 121.5351, "緯度": 25.0270},
        {"店名": "店鋪D", "地址": "台北市南港區經貿二路10號", "資本額": 950000, "經度": 121.6035, "緯度": 25.0240},
        {"店名": "店鋪E", "地址": "台北市北投區光明路35號", "資本額": 700000, "經度": 121.5121, "緯度": 25.1505},
        {"店名": "店鋪F", "地址": "台北市士林區天母路45號", "資本額": 1100000, "經度": 121.5236, "緯度": 25.1060},
    ]

    store_df = pd.DataFrame(store_data)
    top_stores = store_df.sort_values(by="資本額", ascending=False).head(5)

    for row in market_data:
        with st.expander(f"{row['業務項目']} - {row['店鋪數量']}家店鋪"):
            st.write(f"**店鋪數量**: {row['店鋪數量']}家")
            st.write(f"**平均資本額**: {row['平均資本額']}元")
            # Link to show the top 5 stores for that business type
            st.write("點擊 [這裡] 查看店家")
    
    st.write("### Top 5 資本額店鋪")
    top_stores['詳情'] = top_stores.apply(
        lambda row: f"[Google 地圖連結](https://www.google.com/maps?q={row['緯度']},{row['經度']})", axis=1
    )
    st.table(top_stores[['店名', '地址', '資本額', '詳情']])


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

    # 1. 選擇劃分依據
    location_type = st.selectbox(
        "請選擇劃分依據（區域別、商圈名稱）",
        options=["區域別", "商圈名稱"],
        help="至少選擇一個劃分依據"
    )

    # 2. 選擇具體的地點
    districts = [
        "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區",
        "內湖區", "南港區", "文山區"
    ]
    shopping_districts = [
        "東區", "西門町", "信義商圈", "士林夜市", "永康街", "南京東路商圈", "忠孝東路商圈",
        "南京三民商圈", "松山文創園區", "華山文創園區", "大安區", "北門商圈", "南門市場"
    ]

    if "區域別" in location_type:
        selected_districts = st.multiselect(
            "選擇區域別",
            options=districts,
            help="選擇您理想開店的區域"
        )

    if "商圈名稱" in location_type:
        selected_shopping_districts = st.multiselect(
            "選擇商圈名稱",
            options=shopping_districts,
            help="選擇您理想開店的商圈"
        )

    # 3. 租金預算
    ping = st.slider(
        "選擇空間大小（坪）",
        min_value=0,
        max_value=10000,
        value=(20, 100),
        step=5,
        help="選擇您的店面空間需求"
    )
    
    # 4. 租金預算
    rent_budget = st.slider(
        "選擇租金預算（每月）",
        min_value=10000,
        max_value=1000000,
        value=(20000, 50000),
        step=5000,
        help="選擇您的租金預算範圍"
    )

    # 5. 營業項目
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
        st.session_state.trade_area_details = [
            {"name": "商圈 A", "type": "玩", "address": "地址 A", "rent": "93,000/月", "contact": {"name": "聯絡人 A", "phone": "0982647283", "email": "iqjdoc@gmail.com"}},
            {"name": "商圈 B", "type": "吃", "address": "地址 B", "rent": "76,000/月", "contact": {"name": "聯絡人 B", "phone": "0926495120", "email": "1004njcsn@gmail.com"}},
        ]
        st.session_state.rental_details = [
            {"address": "出租地址 1", "rent": "73,000/月", "rent_ping": "2,433/坪", "size": "30 坪", "landlord": {"name": "章先生","phone": "0927464741", "email": "xi09312@gmail.com"}},
            {"address": "出租地址 2", "rent": "85,000/月", "rent_ping": "1,700/坪", "size": "50 坪", "landlord": {"name": "洪小姐", "phone": "0998876232", "email": "snmo8j9ed@gmail.com"}},
        ]

    # 顯示查詢結果
    if st.session_state.trade_area_details:
        st.subheader("商圈資訊")
        for area in st.session_state.trade_area_details:
            with st.expander(f"{area['name']} - 周邊平均租金 {area['rent']}"):
                st.write(f"**地址**: {area['address']}")
                st.write(f"**類型**: {area['type']}")
                if st.button(f"想進一步了解 {area['name']}", key=f"area_{area['name']}"):
                    contact = area['contact']
                    st.write(f"聯絡人: {contact['name']}")
                    st.write(f"電話: {contact['phone']}")
                    st.write(f"Email: {contact['email']}")

    if st.session_state.rental_details:
        st.subheader("附近店面出租資訊")
        for rental in st.session_state.rental_details:
            with st.expander(f"{rental['address']} - {rental['rent']}"):
                st.write(f"**地址**: {rental['address']}")
                st.write(f"**租金**: {rental['rent']}; {rental['rent_ping']}")
                st.write(f"**坪數**: {rental['size']}")
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"聯絡房東 ({rental['address']})"):
                        landlord = rental['landlord']
                        st.write(f"聯絡人: {landlord['name']}")
                        st.write(f"電話: {landlord['phone']}")
                        st.write(f"Email: {landlord['email']}")
                with col2:
                    if st.button(f"適不適合我開店", key=f"check_{rental['address']}"):
                        st.session_state.selected_rental = rental
                        st.session_state.page = "analysis_page"
    if st.session_state.get("page", None) == "analysis_page":
        st.session_state.page = None
        # 顯示兩個tab
        tabs = st.tabs(["商機分析", "競爭市場"])
        with tabs[0]:
            opportunity_analysis_page()
        with tabs[1]:
            competitive_market_page()

locations_data = {
    "地點": ["A區", "B區", "C區", "D區", "E區"],
    "每日平均流動人潮": [1000, 5000, 3000, 1500, 4500],
    "常住人口": [50000, 200000, 150000, 100000, 250000],
    "平均潛在消費力": [30000, 50000, 40000, 35000, 60000],
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
    avg_traffic = st.slider("每日平均流動人潮 >= ", min_value=0, max_value=10000, value=2000)

    # 常住人口
    population = st.slider("常住人口 >= ", min_value=0, max_value=1000000, value=100000)

    # 平均潛在消費力
    spending_power = st.slider("平均潛在消費力 >= ", min_value=0, max_value=100000, value=30000)

    # 熱門時段（多選）
    popular_times = st.multiselect(
        "熱門時段",
        ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00",
         "17:00-19:00", "18:00-20:00", "20:00-22:00"]
    )

    # 篩選符合條件的地點
    filtered_df = locations_df[
        (locations_df["每日平均流動人潮"] >= avg_traffic) &
        (locations_df["常住人口"] >= population) &
        (locations_df["平均潛在消費力"] >= spending_power) &
        (locations_df["熱門時段"].apply(lambda x: any(time in popular_times for time in x)))
    ]

    # 顯示符合條件的前五個地點
    st.subheader("符合條件的前 5 個地點：")
    top_locations = filtered_df.head(5)

    for _, row in top_locations.iterrows():
        st.write(f"地點：{row['地點']}, 每日平均流動人潮：{row['每日平均流動人潮']}, 常住人口：{row['常住人口']}, "
                 f"平均潛在消費力：{row['平均潛在消費力']}, 熱門時段：{', '.join(row['熱門時段'])}")

        # 在每一行後顯示按鈕
        if st.button(f"查看 {row['地點']} 附近店面出租資訊", key=row['地點']):
            show_rental_info(row['地點'])

# 顯示出租資訊
def show_rental_info(location):
    st.subheader(f"在 {location} 附近的店面出租資訊")

    # 假資訊
    rental_info = {
        "店面名稱": ["店面A", "店面B", "店面C"],
        "租金": ["50000元/月", "60000元/月", "55000元/月"],
        "面積": ["30㎡", "40㎡", "35㎡"],
        "聯絡方式": ["0922-xxxxxx", "0933-xxxxxx", "0911-xxxxxx"]
    }

    rental_df = pd.DataFrame(rental_info)
    for _, row in rental_df.iterrows():
        st.write(f"店面名稱：{row['店面名稱']}, 租金：{row['租金']}, 面積：{row['面積']}, 聯絡方式：{row['聯絡方式']}")

    # 提供聯絡房東按鈕
    if st.button("聯絡房東", key="contact_landlord"):
        contact_landlord()

# 聯絡房東的功能
def contact_landlord():
    st.write("您可以通過以下方式聯絡房東：")
    st.write("電話：0922-485436 或發送電子郵件至 landlord@example.com")

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
    if 'shop_type' not in st.session_state:
        st.session_state.shop_type = '請選擇'
    if 'decoration' not in st.session_state:
        st.session_state.decoration = []
    if 'property_type' not in st.session_state:
        st.session_state.property_type = '請選擇'

    # required fields
    st.session_state.address = st.text_input("地址 (必填)", value=st.session_state.address)
    st.session_state.area = st.text_input("坪數 (必填)", placeholder="例如：30坪", value=st.session_state.area)
    st.session_state.floor = st.text_input("樓層 (必填)", placeholder="例如：1樓", value=st.session_state.floor)
    st.session_state.rent = st.text_input("理想租金 (必填)", placeholder="例如：30000元/月", value=st.session_state.rent)

    st.session_state.shop_type = st.selectbox(
        "店舖類型 (必填)",
        ["請選擇", "餐飲", "零售", "辦公室", "倉庫", "其他"],
        index=["請選擇", "餐飲", "零售", "辦公室", "倉庫", "其他"].index(st.session_state.shop_type)
    )

    # optional fields
    st.session_state.decoration = st.multiselect(
        "裝潢 (選填)",
        ["基本裝修", "精緻裝修", "未裝修"],
        default=st.session_state.decoration
    )

    st.session_state.property_type = st.selectbox(
        "型態 (選填)",
        ["請選擇", "住宅改商用", "商業用途", "工業用途"],
        index=["請選擇", "住宅改商用", "商業用途", "工業用途"].index(st.session_state.property_type)
    )

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
            st.write(f"**店舖類型**: {st.session_state.shop_type}")
            if st.session_state.decoration:
                st.write(f"**裝潢**: {', '.join(st.session_state.decoration)}")
            else:
                st.write("**裝潢**: 無")
            if st.session_state.property_type != "請選擇":
                st.write(f"**型態**: {st.session_state.property_type}")
            else:
                st.write("**型態**: 無")

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
    if 'store_type' not in st.session_state:
        st.session_state.store_type = case['store_type']

    st.session_state.address = st.text_input("地址", value=st.session_state.address)
    st.session_state.size = st.text_input("坪數 (坪)", value=st.session_state.size)
    st.session_state.floor = st.text_input("樓層", value=st.session_state.floor)
    st.session_state.rent = st.text_input("理想租金 (元)", value=st.session_state.rent)
    st.session_state.store_type = st.text_input("店舖類型", value=st.session_state.store_type)

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
            "店舖類型": st.session_state.store_type,
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
            "store_type": "餐飲",
            "status": "已出租"
        },
        {
            "case_id": "C002",
            "address": "台北市中正區公園路30-1號",
            "size": 30,
            "floor": "2樓",
            "ideal_rent": 30000,
            "store_type": "零售",
            "status": "尚未出租"
        },
        {
            "case_id": "C003",
            "address": "台北市大安區新生南路三段88之2號",
            "size": 100,
            "floor": "1樓",
            "ideal_rent": 80000,
            "store_type": "其他",
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
            st.write(f"店舖類型: {case['store_type']}")
            st.write(f"交易狀態: {case['status']}")

            # 編輯/更新按鈕
            if st.button("編輯/更新", key=case['case_id']):
                edit_case(case)
            
            st.divider()

# 登入頁面函式
def login_page():
    st.title("登入頁面")
    with st.form("login_form"):
        user_name = st.text_input("使用者名稱", placeholder="請輸入您的名稱")
        phone = st.text_input("電話", placeholder="請輸入您的電話號碼")
        email = st.text_input("Email", placeholder="請輸入您的電子郵件")
        submitted = st.form_submit_button("登入")

        if submitted:
            if not user_name or not phone or not email:
                st.error("請完整填寫所有欄位！")
            else:
                user_data["user_name"] = user_name
                user_data["phone"] = phone
                user_data["email"] = email
                st.session_state["logged_in"] = True
                st.rerun()  # 進入主頁面

# 主頁面函式
def main_page():
    st.sidebar.write(f"👤 使用者：{user_data['user_name']}")
    st.sidebar.write(f"📞 電話：{user_data['phone']}")
    st.sidebar.write(f"📧 Email：{user_data['email']}")

    st.title("🏢 Welcome to SmartRent")
    tabs = st.tabs(["🙋‍♂️ 我是業者", "💁‍♂️ 我是房東"])

    # 業者
    with tabs[0]:
        purpose = st.radio("請選擇造訪目的", ["我要租店面", "我要找熱點"])
        if purpose == "我要租店面":
            rent_store_page()
        elif purpose == "我要找熱點":
            find_hotspot_page()

    # 房東
    with tabs[1]:
        landlord_page()

# 啟動
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_page()
else:
    main_page()