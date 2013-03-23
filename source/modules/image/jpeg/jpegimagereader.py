# This is the image module for JPG

#TABLE: Image_App:LONGTEXT, Image_AppList:LONGTEXT, Image_Bits:INT, Image_Quantization:INT, Image_ICCList:LONGTEXT, Image_Huffman_dc:LONGTEXT, Image_Huffman_ac:LONGTEXT, Image_Layer:LONGTEXT, Image_Tile:LONGTEXT, Jfif:LONGTEXT, ICC_Profile:LONGTEXT, Jfif_version:LONGTEXT, Jfif_density:LONGTEXT, Jfif_unit:LONGTEXT, Adobe:LONGTEXT, Adobe_transform:LONGTEXT, Progression:LONGTEXT, Quality:LONGTEXT, Optimize:LONGTEXT, Progressive:BOOLEAN, Flashpix:LONGTEXT, DPIx:INT, DPIy:INT, imagewidth:INT, imagelength:INT, bitspersample:INT, compression:LONGTEXT, photometricinterpretation:LONGTEXT, imagedescription:LONGTEXT, make:LONGTEXT, model:LONGTEXT, stripoffsets:INT, orientation:LONGTEXT, samplesperpixel:INT, rowsperstrip:INT, stripbyteconunts:INT, xresolution:INT, yresolution:INT, planarconfiguration:LONGTEXT, resolutionunit:INT, transferfunction:LONGTEXT, software:LONGTEXT, datetime:LONGTEXT, artist:LONGTEXT, whitepoint:LONGTEXT, primarychromaticities:LONGTEXT, jpegifoffset:INT, jpegifbytecount:INT, ycbcrcoefficients:INT, ycbcrsubsampling:INT, ycbcrpositioning:INT, referenceblackwhite:LONGTEXT, relatedimagefileformat:LONGTEXT, relatedimagelength:INT, relatedimagewidth:INT, cfarepeatpatterndim:LONGTEXT, cfapattern:LONGTEXT, batterylevel:INT, copyright:LONGTEXT, exposuretime:INT, fnumber:INT, exifoffset:INT, intercolorprofile:LONGTEXT, exposureprogram:LONGTEXT, isospeedratings:INT, oecf:LONGTEXT, interlace:LONGTEXT, timezoneoffset:LONGTEXT, selftimermode:INT, exifversion:INT, datetimeoriginal:LONGTEXT, datetimedigitized:LONGTEXT, componentsconfiguration:LONGTEXT, compressedbitsperpixel:INT, shutterspeedvalue:INT, aperturevalue:INT, brightnessvalue:INT, exposurebiasvalue:INT, maxaperturevalue:INT, subjectdistance:INT, meteringmode:LONGTEXT, lightsource:LONGTEXT, flash:LONGTEXT, focallength:INT, flashenergy:INT, spatialfrequencyresponse:INT, noise:INT, imagenumber:INT, securityclassification:LONGTEXT, imagehistory:LONGTEXT, exposureindex:LONGTEXT, tiffepstandardid:INT, makernote:LONGTEXT, usercomment:LONGTEXT, subsectime:INT, subsectimeoriginal:INT, subsectimedigitized:INT, flashpixversion:INT, colorspace:INT, exifimagewidth:INT, exifimageheight:INT, relatedsoundfile:LONGTEXT, exifinteroperabilityoffset:INT, spatialfrequenceresponse:INT, focalplanexresolution:INT, focalplaneyresolution:INT, focalplaneresolutionunit:INT, subjectlocation:LONGTEXT, sensingmethod:LONGTEXT, filesource:LONGTEXT, scenetype:LONGTEXT, gpsversionid:INT, gpslatituderef:INT, gpslatitude:INT, gpslongtituderef:INT, gpslongtitude:INT, gpsaltituderef:INT, gpsaltitude:INT, gpstimestamp:INT, gpssatellites:INT, gpsstatus:LONGTEXT, gpsmeasuremode:LONGTEXT, gpsdop:LONGTEXT, gpsspeedref:INT, gpsspeed:INT, gpstrackref:INT, gpstrack:INT, gpsimgdirectionref:INT, gpsimgdirection:INT, gpsmapdatum:INT, gpsdestlatituderef:INT, gpsdestlatitude:INT, gpsdestlongituderef:INT, gpsdestlongitude:INT, gpsdestbearingref:INT, gpsdestbearing:INT, gpsdistanceref:INT, gpsdestdistance:INT,OtherInfo:LONGTEXT, XMPtag:LONGTEXT 

