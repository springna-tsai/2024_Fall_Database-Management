#!/usr/bin/env python
# coding: utf-8

# #### Import

# In[1]:


import duckdb
import pandas as pd

con = duckdb.connect('data.db')


# In[2]:


# show table
con.sql('show tables')


# ## 查詢周邊商圈、租房資訊

# ### 商圈平均租金以及周邊捷運站

# In[ ]:


def get_organization_data(district = None):
    # 檢查使用者是否勾選 district，若有則根據選擇的區域回傳，否則回傳全部
    where_clause = f"WHERE district = '{district}'" if district else ""
    
    res = con.sql(f"""--sql
        WITH nearest_stations AS (
            SELECT 
                s.district,
                s.case_name,
                s.address,
                s.monthly_rent,
                s.area_ping,
                m.station_id,
                m.station_name,
                MIN(
                    6371 * ACOS(
                        COS(RADIANS(s.latitude)) * COS(RADIANS(m.latitude)) *
                        COS(RADIANS(m.longitude) - RADIANS(s.longitude)) +
                        SIN(RADIANS(s.latitude)) * SIN(RADIANS(m.latitude))
                    )
                ) AS nearest_distance_km
            FROM shop_rental_listing s
            CROSS JOIN MRT_Station_Info m
            GROUP BY s.district, s.case_name, s.address, s.monthly_rent, s.area_ping, m.station_id, m.station_name
            HAVING nearest_distance_km <= 1
        )
        SELECT 
            mba.name , -- 商圈名稱
            ROUND(AVG(ns.monthly_rent)) AS average_monthly_rent,
            ns.station_name,
            mba.tag ,
            ns.district
        FROM nearest_stations ns
        JOIN MRT_Business_Area mba ON ns.station_id = mba.station_id -- 加入商圈數據
        {where_clause} -- 動態加入條件
        GROUP BY mba.name, mba.tag, ns.station_name, ns.district
        ORDER BY ns.district, ns.station_name; 
        """)
    df = res.df()
    return df

# 範例
get_organization_data(district = '中山區')
# get_organization_data()


# In[ ]:


def get_filtered_shop_rentals(district=None, min_rent=None, max_rent=None, min_area=None, max_area=None):
    # 動態構建 WHERE 條件
    conditions = []
    if district is not None:
        conditions.append(f"s.district = '{district}'")
    if min_rent is not None:
        conditions.append(f"s.monthly_rent >= {min_rent}")
    if max_rent is not None:
        conditions.append(f"s.monthly_rent <= {max_rent}")
    if min_area is not None:
        conditions.append(f"s.area_ping >= {min_area}")
    if max_area is not None:
        conditions.append(f"s.area_ping <= {max_area}")
    
    # 將條件組合成 WHERE 子句
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    # 執行 SQL 查詢
    query = f"""--sql
    SELECT 
        s.case_id,
        s.district,
        s.village,
        s.case_name,
        s.address, 
        s.monthly_rent, 
        ROUND(s.monthly_rent / s.area_ping) AS monthly_rent_per_ping, 
        s.area_ping, 
        s.shop_floor, 
        s.total_floor,
        s.deposit, 
        r.name, 
        r.phone
    FROM Shop_Rental_Listing s
    LEFT JOIN Representative r ON s.phone = r.phone
    
    {where_clause} -- 動態加入條件
    """
    res = con.sql(query)
    df = res.df()
    return df

# 範例
# get_filtered_shop_rentals(min_rent=10000, max_rent=30000, min_area=10, max_area=50)
# get_filtered_shop_rentals()


# ## 店面資料與所在商圈及鄰近捷運站

# In[7]:


