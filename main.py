from bs4 import BeautifulSoup
import discord
from dotenv import load_dotenv
from io import BytesIO
import os
import pickledb
from PIL import Image, ImageDraw, ImageFont
import random
import requests
import time
from webserver import keep_alive

### Import Services
from services.stackoverflow import get_stackoverflow_result

db = pickledb.load('isclub.db', False)
db.set("IS CLUB", {
                'channel_target': 1131453777313009684,
                'channel_roadmap': 1132260760333078538,
                'channel_networking': 1129602717422211082,
                'channel_qna': 1131468926899990538,
                'admin_role': 1117415326498422834
                })

class ISClubClient(discord.Client):

    async def on_ready(self):
        """
        Event on discord whenever discord bot successfully login
        """
        print(f'Successfully logged on as {self.user}!')
        
    # Only for IS CLUB
    async def on_member_join(self, member):
        """
        Event on discord that will trigger anytime new member join the server 
        """
        channel_target = self.get_channel(db.get('IS CLUB')['channel_target'])
        channel_roadmap = self.get_channel(db.get('IS CLUB')['channel_roadmap'])
        channel_networking = self.get_channel(db.get('IS CLUB')['channel_networking'])
        channel_qna = self.get_channel(db.get('IS CLUB')['channel_qna'])
        
        with BytesIO() as image_binary:  
            self.generate_img(str(member)).save(image_binary, 'PNG')
            image_binary.seek(0)
            await channel_target.send(file=discord.File(fp=image_binary, filename='image.png'))
        
        await member.send(
            f"""
            Welcome to the **IS Club** community, {member.mention}! :handshake:

**IS Club** dibuat dengan harapan mahasiswa SI dapat menemukan bidang yang diminati dan ditekuni, jadi buat komunitas ini menjadi tempat yang nyaman untuk belajar :innocent:
            > **GUIDELINE**
            > You can introduce yourself in channel {channel_networking.mention}
            > You can see the learning roadmaps here {channel_roadmap.mention}
            > For further questions, you can ask at {channel_qna.mention}
            """)
        
        
    async def on_message(self, message):
        """
        Event on discord that will trigger anytime user interact in the chat channel in a spesific command
        """

        if message.author == self.user:
            return
        
        if message.content.startswith('>add-server'):
            server = message.guild.name
            if db.get(server):
                await message.channel.send(f'{server} has already in bot database')
                return

            if not db.get(server):
                db.set(server, {
                'channel_target': 1131453777313009684,
                'channel_roadmap': 1132260760333078538,
                'channel_networking': 1129602717422211082,
                'channel_qna': 1131468926899990538,
                'admin_role': 1117415326498422834
                })
                if db.get(server): await message.channel.send(f'{server} has been added to bot database') 
            
            else:
                await message.channel.send(f'failed to add {server} to database')
        
        if message.content.startswith('>get-server-info'):
            server_info = db.get(message.guild.name)
            if server_info:
                await message.channel.send(f'Server Name\t:\t{message.guild.name}\nAttributes\t\t:\t{server_info}')
                return
            await message.channel.send("Add your server to bot database by command `>add-server`")

        if message.content.startswith('>update'):
            role = message.guild.get_role(1117415326498422834) # get admin id so that only admin can access the command
            
            if role not in message.author.roles:
                return
            
            try:
                msg = ' '.join(message.content.split()[1:])
            except:
                return
            
            server = message.guild.name
            channel, id = msg.split()
            db.get(server)[channel] = int(id)

            if db.get(server)[channel] == int(id):
                await message.channel.send(f'{channel} in {server} has been updated to {id}')
            else:
                await message.channel.send(f'failed to update {channel} in {server}')

        if message.content.startswith('>delete'):
            role = message.guild.get_role(1117415326498422834) # get admin id so that only admin can access the command
            
            if role not in message.author.roles:
                return
            
            msg = ' '.join(message.content.split()[1:])
            server = message.guild.name
            channel = msg
            if db.get(server)[channel]:
                db.get(server)[channel] = None
            
            if db.get(server)[channel] is None: await message.channel.send(f'{channel} on server {server} has been deleted')

        if message.content.startswith('>jokes'):
            content = await self.get_jokes()
            await message.channel.send(content)

        if message.content.startswith('>img'):
            msg = ' '.join(message.content.split()[1:])
            image_url = await self.get_image(msg)
            if not image_url:
                await message.channel.send('no image found, try again.')
                return
            
            with BytesIO() as image_binary:
                Image.open(requests.get(image_url, stream=True).raw).save(image_binary, 'PNG')
                image_binary.seek(0)
                await message.channel.send(file=discord.File(fp=image_binary, filename=f'{msg}.png'))

            return
                
        
        if message.content.startswith('>info'):
            content = f"""
> **IS Club Bot Commands**
> `>info`
> Get list of commands
> 
> `>jokes` 
> Get random dad jokes
> 
> `>img [search]`
> Get random images based on user input
"""
            await message.channel.send(content)

        
        if message.content.startswith('>admin-privilege-1991'):
            role = message.guild.get_role(1117415326498422834) # get admin id so that only admin can access the command
            
            if role not in message.author.roles:
                return
            
            content = f"""
> **IS Club Bot Commands (Admin Only)**
> 
> `>update [channel_target, channel_roadmap, channel_networking, channel_qna] [id]`
> Update channel id in the discord bot database
> 
> `>get-server-info`
> Get channel loaded in the bot database
> 
> `>delete [channel_target, channel_roadmap, channel_networking, channel_qna]`
> Delete channel id saved in discord bot database
> 
> `>update [admin_role] [id]`
> Update admin role id in the discord bot database
"""

            await message.channel.send(content)
            
        if message.content.startswith('>so'):
            query = message.content[len('>so '):].strip()
            response = get_stackoverflow_result(query)
            
            if 'items' in response:
                results = response['items'][:5]
                if results:
                    reply = 'Here are some relevant questions from Stack Overflow:\n'
                    for i, result in enumerate(results):
                        title = result['title']
                        link = result['link']
                        reply += f'{i}. [{title}]({link})\n'
                else:
                    reply = 'Sorry, no relevant questions found. Try a different query.'
            else:
                reply = 'Sorry, there was an error fetching results. Please try again later.'
            
            await message.channel.send(reply)
        

    async def get_jokes(self):
        """
        HTML Request to external endpoint to get random dad joke   
        """
        header = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36',
                'Accept': 'application/json',
            }
        
        time.sleep(2)
        try:
            fetch = requests.get('https://icanhazdadjoke.com/', headers=header)
            content = fetch.json()['joke']
        except:
            content = "can't connect with the endpoint."

        return content
    
    async def get_image(self, user_input):
        """
        Scraping the website om IMGUR using beautifulsoup to get random image according to certain user input   
        """
        time.sleep(2)
        try:
            data = requests.get(f'https://imgur.com/search?q={user_input}', headers={
                    'User-Agent': 'Chrome/115.0.0.0',
                }).content
            soup = BeautifulSoup(data, 'html.parser')
            images = soup.find_all(class_='post')
            img = images[random.randint(0, len(images)-1)].find('img')

        except:
            return False
        
        return 'https:' + img['src']
    
    def generate_img(self, username):
        width = 512
        height = 256
        message = f"Welcome to IS Club"

        img = Image.new("RGB", size=(width, height), color='#313338')
        font = ImageFont.truetype('assets/font/Poppins-Regular.ttf',size=30)

        drawnImg = ImageDraw.Draw(img)

        _, _, textWidth, textHeight = drawnImg.textbbox((0, 0), message, font=font)
        _, _, textWidth2, textHeight2 = drawnImg.textbbox((0, 0), username, font=font)
        yText = ((height - textHeight) / 2)-(textHeight2/2)
        drawnImg.text(((width - textWidth) / 2, yText), message, font=font, fill=(255, 255, 255))
        drawnImg.text(((width-textWidth2)/2, yText+textHeight2), username, font=font, fill=(255, 255, 255))

        return img

# Configurations
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = ISClubClient(intents=intents)
load_dotenv()
keep_alive()
client.run(os.getenv('TOKEN'))