from nonebot import on_command,get_driver
path=get_driver().config.bot_path
from nonebot.adapters.onebot.v11 import MessageSegment,Message
from nonebot.params import CommandArg
import json,base64,os,urllib.request
from io import BytesIO
from PIL import ImageDraw,Image,ImageFont

def get_aliasdata():
    with open(f"./{path[0]}/src/Alias.json","r",encoding="UTF-8") as fs:
        alias_data=json.load(fs)
        alias_dict={}
        for info in alias_data:
            Now_Data=alias_data[info]
            alias_list=Now_Data["Alias"]
            alias_dict[info]=alias_list
        return alias_dict      

def get_musicdata():
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
    
async def draw_single(all_data,sid):
    song_info=all_data[sid]
    img=Image.open(f"./{path[0]}/src/Pic/Single_Song.png")
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",30)
    Basic_info=ImageDraw.Draw(img)
    artist=song_info[7]
    title=song_info[0]
    if len(artist)>=20:
        artist=artist[0:19]+"..."
    if len(title)>=20:
        title=title[0:19]+"..."
    sver=song_info[10]
    new=song_info[11]
    is_new=""
    if sver=="MiLK PLUS":
        sver="maimai MiLK PLUS"
    if new==True:
        is_new="是"
    else:
        is_new="否"
    info_str=f"歌曲名:{title}\n艺术家:{artist}\nBPM:{song_info[9]}\n版本:{sver}\n是否为新歌:{is_new}"
    Basic_info.text((635,252),song_info[1],(0,0,0),font,stroke_width=3,stroke_fill=(255,255,255))
    Basic_info.text((750,252),song_info[8],(0,0,0),font,stroke_width=3,stroke_fill=(255,255,255))
    Basic_info.text((550,335),info_str,(0,0,0),font,stroke_width=3,stroke_fill=(255,255,255))
    down_songpic(str(sid),str(song_info[2]))
    song_pic=Image.open(f"./{path[0]}/src/song_Pic/{sid}.png")
    song_pic_resize=song_pic.resize([275,275])
    img.paste(song_pic_resize,(217,280),song_pic_resize)
    if song_info[3]=="DX":
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_DX.png")
    else:
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_SD.png")
    img.paste(song_type,(217,515),song_type)
    charts=song_info[5]
    charts_info=ImageDraw.Draw(img)
    if len(charts)<5:
        charts_info.text((1050,680),"-(-)",(189,8,230),font,stroke_width=3,stroke_fill=(255,255,255))
        y=790
        for _count in range(6):
            charts_info.text((1050,y),"--",(189,8,230),font,stroke_width=3,stroke_fill=(255,255,255))
            y+=78
        charts_info.text((685,1403),"--",(189,8,230),font,stroke_width=3,stroke_fill=(255,255,255))
    lv=song_info[4]
    ds=song_info[12]
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
    return image_ba64
    
SearchSong=on_command("查找乐曲",priority=10)
@SearchSong.handle()
async def SearchSong_Fanc(command_arg:Message=CommandArg()):
    user_args=str(command_arg).strip().lower().strip(" ")
    if user_args=="":
        await SearchSong.finish("⭐未检测到字符输入⭐",reply_message=True)
    alias_dict=get_aliasdata()
    song_dict=get_musicdata()
    searched_songs=[]
    for info in alias_dict:
        data=alias_dict[info]
        for alias in data:
            if str(alias).lower().strip(" ")==user_args:
                searched_songs.append(info)
    if len(searched_songs)==0:
        await SearchSong.finish("⭐小圆没找到这首歌呢⭐",reply_message=True)
    else:
        if len(searched_songs)>=2:
            message=""
            for sid in searched_songs:
                title=song_dict[sid][0]
                message=message+f"{sid}.{title}\n"
            await SearchSong.finish("⭐小圆找到了下述歌曲⭐\n"+message+"⭐请使用精确查找 [歌曲ID]来查找下述歌曲⭐",reply_message=True)
        else:
            image_ba64=await draw_single(song_dict,searched_songs[0])
            await SearchSong.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

#====================分割线====================

ID_Search=on_command("精确查找",priority=10)
@ID_Search.handle()
async def ID_Search_Fanc(command_arg:Message=CommandArg()):
    user_args=str(command_arg).strip().lower().strip(" ")
    song_dict=get_musicdata()
    if user_args=="":
        await SearchSong.finish("⭐未检测到字符输入⭐",reply_message=True)
    try:
        int(user_args)
        _test=song_dict[user_args]
    except:
        await ID_Search.finish("⭐歌曲ID错误⭐",reply_message=True)
    image_ba64=await draw_single(song_dict,user_args)
    await ID_Search.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

#====================分割线====================

Alia_Search=on_command("别名查找",priority=10)
@Alia_Search.handle()
async def Alia_Search_Fanc(command_arg:Message=CommandArg()):
    user_args=str(command_arg).strip()
    alias_dict=get_aliasdata()
    if user_args=="":
        await SearchSong.finish("⭐未检测到字符输入⭐",reply_message=True)
    try:
        int(user_args)
        _test=alias_dict[user_args]
    except:
        await ID_Search.finish("⭐歌曲ID错误⭐",reply_message=True)
    alias_list=alias_dict[user_args]
    message=""
    tip=""
    if len(alias_list)>11:
        alias_list=alias_list[0:11]
        tip="\n⭐由于列表过长,已自动截取前10个别名⭐"
    for info in alias_list:
        if info==alias_list[0]:
            pass
        else:
            message+=f"\n{info}"
    await Alia_Search.finish(f"⭐{user_args}.{alias_list[0]}的别名有⭐{message}{tip}",reply_message=True)

