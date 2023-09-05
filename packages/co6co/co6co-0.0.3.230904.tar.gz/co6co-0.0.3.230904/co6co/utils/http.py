import requests
 

def download(url,timeout:int|tuple|None=None,proxy:str=None,header_dict:dict=None)->bytes:
    return get(requests.utils.requote_uri(url),timeout,proxy,header_dict)
    
def get(url,timeout:int|tuple|None=None,proxy:str=None,header_dict:dict=None)->requests.Response:
    proxies={}
    if proxy!=None:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }
    headers={
        #"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        #"Accept-Encoding":"gzip, deflate, br",
        #"Accept-Language":"zh-CN,zh;q=0.9",
        #"Cache-Control":"no-cache",
        #"Pragma":"no-cache",
        #"Sec-Ch-Ua":'"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        #"Sec-Ch-Ua-Mobile":"?0",
        #"Sec-Ch-Ua-Platform":'"Windows"',
        #"Sec-Fetch-Dest":"document",
        #"Sec-Fetch-Mode":"navigate",
        #"Sec-Fetch-Site":"none",
        #"Sec-Fetch-User":"?1",
        #"Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        #'User-Agent':'BaiduSipder'
    }
    if header_dict !=None:
        header_dict.update(headers)
        headers=header_dict
    if timeout == None:timeout=(5, 15)
    resp = requests.get(url,headers=headers, timeout=timeout,allow_redirects=True,proxies=proxies)
    if len(resp.history) > 0: # 存在302 跳转
        location_url = resp.history[len(resp.history) - 1].headers.get('Location')
        resp=requests.get(location_url,headers=headers,timeout=(15, 30),proxies=proxies)
        return resp
    return resp