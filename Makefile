# Makefile - Makefile for creating the visualization "final_video.webm"
#
# Written in 2016 by Stephan Kulla ( http://kulla.me )
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without
# any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

LENGTH := $(shell expr 3 \* 60 + 54)

.PHONY: all
all: final.mp4 final.webm

FFMPEG_CUT_VIDEO := -t $(LENGTH) -y \
	            -af 'afade=out:st=$(shell expr $(LENGTH) - 2):d=2' \
	            -vf 'fade=out:st=$(shell expr $(LENGTH) - 1):d=1'
GOURCE := gource --load-config gource.conf -r 30 -o - -1280x720 git.log

final.webm: video.webm
	ffmpeg -i video.webm $(FFMPEG_CUT_VIDEO) final.webm

video.webm: audio.mp3 git.log logo.png
	$(GOURCE) | ffmpeg -f image2pipe -vcodec ppm -i - \
		-codec:v libvpx -quality best -cpu-used 0 -b:v 1M \
		-qmin 10 -qmax 42 -maxrate 2M -bufsize 2M -threads 4 \
		-an -pass 1 -f webm -y -r 30 /dev/null
	$(GOURCE) | ffmpeg -f image2pipe -vcodec ppm -i - -i $< \
		-codec:v libvpx -quality best -cpu-used 0 -b:v 1M -qmin 10 \
		-qmax 42 -maxrate 2M -bufsize 2M -threads 4 \
		-codec:a libvorbis -b:a 164k -pass 2 -y -r 30 -f webm $@

video.mp4: audio.mp3 git.log logo.png
	$(GOURCE) | ffmpeg -r 30 -f image2pipe -vcodec ppm -i - -i $< \
		-c:v libx264 -preset veryslow -tune animation -crf 14 -f mp4 \
		-movflags +faststart -c:a aac -b:a 192k -r 30 \
		$(FFMPEG_VIDEO_CUT) $@

git.log: mkrepo.py query_result create_mfnf_git.py
	python3 mkrepo.py query_result > $@

logo.png: logo.svg
	convert $< -resize x50 $@

.PHONY: clean
clean:
	git clean -f -X
