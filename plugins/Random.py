from nonebot import on_command,get_driver
path=get_driver().config.bot_path
from nonebot.adapters.onebot.v11 import MessageSegment,Message
from nonebot.params import CommandArg
import json,random,os,urllib.request,base64
from io import BytesIO
from PIL import ImageDraw,Image,ImageFont

def get_musicdata():
    path=get_driver().config.bot_path
    with open(f"./{path[0]}/src/MusicData.json","r",encoding="UTF-8") as fs:
        All_Songs=json.load(fs)
        Dict={}
        for NowSongInfo in All_Songs:
            title=NowSongInfo["title"]
            stype=NowSongInfo["type"]
            if title in Dict.keys() and stype=="DX":
                title=title+"[DX]"
            sid=NowSongInfo["id"]
            lv=NowSongInfo["level"]
            ds=NowSongInfo["ds"]
            charts=NowSongInfo["charts"]
            dxs_max=[]
            for element in charts:
                _charts=element["notes"]
                x=0
                z=0
                for x in range(len(_charts)):
                    z+=_charts[x]
                    x+=1
                dxs_max.append(z*3)
            basic_info=NowSongInfo["basic_info"]
            artist=basic_info["artist"]
            genre=basic_info["genre"]
            bpm=basic_info["bpm"]
            sfrom=basic_info["from"]
            new=basic_info["is_new"]
            info=[title,sid,"https://www.diving-fish.com/covers/{:05}.png".format(int(sid)),stype,lv,charts,dxs_max,artist,genre,bpm,sfrom,new,ds]
            Dict[sid]=info
        return Dict

def down_songpic(sid:str,url:str):
    if os.path.exists(f"./{path[0]}/src/Song_Pic")==False:
        os.makedirs(f"./{path[0]}/src/Song_Pic")
    if os.path.exists(f"./{path[0]}/src/Song_Pic/{sid}.png")==False:
        urllib.request.urlretrieve(url,f"./{path[0]}/src/Song_Pic/{sid}.png")

