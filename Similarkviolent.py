from math import sqrt

#动态规划算法
class CompareSimilarKDynamic():
    def __init__(self,source_data,compare_data,compare_count):
        self.source_data = source_data.loc[:,["trade_date","open","close"]].dropna(axis=0,how="any").to_dict("records")
        self.compare_data = compare_data.loc[:,["trade_date","open","close"]].dropna(axis=0,how="any").to_dict("records")
        self.compare_count = compare_count

    #计算公式∑X、∑Y、∑X^2、∑Y^2
    def calc_atom(self,source,data,field):
        source_square_add = 0
        source_add = 0
        data_square_add = 0
        data_add = 0
        for index, value in enumerate(source):
            source_add += source[index][field]
            data_add += data[index][field]
            source_square_add += source[index][field] * source[index][field]
            data_square_add += data[index][field] * data[index][field]
        return [source_add,data_add,source_square_add,data_square_add,len(source)]

    # 计算公式∑XY
    def calc_mul_add(self, source, data, field):
        mul_add = 0
        for index, value in enumerate(source):
            mul_add += source[index][field] * data[index][field]
        return mul_add

    #计算皮尔逊系数(∑XY-∑X*∑Y/N)/(Math.sqrt((∑X^2-(∑X)^2/N)*((∑Y^2-(∑Y)^2/N)))
    def calc_pearson(self,mul,data):
        return (mul-data[0]*data[1]/data[4])/(sqrt((data[2]-data[0]*data[0]/data[4]) * (data[3]-data[1]*data[1]/data[4])))

    #动态规划计算皮尔逊系数，使之前计算过的不再进行计算
    def dynamic(self,atom,field,index):
        value = self.compare_data[index + self.compare_count]
        atom[1] = atom[1] - self.compare_data[index][field] + value[field]
        atom[3] = atom[3] - (self.compare_data[index][field] * self.compare_data[index][field]) + (value[field] * value[field])
        return atom

    def compare_dynamic(self):
        temp_compare = self.compare_data[0:self.compare_count]
        #分别计算开盘价和收盘价的∑XY
        mul_open = self.calc_mul_add(self.source_data,temp_compare,"open")
        mul_close = self.calc_mul_add(self.source_data,temp_compare,"close")
        #分别计算开盘价和收盘价的计算公式∑X、∑Y、∑X^2、∑Y^2
        atom_open = self.calc_atom(self.source_data,temp_compare,"open")
        atom_close = self.calc_atom(self.source_data, temp_compare, "close")
        #第一组数据的皮尔逊系数，开盘价和收盘价分别计算并各占0.5
        similar_value = 0.5 * self.calc_pearson(mul_open,atom_open) + 0.5 * self.calc_pearson(mul_close,atom_close)
        result = {
            "start_time" : temp_compare[0]["trade_date"],
            "end_time" : temp_compare[-1]["trade_date"],
            "pearson_index" : similar_value
        }
        #开始循环第一组数据后面的数据
        for index,value in enumerate(self.compare_data[1:]):
            if index <= len(self.compare_data[1:]) - self.compare_count:
                temp_compare = self.compare_data[1:][index:index+self.compare_count]
                mul_open = self.calc_mul_add(self.source_data, temp_compare, "open")
                mul_close = self.calc_mul_add(self.source_data, temp_compare, "close")
                atom_open = self.dynamic(atom_open,"open",index)
                atom_close = self.dynamic(atom_close,"close",index)
                similar_value = 0.5 * self.calc_pearson(mul_open,atom_open) + 0.5 * self.calc_pearson(mul_close,atom_close)
                if (result["pearson_index"] < similar_value):
                    result = {
                        "start_time": temp_compare[0]["trade_date"],
                        "end_time": temp_compare[-1]["trade_date"],
                        "pearson_index": similar_value
                    }
        return result


