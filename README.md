# Flask-SimilarKLine

## index.py(https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/index.py)
- **`query_page()`**:
  + 查询页面视图函数
  
- **`add_charts()`**：
  + 接受前端发送的Ajax请求，读取请求参数，并对参数进行验证。
  + 根据接收到的参数，到数据库进行数据查询，计算结果。
  + 根据计算结果，使用开源库`pyecharts`绘制K线图。
  + 将已计算的结果进行缓存，下次查询相同的数据时，可立即返回结果。
  
- **`show_progress()`**:
  + 进度条加载
  
- **`plot_k_line()`**:
  + 使用`pyecharts`绘制K线图
  
- **`form_validation()`**：
  + 对接收的表单进行验证
  
## Similarkviolent.py(https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/Similarkviolent.py)
  使用动态规划优化的基于皮尔逊系数寻找相似股票走势
  
## ReadData.py（https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/ReadData.py）
  查询数据库相关操作
  
## config.py(https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/config.py)
  数据库配置文件
  
## 页面显示结果
- 下图为查询页面：
<div align=center><img src="https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/result_img/start_page.png" width="700" height="350"/></div>
<div align=center><img src="https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/result_img/select-page.png" width="700" height="350"/></div>
- 下图为查询过程中页面
  <div align=center><img src="https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/result_img/proress-page.png" width="700" height="350"/></div>
- 下图为查询结果显示页面
 <div align=center><img src="https://github.com/ChengJiaGen/Flask-SimilarKLine/blob/master/result_img/result-page.png" width="700" height="350"/></div>


  
