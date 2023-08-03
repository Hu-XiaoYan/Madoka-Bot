from nonebot import on_command,get_driver
path=get_driver().config.bot_path
token=get_driver().config.dev_token
from nonebot.adapters.onebot.v11 import MessageSegment,Message,Event
from nonebot.params import CommandArg
import json,os,urllib.request,base64,aiohttp,decimal,random
from io import BytesIO
from PIL import ImageDraw,Image,ImageFont
from nonebot.permission import SUPERUSER

def check_ypos(chart:int):
    if chart==0:
        return 1060
    elif chart==1:
        return 1300
    elif chart==2:
        return 1540
    elif chart==3:
        return 1780
    else:
        return 2020
    
def check_rank(achi:str):
    if achi<50.0:
        return "d"
    elif achi<60.0:
        return "c"
    elif achi<70.0:
        return "b"
    elif achi<75.0:
        return "bb"
    elif achi<80.0:
        return "bbb"
    elif achi<90.0:
        return "a"
    elif achi<94.0:
        return "aa"
    elif achi<97.0:
        return "aaa"
    elif achi<98.0:
        return "s"
    elif achi<99.0:
        return "sp"
    elif achi<99.5:
        return "ss"
    elif achi<100.0:
        return "ssp"
    elif achi<100.5:
        return "sss"
    else:
        return "sssp"

async def get_playerdata(token,post_data):
    async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/dev/player/records",headers={'developer-token':token[0]},params=post_data) as resp_record:
        user_data=await resp_record.json()
        if resp_record.status==200:
            pass
        elif resp_record.status==400:
            await PlayerSongInfo.finish("⭐小圆没有找到该玩家⭐",reply_message=True)
        elif resp_record.status==403:
            await PlayerSongInfo.finish("⭐该玩家设置了隐私⭐",reply_message=True)
        else:
            await PlayerSongInfo.finish("⭐小圆把用户数据弄丢了⭐",reply_message=True)
        return user_data

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
            ds_str=""
            for element in ds:
                ds_str=f"{element}/{ds_str}"
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
            info=[title,sid,"https://www.diving-fish.com/covers/{:05}.png".format(int(sid)),stype,lv,charts,dxs_max,artist,genre,bpm,sfrom,new,ds_str,ds]
            Dict[sid]=info
        return Dict

def down_songpic(sid:str,url:str):
    if os.path.exists(f"./{path[0]}/src/Song_Pic")==False:
        os.makedirs(f"./{path[0]}/src/Song_Pic")
    if os.path.exists(f"./{path[0]}/src/Song_Pic/{sid}.png")==False:
        urllib.request.urlretrieve(url,f"./{path[0]}/src/Song_Pic/{sid}.png")

async def draw_achi(sarg,alias_data,music_data,player_data):
    geted_data=[]
    if sarg.isdigit()==True:
        if sarg not in music_data.keys():
            await PlayerSongInfo.finish("⭐歌曲ID错误,请检查⭐",reply_message=True)
        else:
            for info in player_data["records"]:
                if int(sarg)==info["song_id"]:
                    geted_data.append(info)
            if len(geted_data)==0:
                await PlayerSongInfo.finish("⭐小圆没找到数据呢⭐",reply_message=True)
            else:
                pass
    else:
        searched_songs=[]
        for info in alias_data:
            data=alias_data[info]
            for alias in data:
                if str(alias).lower().strip(" ")==sarg:
                    searched_songs.append(info)
        if len(searched_songs)>=2:
            message=""
            for sid in searched_songs:
                title=music_data[sid][0]
                message=message+f"{sid}.{title}\n"
            await PlayerSongInfo.finish("⭐小圆找到了下述歌曲⭐\n"+message+"⭐请使用单曲成绩 [歌曲ID]来查找下述歌曲⭐",reply_message=True)
        else:
            for info in player_data["records"]:
                if int(searched_songs[0])==info["song_id"]:
                    geted_data.append(info)
            if len(geted_data)==0:
                await PlayerSongInfo.finish("⭐小圆没找到数据呢⭐",reply_message=True)
            else:
                pass
    all_info=music_data[str(geted_data[0]["song_id"])]
    title=all_info[0]
    sid=all_info[1]
    url=all_info[2]
    stype=all_info[3]
    artist=all_info[7]
    ds=all_info[12].split("/")
    ds_rev=list(reversed(ds))
    genre=all_info[8]
    bpm=all_info[9]
    version=all_info[10]
    new=all_info[11]
    if stype=="MiLK PLUS":
        stype="maimai MiLK PLUS"
    if new==True:
        is_new="是"
    else:
        is_new="否"
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",50)
    bg=Image.open(f"./{path[0]}/src/Pic/single_achi.png")
    down_songpic(sid,url)
    cover=Image.open(f"./{path[0]}/src/Song_Pic/{sid}.png")
    cover_re=cover.resize([440,440],Image.ANTIALIAS)
    _text=ImageDraw.Draw(bg)
    if len(title)>20:
        title=title[0:20]+"..."
    _text.text([975,345],sid,(255,255,255),font,stroke_width=5,stroke_fill=(0,0,0))
    _text.text([1160,345],genre,(255,255,255),font,stroke_width=5,stroke_fill=(0,0,0))
    _text.text([860,495],f"歌曲名:{title}\n艺术家:{artist}\nBPM:{bpm}\n版本:{version}\n是否为新歌:{is_new}",(255,255,255),font,stroke_width=5,stroke_fill=(0,0,0))
    bg.paste(cover_re,[310,386])
    if stype=="DX":
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_DX.png")
    else:
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_SD.png")
    bg.paste(song_type,(310,780),song_type)
    bg_=draw_detail(bg,geted_data,ds_rev)
    out_buffer=BytesIO()   
    bg_.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    return image_ba64

