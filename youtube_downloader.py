from langchain_community.document_loaders import YoutubeLoader

url = "https://www.youtube.com/watch?v=QsYGlZkevEg"
loader = YoutubeLoader.from_youtube_url(url)

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=QZmnju-fPoo",
    add_video_info=False,
    language=["en"],
    translation="en",
)

documents = loader.load()
doc = str(documents[0])
print(doc)