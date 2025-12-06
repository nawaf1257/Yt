import discord
from discord import app_commands
from discord.ext import commands

TOKEN = "MTQ0NDc3MzI2MjA3OTk1NTA3NQ.GYJrRP.qEi4aK7NaWELWfnGEl7e2fgMmWL7Gq3-Fi063s"
GUILD_ID = 1443114041018159118
WELCOME_CHANNEL_ID = 1443217219495530647
AUTO_ROLE_ID = 1443215683029569606

# رومات النظام
ROOM_RATE_PEOPLE = 1443123217790144623
ROOM_SUGGESTIONS = 1443913955910094848
ROOM_TICKET_RATE = 1443159868881244295

# رومات التقديم والرتب
APPLICATION_SEND_CHANNEL = 1443582862266732665
APPLICATION_RECEIVE_CHANNEL = 1443583543052861470
APPLICATION_ACCEPT_ROLE = 1443582548557959472
APPLICATION_REJECT_ROLE = 1443582599636324362

ALLOWED_ROLES = [
    1443582249755869338,
    1444759657607598222,
    1443118374451417088,
    1444336060648656997,
    1444335457893613618,
    1443214784676888638,
    1444337341169668177
]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # نستخدم App Commands (Slash Commands)

user_xp = {}

# ===========================
# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"{bot.user} شغال الآن!")
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    activity = discord.Game(name="/help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

# ===========================
# ترحيب تلقائي + إعطاء رتبة
@bot.event
async def on_member_join(member):
    guild = bot.get_guild(GUILD_ID)
    role = guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"هلا {member.mention}, نورت السيرفر!")

# ===========================
# نظام الرسائل الخاصة بالآراء والتقييمات + زيادة XP + التقديم
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_xp[message.author.id] = user_xp.get(message.author.id, 0) + 10

    # تقييم الأشخاص
    if message.channel.id == ROOM_RATE_PEOPLE:
        words = message.content.split(" ", 1)
        if len(words) < 2:
            await message.channel.send("⚠️ اكتب: @الشخص رأيك فيه", delete_after=5)
            await message.delete()
            return
        target = message.mentions[0] if message.mentions else words[0]
        text = words[1] if message.mentions else message.content.replace(words[0], "", 1).strip()
        await message.delete()
        sent = await message.channel.send(
            f"📌 **تقييم جديد!**\n"
            f"👤 **الكاتب:** {message.author.mention}\n"
            f"🎯 **المقيّم له:** {target.mention}\n"
            f"💬 **النص:** {text}"
        )
        await sent.add_reaction("👍")
        await sent.add_reaction("👎")
        return

    # الاقتراحات
    if message.channel.id == ROOM_SUGGESTIONS:
        await message.delete()
        sent = await message.channel.send(
            f"📝 **اقتراح جديد!**\n"
            f"👤 **من:** {message.author.mention}\n"
            f"💡 **النص:** {message.content}"
        )
        await sent.add_reaction("👍")
        await sent.add_reaction("👎")
        return

    # تقييم التذاكر
    if message.channel.id == ROOM_TICKET_RATE:
        await message.delete()
        sent = await message.channel.send(
            f"🎟️ **تقييم تذكرة**\n"
            f"👤 **المستخدم:** {message.author.mention}\n"
            f"💬 **التقييم:** {message.content}"
        )
        await sent.add_reaction("👍")
        await sent.add_reaction("👎")
        return

    # التقديم
    if message.channel.id == APPLICATION_SEND_CHANNEL:
        await message.delete()
        channel = bot.get_channel(APPLICATION_RECEIVE_CHANNEL)
        embed = discord.Embed(
            title="📩 طلب تقديم جديد",
            description=message.content,
            color=discord.Color.blue()
        )
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        row = discord.ui.View()
        accept_button = discord.ui.Button(label="قبول", style=discord.ButtonStyle.green)
        reject_button = discord.ui.Button(label="رفض", style=discord.ButtonStyle.red)

        async def accept_callback(interaction: discord.Interaction):
            await message.author.add_roles(message.guild.get_role(APPLICATION_ACCEPT_ROLE))
            await interaction.response.send_message(f"{message.author.mention} تم قبول الطلب", ephemeral=True)
            await message.author.send(f"✅ تم قبول طلبك! تم إعطائك رتبة القبول.")

        async def reject_callback(interaction: discord.Interaction):
            await message.author.add_roles(message.guild.get_role(APPLICATION_REJECT_ROLE))
            await interaction.response.send_message(f"{message.author.mention} تم رفض الطلب", ephemeral=True)
            await message.author.send(f"❌ تم رفض طلبك! تم إعطائك رتبة الرفض.")

        accept_button.callback = accept_callback
        reject_button.callback = reject_callback
        row.add_item(accept_button)
        row.add_item(reject_button)

        await channel.send(embed=embed, view=row)
        return

    await bot.process_commands(message)

