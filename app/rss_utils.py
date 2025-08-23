"""
RSS utilities to manage podcast feed.
Compatible with Spotify / Apple / Google Podcasts.
"""

from pathlib import Path
import datetime
import xml.etree.ElementTree as ET

RSS_FILE = Path("feed.xml")

# Register namespaces so ElementTree writes them properly
ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")

def ensure_feed_exists():
    """Create RSS feed if it does not exist yet."""
    if not RSS_FILE.exists():
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")

        # Basic channel metadata
        ET.SubElement(channel, "title").text = "My AI Generated Podcast"
        ET.SubElement(channel, "link").text = "https://my-ai-podcast.s3.us-east-2.amazonaws.com/rss/feed.xml"
        ET.SubElement(channel, "language").text = "pt-BR"
        ET.SubElement(channel, "description").text = "Narrativas criadas com IA em múltiplos estilos."

        # iTunes / Spotify required metadata
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = "joakft"
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit").text = "no"
        ET.SubElement(
            channel,
            "{http://www.itunes.com/dtds/podcast-1.0.dtd}category",
            text="Education"
        )
        ET.SubElement(
            channel,
            "{http://www.itunes.com/dtds/podcast-1.0.dtd}image",
            href="https://my-ai-podcast.s3.us-east-2.amazonaws.com/cover.jpg"
        )

        # Owner info (required)
        owner = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}owner")
        ET.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}name").text = "joakft"
        ET.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}email").text = "joakft@gmail.com"

        tree = ET.ElementTree(rss)
        tree.write(RSS_FILE, encoding="utf-8", xml_declaration=True)


def add_episode(title: str, description: str, audio_url: str, duration: str = "00:03:00"):
    """
    Add an episode to the RSS feed.
    - title: short title of episode
    - description: full text (UTF-8)
    - audio_url: public S3 URL of the mp3
    - duration: HH:MM:SS (optional)
    """
    ensure_feed_exists()

    tree = ET.parse(RSS_FILE)
    root = tree.getroot()
    channel = root.find("channel")

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title

    # Short summary in <description>
    summary = (description[:400] + "...") if len(description) > 400 else description
    ET.SubElement(item, "description").text = summary

    # Full text inside <content:encoded> (CDATA)
    content_el = ET.SubElement(item, "{http://purl.org/rss/1.0/modules/content/}encoded")
    content_el.text = f"<![CDATA[{description}]]>"

    ET.SubElement(item, "pubDate").text = datetime.datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    ET.SubElement(item, "guid").text = audio_url
    ET.SubElement(item, "enclosure", url=audio_url, type="audio/mpeg")
    ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = duration

    tree.write(RSS_FILE, encoding="utf-8", xml_declaration=True)
    return f"Episode '{title}' added to feed.xml"
