from discord_webhook import DiscordWebhook


def send_discord_message(message):
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1005086331640234025/KLb-FAYbF3_Wcuwz9HC1PX2RIVPAubQ1Q-dJNmgp8dsqWUYTTBMGaBsa0qBIBGFSjOCv", content=message)
    webhook.execute()