# ===========================
# أوامر البوت (بروفايل، XP، Rank، إعطاء/إزالة رتبة، هايد/اظهار)
@tree.command(name="بروفايل", description="عرض بروفايل العضو", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="اختر العضو")
async def بروفايل(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"بروفايل {member}", color=discord.Color.blue())
    embed.add_field(name="الاسم", value=member.name, inline=True)
    embed.add_field(name="الأيدي", value=member.id, inline=True)
    embed.set_thumbnail(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="xp", description="عرض XP العضو", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="اختر العضو")
async def xp(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    xp_value = user_xp.get(member.id, 0)
    await interaction.response.send_message(f"{member.mention} لديك {xp_value} XP")

@tree.command(name="rank", description="عرض Rank العضو", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="اختر العضو")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    xp_value = user_xp.get(member.id, 0)
    rank_value = xp_value // 100
    await interaction.response.send_message(f"{member.mention} رتبتك {rank_value}")

@tree.command(name="اعطاء", description="إعطاء رتبة للعضو", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="اختر العضو", role="اختر الرتبة")
async def اعطاء(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("⚠️ ليس لديك إذن لإعطاء الرتب.", ephemeral=True)
        return
    await member.add_roles(role)
    await interaction.response.send_message(f"{member.mention} تم إعطاءك رتبة {role.name}")

@tree.command(name="ازاله", description="إزالة رتبة من العضو", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="اختر العضو", role="اختر الرتبة")
async def ازاله(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("⚠️ ليس لديك إذن لإزالة الرتب.", ephemeral=True)
        return
    await member.remove_roles(role)
    await interaction.response.send_message(f"{member.mention} تم إزالة رتبة {role.name}")

@tree.command(name="هايد", description="إخفاء الروم الحالي", guild=discord.Object(id=GUILD_ID))
async def هايد(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("⚠️ ليس لديك إذن لإدارة القنوات.", ephemeral=True)
        return
    await channel.set_permissions(interaction.guild.default_role, read_messages=False)
    await interaction.response.send_message(f"{channel.mention} تم إخفاؤها", ephemeral=True)

@tree.command(name="اظهار", description="إظهار الروم الحالي", guild=discord.Object(id=GUILD_ID))
async def اظهار(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("⚠️ ليس لديك إذن لإدارة القنوات.", ephemeral=True)
        return
    await channel.set_permissions(interaction.guild.default_role, read_messages=True)
    await interaction.response.send_message(f"{channel.mention} تم إظهارها", ephemeral=True)

# ===========================
# قائمة الأوامر مع عرض التقديم
@tree.command(name="اوامر", description="عرض قائمة أوامر البوت", guild=discord.Object(id=GUILD_ID))
async def اوامر(interaction: discord.Interaction):
    if not any(role.id in ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("⚠️ أنت لا تملك رتبة تسمح لك باستخدام هذا الأمر.", ephemeral=True)
        return

    embed = discord.Embed(title="📜 قائمة أوامر البوت", color=discord.Color.blue())
    embed.add_field(name="/بروفايل @عضو", value="عرض بروفايل العضو (الاسم، ID، الصورة)", inline=False)
    embed.add_field(name="/xp @عضو", value="عرض XP العضو", inline=False)
    embed.add_field(name="/rank @عضو", value="عرض Rank العضو المستمد من XP", inline=False)
    embed.add_field(name="/اعطاء @عضو @رتبة", value="إعطاء رتبة للعضو", inline=False)
    embed.add_field(name="/ازاله @عضو @رتبة", value="إزالة رتبة من العضو", inline=False)
    embed.add_field(name="/هايد", value="إخفاء الروم الحالي عن الأعضاء", inline=False)
    embed.add_field(name="/اظهار", value="إظهار الروم الحالي للأعضاء", inline=False)
    embed.add_field(name="روم تقييم الأشخاص", value="اكتب: @عضو رأيك فيه → يحذف الرسالة ويضيفها مع 👍 👎", inline=False)
    embed.add_field(name="روم الاقتراحات", value="اكتب اقتراحك → يحذف الرسالة ويضيفها مع 👍 👎", inline=False)
    embed.add_field(name="روم تقييم التذاكر", value="اكتب تقييم التذكرة → يحذف الرسالة ويضيفها مع 👍 👎", inline=False)
    embed.add_field(name="نظام التقديم", value=f"ارسل طلبك في روم <#{APPLICATION_SEND_CHANNEL}> → يرسل للبوت مع أزرار قبول/رفض", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(TOKEN)