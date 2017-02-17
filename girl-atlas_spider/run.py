#coding:utf-8
'''
运行此爬虫可以得到girl-atlas的妹子图
'''
from multiprocessing import Process, Queue, Pool
import re, os, random
from time import sleep
from bs4 import BeautifulSoup


seed_url = 'https://www.girl-atlas.com'
headers = {'user-agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0"}
imgheaders = {'Referer': 'https://www.girl-atlas.com/album/58a5dd2c92d3027f3583729b', 
              'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0'}
def get_html(url):
    """通过get方式获得页面
    """
    import urllib2
    req=urllib2.Request(url, headers=headers)#req表示向服务器发送请求#
    response=urllib2.urlopen(req)#response表示通过调用urlopen并传入req返回响应response#
    html=response.read()#用read解析获得的HTML文件#
    return html

def info_analysis(info):
    url = seed_url+info.get('href')
    try:
        content = info.string.strip()
    except:
        content = "other"
    try:
        pattern = re.compile("\[[^\]]+]")
        directory = str(pattern.search(content).group())
        directory = directory[1:len(directory)-1]
    except:
        directory = "other"
    directory = os.path.join("data", "%s" % (directory)).decode()
    filename = os.path.join(directory, "%s" % (content)).decode()
    return (url,directory,filename)
    


def download_url_img(img):
    url = img[0]
    seed_filename = img[2]
    sleep(random.uniform(1,3)) #随机睡眠时间
    imgheaders['Referer'] = url
    html = str(get_html(url))
    soup = BeautifulSoup(html).find("ul",{"class":"slideview"})
    soup_list = soup.findAll("img")
    imgs = []
    for i in range(len(soup_list)):
        filename = os.path.join(seed_filename, "%s.jpg" % (i)).decode()
        img = (soup_list[i].get("delay"),seed_filename,filename)
        imgs.append(img)
    # 多线程下载图片
    download(imgs, processes=5)

def setup_download_dir(directory):
    """ 设置文件夹，文件夹名为传入的 directory 参数，若不存在会自动创建 """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            pass
    return True

def get_img(url):
    import urllib2
    req=urllib2.Request(url, headers=imgheaders)#req表示向服务器发送请求#
    response=urllib2.urlopen(req)#response表示通过调用urlopen并传入req返回响应response
    return response

def download_one(img):
    """ 下载一张图片 """
    url, directory, filepath = img
    # 如果文件已经存在，放弃下载
    if os.path.exists(filepath):
        print('exists:', filepath)
        return
    setup_download_dir(directory)
    resp = get_img(url)
    with open(filepath, 'wb') as f:
        f.write(resp.read())
        print "download img success!"
        

def download(imgs, processes=10):
    """ 并发下载所有图片 """
    pool = Pool(processes)
    for img in imgs:
        pool.apply_async(download_one, (img, ))
    pool.close()
    pool.join()
    print  u'下载完毕'

def start():
    page = 1
    while True:
        sleep(random.uniform(2,5)) #随机睡眠时间
        url = seed_url+'?p='+str(page)
        print "Downloading:"+url
        html = str(get_html(url))
        if html is None: break 
        soup = BeautifulSoup(html).find("div",{"class":"main col-md-9"})
        if soup is None: break 
        soup_list = soup.findAll("div",{"class":"album-item row"})
        for i in soup_list:
            info = i.find("div",{"class","col-md-11 col-sm-11"}).find('a')
            picture_info = info_analysis(info)
            download_url_img(picture_info)
        page+=1
        
        
if __name__ == "__main__":
    start()
