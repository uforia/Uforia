# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the audio module for MP4

# TABLE: length:REAL, bitrate:INT, number_of_channels:INT, sample_rate:BIGINT, bits_per_sample:INT, title:LONGTEXT, album:LONGTEXT, artist:LONGTEXT, album_artist:LONGTEXT, composer:LONGTEXT, year:INT, comment:LONGTEXT, description:LONGTEXT, purchase_date:DATE, grouping:LONGTEXT, genre:LONGTEXT, lyrics:LONGTEXT, podcast_url:LONGTEXT, podcast_episode:LONGTEXT, podcast_category:LONGTEXT, podcast_keywords:LONGTEXT, encoded_by:LONGTEXT, copyright:LONGTEXT, album_sort_order:LONGTEXT, album_artist_sort_order:LONGTEXT, artist_sort_order:LONGTEXT, title_sort_order:LONGTEXT, composer_sort_order:LONGTEXT, show_sort_order:LONGTEXT, show_name:LONGTEXT, part_of_compilation:BOOLEAN, part_of_album:BOOLEAN, is_podcast:BOOLEAN, tempo:BIGINT, track_number:INT, total_tracks:INT, disc_number:INT, total_discs:INT, covers_format:LONGTEXT

import sys
import traceback
import mutagen.mp4
import python_dateutil as dateutil

def process(fullpath, config, rcontext, columns=None):
        # Try to parse mp4 data
        try:
            audio = mutagen.mp4.MP4(fullpath)

            # Source of these properties: mp4.py from mutagen (MP4Info class)
            assorted = [
                audio.info.length,
                audio.info.bitrate,
                audio.info.channels,
                audio.info.sample_rate,
                audio.info.bits_per_sample]

            # Source of these properties: mp4.py from mutagen (MP4Tags class)
            tag_names = ['\xa9nam', '\xa9alb', '\xa9ART', 'aART', '\xa9wrt',
                         '\xa9day', '\xa9cmt', 'desc', 'purd', '\xa9grp',
                         '\xa9gen', '\xa9lyr', 'purl', 'egid', 'catg', 'keyw',
                         '\xa9too', 'cprt', 'soal', 'soaa', 'soar', 'sonm',
                         'soco', 'sosn', 'tvsh', 'cpil', 'pgap', 'pcst',
                         'tmpo']

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

            # Close connection with file
            del audio

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Fix date format
            index = columns.index('purchase_date')
            if assorted[index] is not None:
                assorted[index] = dateutil.parser.parse(assorted[index]).isoformat()

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nMP4 file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
