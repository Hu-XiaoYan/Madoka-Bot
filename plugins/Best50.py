from nonebot import on_command,get_driver
path=get_driver().config.bot_path
from nonebot.adapters.onebot.v11 import MessageSegment,Message,Event
from nonebot.params import CommandArg
import os,urllib.request,json,sqlite3,aiohttp,base64
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO

async def ingore_rule(event):
    ingore_groups=["716163111","1164911051"]
    groupid=event.get_session_id().split("_")[1]
    for element in ingore_groups:
        if element==groupid:
            return False
    return True

async def b50_request(post_data):
    async with aiohttp.request("POST","https://www.diving-fish.com/api/maimaidxprober/query/player",json=post_data) as resp:
        b50_details=await resp.json()
        if resp.status==400:
            return 400,None
        elif resp.status==403:
            return 403,None
        return 0,b50_details

async def check_database(username:str):
    conn=sqlite3.connect(f"./{path[0]}/src/Madoka_Bot.db")
    cur=conn.cursor()
    cur.execute(f"SELECT * FROM B50_Setting WHERE USERNAME='{username}'")
    _cur=cur.fetchall()
    if len(_cur)==0:
        pass
    else:
        for _count in range(len(_cur)):
            getting=_cur[_count]
            name=getting[0]
            plate=getting[1]
            sub=getting[2]
            dplate=getting[3]
            icon=getting[4]
            if name==username:
                cur.close()
                conn.commit()
                return plate,sub,dplate,icon
    cur.execute(f"INSERT INTO B50_Setting (USERNAME) VALUES ('{username}')")
    cur.close()
    conn.commit()
    return -1,-1,0,-1

def draw_rating(rating:int,bg):
    rating_list=list(str(rating))
    rating_list.reverse()
    z=0
    for element in rating_list:
        num=Image.open(f"./{path[0]}/src/Pic/{element}.png")
        x=z*26
        bg.paste(num,[558-x,70],num)
        z+=1

def down_songpic(sid:str,url:str):
    if os.path.exists(f"./{path[0]}/src/Song_Pic")==False:
        os.makedirs(f"./{path[0]}/src/Song_Pic")
    if os.path.exists(f"./{path[0]}/src/Song_Pic/{sid}.png")==False:
        urllib.request.urlretrieve(url,f"./{path[0]}/src/Song_Pic/{sid}.png")

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

def return_ra_bg(rating:int):
    if rating<1000:
        return "white"
    elif rating<2000:
        return "blue"
    elif rating<4000:
        return "green"
    elif rating<7000:
        return "orange"
    elif rating<10000:
        return "red"
    elif rating<12000:
        return "murasaki"
    elif rating<13000:
        return "copper"
    elif rating<14000:
        return "silver"
    elif rating<14500:
        return "gold"
    elif rating<15000:
        return "platinum"
    else:
        return "rainbow"

def return_dx_star(min:int,max:int):
    final=min/max*100
    final_round=round(final,2)
    if final_round<85:
        return 0
    elif final_round<90.00:
        return 1
    elif final_round<93.00:
        return 2
    elif final_round<95.00:
        return 3
    elif final_round<97.00:
        return 4
    else:
        return 5

async def generate_best50(b50_data):
    song_info=b50_data["charts"]
    rating=b50_data["rating"]
    nickname=b50_data["nickname"]
    realname=b50_data["username"]
    b15info=song_info["dx"]
    b35info=song_info["sd"]
    gp=b50_data["plate"]
    rank=b50_data["additional_rating"]
    if len(b15info)==0 and len(b35info)==0:
        await Best50.finish("⭐小圆发现你没有导入数据哦⭐",reply_message=True)
    p,s,d,i=await check_database(realname)
    musicdata=get_musicdata()
    img=Image.open(f"./{path[0]}/src/Pic/best50_bg.png")
    nameplate,frame,icon=draw_userinfo(str(p),str(s),gp,str(d),int(rank),str(i))
    sub_resize=frame.resize([2200,921])
    img.paste(sub_resize,[0,0])
    nameplate_resize=nameplate.resize([1440,232])
    img.paste(nameplate_resize,[40,40],nameplate_resize)
    resize_icon=icon.resize([232,232])
    img.paste(resize_icon,[40,40],resize_icon)
    ra_plate=return_ra_bg(rating)
    ra_open=Image.open(f"./{path[0]}/src/Pic/rating_{ra_plate}.png")
    resize_ra_plate=ra_open.resize([332,65])
    img.paste(resize_ra_plate,[300,52],resize_ra_plate)
    name_base=Image.open(f"./{path[0]}/src/Pic/name_base.png")
    img.paste(name_base,[300,132],name_base)
    usertitle=Image.open(f"./{path[0]}/src/Pic/usertitle.png")
    img.paste(usertitle,[300,212],usertitle)
    mini_rank=Image.open(f"./{path[0]}/src/Pic/rankplate/m{rank}.png")
    mini_rank_resize=mini_rank.resize([133,59])
    img.paste(mini_rank_resize,[525,137],mini_rank_resize)
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",30)
    userinfo=ImageDraw.Draw(img)
    userinfo.text((303,152),f"{nickname}",(255,94,128),font,stroke_width=3,stroke_fill=(247,198,220))
    draw_rating(rating,img)
    draw_best(b15info,img,musicdata,15)
    draw_best(b35info,img,musicdata,35)
    out_buffer=BytesIO()   
    img.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    await Best50.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)