def draw_detail(bg,played_data,ds_rev):
    x=400
    z=1558
    for element in played_data:
        achi_per=str(element["achievements"])+"%"
        achi=element["achievements"]
        fc=element["fc"]
        fs=element["fs"]
        chart=element["level_index"]
        y=check_ypos(chart)
        rank=check_rank(achi)
        for element in list(achi_per):
            _char=Image.open(f"./{path[0]}/src/Pic/x{element}.png")
            bg.paste(_char,[x,y],_char)
            x+=50
        x=400
        _rank=Image.open(f"./{path[0]}/src/Pic/rank_{rank}.png")
        bg.paste(_rank,[920,y-25],_rank)
        if fc=="":
            pass
        else:
            _fc=Image.open(f"./{path[0]}/src/Pic/2_{fc}.png")
            bg.paste(_fc,[1223,y-37],_fc)
        if fs=="":
            pass
        else:
            _fs=Image.open(f"./{path[0]}/src/Pic/2_{fs}.png")
            bg.paste(_fs,[1373,y-37],_fs)
        ds_list=ds_rev[chart+1]
        for element in ds_list:
            _char=Image.open(f"./{path[0]}/src/Pic/x{element}.png")
            bg.paste(_char,[z,y],_char)
            z+=50
        z=1558
        y+=240
    return bg

PlayerSongInfo=on_command("单曲成绩",priority=10)
@PlayerSongInfo.handle()
async def PlayerSongInfo_fanc(event:Event,command_arg:Message=CommandArg()):
    sarg=str(command_arg).strip()
    if sarg=="":
        await PlayerSongInfo.finish("⭐未检测到字符输入⭐",reply_message=True)
    user_id=str(event.get_user_id())
    post_data={"qq":user_id}
    player_data=await get_playerdata(token,post_data)
    alias_data=get_aliasdata()
    music_data=get_musicdata()
    image_ba64=await draw_achi(sarg,alias_data,music_data,player_data)
    await PlayerSongInfo.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

#====================分割线====================

async def b50_request(post_data):
    async with aiohttp.request("POST","https://www.diving-fish.com/api/maimaidxprober/query/player",json=post_data) as resp:
        b50_details=await resp.json()
        if resp.status==400:
            return 400,None
        elif resp.status==403:
            return 403,None
        return 0,b50_details

def compute_rank(ra:int,achievement:float):
    if achievement<10.0:
        baseRa=0.0
    elif achievement<20.0:
        baseRa=1.6
    elif achievement<30.0:
        baseRa=3.2
    elif achievement<40.0:
        baseRa=4.8
    elif achievement<50.0:
        baseRa=6.4
    elif achievement<60.0:
        baseRa=8.0
    elif achievement<70.0:
        baseRa=9.6
    elif achievement<75.0:
        baseRa=11.2
    elif achievement<80.0:
        baseRa=12.0
    elif achievement<90.0:
        baseRa=12.8
    elif achievement<94.0:
        baseRa=13.6
    elif achievement<97.0:
        baseRa=16.8
    elif achievement<98.0:
        baseRa=20.0
    elif achievement<99.0:
        baseRa=20.3
    elif achievement<99.5:
        baseRa=20.8
    elif achievement<100.0:
        baseRa=21.1
    elif achievement<100.5:
        baseRa=21.6
    elif achievement>=100.5:
        baseRa=22.4
        achievement=100.5
    str_ds=str(ra/((achievement/100)*baseRa)+0.1)
    return decimal.Decimal(str_ds).quantize(decimal.Decimal("0.0"))

def compute_board(ra:int):
    achi_list=[97.0,98.0,99.0,99.5,100.0,100.5]
    out_list=[]
    for info in achi_list:
        t=compute_rank(ra,info)
        if t>15:
            t="----"
        out_list.append(t)
    return f"{out_list[0]} {out_list[1]}  {out_list[2]}  {out_list[3]}   {out_list[4]}   {out_list[5]}"

