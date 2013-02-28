'''
Created on 16 feb. 2013

@author: Jimmy van den Berg
'''
#!/usr/bin/env python

# This is the module for mp3 and mpeg

#TABLE: Title:LONGTEXT, Subtitle:LONGTEXT, Artist:LONGTEXT, AlbumArtist:LONGTEXT, Album:LONGTEXT, TrackNumber:INT(3), TotalTracks:INT(3), DiscNumber:INT(3), TotalDiscs:INT(3), CDID:INT(3), Publisher:LONGTEXT, Composer:LONGTEXT, Conductor:LONGTEXT, GroupContent:LONGTEXT, ReleaseDate:DATE, RecordingYear:INT(4), BeatsPerMinute:INT(6), DurationInSeconds:INT(6), PlayCount:INT(6), TermsOfUse:LONGTEXT, Language:LONGTEXT, Rating:INT(3), Genre:LONGTEXT, CommentText:LONGTEXT, CommentDescription:LONGTEXT, CommentLanguage:LONGTEXT, EncodedBy:LONGTEXT, Copyright:LONGTEXT, Mood:LONGTEXT, Compilation:LONGTEXT, UserText:LONGTEXT, UserDescription:LONGTEXT, LyricsText:LONGTEXT, LyricsDescription:LONGTEXT, LyricsLanguage:LONGTEXT, ImageDescription:LONGTEXT, ImageType:LONGTEXT, ImageURL:LONGTEXT, ChapterTitle:LONGTEXT, ChapterSubtitle:LONGTEXT, ChapterStartTime:DATE, ChapterEndTime:DATE, ChapterStartOffset:DATE, ChapterEndOffset:DATE, CommercialURL:LONGTEXT, CopyrightURL:LONGTEXT, ArtistURL:LONGTEXT, AudioFileURL:LONGTEXT, AudioScourceURL:LONGTEXT, InternetRadioURL:LONGTEXT, PaymentURL:LONGTEXT, PublisherURL:LONGTEXT, UserURL:LONGTEXT   

# import for external lib eyed3
# This lib is used for the audio module, so please install it with the following command: pip install eyeD3
import eyed3
import sys
import imp

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise


