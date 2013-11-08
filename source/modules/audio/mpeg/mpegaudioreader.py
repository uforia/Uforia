# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#!/usr/bin/env python

# This is the audio module for mp3 and mpeg

# TABLE: title:LONGTEXT, subtitle:LONGTEXT, artist:LONGTEXT, album_artist:LONGTEXT, album:LONGTEXT, track_number:INT, total_tracks:INT, disc_number:INT, total_discs:INT, cdid:INT, publisher:LONGTEXT, composer:LONGTEXT, conductor:LONGTEXT, group_content:LONGTEXT, release_date:TEXT, recording_year:INT(4), bpm:INT, duration_in_seconds:DOUBLE, play_count:INT, terms_of_use:LONGTEXT, language:LONGTEXT, rating:INT(3), genre:LONGTEXT, comment_text:LONGTEXT, comment_description:LONGTEXT, comment_language:LONGTEXT, encoded_by:LONGTEXT, copyright:LONGTEXT, mood:LONGTEXT, compilation:LONGTEXT, user_text:LONGTEXT, user_description:LONGTEXT, lyrics_text:LONGTEXT, lyrics_description:LONGTEXT, lyrics_language:LONGTEXT, image_description:LONGTEXT, image_type:LONGTEXT, image_url:LONGTEXT, chapter_title:LONGTEXT, chapter_subtitle:LONGTEXT, chapter_start_time:TEXT, chapter_end_time:TEXT, chapter_start_pffset:TEXT, chapter_end_offset:TEXT, commercial_url:LONGTEXT, copyright_url:LONGTEXT, artist_url:LONGTEXT, audio_file_url:LONGTEXT, audio_source_url:LONGTEXT, internet_radio_url:LONGTEXT, payment_url:LONGTEXT, publisher_url:LONGTEXT, user_url:LONGTEXT , APEv2_tag:BLOB, XMP:LONGTEXT

# import for external lib eyed3
import sys
import traceback
import eyed3
from mutagen.apev2 import APEv2