import sys, traceback
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def process(fullpath, config, columns=None):  
        try:
            # Try to parse JPG data   
            image = Image.open(fullpath, "r")
            
            # Create an empty list
            assorted = [image.app, image.applist, image.bits, image.quantization, image.icclist, image.huffman_dc, image.huffman_ac, image.layer, image.tile]
            info_dictionary = image.info
            
            # Check if jfif is in info dictionary, if so put it in our list
            if "jfif" in info_dictionary:
                assorted.append(info_dictionary["jfif"])
                info_dictionary.pop("jfif")
            else:
                assorted.append(None)
            
            # Check if icc_profile is in info dictionary, if so put it in our list    
            if "icc_profile" in info_dictionary:
                assorted.append(info_dictionary["icc_profile"])
                info_dictionary.pop("icc_profile")
            else:
                assorted.append(None)    
                  
            # Check if jfif_version is in info dictionary, if so put it in our list       
            if "jfif_version" in image.info:
                assorted.append(info_dictionary["jfif_version"])
                info_dictionary.pop("jfif_version")
            else:
                assorted.append(None)    
                
            # Check if jfif_density is in info dictionary, if so put it in our list       
            if "jfif_density" in image.info:
                assorted.append(info_dictionary["jfif_density"])
                info_dictionary.pop("jfif_density")
            else:
                assorted.append(None)

            # Check if jfif_unit is in info dictionary, if so put it in our list                      
            if "jfif_unit" in image.info:
                assorted.append(info_dictionary["jfif_unit"])
                info_dictionary.pop("jfif_unit")
            else:
                assorted.append(None)  
            
            # Check if adobe is in info dictionary, if so put it in our list
            if "adobe" in info_dictionary:
                assorted.append(info_dictionary["adobe"])
                info_dictionary.pop("adobe")
            else:
                assorted.append(None)
                
            # Check if adobe_transform is in info dictionary, if so put it in our list       
            if "adobe_transform" in image.info:
                assorted.append(info_dictionary["adobe_transform"])
                info_dictionary.pop("adobe_transform")
            else:
                assorted.append(None) 
            
            # Check if progression is in info dictionary, if so put it in our list    
            if "progression" in info_dictionary:
                assorted.append(info_dictionary["progression"])
                info_dictionary.pop("progression")
            else:
                assorted.append(None)
            
            # Check if gamma is in info dictionary, if so put it in our list      
            if "quality" in info_dictionary:
                assorted.append(info_dictionary["quality"])
                info_dictionary.pop("quality")
            else:
                assorted.append(None)
            
            # Check if optimize is in info dictionary, if so put it in our list     
            if "optimize" in info_dictionary:
                assorted.append(info_dictionary["optimize"][0])
                info_dictionary.pop("optimize")
            else:
                assorted.append(None)
                
            # Check if optimize is in info dictionary, if so put it in our list     
            if "progressive" in info_dictionary:
                assorted.append(info_dictionary["progressive"])
                info_dictionary.pop("progressive")
            else:
                assorted.append(None)

            # Check if flashpix is in info dictionary, if so put it in our list       
            if "flashpix" in image.info:
                assorted.append(info_dictionary["flashpix"])
                info_dictionary.pop("flashpix")
            else:
                assorted.append(None)
                                 
            # Check if dpi is in info dictionary, if so put it in our list                            
            if "dpi" in info_dictionary:
                assorted.append(info_dictionary["dpi"][0])
                assorted.append(info_dictionary["dpi"][1])
                info_dictionary.pop("dpi")
            else:
                assorted.append(None)
                assorted.append(None)
                
            # Check if exif is in info dictionary, if so decode and put in our list                    
            if "exif" in info_dictionary:
                # Get all keys and check if they are in the JPEG
                for key in TAGS:
                    if key == 0x8825:
                        # In Key 0x8825 some GPS data is stored
                        for gpskey in GPSTAGS:
                            assorted.append(image._getexif().get(gpskey))
                    else:
                        assorted.append(image._getexif().get(key))
                info_dictionary.pop("exif")        
            else:
                for key in TAGS:
                    if key == 0x8825:
                        for gpskey in GPSTAGS:
                            assorted.append(None)
                    else:
                        assorted.append(None)  
                
            # If there are still other values in the dict then put those in column
            assorted.append(info_dictionary)            
                            
            # Delete variable
            del info_dictionary, image
            
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
                print "\nJPEG file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            return assorted
            
        except:
            traceback.print_exc(file=sys.stderr)
        
            # Store values in database so not the whole application crashes
            return None
