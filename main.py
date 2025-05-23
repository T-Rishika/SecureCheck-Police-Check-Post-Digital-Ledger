import streamlit as st
import pandas as pd
import pymysql
import mysql.connector as mysql

#Database Conection
def create_connection():
    try:
        connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Tula@0987654",
        database="TrafficStops",
        #auth_plugin='mysql_native_password'
        )
        return connection
    except Exception as e:
            st.error(f"Database Connection error: {e}")
            return None
    
#fetch data from Database
def fetch_data(query):
     connection= create_connection()
     if connection:
          try:
               with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    df = pd.DataFrame(result)
                    return df
          finally:
               connection.close()
     else:
        return pd.DataFrame()
     

#streamlit UI
st.set_page_config(page_title="SecureCheck Police Dashboard", layout="wide")

st.title("SecureCheck: Police Check Post Digital Ledger")

st.markdown("real time monitoring and insights for law enforcement")

file_path=r"C:\Users\Keerthana\Desktop\SecureCheckProject\traffic_stops - traffic_stops_with_vehicle_number.csv"
df=pd.read_csv(file_path)
st.dataframe(df)    

st.header("Advanced insights !!")

st.subheader("🚗 Vehicle-Based Analysis")
selected_query = st.selectbox("🚗 Vehicle-Based Analysis",["Top 10 vehicles involved in Drug-related stop",
                                                           "Most frequently searched vehicles"])

query_map = {
     "Top 10 vehicles involved in Drug-related stop": """SELECT COUNT(*) AS C, vehicle_number FROM check_post_logs
                                                                                              WHERE drugs_related_stop = 1 
                                                                                              GROUP BY vehicle_number 
                                                                                              order by C DESC
                                                                                              LIMIT 10;""",
     "Most frequently searched vehicles": """SELECT COUNT(*) AS count, vehicle_number FROM check_post_logs 
                                                                                      WHERE search_conducted = 1 
                                                                                      GROUP BY vehicle_number 
                                                                                      ORDER BY count DESC LIMIT 10;"""
}
if st.button("run query", key='Vehicle'):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)
     else:
          st.warning("no results")

st.subheader("🧍 Demographic-Based")
selected_query = st.selectbox("🧍 Demographic-Based",["Driver age group with highest arrest rate",
                                                      "Gender distribution of drivers stopped in each country",
                                                      "Highest search rate( race and gender combination)"])
query_map = {
     "Driver age group with highest arrest rate": """SELECT age_group, ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2 ) AS arrest_rate
                                                                           FROM (
                                                                                SELECT CASE 
                                                                                WHEN driver_age BETWEEN 18 AND 20 THEN '18-20'
                                                                                WHEN driver_age BETWEEN 21 AND 30 THEN '21-30'
                                                                                WHEN driver_age BETWEEN 31 AND 40 THEN '31-40'
                                                                                WHEN driver_age BETWEEN 41 AND 50 THEN '41-50'
                                                                                WHEN driver_age BETWEEN 51 AND 60 THEN '51-60'
                                                                                WHEN driver_age BETWEEN 61 AND 70 THEN '61-70'
                                                                                ELSE '70+'
                                                                                END AS age_group,is_arrested FROM check_post_logs
                                                                                ) AS age_grouped_data
                                                                                GROUP BY age_group
                                                                                ORDER BY arrest_rate DESC;""",
     "Gender distribution of drivers stopped in each country": """select country_name,driver_gender, COUNT(*) as count FROM check_post_logs
                                                                                                                       group by country_name, driver_gender;""",
     "Highest search rate( race and gender combination)":"""SELECT driver_race AS driver_race ,driver_gender AS driver_gender, 
                                                                      ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2 ) AS search_rate 
                                                                      FROM check_post_logs
                                                                      GROUP BY driver_race,driver_gender 
                                                                      ORDER BY search_rate  desc
                                                                      LIMIT 1;
                                                            """
}
if st.button("run query", key='Demographic'):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)
     else:
          st.warning("no results")

st.subheader("🕒 Time & Duration Based")
selected_query = st.selectbox("🕒 Time & Duration Based",["Time of day with the most traffic stops",
                                                           "Are stops during the night more likely to lead to arrests?"])
