import pymysql,re,datetime,sys
import codecs
def convertpost(postid):
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='root',
                                db='bw_bbs',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        sql = "select title from discussions where id="+str(postid)
        cursor.execute(sql)
        result = cursor.fetchone()
        title=result['title']
        sql = "select content,user_id,created_at,number from posts where discussion_id="+str(postid)+""
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            content=result['content']
            userid=result['user_id']
            cdate=result['created_at']
            N=result['number']
            sql = "select username from users where id="+str(userid)
            cursor.execute(sql)
            result = cursor.fetchone()
            username=result['username']
            convert_md2bbcode(content,title,cdate,username,postid,N)
    connection.close()
def convert_md2bbcode(content,title,cdate,username,postid,N):
    d=re.compile(r'<[^>]*>')
    content = d.sub('', content) #删除所有的html标签 只保留markdown标签
    d=re.compile(r'(^```(.*)```)')
    content = d.sub(r'[code]\2[/code]', content) #替换粗体
    d=re.compile(r'(\[upl-image-preview\surl=(.*?)\])')
    content = d.sub(r'[img]\2[/img]', content) #替换图片
    d=re.compile(r'(!\[([\s\S]*?)\]\(([\s\S]*?)\))')
    content = d.sub(r'[img]\3[/img]', content)
    d=re.compile(r'(\[([\s\S]*?)\]\(([\s\S]*?)\))')
    content = d.sub(r'[urlplus=\2]\3[/urlplus]', content) #替换url
    d=re.compile(r'(`{1,2}([^`](.*?))`{1,2})')
    content = d.sub(r'[highlight]\2[/highlight]', content) #替换高亮
    d=re.compile(r'(\*{2}([^*].*?)\*{2})')
    content = d.sub(r'[b]\2[/b]', content) #替换粗体
    d=re.compile(r'(^([0-9]*).\s(.*))')
    content = d.sub(r'[list=\2][*]\3[/list]', content) #替换有序列表
    d=re.compile(r'(^```(.*)```)')
    content = d.sub(r'[code]\2[/code]', content) #替换代码
    d=re.compile(r'(\*([^*].*?)\*)')
    content = d.sub(r'[i]\2[/i]', content) #替换斜体
    content=content.replace('[urlplus=img]','[img]') #修复可能存在的误替换
    #替换标题
    lines=content.split('\n')
    bbcode=''
    count=0
    count1=0
    count2=0
    for line in lines:
        if re.match(r'^(#+)(.*)(#+)',line):
            well=re.match(r'^(#+)(.*)(#+)',line).group().count('#')
            line=re.sub(r'\#+','',line)
            line='[size='+str(int(200-(well/2-1)*25))+']'+line+'[/size]'
        if re.match(r'^(#+)(.*)',line):
            well=re.match(r'^(#+)(.*)',line).group().count('#')
            line=re.sub(r'\#+','',line)
            line='[size='+str(int(200-(well-1)*25))+']'+line+'[/size]'
        #无序列表
        if (re.match(r'\*{1}\s{1}',line)):
            if(count==0):
                count=1
                bbcode=bbcode+'[list]'+'\n'
            line='[*]'+line.replace('* ','')
        else:
            if(count==1):
                bbcode=bbcode+'[/list]'+'\n'
                count=0
        #引言
        if (re.match(r'>',line)):
            if(count1==0):
                count1=1
                bbcode=bbcode+'[quote]'+'\n'
            line=''+line.replace('>','')
        else:
            if(count1==1):
                bbcode=bbcode+'[/quote]'+'\n'
                count1=0
        if (re.match(r'```',line)):
            if(count2==0):
                count2=1
                line='[code]'
            else:
                line='[/code]'
                count2=0
        bbcode=bbcode+line+'\n'
    bbcode=bbcode.replace('www.betaworld.cn/','slzkud.cn/oldbbs/')
    bbcode=bbcode.replace('&gt; ','&gt; ')
    print(title)
    reminfo='[i][b]本文章原本发布于BetaWorld旧论坛，原发布标题“'+title+'”，由'+username+'发布于'+datetime.datetime.strftime(cdate, "%Y年%m月%d日")+'。[/b][/i]\n[i][b]本贴仅为搬运留存，不负责后续事宜。[/b][/i]\n\n'
    bbcode=reminfo+bbcode
    fiobj=codecs.open(sys.path[0]+'\\'+title.replace('/','')+"_"+str(postid)+"_"+str(N)+'F.txt','w','utf-8')
    fiobj.write(bbcode)
    fiobj.close
pids=[10,21,33,127,198,208,210,224,192,181,191,15,19,225]
for pid in pids:
    convertpost(pid)