con.sql("""--sql
    WITH distances AS (
    SELECT
        s.case_id,
        s.district,
        s.village,
        s.case_name,
        s.monthly_rent,
        s.area_ping,
        s.address,
        m.station_id,
        m.station_name,
        (
            6371 * ACOS(
                COS(RADIANS(s.latitude)) * COS(RADIANS(m.latitude)) *
                COS(RADIANS(m.longitude) - RADIANS(s.longitude)) +
                SIN(RADIANS(s.latitude)) * SIN(RADIANS(m.latitude))
            )
        ) AS distance_km
    FROM Shop_Rental_Listing s
    CROSS JOIN MRT_Station_Info m
),
nearest_stations AS (
    SELECT
        d.case_id, 
        d.district,
        d.case_name,
        d.address,
        d.village,
        d.station_id,
        d.station_name,
        d.monthly_rent,
        d.area_ping,
        MIN(d.distance_km) AS nearest_distance_km
    FROM distances d
    GROUP BY d.case_id, d.district, d.case_name, d.address, d.village, d.station_id, d.station_name, d.monthly_rent, d.area_ping
    HAVING MIN(d.distance_km) <= 1
)
SELECT 
    ns.case_id,
    ns.district,
    ns.village,
    ns.address,
    ns.case_name,
    ns.station_id,
    ns.station_name,
    ns.monthly_rent,
    ns.area_ping,
    mba.name, -- 商圈名稱
    mba.tag
FROM nearest_stations ns
JOIN MRT_Business_Area mba ON ns.station_id = mba.station_id -- 加入商圈數據d.
ORDER BY ns.case_id, ns.village, ns.nearest_distance_km ASC;
""")


# In[81]:


def get_shop_flow_data(case_id=None):
    # 動態構建 WHERE 條件
    conditions = []
    if case_id:
        conditions.append(f"cf.case_id = '{case_id}'")
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    res = con.sql(f"""--sql
    WITH mrt_distances AS (
        SELECT
            s.case_id,
            s.district,
            s.village,
            s.case_name,
            m.station_id AS mrt_station_id,
            (
                6371 * ACOS(
                    COS(RADIANS(s.latitude)) * COS(RADIANS(m.latitude)) *
                    COS(RADIANS(m.longitude) - RADIANS(s.longitude)) +
                    SIN(RADIANS(s.latitude)) * SIN(RADIANS(m.latitude))
                )
            ) AS mrt_distance_km
        FROM Shop_Rental_Listing s
        CROSS JOIN MRT_Station_Info m
    ),
    ubike_distances AS (
        SELECT
            s.case_id,
            s.district,
            s.village,
            s.case_name,
            u.station_id AS ubike_station_id,
            (
                6371 * ACOS(
                    COS(RADIANS(s.latitude)) * COS(RADIANS(u.latitude)) *
                    COS(RADIANS(u.longitude) - RADIANS(s.longitude)) +
                    SIN(RADIANS(s.latitude)) * SIN(RADIANS(u.latitude))
                )
            ) AS ubike_distance_km
        FROM Shop_Rental_Listing s
        CROSS JOIN Ubike_Station_Info u
    ),
    mrt_nearest_stations AS (
        SELECT 
            d.case_id,
            d.district,
            d.case_name,
            d.village,
            d.mrt_station_id
        FROM mrt_distances d
        WHERE d.mrt_distance_km <= 1
    ),
    ubike_nearest_stations AS (
        SELECT 
            d.case_id,
            d.district,
            d.case_name,
            d.village,
            d.ubike_station_id
        FROM ubike_distances d
        WHERE d.ubike_distance_km <= 1
    ),
    -- 不在此處過濾時段，使 MRT flow 保留所有時段
    mrt_flow_data AS (
        SELECT
            mf.station_id AS mrt_station_id, 
            mf.time_period,
            ROUND(AVG(mf.entrance_count + mf.exit_count)) AS avg_mrt_flow
        FROM MRT_Flow_Record mf
        WHERE mf.date >= CURRENT_DATE - INTERVAL '2 years' AND time_period NOT BETWEEN 2 AND 5
        GROUP BY mf.station_id, mf.time_period
    ),
    ubike_flow_data AS (
        SELECT
            uf.station_id AS ubike_station_id,
            uf.time_period,
            ROUND(AVG(uf.rent_count + uf.return_count)) AS avg_ubike_flow
        FROM Ubike_Station_Rental_Record uf
        WHERE uf.date >= CURRENT_DATE - INTERVAL '2 years'
        GROUP BY uf.station_id, uf.time_period
    ),
    -- 將 mrt_nearest_stations 與 mrt_flow_data JOIN，彙整出以 case_id 為單位的 MRT flow 資料
    mrt_case_flow AS (
        SELECT
            mrt.case_id,
            mrt.district,
            mrt.case_name,
            mrt.village,
            mf.time_period,
            AVG(mf.avg_mrt_flow) AS avg_mrt_flow
        FROM mrt_nearest_stations mrt
        JOIN mrt_flow_data mf ON mf.mrt_station_id = mrt.mrt_station_id
        GROUP BY mrt.case_id, mrt.district, mrt.case_name, mrt.village, mf.time_period
    ),
    -- 將 ubike_nearest_stations 與 ubike_flow_data JOIN，彙整出以 case_id 為單位的 Ubike flow 資料
    ubike_case_flow AS (
        SELECT
            ubike.case_id,
            ubike.district,
            ubike.case_name,
            ubike.village,
            uf.time_period,
            AVG(uf.avg_ubike_flow) AS avg_ubike_flow
        FROM ubike_nearest_stations ubike
        JOIN ubike_flow_data uf ON uf.ubike_station_id = ubike.ubike_station_id
        GROUP BY ubike.case_id, ubike.district, ubike.case_name, ubike.village, uf.time_period
    ),
    -- FULL JOIN 將MRT與Ubike的case flow合併，確保沒有MRT資料的時段依然會出現
    combined_flow AS (
        SELECT
            COALESCE(mcf.case_id, ucf.case_id) AS case_id,
            COALESCE(mcf.district, ucf.district) AS district,
            COALESCE(mcf.case_name, ucf.case_name) AS case_name,
            COALESCE(mcf.village, ucf.village) AS village,
            COALESCE(mcf.time_period, ucf.time_period) AS time_period,
            ROUND(COALESCE(mcf.avg_mrt_flow,0) + COALESCE(ucf.avg_ubike_flow,0)) AS avg_total_flow
        FROM mrt_case_flow mcf
        FULL JOIN ubike_case_flow ucf 
            ON mcf.case_id = ucf.case_id
           AND mcf.time_period = ucf.time_period
    ),
    business_area_info AS (
        SELECT 
            ns.case_id,
            mba.name AS business_area_name,
            mba.tag AS business_area_tag
        FROM mrt_nearest_stations ns
        JOIN MRT_Business_Area mba ON ns.mrt_station_id = mba.station_id
        GROUP BY ns.case_id, mba.name, mba.tag
    )
    SELECT 
        cf.case_id,
        cf.district,
        cf.village,
        cf.case_name,
        bai.business_area_name,
        cf.time_period,
        cf.avg_total_flow
    FROM combined_flow cf
    LEFT JOIN business_area_info bai ON cf.case_id = bai.case_id
    {where_clause}
    ORDER BY cf.district, cf.village, cf.case_name, bai.business_area_name, cf.time_period ASC;
    """)
    df = res.df()
    return df