#====================分割线====================

async def draw_dslist(data1,data2):
    music_data=get_musicdata()
    del_list=[]
    for info in music_data:
        now_info=music_data[info]
        ds_l=now_info[12]
        ds_bool=0
        for ds_info in ds_l:
            if float(ds_info)>=data1 and float(ds_info)<=data2:
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
        await DS_Search.finish("⭐小圆没找到指定范围的歌曲呢⭐",reply_message=True)
    if len(music_data)%7!=0:
        row=(len(music_data)//7+1)*390+1050
    else:
        row=(len(music_data)//7)*390+1050
    img=Image.new("RGB",(2230,row),(255,255,255))
    head=Image.open(f"./{path[0]}/src/Pic/head.png")
    foot=Image.open(f"./{path[0]}/src/Pic/foot.png")
    img.paste(head,(0,0),head)
    img.paste(foot,(0,row-550),foot)
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",50)
    font_ti=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",20)
    img_text=ImageDraw.Draw(img)
    img_text.text((350,215),f"定数 > {data1}-{data2} < 列表",(247,198,220),font,stroke_width=3,stroke_fill=(255,94,128))
    _count=0
    y=550
    for info in music_data:
        value=music_data[info]
        title=value[0]
        sid=value[1]
        url=value[2]
        stype=value[3]
        ds=value[12]
        if _count>6:
            y+=390
            _count=0
        if len(title)>12:
            title=title[0:12]+"..."
        ds_bg=Image.open(f"./{path[0]}/src/Pic/ds_search_base.png")
        img.paste(ds_bg,(_count*290+115,y),ds_bg)
        down_songpic(str(sid),str(url))
        song_pic=Image.open(f"./{path[0]}/src/Song_Pic/{sid}.png")
        song_pic_resize=song_pic.resize([202,202])
        img.paste(song_pic_resize,(137+(_count*290),y+18),song_pic_resize)
        songinfo=ImageDraw.Draw(img)
        songinfo.text((125+(_count*290),y+250),f"ID:{sid}",(255,255,255),font_ti)
        songinfo.text((125+(_count*290),y+270),title,(255,255,255),font_ti)
        ds_list=[str(x) for x in ds]
        ds_str="/".join(ds_list)
        songinfo.text((125+(_count*290),y+305),ds_str,(0,0,0),font_ti)
        if stype=="DX":
            dx_pic=Image.open(f"./{path[0]}/src/Pic/Song_DX.png")
            img.paste(dx_pic,(115+(_count*290),y),dx_pic)
        else:
            sd_pic=Image.open(f"./{path[0]}/src/Pic/Song_SD.png")
            img.paste(sd_pic,(115+(_count*290),y),sd_pic)
        _count+=1
    out_buffer=BytesIO()   
    img.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    return image_ba64

DS_Search=on_command("定数查找",priority=10)
@DS_Search.handle()
async def DS_Search_Fanc(command_arg:Message=CommandArg()):
    user_args=str(command_arg).strip().split(" ")
    song_dict=get_musicdata()
    if len(user_args)==0:
        await DS_Search.finish("⭐未检测到字符输入⭐",reply_message=True)
    elif len(user_args)>=3:
        await DS_Search.finish("⭐给予参数过多⭐",reply_message=True)
    for info in user_args:
        try:
            float(info)
            if float(info)>15 or float(info)<1:
                raise ValueError
        except:
            await DS_Search.finish("⭐参数错误,请检查⭐",reply_message=True)
    if len(user_args)==1:
        if float(user_args[0])==15.0:
            await DS_Search.send(f"⭐什么时候DX分理论?⭐",reply_message=True)
            image_ba64=await draw_single(song_dict,"692")
            await DS_Search.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)
        else:
            image_ba64=await draw_dslist(float(user_args[0]),float(user_args[0]))
            await DS_Search.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)
    else:
        if float(user_args[0])>=float(user_args[1]):
            image_ba64=await draw_dslist(float(user_args[1]),float(user_args[0]))
            await DS_Search.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)
        else:
            image_ba64=await draw_dslist(float(user_args[0]),float(user_args[1]))
            await DS_Search.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

#====================分割线====================

DanTable=on_command("段位表",priority=10)
@DanTable.handle()
async def DanTable_fanc(command_arg:Message=CommandArg()):
    usr_mes=str(command_arg).strip()
    if usr_mes=="1":
        await DanTable.finish(MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Pic/course_0.png"),reply_message=True)
    elif usr_mes=="2":
        await DanTable.finish(MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Pic/course_1.png"),reply_message=True)
    elif usr_mes=="3":
        await DanTable.finish(MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Pic/course_2.png"),reply_message=True)
    else:
        await DanTable.finish("⭐现在可获取的段位表有⭐\n1.国服表段位认定\n2.国服真段位认定\n3.国服随机段位认定\n⭐段位版本UNiVERSE PLUS⭐",reply_message=True)