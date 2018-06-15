This is the README file for the XML file compiler project.

===========
Overview
===========

This module is a tool for reading a set of specified
textual files, and organizing the elements of those files
into a sequence.

The files to be included are specified from the content of the first file.
The content of the first file must specify the content of slot 0 and slot 99
The First line of the first file must be a comment line to identify the
comment character(s) for use by all the files.

The sequence of elements specified within the files
is then output to a result file in the specified sequence.  Each
of the input files can contain multiple elements (for example,
output element X in slot 5, and output element Y in slot 98, where
element X is placed early on
in the output file, and element Y is almost the last element
in the output file --- Thus,
you can have elements in a file that are prerequsets to other elements.
The elements are (randomly) inserted into slots; each slot is output in
numerical order.

Element prerequesets must be placed in a lower numbered slot (the content of
slots is considered a randomly ordered list).
    
=========================
metadata tag restrictions
=========================
<metadata> cannot be nested, multiple <metadata> in a file are allowed

=========================
Comments
=========================

The comment characters cannot include an angle bracket (that is, not '<' or '>')
The comment characters can be 1 to 3 characters long, and for the first line
must be followed by a space character (subsequent comments
do not require the space after the comment charcters)

Comments are only processed if the comment character(s) are the first non-blank
character(s) in the line.
To add a comment to a slot, the first character of such a comment line must
not be the comment character(s) otherwise the comment character will be stripped and
you will lose the comment characteristic.

Lines starting with comment characters from the input file are included in the output file.
However, the comment character will be stripped.  To stop this, make sure the comment
characters are not the first characters in the line.

The comment character(s) is defined by the first line of the master file and apply to
all files specified in the <filelist></filelist>. 

XML Comments are allowed within a <metadata> </metadata> tag block
XML data must be on lines starting with the comment characters for example: ::
    
        # identifies '#' as a comment charcter
        #<metadata repeater="dlx2-887354">
        #<!-- a metadata comment-->
        #</metadata>

The first file must contain Slot-0 and Slot-99 elements as well as
a file list element (which may be empty).

The first file can consist of: ::
    
        # identifies '#' as a comment charcter
        #<metadata repeater="dlx2-887354">
        #<!-- a metadata comment-->
        #   <filelist>
        #       <file>file1 path</file>
        #       <file>file2 path</file>
        #       <file>filelast path</file>
        #   </filelist>
        #   <slot id=0>
        text that goes into slot 0 line 1
          # comment to go into slot 0 as line 2
        line 3
        ...
        line n
        #   </slot>
        #   <slot id=99>
        text that goes into slot 99 line 1
          # comment to go into slot 99
        line 2
        ...
        line n
        #   </slot>
        #</metadata>

The files element is only valid in the first file.

1) If the first file does not contain a <metadata></metatdata> tag, the entire
first file is output as is.

2) If the first file contains a <metadata></metatdata> tag, but no <slot></slot> tags
the entire first file is output as is.

3) If the first file contains a <metadata></metatdata> tag, but no <filelist></filelist> tags
or all empty <filelist></filelist> tags,
the entire first file is output in accordance to slot deffinitions

After exceptions 1-3 above: 
The first file must specify slots 0 and 99, and may specify other slots.
Only the first file can specify slots 0 and 99
Only one element can be placed in slots 0 and 99.

This module is described in the domain of a Radio Repeater controller but
I expect that it may be of general use.

=========================
Basic Usage Examples
=========================

The following is an abridged example of a primary file: ::

    ; Master File for creating the commands for XXX repeater
    ;<metadata repeater="dlx2-887354">
    
    ;<filelist>
    ;<file>setupport1.txt</file>
    ;<file>setupport2.txt</file>
    ;<file>setupport3.txt</file>
    ;<file>setupport4.txt</file>
    ;<file>setupport5.txt</file>
    ;<file>disableAutoPatch.txt</file> 
    ;<file>macros.txt</file>
    ;<file>schedules.txt</file>
    ;<file>users.txt</file>
    ;</filelist>
    
    ;<slot id="0">
    N050 08 1	;enable audio out Main Port from Serial Port
    N188        ; see if any users are logged in
    N050 08 0	;Mute audio out Main Port from Serial Port
    N073        ; look for preaccess enabled ports
    N076 1      ; list preaccess stop conditions
    N156        ; get the status of all TX ptt enabled ports
    
    N007 1	; get the DTMF Mute/Cover tones for ports 1-5
    N007 2
    N007 3
    N007 4
    N007 5
    
    N061 1 ; disconnect ports from 1

    ;</slot>
    
    ;<slot id="99">
    
            ; These timers may help prevent DTMF Voice Falsing
    020 020 100	;DTMF Mute Delay 100ms
    020 043 50	;Keyup delay Rx 1 .5sec
    
    N049 1 0440 0350 ;set preacces tone on port 1 to default
    N070 1
    
    N053 900 N035   ;RESET CONTROLLER macro
    N010 900 C23D32  ;and rename it
    N000 11 ;set port 1 to a repeater
    N000 15 ;connect ports 1 and 5 (IRLP)
    n195 0 ;disable hf
    050 08 1	;enable audio out Main Port from Serial Port
    ;</slot>
    ;</metadata>
    ; the following are ignored comments
    ;---------------------------------------------------
    ; default command numbers?
    ; 080 is N
    ; 307 is *
    ; 310 is C310
    ;Command number 080 is named N.
    
