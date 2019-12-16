# -*- coding:utf-8 -*-
# Author : ZhangPeng
# Contact ：2838215550@qq.com
# Data : 2019/11/20 16:39
from lxml import html as ht
import requests

# 禁用安全请求警告（HTTPS）
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

numToChinese = {"0": u"零", "1": u"一", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八",
                "9": u"九"}
etree = ht.etree
# 会话
sessionCenter = requests.session()
# 学号 5120176308
userName = ''
# 密码 XXXXXXXX
userPass = ''


# 获取登陆验证码
def get_captcha():
    html = sessionCenter.get("http://cas.swust.edu.cn/authserver/captcha")
    with open("captcha.png", "wb") as yzm:
        yzm.write(html.content)
        yzm.close()
    return input("请输入验证码：")


# 自动识别验证码
def auto_captcha():
    pass


# 登陆教务处并且获取课表HTML数据
def login_office():
    session = sessionCenter
    url = 'https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:DEFAULT_EVENT'
    session.get(url=url, verify=False)
    url = 'https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:courseTable'
    html = session.get(url=url, verify=False)
    return html.text


# 明文密码加密为密文
def encrypt(plaintext_text, public_modulus_hex, public_exponent_hex='10001'):
    public_modulus = int(public_modulus_hex, 16)
    public_exponent = int(public_exponent_hex, 16)
    # Beware, plaintext must be short enough to fit in a single block!
    plaintext = int(plaintext_text[::-1].encode('utf-8').hex(), 16)
    ciphertext = pow(plaintext, public_exponent, public_modulus)
    return '%X' % ciphertext  # return hex representation


# 获取后台发来的加密算法的秘钥和加密模式
def get_key():
    reponse = sessionCenter.get('http://cas.swust.edu.cn/authserver/getKey')
    # print(dict(reponse.text).get('moduls'))
    return reponse.text[12:-21], reponse.text[-7:-2]


# 解析获取到的html课表数据
def clean_data(html):
    html = etree.HTML(html)
    courseData = []
    for j in range(0, 7):
        weekCourse = []
        # 周一到周日:last()-weekDay
        weekDay = 6 - j
        for i in range(1, 7):
            mpath = "//div[@id='CourseTable']//tbody/tr[" + str(i) + "]/td[last()-" + str(weekDay) + "]//span/text()"
            myCourseData = html.xpath(mpath)
            weekCourse.append(myCourseData)
        courseData.append(weekCourse)
    return courseData


# 展示课表数据
def show_course_data(courseDate):
    data = ['数据库原理及应用A', '陈骏', '01-13(2)', '东1204']
    for week in range(0, 7):
        print("周{}".format(numToChinese[str(week + 1)]), )
        for lecture in range(0, 6):
            # print("第{}讲".format(lecture+1,data[0],data[1],data[2],data[3]),end='')
            print("第{}讲".format(numToChinese[str(lecture + 1)]))
            data = courseDate[week][lecture]
            count = 0
            keyName = ''
            for keyValue in data:
                if count % 5 == 0:
                    keyName = '课程名:' + keyValue
                elif count % 5 == 1:
                    count += 1
                    continue
                elif count % 5 == 2:
                    keyName = '教师:' + keyValue
                elif count % 5 == 3:
                    keyName = '周次:' + keyValue[:5] + " 第" + numToChinese[keyValue[6]] + "学期"
                elif count % 5 == 4:
                    keyName = '地点:' + keyValue
                print(keyName)
                count += 1
            print("")
        print("")


def set_user_info():
    global userName, userPass
    userName = input('请输入一站式服务大厅登陆账号(输入结束请按回车确认):')
    while not len(userName):
        userName = input('登陆账号为空，请重新输入(输入结束请按回车确认):')
    userPass = input('请输入一站式服务大厅登陆密码(输入结束请按回车确认):')
    while not len(userPass):
        userPass = input('登陆密码为空，请重新输入(输入结束请按回车确认):')


