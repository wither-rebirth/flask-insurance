import random
import time
#获取今天的字符串


today = time.strftime("%Y%m%d",time.localtime(time.time()))
charset_word = "ABCDEFGHIGKLMNOPQRSTUVWXYZ"
charset_num = "012345678901234567890123456789"
result = random.sample(charset_word, 4)
result_1 = random.sample(charset_num, 6)
result_2 = random.sample(charset_word, 1)
result_3 = random.sample(charset_num, 21)
crime_id = "".join(result) + today + "".join(result_1)
insurance_id = "".join(result_2) + "".join(result_3)

#result_list_crime = random.sample(charset_word, 4) + today + random.sample(charset_num, 6)
print(crime_id)
print(insurance_id)