Random=on_command("随机乐曲",priority=10)
@Random.handle()
async def Random_fanc(command_arg:Message=CommandArg()):
    user_args=str(command_arg).strip().split(" ")
    AllSong_Dict=get_musicdata()
    for arg in user_args:
        filter_type=["SD","DX"]
        filter_lv=["1","2","3","4","5","6","7","7+","8","8+","9","9+","10","10+","11","11+","12","12+","13","13+","14","14+","15"]
        filter_diff={"绿":0,"黄":1,"红":2,"紫":3,"白":4}
        if arg in filter_type:
            del_list=[]
            for info in AllSong_Dict:
                stype=AllSong_Dict[info][3]
                if stype==arg:
                    pass
                else:
                    del_list.append(info)
            for del_id in del_list:
                del AllSong_Dict[del_id]
        elif arg in filter_lv:
            del_list=[]
            if arg=="15":
                await Random.send(f"⭐随你妈,这不DX分理论一下交个作业?⭐",reply_message=True)
            for info in AllSong_Dict:
                level_list=AllSong_Dict[info][4]
                if arg in level_list:
                    pass
                else:
                    del_list.append(info)
            for del_id in del_list:
                del AllSong_Dict[del_id]
            for diff_arg in user_args:
                if diff_arg in filter_diff.keys():
                    del_list=[]
                    charts_id=filter_diff[diff_arg]
                    for info in AllSong_Dict:
                        level_list=AllSong_Dict[info][4]
                        if level_list[charts_id]==arg:
                            pass
                        else:
                            del_list.append(info)
                    for del_id in del_list:
                        del AllSong_Dict[del_id]
                else:
                    pass
    for arg in user_args:
        if arg in filter_type or arg in filter_lv or arg in filter_diff.keys():
            pass
        else: 
            await Random.finish(f"⭐参数错误,请检查⭐",reply_message=True)
    if len(AllSong_Dict)==0:
        await Random.finish(f"⭐未找到相符的乐曲⭐",reply_message=True)
    random_num=random.randint(0,len(AllSong_Dict)-1)
    random_sid=list(AllSong_Dict.keys())[random_num]
    random_songinfo=AllSong_Dict[random_sid]
    img=Image.open(f"./{path[0]}/src/Pic/Single_Song.png")
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",30)
    Basic_info=ImageDraw.Draw(img)
    artist=random_songinfo[7]
    title=random_songinfo[0]
    if len(artist)>=20:
        artist=artist[0:19]+"..."
    if len(title)>=20:
        title=title[0:19]+"..."
    sver=random_songinfo[10]
    new=random_songinfo[11]
    is_new=""
    if sver=="MiLK PLUS":
        sver="maimai MiLK PLUS"
    if new==True:
        is_new="是"
    else:
        is_new="否"
    info_str=f"歌曲名:{title}\n艺术家:{artist}\nBPM:{random_songinfo[9]}\n版本:{sver}\n是否为新歌:{is_new}"
    Basic_info.text((635,252),random_songinfo[1],(0,0,0),font,stroke_width=3,stroke_fill=(255,255,255))
    Basic_info.text((750,252),random_songinfo[8],(0,0,0),font,stroke_width=3,stroke_fill=(255,255,255))
    Basic_info.text((550,335),info_str,(0,0,0),font,stroke_width=3,stroke_fill=(255,255,255))
    down_songpic(str(random_sid),str(random_songinfo[2]))
    song_pic=Image.open(f"./{path[0]}/src/song_Pic/{random_sid}.png")
    song_pic_resize=song_pic.resize([275,275])
    img.paste(song_pic_resize,(217,280),song_pic_resize)
    if random_songinfo[3]=="DX":
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_DX.png")
    else:
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_SD.png")
    img.paste(song_type,(217,515),song_type)
    charts=random_songinfo[5]
    charts_info=ImageDraw.Draw(img)
    if len(charts)<5:
        charts_info.text((1050,680),"-(-)",(189,8,230),font,stroke_width=3,stroke_fill=(255,255,255))
        y=790
        for _count in range(6):
            charts_info.text((1050,y),"--",(189,8,230),font,stroke_width=3,stroke_fill=(255,255,255))
            y+=78
        charts_info.text((685,1403),"--",(189,8,230),font,stroke_width=3,stroke_fill=(255,255,255))
    lv=random_songinfo[4]
    ds=random_songinfo[12]
    color=[(130,217,86),(211,217,29),(255,140,151),(166,84,230),(189,8,230)]
    x=435
    for _count in range(len(charts)):
        charts_info.text((x,680),f"{lv[_count]}({ds[_count]})",color[_count],font,stroke_width=3,stroke_fill=(255,255,255))
        notes=charts[_count]["notes"]
        charter=charts[_count]["charter"]
        if len(notes)<5:
            notes.insert(3,"--")
        y=790
        total=0
        for info in notes:
            charts_info.text((x,y),str(info),color[_count],font,stroke_width=3,stroke_fill=(255,255,255))
            if info!="--":
                total+=int(info)
            y+=78
        charts_info.text((x,y),str(total),color[_count],font,stroke_width=3,stroke_fill=(255,255,255))
        x+=150
        if _count==2:
            charts_info.text((630,1267),charter,color[_count],font,stroke_width=3,stroke_fill=(255,255,255))
        elif _count==3:
            charts_info.text((630,1332),charter,color[_count],font,stroke_width=3,stroke_fill=(255,255,255))
        elif _count==4:
            charts_info.text((685,1403),charter,color[_count],font,stroke_width=3,stroke_fill=(255,255,255))
    out_buffer=BytesIO()   
    img.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    await Random.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

#====================分割线====================

