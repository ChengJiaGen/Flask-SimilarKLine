from flask import Flask, render_template,request,jsonify,json,redirect,url_for
from Similarkviolent import CompareSimilarKDynamic
from pyecharts import Kline,Page
from ReadData import ReadData
import os
import re
import config


app = Flask(__name__)
#app.config.from_object(config)


REMOTE_HOST = "https://pyecharts.github.io/assets/js"

progress_dict = {}



@app.route("/")
def query_page():
    read_data = ReadData()
    ts_code_name_list = read_data.mysql_read_ts_code_name()
    page = Page()

    return render_template("index.html",ts_code_list = ts_code_name_list,host=REMOTE_HOST,script_list = page.get_js_dependencies())

@app.route('/charts',methods=["POST"])
def add_charts():
    ajax_data = request.values.to_dict()
    source_ts_code = ajax_data.get("ts_name")
    inquire_days = ajax_data.get("inquire_days")
    result_num = ajax_data.get("result_num")
    uuid = ajax_data.get("uuid")
    global progress_dict
    progress_uuid = uuid
    progress_dict[progress_uuid] = 0
    #对前端传入的值进行过滤
    form_data = {"source_ts_code":source_ts_code,"inquire_days":inquire_days,"result_num":result_num}
    validation_result = form_validation(form_data)
    if validation_result["result"] == False:
        return jsonify({"status": "error", "status_code": 1003})
    #对后台接收的数据进行处理
    day_num = int(inquire_days)
    #定义pyechart的page
    page = Page()
    # 需要被对比的股票的列表
    read_data = ReadData()
    ts_code_name_list = read_data.mysql_read_ts_code_name()
    #此处可设置对比股票的数量
    ts_code_list = [ts_code[0] for ts_code in ts_code_name_list][:50]
    #定义缓存的文件路径
    save_folder_path = "cache_data/{0}".format(source_ts_code)
    save_file_path = save_folder_path + "/" + source_ts_code + "-" + str(inquire_days) + ".json"
    # 开始绘制选中股票的K线图
    source_data = read_data.mysql_read_data(source_ts_code)
    if len(source_data) == 0:
        return jsonify({"status": "error", "status_code": 1001})
    elif len(source_data) < day_num:
        return jsonify({"status": "error", "status_code": 1002})
    else:
        source_data = read_data.mysql_read_data(source_ts_code).iloc[-day_num:]
        #查询股票的名称
        source_ts_name = [ code_name[1] for code_name in  ts_code_name_list if source_ts_code in code_name ][0]
        source_plot_left_title = "源股票K线图"
        source_plot_legend_title = "日K  股票代码：{0}({1})".format(source_ts_code,source_ts_name)
        kline = plot_k_line(source_data, source_plot_left_title, source_plot_legend_title)
        page.add(kline)
        # 判断选择的内容是否有缓存
        if os.path.exists(save_file_path):
            progress_dict[progress_uuid] = 100
            with open(save_file_path,"r") as load_f:
                reverse_result = json.load(load_f)
        else:
            #读取选中股票的数据
            #开始进行计算
            results_dict = {}
            for index,ts_code in enumerate(ts_code_list):
                compare_data = read_data.mysql_read_data(ts_code).iloc[:-day_num]
                if len(compare_data) < day_num:
                    continue
                else:
                    compare = CompareSimilarKDynamic(source_data, compare_data, day_num)
                    result = compare.compare_dynamic()
                    results_dict[ts_code] = result
                    progress_dict[progress_uuid] =round ( (index + 1) / len(ts_code_list) * 100 ,2)
            reverse_result = sorted(results_dict.items(), key=lambda item: item[1]["pearson_index"], reverse=True)
            #将计算结果缓存
            save_folder = os.path.exists(save_folder_path)
            if not save_folder:
                os.makedirs(save_folder_path)
            with open(save_file_path,"w") as f:
                json.dump(reverse_result[:10],f)
        #根据计算结果进行画图
        for ts_result in reverse_result[:int(result_num)]:
            result_data = read_data.mysql_read_date(ts_result[0],ts_result[1]["start_time"],ts_result[1]["end_time"])
            result_ts_name = [code_name[1] for code_name in ts_code_name_list if ts_result[0] in code_name][0]
            result_plot_left_title = "相似度-皮尔逊系数为：{}".format(round(ts_result[1]["pearson_index"],3))
            result_plot_legend_title = "日K  股票代码：{0}({1})".format(ts_result[0],result_ts_name)
            kline = plot_k_line(result_data, result_plot_left_title, result_plot_legend_title)
            page.add(kline)
        page.render()
        chart_page_html = render_template("charts.html",myechart=page.render_embed(),host=REMOTE_HOST,script_list = page.get_js_dependencies())
        # 将进度条的进度清0
        progress_dict[progress_uuid] = 0
        return jsonify({ "status":"success","status_code":2001,"result":chart_page_html})

@app.route("/progress/<string:uuid>")
def show_progress(uuid):
    try:
        return jsonify({"num":progress_dict[uuid]})
    except KeyError:
        return redirect(url_for("query_page"))


def deal_date(str_date):
    str_list = list(str_date)
    str_list.insert(4, "/")
    str_list.insert(-2, "/")
    str_date = "".join(str_list)
    return str_date

def plot_k_line(data,left_title,legend_title,):
    data_day_list = data["trade_date"].tolist()
    data_price_list = data.loc[:, ["open", "close", "low", "high"]].values.tolist()
    data_date_list = list(map(deal_date, data_day_list))
    kline = Kline(left_title)
    kline.add(legend_title, data_date_list, data_price_list,xaxis_rotate=45)
    kline.render()
    return kline

def form_validation(form_data):
    validation_result = {
        "result" : True
    }
    source_ts_name_len = len(form_data["source_ts_code"])
    source_ts_name_re = "\\w{6}.\\w{2}"
    if source_ts_name_len == 9:
        if  not re.match(source_ts_name_re,form_data["source_ts_code"]):
            validation_result["result"] = False
    else:
        validation_result["result"] = False
    try:
        inquire_days = int(form_data["inquire_days"])
        result_num = int(form_data["result_num"])
        if not (inquire_days == 30 or inquire_days == 45 or inquire_days == 60):
            validation_result["result"] = False
        if not (result_num == 1 or result_num == 5 or result_num == 10):
            validation_result["result"] = False
        return validation_result
    except Exception as e:
        validation_result["result"] = False
        return validation_result


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