# 範例呼叫
# get_shop_flow_data(case_name='正隆官邸優質店面一樓', business_area_name='永康(商圈)')
# get_shop_flow_data(case_name='正隆官邸優質店面一樓')
# get_shop_flow_data()


# ## 村裡人口、年齡、性別

# In[ ]:


def get_village_data(district=None):
    # 動態構建 WHERE 條件
    conditions = []
    if district:
        conditions.append(f"vi.district = '{district}'")
    
    # 合成 WHERE 子句
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    res = con.sql(f"""--sql
        SELECT vi.district, vi.village, vi.household_count, vi.avg_income,
        ROUND(AVG(vi.avg_income) OVER (PARTITION BY vi.district)) AS nearby_avg_income, vi.median_income,
        ROUND(AVG(vi.household_count) OVER (PARTITION BY vi.district)) AS nearby_avg_density,
        ROUND(vi.male_population * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS male_population_ratio, 
        ROUND(vi.female_population * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS female_population_ratio, 
        ROUND(v.age_0_9 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS avg_0_9_ratio, 
        ROUND(v.age_10_19 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS avg_10_19_ratio, 
        ROUND(v.age_20_29 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS avg_20_29_ratio, 
        ROUND(v.age_30_64 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS avg_30_64_ratio, 
        ROUND(v.age_over_65 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.village), 4) AS avg_over_65_ratio,
        ROUND(v.age_0_9 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.district), 4) AS nearby_0_9_ratio, 
        ROUND(v.age_10_19 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.district), 4) AS nearby_10_19_ratio, 
        ROUND(v.age_20_29 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.district), 4) AS nearby_20_29_ratio, 
        ROUND(v.age_30_64 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.district), 4) AS nearby_30_64_ratio, 
        ROUND(v.age_over_65 * 1.0 / SUM(vi.male_population + vi.female_population) OVER (PARTITION BY vi.district), 4) AS nearby_over_65_ratio 
        FROM Village_Info vi
        LEFT JOIN Village_Population_By_Age v ON vi.district = v.district AND vi.village = v.village
        {where_clause}
    """)
    df = res.df()
    return df