async def search_song(data1,data2,string,mode,data3):
    music_data=get_musicdata()
    del_list=[]
    for info in music_data:
        now_info=music_data[info]
        ds_l=now_info[12]
        ds_bool=0
        if mode==1:
            lv_count=0
            for ds_info in ds_l:
                if float(ds_info)>=float(data1) and float(ds_info)<=float(data2) and lv_count==data3:
                    ds_bool=1
                    lv_count=0
                    break
                lv_count+=1
            if ds_bool==1:
                pass
            else:
                del_list.append(info)
        else:
            for ds_info in ds_l:
                if float(ds_info)>=float(data1) and float(ds_info)<=float(data2):
                    ds_bool=1
                    break
            if ds_bool==1:
                pass
            else:
                del_list.append(info)  
    for del_id in del_list:
        try:
            del music_data[del_id]
        except:
            pass
    if len(music_data)==0:
        await Class_Song.finish("⭐小圆没找到指定范围的歌曲呢⭐",reply_message=True)
    geted_sid=[]
    for _count in range(4):
        random_num=random.randint(0,len(music_data)-1)
        random_sid=list(music_data.keys())[random_num]
        geted_sid.append(random_sid)
    img=Image.open(f"./{path[0]}/src/Pic/class_base.png")
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",30)
    font2=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",17)
    font3=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",14)
    title_info=ImageDraw.Draw(img)
    title_info.text((410,95),string,(255,94,128),font,stroke_width=3,stroke_fill=(247,198,220))
    x=240
    y=220
    _count=0
    for info in geted_sid:
        if _count>1:
            x+=530
            y=220
            _count=0
        title=music_data[info][0]
        artist=music_data[info][7]
        genre=music_data[info][8]
        sver=music_data[info][10]
        ds=music_data[info][12]
        if len(artist)>=14:
            artist=artist[0:14]+"..."
        if len(title)>=14:
            title=title[0:14]+"..."
        if sver=="MiLK PLUS":
            sver="maimai MiLK PLUS"
        ds_list=[str(x) for x in ds]
        ds_str="/".join(ds_list)
        info_str=f"歌曲名:{title}\n艺术家:{artist}\nBPM:{music_data[info][9]}\n版本:{sver}\n定数:{ds_str}"
        song_info=ImageDraw.Draw(img)
        song_info.text((x,y),info,(0,0,0),font2,stroke_width=1,stroke_fill=(255,255,255))
        song_info.text((x-50,y+20),info_str,(0,0,0),font2,stroke_width=1,stroke_fill=(255,255,255))
        song_info.text((x+47,y+1),genre,(0,0,0),font3,stroke_width=1,stroke_fill=(255,255,255))
        song_pic=Image.open(f"./{path[0]}/src/song_Pic/{info}.png")
        song_pic_resize=song_pic.resize([110,110])
        img.paste(song_pic_resize,(x-162,y+14),song_pic_resize)
        y+=192
        _count+=1
    out_buffer=BytesIO()   
    img.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    await Class_Song.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

Class_Song=on_command("课题曲",priority=10)
@Class_Song.handle()
async def Class_Song_fanc(command_arg:Message=CommandArg()):
    offical_class={"EXPERT初级":[7.0,9.6,2],"EXPERT中级":[9.7,11.6,2],"EXPERT上级":[11.7,13.9,2],"MASTER初级":[10.0,11.9,3]
                   ,"MASTER中级":[12.0,13.2,3],"MASTER上级":[13.3,14.4,3],"MASTER超上级":[14.5,14.9,3]}
    user_args=str(command_arg).strip().split(" ")
    if len(user_args)==0:
        await Class_Song.finish("⭐未检测到字符输入⭐",reply_message=True)
    elif len(user_args)==1:
        if user_args[0] not in offical_class.keys():
            try:
                float(user_args[0])
                if float(user_args[0])>14.9 or float(user_args[0])<1.0:
                    raise
            except:
                await Class_Song.finish(f"⭐参数错误,请检查⭐",reply_message=True)
        if user_args[0] in offical_class.keys():
            await search_song(offical_class[user_args[0]][0],offical_class[user_args[0]][1],f"随机段位认定:{user_args[0]}",1,offical_class[user_args[0]][2])
        else:
            await search_song(user_args[0],user_args[0],f"自定义课题曲:{user_args[0]}-{user_args[0]}",None,None)
    elif len(user_args)==2:
        for info in user_args:
            try:
                float(info)
                if float(info)>14.9 or float(info)<1.0:
                    raise
            except:
                await Class_Song.finish(f"⭐参数错误,请检查⭐",reply_message=True)
        if float(user_args[0])>=float(user_args[1]):
            await search_song(user_args[1],user_args[0],f"自定义课题曲:{user_args[1]}-{user_args[0]}",None,None)
        else:
            await search_song(user_args[0],user_args[1],f"自定义课题曲:{user_args[0]}-{user_args[1]}",None,None)
    else:
        await Class_Song.finish("⭐给予参数过多⭐",reply_message=True)