def process(fullpath, config, rcontext, columns=None):

    # The whole parse data method is in a try block to catch any exception
    try:
        # Read the audio file and get the two data
        # classes from it (Tag and AudioInfo)
        track = eyed3.load(fullpath)
        track_tag = track.tag
        track_info = track.info

        # A variable to store mutiple strings in a list
        list_of_strings = []

        # Init list
        assorted = []

        # Store the title in the list
        assorted.append(track_tag.title)

        '''
        To get a tag from the audio file we need to set a frame
        in the eyed3 lib. In return we get mutiple frames or NoneType.
        For each frame we get the correct variable and this is stored
        in a list. After the loop we parse all found data into one string,
        this string for example look like: subtitle / subtitle / subtitle

        *The eyed3 lib says that it will never occur that there are
        multiple frames, that is why we store all data in one string,
        but to be sure of this, we still irritate through all frames*

        Because a NoneType can not be irritated we use the "or",
        so when we get a NoneType the for loop uses an empty list.
        Wich will result in an empty string because
        nothing is added to the list.
        '''
        # Store the subtitle in the list
        for subtitle_frame in track_tag.frame_set["TIT3"] or []:
            list_of_strings.append(subtitle_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the artist in the list
        assorted.append(track_tag.artist)

        # Store the album artist in the list
        list_of_strings = []
        for album_artist_frame in track_tag.frame_set["TPE2"] or []:
            list_of_strings.append(album_artist_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the album in the list
        assorted.append(track_tag.album)

        '''
        Some tags return an array or list of items.
        To get the correct data of these lists we first need to know
        if the list is not a NoneType or empty.
        If we don't check this an empty list will result in an exception,
        "[0]" can not be used an such list

        If the list is empty we still need to give something in return
        to the database, so we first define the variable to None.
        '''
        # Store the track_number in the list
        track_number = None
        track_total = None
        if(track_tag.track_num):
            track_number = track_tag.track_num[0]
            track_total = track_tag.track_num[1]
        assorted.append(track_number)
        assorted.append(track_total)

        # Store the disc_number in the list
        disc_number = None
        disc_total = None
        if(track_tag.disc_num):
            disc_number = track_tag.disc_num[0]
            disc_total = track_tag.disc_num[1]
        assorted.append(disc_number)
        assorted.append(disc_total)

        # delete variables
        del track_number, track_total, disc_number, disc_total

        # Store the cd_id in the list
        assorted.append(track_tag.cd_id)

        # Store the publisher in the list
        assorted.append(track_tag.publisher)

        # Store the composer in the list
        list_of_strings = []
        for composer_frame in track_tag.frame_set["TCOM"] or []:
            list_of_strings.append(composer_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the conductor in the list
        list_of_strings = []
        for conductor_frame in track_tag.frame_set["TPE3"] or []:
            list_of_strings.append(conductor_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the group content in the list
        list_of_strings = []
        for group_content_frame in track_tag.frame_set["TIT1"] or []:
            list_of_strings.append(group_content_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the releasedate and the recording year in the list
        assorted.append(track_tag.release_date)
        assorted.append(track_tag.recording_date)

        # Store beats per minute in the list
        assorted.append(track_tag.bpm)

        # Store the duration of the song in the list
        assorted.append(track_info.time_secs)

        # Store the play count of the song in the list
        assorted.append(track_tag.play_count)

        # Store the terms of use in the list
        assorted.append(track_tag.terms_of_use)

        # Store the language in the list
        list_of_strings = []
        for language_frame in track_tag.frame_set["TLAN"] or []:
            list_of_strings.append(language_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the rating in the list
        rating = 0
        for rating in track_tag.popularities:
            rating = rating.rating
        assorted.append(rating)

        # Store the genre in the list
        genre = None
        if(track_tag.genre):
            genre = track_tag.genre.name
        assorted.append(genre)

        # Store the comment data in the list
        comment_description = None
        comment_lang = None
        comment_text = None
        for comment in track_tag.comments:
            comment_description = comment.description
            comment_lang = comment.lang
            comment_text = comment.text
        assorted.append(comment_text)
        assorted.append(comment_description)
        assorted.append(comment_lang)

        # delete variables
        del rating, genre, comment_description, comment_lang, comment_text

        # Store the encoded by in the list
        list_of_strings = []
        for encoded_by_frame in track_tag.frame_set["TENC"] or []:
            list_of_strings.append(encoded_by_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the copyright in the list
        list_of_strings = []
        for copyright_frame in track_tag.frame_set["TCOP"] or []:
            list_of_strings.append(copyright_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the mood in the list
        list_of_strings = []
        for mood_frame in track_tag.frame_set["TMOO"] or []:
            list_of_strings.append(mood_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the compilation in the list
        list_of_strings = []
        for compitation_frame in track_tag.frame_set["TPE4"] or []:
            list_of_strings.append(compitation_frame.text)
        assorted.append(' / '.join(list_of_strings))

        # Store the user text data in the list
        user_text_description = None
        user_text_text = None
        for user_text in track_tag._user_texts:
            user_text_description = user_text.description
            user_text_text = user_text.text
        assorted.append(user_text_text)
        assorted.append(user_text_description)

        # Store the lyrics data in the list
        lyrics_description = None
        lyrics_text = None
        lyrics_lang = None
        for lyric in track_tag.lyrics:
            lyrics_description = lyric.description
            lyrics_text = lyric.text
            lyrics_lang = lyric.lang
        assorted.append(lyrics_text)
        assorted.append(lyrics_description)
        assorted.append(lyrics_lang)

        # Store the image data in the list
        image_description = None
        image_url = None
        image_picturetype = None
        for image in track_tag.images:
            image_description = image.description
            image_url = image.image_url
            image_picturetype = image.picTypeToString(image.picture_type)
        assorted.append(image_description)
        assorted.append(image_picturetype)
        assorted.append(image_url)

        # delete variables
        del user_text_description, user_text_text, lyrics_description
        del lyrics_lang, lyrics_text, image_description, image_url
        del image_picturetype

        # Store the chapter data in the list
        chapter_title = None
        chapter_subtitle = None
        chapter_starttime = None
        chapter_endtime = None
        chapter_startoffset = None
        chapter_endoffset = None
        for chapter in track_tag.chapters:
            chapter_title = chapter.title
            chapter_subtitle = chapter.subtitle
            if(chapter.times):
                chapter_starttime = chapter.times[0]
                chapter_endtime = chapter.times[1]
            if(chapter.offsets):
                chapter_startoffset = chapter.offsets[0]
                chapter_endoffset = chapter.offsets[1]
        assorted.append(chapter_title)
        assorted.append(chapter_subtitle)
        assorted.append(chapter_starttime)
        assorted.append(chapter_endtime)
        assorted.append(chapter_startoffset)
        assorted.append(chapter_endoffset)

        # delete variables
        del chapter_title, chapter_subtitle, chapter_starttime
        del chapter_endtime, chapter_startoffset, chapter_endoffset

        # Store all URL's in the list
        assorted.append(track_tag.commercial_url)
        assorted.append(track_tag.copyright_url)
        assorted.append(track_tag.artist_url)
        assorted.append(track_tag.audio_file_url)
        assorted.append(track_tag.audio_source_url)
        assorted.append(track_tag.internet_radio_url)
        assorted.append(track_tag.payment_url)
        assorted.append(track_tag.publisher_url)

        user_url = None
        for user_url_tag in track_tag._user_urls:
            user_url = user_url_tag.url
        assorted.append(user_url)

        # Delete all variables that are not used anymore
        del user_url, list_of_strings, track_info, track_tag, track

        # Get APEv2 tag from MP3,
        # because we don't know the key:value we store all data in one column
        try:
            apev2_tag = APEv2(fullpath)
        except:
            apev2_tag = None
        assorted.append(apev2_tag)

        # Delete variable
        del apev2_tag

        # Store the embedded XMP metadata
        if config.ENABLEXMP:
            import libxmp
            xmpfile = libxmp.XMPFiles(file_path=fullpath)
            assorted.append(str(xmpfile.get_xmp()))
            xmpfile.close_file()
        else:
            assorted.append(None)

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nMPEG file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        # Store in database
        return assorted

    except:
        traceback.print_exc(file=sys.stderr)
        return None