query_map = {
     "Time of day with the most traffic stops": """SELECT COUNT(*), HOUR(stop_time) FROM check_post_logs
                                                                                    group by HOUR(stop_time)
                                                                                    ORDER BY COUNT(*) DESC;""",
     "Are stops during the night more likely to lead to arrests?":"""SELECT time, ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2 ) as arrests
                                                                      from(
                                                                           SELECT CASE 
                                                                                WHEN HOUR(stop_time) <5 AND HOUR(stop_time)>22 THEN 'night_time'
                                                                                WHEN HOUR(stop_time) > 5 AND HOUR(stop_time)<=22  THEN 'day_time'
                                                                                END AS time,is_arrested FROM check_post_logs
                                                                           ) AS time_grouped_data
                                                                           GROUP BY time
                                                                           ORDER BY arrests DESC
                                                                 """
}

if st.button("run query", key='Time'):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)
     else:
          st.warning("no results")


st.subheader("⚖️ Violation-Based")
selected_query = st.selectbox("⚖️ Violation-Based",["Violations most associated with searches or arrests",
                                                    "Violations most common among younger drivers(<25 years)",
                                                    "violation that rarely results in search or arrest"])
query_map = {
     "Violations most associated with searches or arrests": """SELECT violation,COUNT(*) AS count FROM check_post_logs
                                                                                          WHERE search_conducted = 1 OR is_arrested = 1
                                                                                          GROUP BY violation
                                                                                          order by count desc;
                                                            """,
     "Violations most common among younger drivers(<25 years)": """SELECT violation,COUNT(*) AS count FROM check_post_logs
                                                                                               WHERE driver_age >25
                                                                                               GROUP BY violation
                                                                                               order by count desc;""",
     "violation that rarely results in search or arrest": """SELECT violation,COUNT(*) AS count FROM check_post_logs
                                                                                          WHERE search_conducted = 0 AND is_arrested = 0
                                                                                          GROUP BY violation
                                                                                          order by count ASC
                                                                                          LIMIT 1;""",
}
if st.button("run query", key='Violation'):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)
     else:
          st.warning("no results")

st.subheader("🌍 Location-Based")
selected_query = st.selectbox("🌍 Location-Based",["The highest rate of drug-related stops (Country)",
                                                           "The arrest rate by country and violation",
                                                           "Country with the most stops with search conducted"])


query_map = {
     "The highest rate of drug-related stops (Country)": """SELECT country_name,COUNT(*) AS count FROM check_post_logs
                                                                                          WHERE drugs_related_stop = 1
                                                                                          GROUP BY country_name
                                                                                          order by count DESC
                                                                                          LIMIT 1;""",
     "The arrest rate by country and violation": """SELECT country_name,violation,
                                                           ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2 ) AS arrest_rate 
                                                           FROM check_post_logs
                                                           GROUP BY country_name,violation
                                                           order by arrest_rate DESC;""",
     "Country with the most stops with search conducted":"""SELECT country_name,
                                                            ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END)*100/COUNT(*),2) as percent_search_conducted 
                                                            FROM check_post_logs
                                                            GROUP BY country_name
                                                            order by percent_search_conducted DESC
                                                            LIMIT 1;"""
}

if st.button("run query", key='Location'):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)
     else:
          st.warning("no results")


st.subheader("Add New Police Log and Predict Outcome and Violation")
with st.form("Add New Police Log and Predict Outcome and Violation"):
     date = st.date_input("Date")
     time = st.time_input("Time")
     country_name = st.selectbox("Country",['Canada','India','USA'])
     driver_gender = st.selectbox("Gender of Driver",['M','F'])
     driver_age = st.number_input("Driver Age", min_value=18, max_value=80)
     driver_race = st.selectbox("Driver Race",['Asian','Black','Hispanic','White','Other'])
     search_conducted = st.selectbox("Was a search conducted?",[0,1])
     search_type = st.selectbox("Search Tye",['Vehicle Search','Frisk','None'])
     drug_related = st.selectbox("Was it Drug Related?",[0,1])
     stop_duration = st.selectbox("Stop Duration",['0-15 Min','16-30 Min','30+ Min'])
     vehicle_number = st.text_input("vehicle Number")

     submit = st.form_submit_button("submit")
filtered_data = pd.DataFrame()
if submit:
     filtered_data = df[
                         (df['driver_gender'] == driver_gender) &
                         (df['driver_age'] == driver_age) &
                         (df['search_conducted'] == int(search_conducted)) &
                         (df['stop_duration'] == stop_duration) &
                         (df['drugs_related_stop'] == drug_related) &
                         (df['vehicle_number'] == vehicle_number)
     ]
     
if not filtered_data.empty:
     predicted_outcome1 = filtered_data['stop_outcome'].mode()[0]
     predicted_outcome2 = filtered_data['violation'].mode()[0]
     
else:
     predicted_outcome1 = 'warning'
     predicted_outcome2 = 'speeding'