# 範例
# get_village_data(district = '士林區', village = '承德里')
# get_village_data(district = '士林區')
# get_village_data()


# ## 競爭市場

# In[88]:


def get_competitive_data(district=None, village=None, type=None):
    # 動態構建 WHERE 條件
    conditions = []
    if district:
        conditions.append(f"district = '{district}'")
    if village:
        conditions.append(f"village = '{village}'")
    if type:
        conditions.append(f"business_type = '{type}'")
    # 合成 WHERE 子句
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    res = con.sql(f"""--sql
            SELECT district, village, business_type, business_sub_type, COUNT(business_name) as shop_cnt, ROUND(AVG(capital)) as avg_capital
            FROM Business_Operation
            {where_clause}
            GROUP BY district, village, business_type, business_sub_type
          """)
    df = res.df()
    return df

# get_village_data(district = '大安區', village = '民輝里')
# get_village_data(district = '大安區')
# get_village_data()


# ## 該村里前五個該商圈最多的 business_sub_type 

# In[ ]:


def get_top5_subtype_data(district=None, village=None):
    # 動態構建 WHERE 條件
    conditions = []
    if district:
        conditions.append(f"district = '{district}'")
    if village:
        conditions.append(f"village = '{village}'")

    # 合成 WHERE 子句
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    res = con.sql(f"""--sql
            SELECT district, village, business_type, business_sub_type, COUNT(business_name) as shop_cnt, ROUND(AVG(capital)) as avg_capital
            FROM Business_Operation
            {where_clause}
            GROUP BY district, village, business_type, business_sub_type
            ORDER BY shop_cnt DESC
            LIMIT 5
          """)
    df = res.df()
    return df

# get_village_data(district = '大安區', village = '民輝里')
# get_village_data(district = '大安區')
# get_village_data()

# subtype 的店鋪資料
def get_business_data(business_sub_type=None, district=None, village=None):
    # 動態構建 WHERE 條件
    conditions = []
    if business_sub_type:
        conditions.append(f"business_sub_type = '{business_sub_type}'")
    if district:
        conditions.append(f"district = '{district}'")
    if village:
        conditions.append(f"village = '{village}'")

    # 合成 WHERE 子句
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    res = con.sql(f"""--sql
            SELECT business_name, address, capital, longitude, latitude, district, village
            FROM Business_Operation 
            {where_clause}
          """)
    df = res.df()
    return df

# 範例
# get_business_data('布疋及服飾品零售業')