# 登陆一站式服务大厅
def login_service_center():
    while True:
        set_user_info()
        # 获取session
        get_session()
        # 获取验证码
        captcha = get_captcha()
        # 自动识别验证码，未完成，请手工输入验证码识，验证码图片文件为captcha.png
        # auto_captcha()
        # 获取加密秘钥参数
        secret = get_key()
        # 获取密文密码
        userPassEncry = encrypt(userPass[::-1], secret[0], secret[1])

        # 构造请求参数
        params = {
            'execution': 'e1s1',
            '_eventId': 'submit',
            'geolocation': '',
            'username': userName,
            'password': userPassEncry,
            'captcha': captcha
        }

        # 登陆认证中心
        url = 'http://cas.swust.edu.cn/authserver/login?service=http://my.swust.edu.cn/mht_shall/a/service/serviceFrontManage/cas'
        html = sessionCenter.post(url=url, data=params)

        # 判断登陆是否成功
        if 'my.swust.edu.cn/mht_shall/a/service/serviceFrontManage;JSESSIONID=' in html.url:
            break
        else:
            print('账号密码或者验证码输入错误！请重新输入！')


# 获取session，建立一次新的会话
def get_session():
    url = 'http://cas.swust.edu.cn/authserver/login?service=http://my.swust.edu.cn/mht_shall/a/service/serviceFrontManage/cas'
    headers = {
        'Referer': 'http://www.swust.edu.cn/',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Language': 'zh-Hans-CN,zh-Hans;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Encoding': 'gzip, deflate'
    }
    newSession = requests.session()
    # 第一次请求网站的时候做异常处理，本地与网站通信是否正常
    try:
        newSession.get(url=url, headers=headers)
    except:
        print("网络错误，请检查网络配置是否正确或者站点是否正常运行！")
        exit(0)
    # 将session保存下来
    global sessionCenter
    sessionCenter = newSession


# 登陆实验预约系统
def login_experiment():
    # 获取在服务大厅该状态的session
    session = sessionCenter
    # 访问实验预约系统
    url = 'http://202.115.175.177/swust/'
    html = session.get(url=url)
    # js重定向认证，request方法无法自动完成，解析出重定向的url
    html = etree.HTML(html.text)
    # 返回的是一个列表
    li = html.xpath("//script/text()")
    # 取列表的第一个字符串里面我们需要的部分(切片)
    str = li[0][17:-2]
    # 拼接构造js重定向的链接
    url = 'http://202.115.175.177/' + str
    # 访问链接获取授权
    session.get(url)

    # 访问实验课表页面
    url = 'http://202.115.175.177/StuExpbook/book/bookResult.jsp'
    html = session.get(url)

    # 爬取课表页面信息
    courseData = []
    pageNum = 1
    while (True):
        # 获取一页课表
        html = get_experiment_one_page(session, pageNum)
        # 解析课表
        mData = clean_experiment_one_page(html)
        # 将课程信息储存
        courseData.extend(mData[0])
        # 判断是否已经是最后一页了，是则爬取结束
        if mData[1]:
            break
        # 爬下一页课程信息
        pageNum += 1
    # 返回列表存放的实验课信息
    return courseData


# 获取实验课表的一页HTML数据
def get_experiment_one_page(session, pageNum='0', currYearterm='2019-2020-1', currTeachCourseCode='%'):
    params = {
        'currYearterm': currYearterm,
        'currTeachCourseCode': currTeachCourseCode,
        'page': pageNum
    }
    url = 'http://202.115.175.177/StuExpbook/book/bookResult.jsp'
    html = session.post(url=url, data=params)
    # 返回该页HTML
    return html.text


# 解析实验课表HTML数据
def clean_experiment_one_page(html):
    # 用etree进行初始化
    html = etree.HTML(html)
    # Xpath解析
    courseData = html.xpath("//div[@id='content']/table//td//text()")
    # 记录是否是最后一页
    lastPage = False
    # 如果是最后一页
    if len(html.xpath('//*[@id="content"]/table/tbody/tr')) != 11:
        lastPage = True
    return courseData, lastPage


# 展示实验课表数据
def show_experiment_data(experimentData):
    for i in range(0, len(experimentData) // 12):
        print('课程名称:', experimentData[0 + i * 12])
        print('项目名称:', experimentData[1 + i * 12])
        print('上课时间:', experimentData[2 + i * 12][2:-1])
        print('上课地点:', experimentData[3 + i * 12])
        print('指导老师:', experimentData[4 + i * 12])
        print('')


if __name__ == "__main__":
    # 登陆一站式服务大厅
    login_service_center()
    # 登陆教务处并且获取课表HTML代码
    course_office = login_office()
    # 进行课表的代码解析
    course_office = clean_data(course_office)
    # 展示课表数据
    show_course_data(course_office)
    # 登陆实验课表平台和获取实验课HTML代码并且解析
    experimentData = login_experiment()
    # 展示实验课课表数据
    show_experiment_data(experimentData)
