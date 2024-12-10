import duckdb
import json
from fastapi import FastAPI


"""
透過 duckdb 的 pgsql 套件連線 pgsql 資料庫，並以 duckdb 高效率的計算引擎進行 query
以下是連線到 pgsql 的相關設定，若到讀取你個人的 pgsql 請在 connection_setting.json 設定相關資料，例如資料庫名稱、密碼等
"""
with open('connection_setting.json', 'r') as f:
    settings = json.load(f)
con = duckdb.connect('')
con.sql("INSTALL postgres;LOAD postgres;")
con.sql(f"""
CREATE or replace SECRET (
    TYPE POSTGRES,
    HOST '{settings['host']}',
    PORT {settings['port']},
    DATABASE '{settings['database']}',
    USER '{settings['user']}',
    PASSWORD '{settings['password']}'
);
""")
con.sql("ATTACH '' AS pg (TYPE POSTGRES);")

"""
以下利用 FastAPI 撰寫 api 並在後續進行 server 和 client 的串接，FastAPI 提供簡單的語法糖，讓我們可以將原先寫好的 fn 進一步包裝為 api
"""
app = FastAPI()

@app.get("/organization_data")
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
            FROM pg.shop_rental_listing s
            CROSS JOIN pg.MRT_Station_Info m
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
        JOIN pg.MRT_Business_Area mba ON ns.station_id = mba.station_id -- 加入商圈數據
        {where_clause} -- 動態加入條件
        GROUP BY mba.name, mba.tag, ns.station_name, ns.district
        ORDER BY ns.district, ns.station_name; 
        """)
    json = res.df().to_dict(orient="records")
    return json

@app.get("/show_flow_data")
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
        FROM pg.Shop_Rental_Listing s
        CROSS JOIN pg.MRT_Station_Info m
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
        FROM pg.Shop_Rental_Listing s
        CROSS JOIN pg.Ubike_Station_Info u
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
        FROM pg.MRT_Flow_Record mf
        WHERE mf.date >= CURRENT_DATE - INTERVAL '2 years' AND time_period NOT BETWEEN 2 AND 5
        GROUP BY mf.station_id, mf.time_period
    ),
    ubike_flow_data AS (
        SELECT
            uf.station_id AS ubike_station_id,
            uf.time_period,
            ROUND(AVG(uf.rent_count + uf.return_count)) AS avg_ubike_flow
        FROM pg.Ubike_Station_Rental_Record uf
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
        JOIN pg.MRT_Business_Area mba ON ns.mrt_station_id = mba.station_id
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
    json = res.df().to_dict(orient='records')
    return json

@app.get("/village_data")
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
        FROM pg.Village_Info vi
        LEFT JOIN pg.Village_Population_By_Age v ON vi.district = v.district AND vi.village = v.village
        {where_clause}
    """)
    json = res.df().to_dict(orient='records')
    return json

@app.get("/competitive_data")
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
            FROM pg.Business_Operation
            {where_clause}
            GROUP BY district, village, business_type, business_sub_type
          """)
    json = res.df().to_dict(orient='records')
    return json

@app.get("/top5_subtype_data")
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
            FROM pg.Business_Operation
            {where_clause}
            GROUP BY district, village, business_type, business_sub_type
            ORDER BY shop_cnt DESC
            LIMIT 5
          """)
    json = res.df().to_dict(orient='records')
    return json

@app.get("/business_data")
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
            FROM pg.Business_Operation 
            {where_clause}
          """)
    json = res.df().to_dict(orient='records')
    return json

@app.get("/filtered_shop_rentals")
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
    FROM pg.Shop_Rental_Listing s
    LEFT JOIN pg.Representative r ON s.phone = r.phone
    
    {where_clause} -- 動態加入條件
    """
    res = con.sql(query)
    json = res.df().to_dict(orient='records')
    return json