# 熱點搜索
def get_organization_flow_data(flow_rank=None, time_periods=None):
    # 動態構建 WHERE 條件
    conditions = []
    if flow_rank is not None:
        conditions.append(f"bar.flow_rank >= {flow_rank}")
    if time_periods:
        # 將 time_periods 格式化為 SQL 可接受的 IN 條件
        formatted_periods = ", ".join([f"'{tp}'" for tp in time_periods])
        conditions.append(f"cf.time_group IN ({formatted_periods})")
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    res = con.sql(f"""--sql
    WITH mrt_distances AS (
    SELECT
        s.case_id,
        s.district,
        s.village,
        s.case_name,
        m.station_id AS mrt_station_id,
        (
            6371 * ACOS(
                COS(RADIANS(s.latitude)) * COS(RADIANS(m.latitude)) *
                COS(RADIANS(m.longitude) - RADIANS(s.longitude)) +
                SIN(RADIANS(s.latitude)) * SIN(RADIANS(m.latitude))
            )
        ) AS mrt_distance_km
    FROM Shop_Rental_Listing s
    CROSS JOIN MRT_Station_Info m
    ),
    ubike_distances AS (
        SELECT
            s.case_id,
            s.district,
            s.village,
            s.case_name,
            u.station_id AS ubike_station_id,
            (
                6371 * ACOS(
                    COS(RADIANS(s.latitude)) * COS(RADIANS(u.latitude)) *
                    COS(RADIANS(u.longitude) - RADIANS(s.longitude)) +
                    SIN(RADIANS(s.latitude)) * SIN(RADIANS(u.latitude))
                )
            ) AS ubike_distance_km
        FROM Shop_Rental_Listing s
        CROSS JOIN Ubike_Station_Info u
    ),
    mrt_flow_data AS (
        SELECT
            mf.station_id AS mrt_station_id, 
            FLOOR((mf.time_period - 1) / 2) + 1 AS time_group,
            ROUND(SUM(mf.entrance_count + mf.exit_count)) AS avg_mrt_flow
        FROM MRT_Flow_Record mf
        WHERE mf.date >= CURRENT_DATE - INTERVAL '2 years' 
        AND mf.time_period NOT BETWEEN 2 AND 5
        GROUP BY mf.station_id, time_group
    ),
    ubike_flow_data AS (
        SELECT
            uf.station_id AS ubike_station_id,
            FLOOR((uf.time_period - 1) / 2) + 1 AS time_group,
            ROUND(SUM(uf.rent_count + uf.return_count)) AS avg_ubike_flow
        FROM Ubike_Station_Rental_Record uf
        WHERE uf.date >= CURRENT_DATE - INTERVAL '2 years'
        GROUP BY uf.station_id, time_group
    ),
    mrt_case_flow AS (
        SELECT
            mrt.case_id,
            mrt.district,
            mrt.case_name,
            mrt.village,
            m.station_name AS mrt_station_name,
            mf.time_group,
            SUM(mf.avg_mrt_flow) AS total_mrt_flow
        FROM mrt_distances mrt
        JOIN mrt_flow_data mf ON mf.mrt_station_id = mrt.mrt_station_id
        JOIN MRT_Station_Info m ON m.station_id = mrt.mrt_station_id
        WHERE mrt.mrt_distance_km <= 1
        GROUP BY mrt.case_id, mrt.district, mrt.case_name, mrt.village, m.station_name, mf.time_group
    ),
    ubike_case_flow AS (
        SELECT
            ubike.case_id,
            ubike.district,
            ubike.case_name,
            ubike.village,
            uf.time_group,
            SUM(uf.avg_ubike_flow) AS total_ubike_flow
        FROM ubike_distances ubike
        JOIN ubike_flow_data uf ON uf.ubike_station_id = ubike.ubike_station_id
        WHERE ubike.ubike_distance_km <= 1
        GROUP BY ubike.case_id, ubike.district, ubike.case_name, ubike.village, uf.time_group
    ),
    combined_flow AS (
        SELECT
            COALESCE(mcf.case_id, ucf.case_id) AS case_id,
            COALESCE(mcf.district, ucf.district) AS district,
            COALESCE(mcf.case_name, ucf.case_name) AS case_name,
            COALESCE(mcf.village, ucf.village) AS village,
            mcf.mrt_station_name,
            COALESCE(mcf.time_group, ucf.time_group) AS time_group,
            COALESCE(mcf.total_mrt_flow, 0) + COALESCE(ucf.total_ubike_flow, 0) AS avg_total_flow
        FROM mrt_case_flow mcf
        FULL JOIN ubike_case_flow ucf 
            ON mcf.case_id = ucf.case_id AND mcf.time_group = ucf.time_group
    ),
    business_area_info AS (
        SELECT 
            ns.case_id,
            mba.name AS business_area_name,
            mba.tag AS business_area_tag
        FROM mrt_distances ns
        JOIN MRT_Business_Area mba ON ns.mrt_station_id = mba.station_id
        WHERE ns.mrt_distance_km <= 1
        GROUP BY ns.case_id, mba.name, mba.tag
    ),
    business_area_flow AS (
        SELECT
            bai.business_area_name,
            SUM(cf.avg_total_flow) AS total_flow
        FROM combined_flow cf
        JOIN business_area_info bai ON cf.case_id = bai.case_id
        GROUP BY bai.business_area_name
    ),
    business_area_ranks AS (
        SELECT
            business_area_name,
            total_flow,
            NTILE(10) OVER (ORDER BY total_flow) AS flow_rank -- 分成10個分位數
        FROM business_area_flow
    )
    SELECT 
        cf.case_id,
        cf.district AS district,
        cf.village AS village,
        bai.business_area_name AS business_area_name,
        cf.mrt_station_name AS mrt_station,
        cf.time_group AS time_period,
        cf.avg_total_flow AS flow,
        bar.flow_rank AS flow_rank
    FROM combined_flow cf
    LEFT JOIN business_area_info bai ON cf.case_id = bai.case_id
    LEFT JOIN business_area_ranks bar ON bai.business_area_name = bar.business_area_name
    {where_clause}
    ORDER BY cf.district, cf.village, cf.case_name, bai.business_area_name, cf.mrt_station_name, cf.time_group ASC;
    """)

    df = res.df()
    return df

