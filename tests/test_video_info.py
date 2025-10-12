import pytest

from video_info import VideoInfo

video_info = VideoInfo()

VALID_YOUTUBE_URLS = ["https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                      "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
                      "http://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                      "http://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
                      "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1"]

INVALID_YOUTUBE_URLS = ["https://www.google.com/", "http://www.google.com/", "https://vimeo.com/123456",
                        "ftp://youtube.com/watch?v=test", ]

TEST_VIDEO_INFO = ["Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)", "Rick Astley",
                   "The official video for “Never Gonna Give You Up” by Rick Astley. \n\nNever: The Autobiography 📚 OUT NOW! \nFollow this link to get your copy and listen to Rick’s ‘Never’ playlist ❤️ #RickAstleyNever\nhttps://linktr.ee/rickastleynever\n\n“Never Gonna Give You Up” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick’s native UK and the US Billboard Hot 100.  It also won the Brit Award for Best single in 1988. Stock Aitken and Waterman wrote and produced the track which was the lead-off single and lead track from Rick’s debut LP “Whenever You Need Somebody”.  The album was itself a UK number one and would go on to sell over 15 million copies worldwide.\n\nThe legendary video was directed by Simon West – who later went on to make Hollywood blockbusters such as Con Air, Lara Croft – Tomb Raider and The Expendables 2.  The video passed the 1bn YouTube views milestone on 28 July 2021.\n\nSubscribe to the official Rick Astley YouTube channel: https://RickAstley.lnk.to/YTSubID\n\nFollow Rick Astley:\nFacebook: https://RickAstley.lnk.to/FBFollowID \nTwitter: https://RickAstley.lnk.to/TwitterID \nInstagram: https://RickAstley.lnk.to/InstagramID \nWebsite: https://RickAstley.lnk.to/storeID \nTikTok: https://RickAstley.lnk.to/TikTokID\n\nListen to Rick Astley:\nSpotify: https://RickAstley.lnk.to/SpotifyID \nApple Music: https://RickAstley.lnk.to/AppleMusicID \nAmazon Music: https://RickAstley.lnk.to/AmazonMusicID \nDeezer: https://RickAstley.lnk.to/DeezerID \n\nLyrics:\nWe’re no strangers to love\nYou know the rules and so do I\nA full commitment’s what I’m thinking of\nYou wouldn’t get this from any other guy\n\nI just wanna tell you how I’m feeling\nGotta make you understand\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\nWe’ve known each other for so long\nYour heart’s been aching but you’re too shy to say it\nInside we both know what’s been going on\nWe know the game and we’re gonna play it\n\nAnd if you ask me how I’m feeling\nDon’t tell me you’re too blind to see\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\n#RickAstley #NeverGonnaGiveYouUp #WheneverYouNeedSomebody #OfficialMusicVideo",
                   "3:33", ]


@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_valid_youtube_urls(url: str) -> None:
    """Test that valid YouTube URLs are accepted."""
    assert video_info.validator(url)


@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_invalid_youtube_urls(url: str) -> None:
    """Test that invalid YouTube URLs are rejected."""
    assert not video_info.validator(url)


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
def test_invalid_input_types(invalid_input) -> None:
    """Test that non-string inputs return error message."""
    assert not video_info.validator(invalid_input)


def test_empty_string() -> None:
    """Test that empty string is rejected."""
    assert not video_info.validator("")


@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_clean_valid_urls(url: str) -> None:
    """Test for cleaning valid YouTube URLs."""
    assert (video_info.clean_youtube_url(url) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ")


@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_clean_invalid_urls(url: str) -> None:
    """Test for checking whether cleaning invalid YouTube URLs is rejected."""
    assert video_info.clean_youtube_url(url) is None


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
def test_clean_invalid_input_types(invalid_input) -> None:
    """Test that non-string inputs return error message."""
    assert video_info.clean_youtube_url(invalid_input) is None


def test_cleaning_empty_string() -> None:
    """Test that empty string is rejected."""
    assert not video_info.validator("") == "Invalid link provided."


@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_get_info_valid_urls(url: str) -> None:
    """Test for getting info of a valid YouTube URLs."""
    assert video_info.get_video_info(url) == TEST_VIDEO_INFO


@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_get_info_invalid_urls(url: str) -> None:
    """Test for getting info of a invalid YouTube URLs."""
    assert video_info.get_video_info(url) == "Invalid link provided."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
def test_get_info_invalid_input_types(invalid_input) -> None:
    """Test that non-string inputs return error message."""
    assert video_info.get_video_info(invalid_input) == "Invalid link provided."


def test_video_unavailable() -> None:
    """Test for the video that is unavailable or private."""
    link = "https://youtu.be/test123"
    assert video_info.get_video_info(
        link) == f"Download error (video may be unavailable or private): {video_info.clean_youtube_url(link)}"


def test_get_info_empty_string() -> None:
    """Test that empty string is rejected."""
    assert video_info.get_video_info("") == "Invalid link provided."
