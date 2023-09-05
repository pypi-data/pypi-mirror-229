from fake_useragent import UserAgent

ua = UserAgent()

AntiHeader = {
    "User-Agent": ua.chrome,
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
}
