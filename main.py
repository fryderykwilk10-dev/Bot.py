import discord
from discord.ext import commands
import asyncio
import datetime

TOKEN = "MTQ2Njc4Njc4MDAwNjA1NjE1NQ.GezM5x.wkVRXBw33CYmupqJvnpVD9R9BlWWID0ijSXPe0"

RATE = 4300
MIN_AMOUNT = 10

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# ===== LEGIT CHECK ======
# =========================

class LegitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ LEGIT", style=discord.ButtonStyle.success)
    async def legit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "✅ Dziękujemy za opinię!",
            ephemeral=True
        )

    @discord.ui.button(label="🟥 FAKE", style=discord.ButtonStyle.danger)
    async def fake(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.user.timeout(datetime.timedelta(days=7))
            await interaction.response.send_message(
                "🟥 Otrzymałeś timeout na 7 dni.",
                ephemeral=True
            )
        except:
            await interaction.response.send_message(
                "❌ Nie mogę nadać timeoutu (sprawdź uprawnienia bota).",
                ephemeral=True
            )

@bot.tree.command(name="legit", description="Panel LEGIT CYGUS MARKET")
async def legit(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🍒 CYGUS MARKET » CZY LEGIT?",
        description="Kliknij przycisk poniżej jeżeli jesteśmy **legit!**",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=LegitView())

# =========================
# ===== TICKET SYSTEM =====
# =========================

class TicketModal(discord.ui.Modal, title="Nowy Ticket"):
    amount = discord.ui.TextInput(label="Kwota (zł)", required=True)
    payment = discord.ui.TextInput(label="Metoda płatności", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.followup.send("❌ Kwota musi być liczbą", ephemeral=True)
            return

        if amount < MIN_AMOUNT:
            await interaction.followup.send(
                f"❌ Minimalna kwota to {MIN_AMOUNT} zł",
                ephemeral=True
            )
            return

        cash = amount * RATE

        category = discord.utils.get(interaction.guild.categories, name="🎟️ Tickety")
        if category is None:
            category = await interaction.guild.create_category("🎟️ Tickety")

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category
        )

        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)

        embed = discord.Embed(title="🎟️ Nowy Ticket", color=discord.Color.green())
        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
        embed.add_field(name="Kwota", value=f"{amount} zł", inline=True)
        embed.add_field(name="Przeliczenie", value=f"{cash:,}$", inline=True)
        embed.add_field(name="Płatność", value=self.payment.value, inline=False)

        await channel.send(embed=embed, view=TicketButtons(amount))
        await interaction.followup.send(
            f"✅ Ticket utworzony: {channel.mention}",
            ephemeral=True
        )

class TicketButtons(discord.ui.View):
    def __init__(self, amount):
        super().__init__(timeout=None)
        self.amount = amount

    @discord.ui.button(label="🔒 Przejmij Ticket", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"✅ Ticket przejęty przez {interaction.user.mention}\n"
            f"💰 Sprzedaż: **{self.amount} zł**"
        )

    @discord.ui.button(label="❌ Zamknij", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket zostanie zamknięty za 5s")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Stwórz Ticket", style=discord.ButtonStyle.success)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

@bot.tree.command(name="ticket-panel", description="Panel ticketów")
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Ticket System",
        description="Kliknij przycisk, aby stworzyć ticket",
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed, view=TicketPanel())

# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ Bot online | Ticket + Legit gotowe")

bot.run(TOKEN)
