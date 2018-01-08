import utils.tools as tools
import time

url = 'http://mp.weixin.qq.com/wxagame/wxagame_settlement'

body = {
    "base_req":{
        "session_id":"7Aa5F4iftQ+xop+zxsDuLZo0Q6a5yz24LxoKU3j7q1OucBKmUMMABEDujJ4ATBJK3cby9HL0rt7aaATVPYTrQIp7zlFIJMWHfhMqOqMxj+a5t0YCcJzjoy/sso86rlkYglHZk/mXqipWS9XcA8/VGw==",
        "fast":1,
        "client_info":{
            "platform":"ios",
            "model":"iPhone 7 Plus<iPhone9,2>",
            "system":"iOS 11.2.1"
        }
    },
    "report_list":[
        {
            "ts":int(time.time()),
            "type":2,
            "score":76,
            "best_score":77,
            "break_record":1,
            "duration":100,
            "times":76
        }
    ]
}

headers = {
    "Referer": "https://servicewechat.com/wx7c8d593b2c3a7703/6/page-frame.html",
    "Connection": "keep-alive",
    "Host": "mp.weixin.qq.com",
    "Content-Length": str(len(str(body))),
    "Content-Type": "application/json",
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153 MicroMessenger/6.6.1 NetType/WIFI Language/zh_CN",
    "Accept-Encoding": "br, gzip, deflate",
    "Accept-Language": "zh-cn"
}

print(body)

html = tools.get_html_by_requests(url, headers = headers, data = body)
print(html)