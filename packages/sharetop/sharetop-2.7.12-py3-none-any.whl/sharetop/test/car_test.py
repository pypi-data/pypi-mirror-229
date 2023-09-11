from sharetop.core.car.car_detail import get_car_sales


# token = "9ada862fa17ce574"
#
# d = get_car_sales(token, car_type='suv', pub_date='202302', is_explain=True)
#
# print(d)

import requests
import json

url = "https://fundgz.1234567.com.cn/js/502003.js"

r = requests.get(url)

data = r.text

deal_data = data.replace("jsonpgz(", "").replace(");", "")

data_json = json.loads(deal_data)

print(data_json)