And the file setupport1.txt could be: ::

    ; setupport1.txt -- setup port 1 file
    ; This file
    ; 1) Sets Reciever and DTMF Decoder Conditions
    ; 2) Set COR and PL Active Levels
    ; 3) Configures DTMF Mute/Cover Tones / Bypass & Enable DTMF Bypass
    ; 4) programs courtesy tones
    ; for port 1
    ;
    ;<metadata>
    ;<slot id="1">
            ;Program Courtesy Tones
    N053 256 040 010 000 0665	;PORT 1 Tone 1 high
    N056 256 040 010 000 0500	;PORT 1 Tone 2 low
    ;</slot>
    
    ;<slot id="11"> 
            ;
    N005 1 1     ;PORT 1 COR Access (Repeater Port)
    N013 1 01    ;PORT 1 COR low PL Active High low to stop tx reset in slot98
    N007 1 31    ;PORT 1 DTMF Mute w/Cover Drop TX when DTMF tones are being received
    ;</slot>
    ;<slot id="12">
    N053 220 064 250 041 007 048 052 043 411 830 680 ; initial id P1-Voice "K7RVM Repeater Female time Welcome"
    N053 226 064 250 278 007 418 514 316 411	; pending id #1 P1-Voice Kilo 7 Romeo Victor Mike Repeater"
    N053 232 064 250 041 007 048 052 587 043 411 046 042 270 001 002 003	; pending id #2 P1-Voice "K7RV pause M Repeater PL is 123"
    N053 238 064 250 041 007 048 052 587 043 411 046 546 042 270 001 002 003	; pending id #3 P1-Voice "K7RV pause M Repeater PL is 123"
    N053 244 030 20 07 27 31 22	;pending id #4 P1-CW "K7RVM"
    N053 250 030 20 07 27 31 22	;Impolite id P1-CW "K7RVM"
    ;</slot>
    
    ;<slot id="20">
    N020 013 200	;Transitter 1 Hang Timer 2 seconds
    N020 118 360	;Receiver 1 Timeout Timer 6 mins
    N041 1 1	;PORT 1 Courtesy Tone enabled
    ;</slot>
    
    
    ;<slot id="98">
    N013 1 11	;PORT 1 COR and PL Active High enable the repeater
    ;</slot>
    ;</metadata>


=========================
Whats New
=========================

Brand new.  It is all new

===============================
Supported Repeater Controllers
===============================

Currently expected to be supporte are: ('dlx2', 'club', 'rlc1', 'rlc1+').
Currently tested is dlx2.

=========================
Elements
=========================

An element is defined within the <slot> tag.
In the prior example, the text between the <slot id='x'></slot> tags
are placed in the specified slots.

A file can contain multiple elements that are placed into the same
slot.  Thus: ::

        #   <slot id=5>
           #<!-- define element x for slot 5 -->
        text that goes into slot 5 line ele-x(1)
            # comment to go into slot 5 line ele-x(2)
        line ele-x(3)
        ...
        line x(n)
        #   </slot>
        #   <slot id=4>
              #<!-- define element y for slot 4 -->
        text that goes into slot 4 line ele-y(1)
               # comment to go into slot 4 as line ele-y(2)
        line ele-y(3)
        ...
        line ele-y(n)
        #   </slot>
        #   <slot id=5>
            #<!-- define element z for slot 5 -->
        text that goes somewhere into slot 5 line ele-z(1)
            # comment to go into slot 5 line ele-z(2)
        line ele-z(3)
        ...
        line ele-z(n)
        #   </slot>

 Note that the order that elements x and z from slot 5 are output is undefined.
 Note that html comments can be placed within the <data></data> fields and will
 appear in the output file.
 Note that comment lines within slots must not start at the beggining of the line

=========================
Slots
=========================

There are 100 slots where slots 0 and 99 are special.
Slots 1-98 contain lists of text that have been assigned to that slot (
the output order of the list within each slot is undefined).

Slots 0 and 99 contain lists with at most one element.

=========================
Filelist
=========================
Multiple filelist tags are allowed.  The filelist contents are
concatenated into a single list of files associated with the parent file (the first file).
All slots in the parent file are processed and then each file in the list
is processed in order.

=========================
Files
=========================
Files in the <filelist> can contain metadata.
If a file does not contain metadata, the file's content is placed in the next empty slot.
Thus, if the first file contains metadata with a <filelist> that contains 5 <file> deffinitions,
and these files do not contain metadata, the first file in the list will be placed in slot 1,
and the last file in the list will be in slot 5 (with slots 2, 3, and 4
filled with the corrosponding
file data). Files that contain metadata can be intermixed with files that do not.

=========================
Repeater Attribute
=========================
If provided, metadata processing will only be done if the specified repeater
controller is to receive the data. **what ever that means**