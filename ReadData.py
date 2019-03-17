import pymysql
import pandas as pd
from config import USERNAME,LOCALHOST,PASSWORD,DATABASE


class ReadData():
    def __init__(self):
        self.conn = pymysql.connect(LOCALHOST,USERNAME,PASSWORD,DATABASE)
        self.cursor = self.conn.cursor()

    def mysql_read_data(self,ts_code):
        self.ts_code = ts_code
        self.sql = "SELECT trade_date,open,close,low,high FROM tb_stock_trade_info WHERE ts_code='{}' ".format(self.ts_code)
        pd_read = pd.read_sql(self.sql,self.conn)
        data = pd.DataFrame(pd_read)
        return data

    def mysql_read_ts_code(self):
        self.sql = "SELECT ts_code FROM db_stock_pro.tb_stock_trade_info group by ts_code"
        try:
            self.cursor.execute(self.sql)
            results_tuple = self.cursor.fetchall()
            self.conn.commit()
            ts_code_list = [result[0] for result in results_tuple]
            return ts_code_list
        except Exception as ee:
            print('mysql_read_ts_code--- Error')

    def mysql_read_date(self,ts_code,start_time,end_time):
        self.sql = "SELECT trade_date,open,close,low,high FROM db_stock_pro.tb_stock_trade_info WHERE ts_code='{0}' " \
                   "and trade_date between '{1}' and '{2}'".format(ts_code,start_time,end_time)
        pd_read = pd.read_sql(self.sql, self.conn)
        data = pd.DataFrame(pd_read)
        return data

    def mysql_read_ts_code_name(self):
        sql = "select ts_code,name from tb_stocks"
        self.cursor.execute(sql)
        ts_code_name_tuple = self.cursor.fetchall()
        self.conn.commit()
        ts_code_name_list = list(ts_code_name_tuple)
        return ts_code_name_list



