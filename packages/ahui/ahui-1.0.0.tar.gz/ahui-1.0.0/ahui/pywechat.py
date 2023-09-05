# 企业微信群机器人-推送多种类型消息的应用
# 函数应用教程见作者(阿辉)博客：http://t.csdn.cn/mjS1z


# 企业微信群机器人key：
def wechat_key(key='key1'):
    keys = {'key1' : 'your_wechat_robot_key'}   # 设置你的默认key
    wkey = keys[key]
    return wkey


# 1.1.企业微信群机器人-推送消息类型-markdown：
# 参数：[content]支持传入字符串(str)/列表(list)/数据框(DataFrame)；[df_links]支持多个链接字段，默认参数空；
# 说明：只支持@1个人/不支持@all；@对象为企业微信英文名，英文名不区分大小写；若@对象无此人仍正常推送消息内容；
# 系统：适用于 Windows、Linux 系统环境下的Python3版本。
def wechat_markdown(top='', title='', content='', user='', links={}, df_links={}, show_cols=False, key=None):

    import pandas as pd
    import requests,json,re

    if key==None:
        key = wechat_key()
    if isinstance(content,str):
        contents = [content]
    elif isinstance(content,list):
        contents = content
    else:
        content = content.copy()
        for col in df_links:
            word = df_links[col]
            content[col] = [f'[{word}]({i})' for i in content[col]]
        columns = content.columns
        for c in columns:
            content[c] = content[c].astype(str)
        if show_cols ==True:
            d = pd.DataFrame(columns).T
            d.columns = columns
            content = pd.concat([d, content], axis=0)
        content['combine'] = ''
        for c in columns:
            content['combine'] = content['combine'] + ' | ' + content[c]
        contents = [''] + content['combine'].tolist()

    ls_links = []
    for k in links:
        link = '[{}]({})'.format(k,links[k])
        ls_links.append(link)
    contents = contents + ls_links

    max_bytes = 3900  # 设置最大允许的消息长度(字节数)
    top_title_bytes = len(top.encode()) + len(title.encode())  # top和title的字节数
    contents_ls = []
    for c,i in zip(contents, range(len(contents))):
        contents_ls.append(c)
        if (top_title_bytes + len(str(contents_ls).encode())) > max_bytes:
            if i > 0:
                num = max_bytes - (len(str(contents[:i]).encode()) + top_title_bytes)        # 剩余空间可显示字节数
                lsc = [j for i,j in zip(range(len(c)), c) if len(c[:i+1].encode()) <= num]   # 从字符串中截取前num个字节(默认编码为'utf-8'、1个汉字3个字节)
                cstr = ''.join(lsc)
                contents = contents[:i] + [cstr + ' ............']
            else:
                num = max_bytes - top_title_bytes
                others = len(str(contents).encode()) - num    # 无法显示的字节数
                lsc = [j for i,j in zip(range(len(c)), c) if len(c[:i+1].encode()) <= num]
                cstr = ''.join(lsc)
                contents = [cstr + ' ............', f'※ 未显示字节数：{others}']     # 若首个元素字符大于限制则进行截取
            print('※ 截取元素数-{} 字符数-{}'.format(len(contents)-1, len(str(contents))))
            break

    contents = [str(i).replace('\\','/') for i in contents]   # 发送内容中不支持转义字符\ 故转为反斜杠/
    title = str(title).replace('\\','/')

    cts = []
    if len(contents)>1:
        for c in contents[1:]:
            string = '>   <font color=\"warning\">{}</font>\n\n'.format(c)
            cts.append(string)
    ctstr = ''.join(cts)

    if user !='':
        mark = {'msgtype': 'markdown',
                'markdown': {'content':'''
                             **{}** \n
                             >主题：<font color=\"info\">{}</font>\n
                             >内容：<font color=\"warning\">{}</font>\n
                             <@{}>'''.format(top,title,contents[0],user)}}
        subs = mark['markdown']['content'].split('<@')[0] + ctstr + '<@' + mark['markdown']['content'].split('@')[1]
        mark['markdown']['content'] = re.sub(' +',' ',subs)
    else:
        mark = {'msgtype': 'markdown',
                'markdown': {'content':'''
                             **{}** \n
                             >主题：<font color=\"info\">{}</font>\n
                             >内容：<font color=\"warning\">{}</font>\n
                             '''.format(top,title,contents[0])}}
        subs = mark['markdown']['content'] + ctstr
        mark['markdown']['content'] = re.sub(' +', ' ', subs)

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + key, headers=headers, data=json.dumps(mark))
    if 'ok' in response.text:
        print(f'【OK】{title}')
    elif 'exceed max length' in response.text:
        raise ValueError('【Fail】内容长度超过限制！')
    else:
        raise ValueError(response.text)


# 1.2.企业微信群机器人-推送消息类型-markdown：
# 简介：基于 wechat_markdown() 函数的二次封装开发；功能上支持@多人、支持推送多个群；
# 参数：[user]支持传入数据类型str/list； [key]支持数据类型str/list，当传入多个元素则用列表形式。
def wechat_markdowns(top='', title='', content='', user='', links={}, df_links={}, show_cols=False, key=None):
    if isinstance(user, str):
        users = [user]
    elif user==[]:
        users = ['']
    else:
        users = user
    if key==None or isinstance(key,str):
        keys = [key]
    else:
        keys = key

    if len(users)>1:
        for key in keys:
            wechat_markdown(title=title, content=content, user='', links=links, df_links=df_links, show_cols=show_cols, key=key, top=top)
            wechat_at(users_name=users, users_phone=[], key=key, content='👆👆👆')
    else:
        for key in keys:
            wechat_markdown(title=title, content=content, user=users[0], links=links, df_links=df_links, show_cols=show_cols, key=key, top=top)