@app.get("/organization_flow_data")
def get_organization_flow_data(rank=None, tag=None):
    filter_condition = f'qualify rank >= {rank}' if rank else ''
    res = con.sql(f"""--sql
        with business_area_info as (
            select
                distinct name, tag, description
            from pg.MRT_Business_Area
        ),
        MRT_UBIKES as (
            select mrt_id, array_agg(distinct ubike_id) as UBIKEs
            from (
                select
                    a.station_id as mrt_id,
                    b.station_id as ubike_id,
                    6371 * ACOS(
                        COS(RADIANS(a.latitude)) * COS(RADIANS(b.latitude)) *
                        COS(RADIANS(b.longitude) - RADIANS(a.longitude)) +
                        SIN(RADIANS(a.latitude)) * SIN(RADIANS(b.latitude))
                    ) AS distance_km
                from pg.MRT_Station_Info as a
                cross join pg.Ubike_Station_Info as b
                where distance_km <= 1
            )
            group by all
        ),
        MRT_avg_daily_cnt as (
            select station_id, avg(total_cnt) as avg_daily_cnt
            from (
                select
                    station_id, date, sum(entrance_count+exit_count) as total_cnt
                from pg.MRT_Flow_Record
                group by all
            )
            group by all
        ),
        UBIKE_avg_daily_cnt as (
            select station_id, avg(total_cnt) as avg_daily_cnt
            from (
                select
                    station_id, date, sum(rent_count+return_count) as total_cnt
                from pg.Ubike_Station_Rental_Record
                group by all
            )
            group by all
        ),
        business_area_mrt_avg_daily_cnt as (
            select
                name, sum(avg_daily_cnt) as mrt_avg_daily_cnt
            from pg.MRT_Business_Area as a
            inner join MRT_avg_daily_cnt as b
                using (station_id)
            group by all
        ),
        business_area_ubike_avg_daily_cnt as (
            select
                name, sum(avg_daily_cnt) as ubike_avg_daily_cnt
            from (
                select
                    name, unnest(UBIKEs) as ubike_station_id
                from pg.MRT_Business_Area as a
                inner join MRT_UBIKES as b 
                    on a.station_id = b.mrt_id
            ) as a
            inner join UBIKE_avg_daily_cnt as b
                on a.ubike_station_id = b.station_id
            group by all
        )
        select
            name, tag, description, (mrt_avg_daily_cnt+ubike_avg_daily_cnt) as avg_daily_cnt,
                ntile(10) over (order by avg_daily_cnt) AS rank
        from business_area_mrt_avg_daily_cnt as a
        left join business_area_ubike_avg_daily_cnt as b using (name)
        inner join business_area_info as c using (name)
        {filter_condition}
        order by rank
        """)


    return res.df().to_dict(orient='records')

    # df = res.df()
    # return df

@app.get("/business_area_shop_rentals")
def get_business_area_shop_rentals(business_area=None):
    filter_condition = f"where name = '{business_area}'" if business_area else ''
    res = con.sql(f"""--sql
        with case_id_station_id as (
            select
                case_id, (station_id),
                6371 * ACOS(
                    COS(RADIANS(a.latitude)) * COS(RADIANS(b.latitude)) *
                    COS(RADIANS(b.longitude) - RADIANS(a.longitude)) +
                    SIN(RADIANS(a.latitude)) * SIN(RADIANS(b.latitude))
                ) AS distance_km
            from pg.Shop_Rental_Listing as a
            cross join pg.MRT_Station_Info as b
            where distance_km <= 1
        )
        select distinct name, c.*
        from pg.MRT_Business_Area as a
        inner join case_id_station_id as b
            using (station_id)
        inner join pg.shop_rental_listing as c
            on b.case_id = c.case_id
        {filter_condition}
        order by all
        """)
    business_area_df = res.df()
    business_area_df = business_area_df.dropna()
    return business_area_df.to_dict(orient='records')

@app.get("/landlord_info")
def get_landlord_info(phone=None):
    filter_condition = f"where phone = '{phone}'" if phone else ''
    res = con.sql(f"from pg.Shop_rental_listing {filter_condition}")
    landlord_df = res.df()
    landlord_df = landlord_df.dropna()
    return landlord_df.to_dict(orient='records')

@app.put("/update_rental")
def update_rental(case_id=None, monthly_rent=None):
    con.sql(f"UPDATE pg.shop_rental_listing SET monthly_rent = {monthly_rent} WHERE case_id = {case_id}")
    