def get_song(b15min,b35min,music_data,player_data):
    record_data=player_data["records"]
    ds_list=[compute_rank(b15min,100.0),compute_rank(b15min,100.5),compute_rank(b35min,100.0),compute_rank(b35min,100.5)]
    rand_list=[]
    return_dict={}
    lv_dict={}
    for ds in ds_list:
        cache_list=[]
        for info in music_data:
            lv=0
            Now_Info=music_data[info]
            ds_l=Now_Info[13]
            for ds_info in ds_l:
                if float(ds_info)<ds and float(ds_info)+0.2>=ds:
                    cache_list.append(info)
                    lv+=1
                    lv_dict[info]=[lv]
                    break
                else:
                    lv+=1
                    pass
        for rec in record_data:
            if float(rec["ds"])<ds and float(rec["ds"])+0.2>=ds and float(rec["achievements"])>=100.5:
                try:
                    cache_list.remove(str(rec["song_id"]))
                except:
                    pass
        for sid in cache_list:
            if sid in rand_list:
                pass
            else:
                rand_list.append(sid)
    if len(rand_list)==0:
        return_dict=[]
    elif len(rand_list)<=4:
        return_dict=rand_list
    else:
        for _count in range(4):
            rand_num=random.randint(0,len(rand_list)-1)
            rand_sid=rand_list[rand_num]
            return_dict[rand_sid]=[lv_dict[rand_sid][0]]
    return return_dict

async def draw_broder(b50_data,player_data,music_data):
    charts=b50_data["charts"]
    b15info=charts["dx"]
    b15max=b15info[0]["ra"]
    b15min=b15info[len(b15info)-1]["ra"]
    b35info=charts["sd"]
    b35max=b35info[0]["ra"]
    b35min=b35info[len(b35info)-1]["ra"]
    sum_b15=0
    sum_b35=0
    for element in b15info:
        sum_b15+=element["ra"]
    for element in b35info:
        sum_b35+=element["ra"]
    b15_board=compute_board(b15min)
    b35_board=compute_board(b35min)
    r_list=get_song(b15min,b35min,music_data,player_data)
    bg=Image.open(f"./{path[0]}/src/Pic/analyse_base.png")
    font_big=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",85)
    font_mid=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",55)
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",25)
    board_text=ImageDraw.Draw(bg)
    board_text.text((250,450),f"B15地板  {b15_board}",(255,94,128),font_big,stroke_width=5,stroke_fill=(247,198,220))
    board_text.text((250,550),f"B35地板  {b35_board}",(255,94,128),font_big,stroke_width=5,stroke_fill=(247,198,220))
    board_text.text((250,650),f"天花板ra:{b35max}/{b15max}  地板ra:{b35min}/{b15min}  (B35/B15)",(255,94,128),font_big,stroke_width=5,stroke_fill=(247,198,220))
    board_text.text((250,750),f"底分组成:{sum_b35}+{sum_b15}={sum_b35+sum_b15}",(255,94,128),font_big,stroke_width=5,stroke_fill=(247,198,220))
    if len(r_list)==0:
        board_text.text((305,1525),"★你太厉害了,小圆已经不知道给你推荐什么歌了,推推自己喜欢的歌吧!★",(255,94,128),font_mid,stroke_width=5,stroke_fill=(247,198,220))
    else:
        print(r_list)
        pl_data=player_data["records"]
        s_base=Image.open(f"./{path[0]}/src/Pic/analyse_sbase.png")
        x=350
        for r_sid in r_list.keys():
            bg.paste(s_base,(x,1300),s_base)
            title=music_data[r_sid][0]
            sid=music_data[r_sid][1]
            url=music_data[r_sid][2]
            ds_str=music_data[r_sid][12]
            if len(title)>13:
                title=title[0:12]+"..."
            down_songpic(sid,url)
            cover=Image.open(f"./{path[0]}/src/Song_Pic/{sid}.png")
            cover_re=cover.resize((252,252))
            bg.paste(cover_re,(x+44,1340),cover_re)
            song_text=ImageDraw.Draw(bg)
            song_text.text((x+25,1635),title,(255,255,255),font)
            song_text.text((x+25,1675),ds_str,(255,255,255),font)
            song_text.text((x+230,1600),f"ID:{sid}",(255,255,255),font)
            drawed=0
            for info in pl_data:
                pl_sid=info["song_id"]
                achi=str(info["achievements"])
                index=info["level_index"]
                if r_sid==str(pl_sid) and index==r_list[r_sid][0]-1:
                    song_text.text((x+25,1715),achi+"%",(0,0,0),font)
                    drawed=1
            if drawed==1:
                pass
            else:
                song_text.text((x+23,1715),"你还没有游玩这首歌的推荐难\n度哦",(0,0,0),font)
            print(drawed)
            x+=380
    out_buffer=BytesIO()   
    bg.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    await analyse.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

analyse=on_command("分析底分",priority=10)
@analyse.handle()
async def analyse_fanc(event:Event):
    userid=event.get_user_id()
    post_data={"qq":str(userid),"b50":True}
    post_data2={"qq":str(userid)}
    status,b50_details=await b50_request(post_data)
    player_data=await get_playerdata(token,post_data2)
    music_data=get_musicdata()
    if status==400:
        await analyse.finish("⭐小圆没有找到该玩家⭐",reply_message=True)
    elif status==403:
        await analyse.finish("⭐该玩家设置了隐私,无法分析⭐",reply_message=True)
    else:
        await draw_broder(b50_details,player_data,music_data)