def search(search_conducted):
     if search_conducted == 1:
          return " "
     else:
          return "No"
def drug(drug_related):
     if drug_related == 1:
          return " "
     else:
          return "Not"
st.write("A",driver_age,"-Year-old",driver_gender,"driver was stopped for ",predicted_outcome2,"at",time,".",search(search_conducted),
         "Search was conducted,and he received a",predicted_outcome1,"The stop lasted",stop_duration,"and was",drug(drug_related),"drug related")


st.subheader("Complex")
selected_query = st.selectbox("Complex",["Yearly Breakdown of Stops and Arrests by Country",
                                         "Driver Violation Trends Based on Age and Race",
                                         "Time Period Analysis of Stops",
                                         "Violations with High Search and Arrest Rates",
                                         "Driver Demographics by Country (Age, Gender, and Race)",
                                         "Top 5 Violations with Highest Arrest Rates"])
query_map = {"Yearly Breakdown of Stops and Arrests by Country": """Select country_name, count(*) as Toatal_stops,
                                                                                          sum(CASE WHEN stop_outcome ='Arrest' THEN 1 ELSE 0 END) AS Total_Arrests, 
                                                                                          YEAR(stop_date) as _Year 
                                                                                          from check_post_logs
                                                                                          group by country_name,_Year""",
               "Driver Violation Trends Based on Age and Race":"""SELECT violation,age_group,driver_race, count(*) as count from
                                                                                     (SELECT violation,driver_race, CASE 
                                                                                     WHEN driver_age BETWEEN 18 AND 20 THEN '18-20'
                                                                                     WHEN driver_age BETWEEN 21 AND 30 THEN '21-30'
                                                                                     WHEN driver_age BETWEEN 31 AND 40 THEN '31-40'
                                                                                     WHEN driver_age BETWEEN 41 AND 50 THEN '41-50'
                                                                                     WHEN driver_age BETWEEN 51 AND 60 THEN '51-60'
                                                                                     WHEN driver_age BETWEEN 61 AND 70 THEN '61-70'
                                                                                     ELSE '70+'
                                                                                     END AS age_group
                                                                                     FROM check_post_logs
                                                                                     ) AS age_grouped_data
                                                                                     group by violation,driver_race,age_group
                                                                                     order by count desc""",
               "Time Period Analysis of Stops": """Select year(stop_date) as _year, month(stop_date) as _month,
                                                                                                    hour(stop_time) as Hour_of_day,
                                                                                                    count(*) as stops from check_post_logs
                                                                                                    group by year(stop_date),
                                                                                                    month(stop_date),
                                                                                                    hour(stop_time)
                                                                                                    """,
               "Violations with High Search and Arrest Rates":""" select violation, ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END)*100/ COUNT(*), 2) AS Search_Rate, 
                                                                                    ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END)*100/ COUNT(*), 2) AS Arrest_Rate
                                                                                    from check_post_logs
                                                                                    GROUP BY violation
                                                                                    order by Search_Rate DESC,Arrest_Rate DESC""",
               "Driver Demographics by Country (Age, Gender, and Race)": """SELECT country_name,age_group,driver_race, count(*) from
                                                                                                    (SELECT country_name,driver_race, CASE 
                                                                                                         WHEN driver_age BETWEEN 18 AND 20 THEN '18-20'
                                                                                                         WHEN driver_age BETWEEN 21 AND 30 THEN '21-30'
                                                                                                         WHEN driver_age BETWEEN 31 AND 40 THEN '31-40'
                                                                                                         WHEN driver_age BETWEEN 41 AND 50 THEN '41-50'
                                                                                                         WHEN driver_age BETWEEN 51 AND 60 THEN '51-60'
                                                                                                         WHEN driver_age BETWEEN 61 AND 70 THEN '61-70'
                                                                                                         ELSE '70+'
                                                                                                         END AS age_group
                                                                                                    FROM check_post_logs
                                                                                                    ) AS age_grouped_data
                                                                                                    group by country_name,driver_race,age_group
                                                                                                    order by country_name,driver_race,age_group""",
                "Top 5 Violations with Highest Arrest Rates":"""select violation,
                                                                      ROUND(SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END)*100/ COUNT(*), 2) AS Arrest_Rate
                                                                      from check_post_logs
                                                                      GROUP BY violation
                                                                      order by Arrest_Rate DESC"""}

if st.button("run query", key='complex'):
     result = fetch_data(query_map[selected_query])
     if not result.empty:
          st.write(result)
     else:
          st.warning("no results")




