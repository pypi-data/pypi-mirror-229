import logging

pattern = "%(asctime)s %(levelname)s %(message)s"
# logging.basicConfig(filename="/temp/ai-media-core.log",
#                     format=pattern,
#                     filemode="w")
# logging.basicConfig(format=pattern)

# Create a custom logger
log = logging.getLogger(__name__)

# handler
formatter_handler = logging.StreamHandler()
formatter_handler.setFormatter(logging.Formatter(pattern))
# formatter_handler.setFormatter(LogFormatter(pattern))
log.addHandler(formatter_handler)
# file_handler = logging.FileHandler("/temp/ai-media-core.log", mode="a", encoding="utf-8")
# log.addHandler(file_handler)

# Custom arguments
# log = logging.LoggerAdapter(log, {"qid": (ThreadHolder.get("qid") or "")})

# Setting the threshold of logger
log.setLevel(logging.INFO)