def process(fullpath):
    # The whole parse data method is in a try block to catch any exception
    try:        
        # Read the audio file and get the two data classes from it (Tag and AudioInfo)
        track = eyed3.load(fullpath)
        track_tag = track.tag
        track_info = track.info
        
        # A variable to store mutiple strings in a list
        list_of_strings = []
        
        # Store the title in a variable, to store it in the database        
        title = track_tag.title                
        
        '''
        To get a tag from the audio file we need to set a frame in the eyed3 lib.
        In return we get mutiple frames or NoneType.
        For each frame we get the correct variable and this is stored in a list.
        After the loop we parse all found data into one string, this string for example look like: subtitle / subtitle / subtitle
        
        *The eyed3 lib says that it will never occur that there are multiple frames, that is why we store all data in one string,
         but to be sure of this, we still irritate through all frames*
         
        Because a NoneType can not be irritated we use the "or", so when we get a NoneType the for loop uses an empty list.
        Wich will result in an empty string because nothing is added to the list.
        '''
        # Store the subtitle in a variable, to store it in the database  
        for subtitle_frame in track_tag.frame_set["TIT3"] or []:
            list_of_strings.append(subtitle_frame.text)
        subtitle = ' / '.join(list_of_strings)

        # Store the artist in a variable, to store it in the database
        artist = track_tag.artist
        
        # Store the album artist in a variable, to store it in the database
        list_of_strings = []
        for album_artist_frame in track_tag.frame_set["TPE2"] or []:
            list_of_strings.append(album_artist_frame.text)
        album_artist = ' / '.join(list_of_strings)
        
        # Store the album in a variable, to store it in the database  
        album = track_tag.album
        
        '''
        Some tags return an array or list of items.
        To get the correct data of these lists we first need to know if the list is not a NoneType or empty.
        If we don't check this an empty list will result in an exception, "[0]" can not be used an such list
        
        If the list is empty we still need to give something in return to the database, so we first define the variable to None.
        '''
        # Store the track_number in a variable, to store it in the database
        track_number = None
        track_total = None
        if(track_tag.track_num):
            track_number = track_tag.track_num[0]
            track_total = track_tag.track_num[1]
        
        # Store the disc_number in a variable, to store it in the database    
        disc_number = None
        disc_total = None
        if(track_tag.disc_num):
            disc_number = track_tag.disc_num[0]
            disc_total = track_tag.disc_num[1]
        
        # Store the cd_id in a variable, to store it in the database     
        cd_id = track_tag.cd_id
         
        # Store the publisher in a variable, to store it in the database     
        publisher = track_tag.publisher
        
        # Store the composer in a variable, to store it in the database  
        list_of_strings = []
        for composer_frame in track_tag.frame_set["TCOM"] or []:
            list_of_strings.append(composer_frame.text)
        composer = ' / '.join(list_of_strings)
        
        # Store the conductor in a variable, to store it in the database     
        list_of_strings = []
        for conductor_frame in track_tag.frame_set["TPE3"] or []:
            list_of_strings.append(conductor_frame.text)
        conductor = ' / '.join(list_of_strings)
        
        # Store the group content in a variable, to store it in the database 
        list_of_strings = []
        for group_content_frame in track_tag.frame_set["TIT1"] or []:
            list_of_strings.append(group_content_frame.text)
        group_content = ' / '.join(list_of_strings) 
        
        # Store the releasedate and the recording year in a variable, to store it in the database 
        release_date = track_tag.release_date
        recording_year = track_tag.recording_date
        
        # Store beats per minute in a variable, to store it in the database
        bpm = track_tag.bpm
        
        # Store the duration of the song in a variable, to store it in the database
        duration = track_info.time_secs
        
        # Store the play count of the song in a variable, to store it in the database
        play_count = track_tag.play_count
        
        # Store the terms of use in a variable, to store it in the database
        terms_of_use = track_tag.terms_of_use
        
        # Store the language in a variable, to store it in the database
        list_of_strings = []
        for language_frame in track_tag.frame_set["TLAN"] or []:
            list_of_strings.append(language_frame.text)
        language = ' / '.join(list_of_strings)
        
        # Store the rating in a variable, to store it in the database 
        rating = 0    
        for rating in track_tag.popularities:
            rating = rating.rating
        
        # Store the genre in a variable, to store it in the database     
        genre = None
        if(track_tag.genre):
            genre = track_tag.genre.name
        
        # Store the comment data in variables, to store it in the database    
        comment_description = None
        comment_lang = None
        comment_text = None    
        for comment in track_tag.comments:
            comment_description = comment.description
            comment_lang = comment.lang
            comment_text = comment.text
        
        # Store the encoded by in a variable, to store it in the database
        list_of_strings = []
        for encoded_by_frame in track_tag.frame_set["TENC"] or []:
            list_of_strings.append(encoded_by_frame.text)
        encoded_by = ' / '.join(list_of_strings)
        
        # Store the copyright in a variable, to store it in the database    
        list_of_strings = []
        for copyright_frame in track_tag.frame_set["TCOP"] or []:
            list_of_strings.append(copyright_frame.text)
        copyright_text = ' / '.join(list_of_strings)
        
        # Store the mood in a variable, to store it in the database    
        list_of_strings = []
        for mood_frame in track_tag.frame_set["TMOO"] or []:
            list_of_strings.append(mood_frame.text)
        mood = ' / '.join(list_of_strings)
        
        # Store the compilation in a variable, to store it in the database 
        list_of_strings = []
        for compitation_frame in track_tag.frame_set["TPE4"] or []:
            list_of_strings.append(compitation_frame.text)
        compilation = ' / '.join(list_of_strings) 
        
        # Store the user text data in variables, to store it in the database     
        user_text_description = None
        user_text_text = None
        for user_text in track_tag._user_texts:
            user_text_description = user_text.description
            user_text_text = user_text.text
        
        # Store the lyrics data in variables, to store it in the database        
        lyrics_description = None
        lyrics_text = None
        lyrics_lang = None
        for lyric in track_tag.lyrics:
            lyrics_description = lyric.description
            lyrics_text = lyric.text
            lyrics_lang = lyric.lang       

        # Store the image data in variables, to store it in the database 
        image_description = None
        image_url = None
        image_picturetype = None
        for image in track_tag.images:
            image_description = image.description
            image_url = image.image_url
            image_picturetype = image.picTypeToString(image.picture_type)
            #TODO: do something with image itself (image module):  image.image_data 
    
        # Store the chapter data in variables, to store it in the database 
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
        
        # Store all URL's in variables, to store it in the database 
        commercial_url = track_tag.commercial_url
        copyright_url = track_tag.copyright_url
        artist_url = track_tag.artist_url
        audio_file_url = track_tag.audio_file_url
        audio_source_url = track_tag.audio_source_url
        internet_radio_url = track_tag.internet_radio_url
        payment_url = track_tag.payment_url
        publisher_url = track_tag.publisher_url
        
        user_url = None
        for user_url_tag in track_tag._user_urls:
            user_url = user_url_tag.url
        
        # Delete all variables that are not used anymore
        del list_of_strings
        del track_info
        del track_tag 
        del track
        
        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nAudio file data:"
            print "Title:        %s" % title
            print "Subtitle:     %s" % subtitle
            print "Arist:        %s" % artist
            print "Album:        %s" % album
            print "Album aritst: %s" % album_artist
            print "Track number: %s" % str(track_number)
            print "Publisher:    %s" % publisher
            print "Conductor:    %s" % conductor
            print "Composer:     %s" % composer
            print "Duration:     %s" % str(duration)
            print "Rating:       %s" % str(rating)
            print
            
        
        # Return all info from the audio file
        return(title, subtitle, artist, album_artist, album, track_number, track_total, disc_number, disc_total, cd_id, publisher, composer, conductor, group_content, release_date, recording_year, bpm, duration, play_count, terms_of_use, language, rating, genre, comment_text, comment_description, comment_lang, encoded_by, copyright_text, mood, compilation, user_text_text, user_text_description, lyrics_text, lyrics_description, lyrics_lang, image_description, image_picturetype, image_url, chapter_title, chapter_subtitle, chapter_starttime, chapter_endtime, chapter_startoffset, chapter_endoffset, commercial_url, copyright_url, artist_url, audio_file_url, audio_source_url, internet_radio_url, payment_url, publisher_url, user_url)
    
    except:
        print "An error occured while parsing audio data: ", sys.exc_info()
        
        # Store values in database so not the whole application crashes
        return (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

    