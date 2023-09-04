# -*- coding: utf-8 -*-

from investlife import *
set_token(token = 'abc')
# data = get_stock_list(listed_state = "1")
data = ipo_list(start_date = "2023-07-28")
print(data.head())