def draw_userinfo(p:str,s:str,gp:str,d:str,rank:int,i:str):
    if i=="-1":
        icon=Image.open(f"./{path[0]}/src/Pic/defaut_icon.png")
    else:
        icon=Image.open(f"./{path[0]}/src/Pic/icon/icon_{i}.png")
    if s=="-1":
        frame=Image.open(f"./{path[0]}/src/Pic/defaut_frame.png")
    else:
        frame=Image.open(f"./{path[0]}/src/Pic/frame/frame_{s}.png")
    if d=="1":
        if rank<11:
            if gp==None:
                nameplate=Image.open(f"./{path[0]}/src/Pic/defaut_nameplate.png")
            elif gp!="":
                nameplate=Image.open(f"./{path[0]}/src/Pic/rankplate/{gp}.png")
            else:
                if p=="-1":
                    nameplate=Image.open(f"./{path[0]}/src/Pic/defaut_nameplate.png")
                else:
                    nameplate=Image.open(f"./{path[0]}/src/Pic/nameplate/nameplate_{p}.png")
            return nameplate,frame
        else:
            nameplate=Image.open(f"./{path[0]}/src/Pic/rankplate/{rank}.png")
            return nameplate,frame
    else: 
        if gp==None:
                nameplate=Image.open(f"./{path[0]}/src/Pic/defaut_nameplate.png")
        elif gp!="":
            nameplate=Image.open(f"./{path[0]}/src/Pic/rankplate/{gp}.png")
        elif gp==None:
                pass
        else:
            if p=="-1":
                nameplate=Image.open(f"./{path[0]}/src/Pic/defaut_nameplate.png")
            else:
                nameplate=Image.open(f"./{path[0]}/src/Pic/nameplate/nameplate_{p}.png")
        return nameplate,frame,icon
    
def draw_best(bestinfo,img,Music_data,best):
    _count=0
    if best==35:
        y=2000
        x=230
    else:
        y=1000
        x=250
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",20)
    font_big=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",30)
    for element in bestinfo:
        if _count>4:
            y+=x
            _count=0 
        level=element["level_label"]
        title=element["title"]
        rate=element["rate"]
        sid=element["song_id"]
        chart_id=element["level_index"]
        ds=element["ds"]
        ra=element["ra"]
        fc=element["fc"]
        fs=element["fs"]
        stype=element["type"]
        achievements=str(element["achievements"])
        dxs=element["dxScore"]
        if len(title)>13:
           title=title[0:13]+"..."
        if level=="Re:MASTER":
            level="ReMASTER"
            color=(0,0,0) 
        else:
            color=(255,255,255)   
        level_bg=Image.open(f"./{path[0]}/src/Pic/{level}_bg.png")
        img.paste(level_bg,(35+(_count*430),y),level_bg)
        songinfo=ImageDraw.Draw(img)
        songinfo.text((180+(_count*430),y+12),title,color,font)
        songinfo.text((180+(_count*430),y+65),achievements+"%",color,font_big)
        rank_img=Image.open(f"./{path[0]}/src/Pic/rank_{rate}.png")
        rank_resize=rank_img.resize([128,60])
        img.paste(rank_resize,[305+(_count*430),y+40],rank_resize)
        id_data=Music_data[str(sid)]
        url=id_data[2]
        dxmax_list=id_data[6]
        dxmax=dxmax_list[chart_id]
        stars=return_dx_star(int(dxs),int(dxmax))
        if stars==0:
            pass
        else:
            star_img=Image.open(f"./{path[0]}/src/Pic/dxstar_{stars}.png")
            star_resize=star_img.resize([28,28])
            img.paste(star_resize,(268+(_count*430),y+107),star_resize)
        dx_info=ImageDraw.Draw(img)
        dx_info.text((185+(_count*430),y+100),f"{dxs}/{dxmax}",(0,0,0),font)
        dx_info.text((185+(_count*430),y+122),f"{ds}->{ra}",(0,0,0),font)
        if fc=="":
            pass
        else:
            fc_image=Image.open(f"./{path[0]}/src/Pic/icon_{fc}.png")
            img.paste(fc_image,(291+(_count*430),y+95),fc_image)
        if fs=="":
            pass
        else:
            fs_image=Image.open(f"./{path[0]}/src/Pic/icon_{fs}.png")
            img.paste(fs_image,(345+(_count*430),y+95),fs_image)
        down_songpic(str(sid),str(url))
        song_pic=Image.open(f"./{path[0]}/src/song_Pic/{sid}.png")
        song_pic_resize=song_pic.resize([148,160])
        img.paste(song_pic_resize,(30+(_count*430),y),song_pic_resize)
        if stype=="DX":
            dx_pic=Image.open(f"./{path[0]}/src/Pic/music_dx.png")
            img.paste(dx_pic,(30+(_count*430),y+142),dx_pic)
        else:
            sd_pic=Image.open(f"./{path[0]}/src/Pic/music_sd.png")
            img.paste(sd_pic,(30+(_count*430),y+142),sd_pic)
        _count+=1

