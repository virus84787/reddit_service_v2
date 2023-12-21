import os
import re

import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo

import config
import time
import urllib.request
from datetime import datetime
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from bs4 import BeautifulSoup

import ssl
context = ssl._create_unverified_context()

bot = telebot.TeleBot(config.TOKEN)
dev_chat_id = config.DEV_CHAT_ID
me_chat_id = config.ME_CHAT_ID
download_tool_site = config.DOWNLOAD_TOOL_SITE
download_tool_site_v2 = config.DOWNLOAD_TOOL_SITE_V2


def iri_to_uri(iri):
    parts = urlsplit(iri)
    uri = urlunsplit(
        (
            parts.scheme,
            parts.netloc.encode("idna").decode("ascii"),
            quote(parts.path),
            quote(parts.query, "="),
            quote(parts.fragment),
        )
    )
    return uri


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def get_post_html(iri):
    url = iri_to_uri(iri)
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    )
    retry_count = 1
    url_response = ...
    while retry_count <= 10:
        try:
            time.sleep(0.1)
            url_response = urllib.request.urlopen(req, context=context)
            break
        except Exception as e:
            bot.send_message(dev_chat_id, "Retry - " + str(retry_count))
            retry_count += 1
    response_data = url_response.read().decode("utf-8")
    return response_data


def get_current_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def get_video_hd_link(iri):
    url = iri_to_uri(download_tool_site + iri)
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    url_response = urllib.request.urlopen(req, context=context)
    response_data = url_response.read().decode("utf-8")
    soup = BeautifulSoup(response_data, "html.parser")
    video_links = soup.find_all("a", class_="btn btn-success btn-lg downloadButton")
    video_hd_link = video_links[0]["href"]
    return video_hd_link

def get_video_hd_link_v2(iri):
    url = iri_to_uri(download_tool_site_v2 + iri)
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    url_response = urllib.request.urlopen(req, context=context)
    response_data = url_response.read().decode("utf-8")
    soup = BeautifulSoup(response_data, "html.parser")
    video_links = soup.find_all("a", class_="downloadbutton")
    video_hd_link = video_links[0]["href"]
    return video_hd_link

def get_imgur_video_link(imgur_page_link):
    imgur_page_html = get_post_html(imgur_page_link)
    imgur_soup = BeautifulSoup(imgur_page_html, "html.parser")
    imgur_video_link = imgur_soup.find("meta", {"property": "og:video:secure_url"})[
        "content"
    ]
    return imgur_video_link


def get_chat_identity(message):
    chat_identity = "Chat ID: " + str(message.chat.id) + "\n"
    if message.chat.title:
        chat_identity = chat_identity + "Chat title: " + message.chat.title + "\n"
    if message.from_user.username:
        chat_identity = chat_identity + "Username: " + message.from_user.username + "\n"
    if message.from_user.full_name:
        chat_identity = chat_identity + "Full name: " + message.from_user.full_name + "\n"
    
    return chat_identity

def get_images_capations_dic(images):
    images_capations  = '\n\n'
    images_capations_dic = {}
    img_count = 0
    part_count = 1
    for image in images:
        img_count +=1
        try:
            if image.find("gallery-caption")["image-caption"]:
                images_capations = images_capations + str(img_count) + '. ' + image.find("gallery-caption")["image-caption"] + '\n'
        except Exception as e:
            print("there is no image-caption")
        if img_count % 10 == 0:
            images_capations_dic[part_count] = images_capations
            images_capations = '\n\n'
            img_count = 0
            part_count += 1
    images_capations_dic[part_count] = images_capations
    return images_capations_dic