# 2.企业微信群机器人-推送消息类型-text：
# 功能：@对象支持使用企业微信英文名或手机号、支持 '@all' 或 @多个人；
# 参数：[content]支持数据类型str/list，列表中的每个元素文本代表一行。
def wechat_text(top='', title='', content='', users_name=[], users_phone=[], key=None):

    import requests,json,re
    if key==None:
        key = wechat_key()
    if isinstance(content,str):
        contents = [content]
    elif isinstance(content,list):
        contents = content
    else:
        raise TypeError('content type is wrong!')

    users_name=[str(i) for i in users_name]
    users_phone=[str(i) for i in users_phone]
    contents = [str(i).replace('\\','/') for i in contents]   # 发送内容中不支持转义字符\ 故转为反斜杠/
    ctstr = '\n'.join(contents)
    text = {'msgtype': 'text',
            'text': {'content':'''
                     ★{}★\n
                     >主题：{}
                     >内容：\n{}
                     '''.format(top,title,ctstr),
                     "mentioned_list": users_name,
                     "mentioned_mobile_list": users_phone}}
    text['text']['content'] = re.sub(' +', ' ', text['text']['content'])
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + key, headers=headers, data=json.dumps(text))
    if 'ok' in response.text:
        print(f'【OK】{title}')
    else:
        raise ValueError(response.text)


# 3.企业微信群机器人-推送消息类型-@群成员：
# 功能：@对象支持使用企业微信英文名或手机号，英文名不区分大小写；支持 '@all' 或 @多个人，若无此人则不@且不影响执行推送。
def wechat_at(users_name=[], users_phone=[], key=None, content=''):
    import requests,json
    if key==None:
        key = wechat_key()
    users_name=[str(i) for i in users_name]
    users_phone=[str(i) for i in users_phone]
    text = {'msgtype': 'text',
            'text': {'content': f'{content}',
                     "mentioned_list": users_name,
                     "mentioned_mobile_list": users_phone}}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + key, headers=headers, data=json.dumps(text))
    if 'ok' in response.text:
        print('【OK】{}'.format(users_name+users_phone))
    else:
        raise ValueError(response.text)


# 4.企业微信群机器人-推送消息类型-图像：
# 参数：[image]支持传入的数据类型-本地图片路径/变量Image/变量bytes；
# 说明：图片最大不能超过2M，支持JPG、PNG格式。
# 安装：PIL(pip install pillow)
def wechat_image(image, key=None, users=[], content=''):

    import requests,json,os,PIL,base64
    from hashlib import md5
    from datetime import datetime
    if key==None:
        key = wechat_key()
    if isinstance(image, str) and image.split('.')[-1].lower() in ['jpg','png']:
        image = open(image, 'rb').read()   # 读取本地图片-bytes
    elif isinstance(image, bytes):
        print('image type is bytes')
    elif isinstance(image, PIL.Image.Image):
        filename = 'report_' + str(datetime.now()).replace(':','') + '.png'
        image.save(filename)
        image = open(filename, 'rb').read()  # bytes
        os.remove(filename)
        print('image type is Image')
    else:
        raise TypeError('image type is wrong!')

    payload = {'msgtype': 'image',
               'image': {'base64': base64.b64encode(image).decode('utf-8'),
                         'md5': md5(image).hexdigest()}}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + key, headers=headers, data=json.dumps(payload))
    if 'ok' in response.text:
        print('【OK】图片已发送！')
        if len(users):
            wechat_at(users_name=users, key=key, content=content)
    elif 'invalid image size' in response.text:
        raise ValueError('【Fail】图片过大超出限制！')
    else:
        raise ValueError(response.text)


# 5.企业微信群机器人-推送消息类型-本地文件：
# 参数：[pathfile]传参要求，图片:最大10MB 支持JPG、PNG格式；语音:最大2MB 播放长度不超过60s 支持AMR格式；视频:最大10MB 支持MP4格式；普通文件:最大20MB
def wechat_file(pathfile, key=None, users=[], content=''):

    from urllib3 import encode_multipart_formdata
    import requests,json,os

    if key==None:
        key = wechat_key()
    upload_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={}&type=file'.format(key)
    file_name = pathfile.split("\\")[-1]
    file_name = file_name.split('/')[-1]  # 支持路径的两种斜杠/\形式
    length = os.path.getsize(pathfile)
    data = open(pathfile, 'rb').read()
    params = {"filename": file_name, "filelength": length, 'file':(file_name, data)}
    encode_data = encode_multipart_formdata(params)
    headers = {"Content-Type": encode_data[1]}
    req = requests.post(upload_url, data=encode_data[0], headers=headers)
    try:
        msgtype = req.json()['type']
        media_id = req.json()['media_id']
    except:
        if 'invalid file size' in req.text:
            raise ValueError('【Fail】文件过大超出限制！')
        else:
            raise ValueError(req.json())
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'.format(key)
    mark = {"msgtype": msgtype, "file": {"media_id": media_id}}
    response = requests.post(url=url, headers=headers, data=json.dumps(mark))
    if 'ok' in response.text:
        print('文件已发送: %s'%file_name)
        if len(users):
            wechat_at(users_name=users, key=key, content=content)
    else:
        raise ValueError(response.text)

# <END>