Best50=on_command("B50",aliases={"b50"},priority=10,rule=ingore_rule)
@Best50.handle()
async def Best50_fanc(event:Event,command_arg:Message=CommandArg()):
    username=str(command_arg).strip()
    userid=event.get_user_id()
    if username=="":
        post_data={"qq":str(userid),"b50":True}
    else:
        post_data={"username":username,"b50":True}
    status,b50_details=await b50_request(post_data)
    if status==400:
        await Best50.finish("⭐小圆没有找到该玩家⭐",reply_message=True)
    elif status==403:
        await Best50.finish("⭐该玩家设置了隐私⭐",reply_message=True)
    else:
        await generate_best50(b50_details)

Best40=on_command("B40",aliases={"b40"},priority=10,rule=ingore_rule)
@Best40.handle()
async def Best40_fanc():
    await Best40.finish(f"⭐别惦记你那Best40了⭐",reply_message=True)

SetDiy=on_command("设置",priority=10,rule=ingore_rule)
@SetDiy.handle()
async def SetDiy_fanc(event:Event,command_arg:Message=CommandArg()):
    userid=event.get_user_id()
    post_data={"qq":str(userid),"b50":True}
    status,b50_data=await b50_request(post_data)
    if status==400:
        await Best50.finish("⭐小圆没有找到该玩家⭐",reply_message=True)
    elif status==403:
        await Best50.finish("⭐该玩家设置了隐私⭐",reply_message=True)
    else:
        pass
    realname=b50_data["username"]
    args=str(command_arg).strip().split(" ")
    try:
        set_type=args[0]
        if set_type=="恢复":
            pass
        else:
            num=args[1]
            numi=int(num)
    except:
        await SetDiy.finish("⭐参数错误,请检查⭐",reply_message=True)
    async def check():
        try:
            if set_type=="姓名框":
                if numi>80 or numi<0:
                    raise
                return 1
            elif set_type=="底板":
                if numi>80 or numi<0:
                    raise
                return 2
            elif set_type=="真段位优先":
                if numi>1 or numi<0:
                    raise
                return 3
            elif set_type=="头像":
                if numi>100 or numi<0:
                    raise
                return 4
            elif set_type=="恢复":
                return 5
            else:
                raise
        except:
            await SetDiy.finish("⭐参数错误,请检查⭐",reply_message=True)
    conn=sqlite3.connect(f"./{path[0]}/src/Madoka_Bot.db")
    cur=conn.cursor()
    cur.execute(f"SELECT USERNAME FROM B50_Setting WHERE USERNAME='{realname}'")
    _cur=cur.fetchall()
    for _count in range(len(_cur)):
        getting=_cur[_count]
        name=getting[0]
        if name==realname:
            x=await check()
            if x==1:
                cur.execute(f"UPDATE B50_Setting SET PLATE='{num}' WHERE USERNAME='{name}'")
            elif x==2:
                cur.execute(f"UPDATE B50_Setting SET FRAME='{num}' WHERE USERNAME='{name}'")
            elif x==3:
                cur.execute(f"UPDATE B50_Setting SET DPLATE='{num}' WHERE USERNAME='{name}'")
            elif x==4:
                cur.execute(f"UPDATE B50_Setting SET ICON='{num}' WHERE USERNAME='{name}'")
            elif x==5:
                cur.execute(f"UPDATE B50_Setting SET PLATE='-1' WHERE USERNAME='{name}'")
                cur.execute(f"UPDATE B50_Setting SET FRAME='-1' WHERE USERNAME='{name}'")
                cur.execute(f"UPDATE B50_Setting SET DPLATE='0' WHERE USERNAME='{name}'")
                cur.execute(f"UPDATE B50_Setting SET ICON='-1' WHERE USERNAME='{name}'")
            cur.close()
            conn.commit()   
            await SetDiy.finish("⭐设置成功⭐",reply_message=True)  
    await SetDiy.finish("⭐没有在数据库找到该玩家⭐\n⭐请先使用“小圆 B50”将你的玩家数据加入数据库⭐",reply_message=True)

ShowPlateFrame=on_command("展示",priority=10,rule=ingore_rule)
@ShowPlateFrame.handle()
async def ShowPlateFrame_fanc(command_arg:Message=CommandArg()):
    show_type=str(command_arg).strip()
    if show_type=="姓名框":
        await ShowPlateFrame.finish(MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Pic/plates.png"),reply_message=True)
    if show_type=="底板":
        await ShowPlateFrame.finish(MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Pic/frames.png"),reply_message=True)
    if show_type=="头像":
        await ShowPlateFrame.finish(MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Pic/icons.png"),reply_message=True)
    else:
        await ShowPlateFrame.finish("⭐参数错误,请检查⭐",reply_message=True)