@bot.message_handler(content_types=["text"])
def get__content(message):
    if (
        "https://www.reddit.com/" in message.text
        or "https://reddit.com/" in message.text
    ):
        chat_identity = get_chat_identity(message)

        try:
            file = open("id.txt", "r")
        except Exception as e:
            file = open("id.txt", "w")
            file.close()
            file = open("id.txt", "r")
        s = file.read()
        id = int(s) if s != "" else 1
        file.close()
        file = open("id.txt", "w")
        file.write(str(id + 1))
        file.close()
        print(
            "-------------------------"
            + "\n"
            + get_current_time()
            + " id: "
            + str(id)
            + " Chat identity: \n"
            + chat_identity
        )
        url_message = message.text
        start_iri = url_message.find("https")
        iri = unquote(url_message[start_iri:])
        print(get_current_time() + " id: " + str(id) + " URL: " + iri)
        try:
            video = None
            post_type = ""
            response_data = get_post_html(iri)
            soup = BeautifulSoup(response_data, "html.parser")

            shreddit_post = soup.find("shreddit-post")

            post_title = shreddit_post["post-title"]
            subreddit_name = shreddit_post["subreddit-prefixed-name"]
            post_type = shreddit_post["post-type"]
            nsfw_flag = shreddit_post("icon-nsfw")
            content_href = shreddit_post["content-href"]

            nsfw = "[NSFW] " if nsfw_flag else ""
            title = subreddit_name + "\n" + nsfw + post_title

            print(get_current_time() + " id: " + str(id) + " Post type: " + post_type)

            if str(message.chat.id) != me_chat_id:
                try:
                    bot.send_message(
                        dev_chat_id,
                        "Chat identity: \n"
                        + chat_identity
                        + "\nPost type: "
                        + post_type
                        + "\nURL: "
                        + iri,
                    )
                except Exception as e:
                    bot.send_message(
                        dev_chat_id,
                        "Chat identity: \n"
                        + chat_identity
                        + "\nPost type: "
                        + post_type
                        + "\nURL: "
                        + iri,
                    )

            if post_type == "crosspost":
                original_link = "https://www.reddit.com" + shreddit_post["content-href"]
                original_post_html = get_post_html(original_link)
                original_post_soup = BeautifulSoup(original_post_html, "html.parser")
                original_post_type = original_post_soup.find("shreddit-post")[
                    "post-type"
                ]
                shreddit_post = original_post_soup.find("shreddit-post")
                post_type = original_post_type
                print(
                    get_current_time()
                    + " id: "
                    + str(id)
                    + " Original post type: "
                    + post_type
                )

            if post_type == "gif" and "https://i.imgur.com/" in content_href:
                post_type = "video"
                print(get_current_time() + " id: " + str(id) + " Post type: gif/imgur")

            if post_type == "video":
                video_hd_link = get_video_hd_link_v2(iri) if get_video_hd_link_v2(iri) else get_video_hd_link(iri)
                try:
                    bot.send_media_group(
                        message.chat.id,
                        [InputMediaVideo(video_hd_link, None, title)],
                        None,
                        message.id,
                    )
                except Exception as e:
                    opener = urllib.request.URLopener()
                    opener.addheader('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')
                    opener.retrieve(video_hd_link, str(id) + ".mp4")
                    video = open(str(id) + ".mp4", "rb")
                    bot.send_media_group(
                        message.chat.id,
                        [InputMediaVideo(video, None, title)],
                        None,
                        message.id,
                    )
                if video:
                    video.close()
                    os.remove(str(id) + ".mp4")

                print(get_current_time() + " id: " + str(id) + " Success: " + post_type)
            elif post_type == "image":
                image_link = content_href
                try:
                    bot.send_media_group(
                        message.chat.id,
                        [InputMediaPhoto(image_link, title)],
                        None,
                        message.id,
                    )
                except Exception as e:
                    bot.send_media_group(
                        message.chat.id,
                        [InputMediaPhoto(image_link, title)],
                        None,
                        message.id,
                    )
                print(get_current_time() + " id: " + str(id) + " Success: " + post_type)
            elif post_type == "gif":
                gif_link = shreddit_post.find("shreddit-player").find("source")["src"]
                try:
                    bot.send_animation(
                        message.chat.id,
                        gif_link,
                        None,
                        title,
                        message.id,
                    )
                except Exception as e:
                    bot.send_animation(
                        message.chat.id, gif_link, None, title, message.id
                    )
                print(get_current_time() + " id: " + str(id) + " Success: " + post_type)
            elif post_type == "gallery":
                images = shreddit_post.find_all("li")
                img_arr = []
                img_count = 0
                part_string = ""
                part_count = 1
                images_capations_dic = get_images_capations_dic(images)
                for image in images:
                    image_link = image.find("a")["href"]
                    if len(img_arr) == 0:
                        if len(images) > 10:
                            part_string = " (Part " + str(part_count) + ")"
                        img_arr.append(InputMediaPhoto(image_link, title + part_string + images_capations_dic[part_count]))
                        part_count += 1
                    else:
                        img_arr.append(InputMediaPhoto(image_link))
                    img_count += 1
                    if img_count == 10:
                        try:
                            bot.send_media_group(
                                message.chat.id, img_arr, None, message.id
                            )
                        except Exception as e:
                            bot.send_media_group(
                                message.chat.id, img_arr, None, message.id
                            )
                        img_arr = []
                        img_count = 0
                if img_arr:
                    try:
                        bot.send_media_group(message.chat.id, img_arr, None, message.id)
                    except Exception as e:
                        bot.send_media_group(message.chat.id, img_arr, None, message.id)
                    print(
                        get_current_time()
                        + " id: "
                        + str(id)
                        + " Success: "
                        + post_type
                    )
            elif post_type == "link":
                external_link = content_href
                if (
                    "https://imgur.com/" in external_link
                    or "https://i.imgur.com/" in external_link
                ):
                    imgur_video_link = get_imgur_video_link(external_link)
                    try:
                        bot.send_media_group(
                            message.chat.id,
                            [InputMediaVideo(imgur_video_link, None, title)],
                            None,
                            message.id,
                        )
                        print(
                            get_current_time() + " id: " + str(id) + " Success: imgur"
                        )
                    except Exception as e:
                        bot.send_media_group(
                            message.chat.id,
                            [InputMediaVideo(imgur_video_link, None, title)],
                            None,
                            message.id,
                        )
                        print(
                            get_current_time() + " id: " + str(id) + " Success: imgur"
                        )
                else:
                    try:
                        bot.reply_to(message, title + "\n\n" + external_link)
                        print(
                            get_current_time()
                            + " id: "
                            + str(id)
                            + " Success: "
                            + post_type
                        )
                    except Exception as e:
                        bot.reply_to(message, title + "\n\n" + external_link)
                        print(
                            get_current_time()
                            + " id: "
                            + str(id)
                            + " Success: "
                            + post_type
                        )
            elif post_type == "text":
                post_textes = shreddit_post.find(
                    "div",
                    {
                        "class": "text-neutral-content md max-h-[253px] overflow-hidden s:max-h-[318px] m:max-h-[337px] l:max-h-[352px] xl:max-h-[452px] text-14"
                    },
                )

                if post_textes:
                    post_text = (
                        remove_html_tags(str(post_textes))
                        .replace("\n\n", "\n")
                        .replace("\n\n", "\n")
                        .replace("\n\n", "\n")
                    )
                else:
                    post_text = ""

                try:
                    bot.send_message(
                        message.chat.id,
                        "*" + title + "*" + "\n" + post_text,
                        reply_to_message_id=message.id,
                        parse_mode="Markdown",
                    )
                except Exception as e:
                    bot.send_message(
                        message.chat.id,
                        "*" + title + "*" + "\n" + post_text,
                        reply_to_message_id=message.id,
                        parse_mode="Markdown",
                    )
                print(get_current_time() + " id: " + str(id) + " Success: " + post_type)
            else:
                url = iri_to_uri(iri)
                file = open("logs_fails.txt", "a")
                file.write(
                    get_current_time()
                    + " id: "
                    + str(id)
                    + "\n"
                    + str(message.chat.id)
                    + "\n"
                    + url
                    + "\n"
                    + "\n"
                )
                file.close()
                try:
                    bot.send_message(
                        message.chat.id,
                        "Supported content for extract not found",
                        None,
                        message.id,
                    )
                except Exception as e:
                    bot.send_message(
                        message.chat.id,
                        "Supported content for extract not found",
                        None,
                        message.id,
                    )
                print(
                    get_current_time()
                    + " id: "
                    + str(id)
                    + ' "Supported content for extract not found"'
                )

        except Exception as e:
            url = iri_to_uri(iri)
            bot.send_message(
                dev_chat_id,
                "Chat identity\n "
                + chat_identity
                + "\nPost type: "
                + post_type
                + "\nURL: "
                + url
                + "\nError: "
                + str(e),
            )
            file = open("logs_errors.txt", "a")
            file.write(
                get_current_time()
                + " id: "
                + str(id)
                + "\n"
                + str(message.chat.id)
                + "\n"
                + url
                + "\n"
                + str(e)
                + "\n"
                + "\n"
            )
            file.close()
            print(
                get_current_time()
                + " id: "
                + str(id)
                + " something went wrong \n Error details: \n"
                + str(e)
            )

            if video:
                video.close()
                os.remove(str(id) + ".mp4")


bot.polling(none_stop=True)
