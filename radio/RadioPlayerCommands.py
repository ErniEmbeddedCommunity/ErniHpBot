from . import RadioPlayer


# if "voice" in msg:
#     if not os.path.exists("voice"):
#         os.makedirs("voice")
#     voiceFile = self.bot.getFile(msg["voice"]["file_id"])
#     self.sender.sendMessage(
#         "Playing your audio over radio at " + str(FmPlayer.freq) + " Hz")
#     self.bot.download_file(
#         voiceFile["file_id"], "voice/" + str(voiceFile["file_id"]) + ".ogg")
#     FmPlayer.play_file(
#         "voice/" + str(voiceFile["file_id"]) + ".ogg")