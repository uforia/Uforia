'''
Created on 2 mrt. 2013

@author: Jimmy van den Berg
'''

# This is the audio module for MP4

#TABLE: Length:REAL, Bitrate:INT, NumberOfChannels:INT, SampleRate:BIGINT, BitsPerSample:INT, Title:LONGTEXT, Album:LONGTEXT, Artist:LONGTEXT, AlbumArtist:LONGTEXT, Composer:LONGTEXT, Year:INT, Comment:LONGTEXT, Description:LONGTEXT, PurschaseDate:DATE, Grouping:LONGTEXT, Genre:LONGTEXT, Lyrics:LONGTEXT, PodcastURL:LONGTEXT, PodcastEpisode:LONGTEXT, PodcastCategory:LONGTEXT, PodcastKeywords:LONGTEXT, EncodedBy:LONGTEXT, Copyright:LONGTEXT, AlbumSortOrder:LONGTEXT, AlbumArtistSortOrder:LONGTEXT, ArtistSortOrder:LONGTEXT, TitleSortOrder:LONGTEXT, ComposerSortOrder:LONGTEXT, ShowSortOrder:LONGTEXT, ShowName:LONGTEXT, PartOfCompilation:BOOLEAN, PartOfAlbum:BOOLEAN,Podcast:BOOLEAN, Tempo:BIGINT, TrackNumber:INT, TotalTracks:INT, DiscNumber:INT, TotalDiscs:INT, CoversFormat:LONGTEXT

import sys
import mutagen.mp4

def process(fullpath, config, columns=None):
        # Try to parse mp4 data
        try:
            audio = mutagen.mp4.MP4(fullpath)
            
            # Source of these properties: mp4.py from mutagen (MP4Info class) 
            assorted = [
                audio.info.length,
                audio.info.bitrate,
                audio.info.channels,
                audio.info.sample_rate,
                audio.info.bits_per_sample
            ]
            
            # Source of these properties: mp4.py from mutagen (MP4Tags class)
            tag_names = ['\xa9nam', '\xa9alb', '\xa9ART', 'aART', '\xa9wrt', '\xa9day', '\xa9cmt', 'desc', 'purd', '\xa9grp', '\xa9gen', '\xa9lyr', 'purl',
                          'egid', 'catg', 'keyw', '\xa9too', 'cprt', 'soal', 'soaa', 'soar', 'sonm', 'soco', 'sosn', 'tvsh', 'cpil', 'pgap', 'pcst', 'tmpo']
            
            for tag_name in tag_names:
                if audio.tags.get(tag_name):
                    assorted.append(audio.tags.get(tag_name)[0])
                else:
                    assorted.append(None)
            
            # Track number and total tracks are stored in an array
            track_number = None
            total_tracks = None
            if audio.tags.get('trkn'):
                track_number, total_tracks = audio.tags.get('trkn')[0]
            assorted.append(track_number)
            assorted.append(total_tracks)
            
            # disc number and total discs are stored in an array
            disc_number = None
            total_discs = None
            if audio.tags.get('disk'):
                disc_number, total_discs = audio.tags.get('disk')[0]
            assorted.append(disc_number)
            assorted.append(total_discs)
            
            # delete variables
            del track_number, total_discs, total_tracks, disc_number
            
            # Get images from audio file
            if audio.tags.get("covr"):
                covers = []
                # Could be multiple images
                for cover in audio.tags.get("covr"):
                    if cover.imageformat == mutagen.mp4.MP4Cover.FORMAT_JPEG:
                        covers.append("JPEG")
                    else:
                        covers.append("PNG")
                
                # Store value in array    
                assorted.append(covers)
                del covers  
            
            #Close connection with file
            del audio
            
            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)
            
            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nMP4 file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i]+':', assorted[i])
                print
            
            return assorted
            
        except:
            print "An error occured while parsing audio data: ", sys.exc_info()
        
            # Store values in database so not the whole application crashes
            return None        