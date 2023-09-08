import json
from urllib import request


def fxCode(code='002063', name='远光', length=10):
    url = '''https://sp1.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=5353&all=1&pointType=string&count=%(length)s&group=quotation_kline_ab&ktype=1&query=%(code)s&code=%(code)s&ktype=1&word=%(code)s&name=%%E5%%90%%8C%%E8%%8A%%B1%%E9%%A1%%BA&format=json&from_mid=1&oe=utf-8&dsp=pc&tn=wisexmlnew&need_di=1&all=1&eprop=dayK&euri=undefined&request_type=sync&stock_type=ab&sid=34948_35106_31253_35048_35065_34584_34505_34917_34812_26350_34973_34868_35113_34991''' % {
        'code': code, 'length': length}
    req = request.Request(url)  # 构造请求
    response = request.urlopen(req).read().decode()  # 获取响应
    jsondata = json.loads(response)
    jsondata = jsondata['Result'][0]['DisplayData']['resultData']['tplData']['result']['p']
    jsonlist = jsondata.split(';')
    datalist = []
    for jsonitem in jsonlist:
        jsonitem2 = jsonitem.split(',')
        datalist.append([code, name] + jsonitem2)
    print(datalist)
    return datalist
    # header = ['代码', '股票', '日期', '开盘', '最高', '最低', '收盘', '成交量', 'MA5', 'MA10', 'MA20', '涨跌幅', '', '差额']
    # writexls('demo01.xls', '股票', header, datalist)