# 範例呼叫：過濾人流為100及時段為10的紀錄
# get_organization_flow_data(time_period=10)


# ## 插入房東資料

# In[105]:


def insert_representative(phone, name, is_agent=True):
    # 檢查是否已存在
    existing = con.sql(f"""--sql
    SELECT *
    FROM Representative 
    WHERE phone = '{phone}'
    """).df()

    # 如果不存在，則插入新記錄
    if existing.empty:
        con.sql(f"""--sql
        INSERT INTO Representative (phone, name, is_agent)
        VALUES ('{phone}', '{name}', {is_agent})
        """)
        return f"成功新增房東資料 : {phone}"
    else:
        return f"房東資料已存在"
    
# 範例
insert_representative('0912345678', 'test')


# ## 插入Shop_Rental_listing

# In[147]:


def insert_shop_rental_listing(case_name, address, longitude, latitude, district, village, monthly_rent, deposit, area_ping, shop_floor,
                               total_floor, phone, is_available=True):
    existing = con.sql(f"""--sql
        SELECT *
        FROM Shop_Rental_Listing 
        WHERE case_name = '{case_name}' 
            AND address = '{address}' 
            AND longitude = '{longitude}' 
            AND latitude = '{latitude}' 
            AND district = '{district}' 
            AND village = '{village}' 
            AND monthly_rent = '{monthly_rent}' 
            AND deposit = '{deposit}' 
            AND shop_floor = '{shop_floor}' 
            AND total_floor = '{total_floor}' 
            AND phone = '{phone}'
    """).df()
    if existing.empty:
        con.sql(f"""--sql
        INSERT INTO Shop_Rental_Listing (
            case_id, case_name, address, longitude, latitude, district,
            village, monthly_rent, deposit, area_ping, shop_floor,
            total_floor, phone, is_available
        )
        VALUES (
            nextval('id_sequence'), '{case_name}', '{address}', {longitude}, {latitude},
            '{district}', '{village}', {monthly_rent}, {deposit}, {area_ping},
            {shop_floor}, {total_floor}, '{phone}', {is_available}
        )
        """)
        return f"成功新增一筆出租資訊"
    else:
        return f"此筆出租資訊已存在"

# 範例
insert_shop_rental_listing('test_case2', 'address', 0, 0, 'district', 'village', 0, 0, 0, '0', 0, '09')


# In[161]:


con.sql("""--sql
    select *
    from Shop_Rental_Listing
    --where case_name = 'test_case'
""")


# ## 更新狀態為已出租

# In[164]:


def mark_as_rented(case_name, address, phone):
    result = con.sql(f"""--sql
    UPDATE Shop_Rental_Listing
    SET is_available = FALSE
    WHERE case_name = '{case_name}' AND address = '{address}'AND phone = '{phone}';
""")  
    
    return f"成功將出租資訊 `{case_name}` 標記為已出租"

mark_as_rented('test_case', 'address', '09')


# In[ ]:




