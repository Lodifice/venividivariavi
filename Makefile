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

LENGTH := $(shell expr 3 \* 60 + 74)
FRAME_TIME := $(shell expr 3 \* 60 + 55)
FPS := 30
SIZE := 1280x720

.PHONY: all
all: video.mp4 last_frame.jpg

GOURCE := gource --load-config gource.conf -r $(FPS) -o - -$(SIZE) git.log

video.mp4: audio.mp3 git.log logo.png
	$(GOURCE) | ffmpeg -f lavfi -i nullsrc=s=$(SIZE):d=$(LENGTH):r=$(FPS) \
		-r $(FPS) -f image2pipe -vcodec ppm -i - -i $< -filter_complex \
		"[0:v][1:v]overlay[v1]; [v1]fade=out:st=$(shell expr $(LENGTH) - 2):d=2[v2]; [2:a]afade=out:st=$(shell expr $(LENGTH) - 7):d=7[a1]" \
		-map "[v2]" -map "[a1]" \
		-c:v libx264 -preset veryslow -tune animation -crf 14 -f mp4 \
		-movflags +faststart -c:a aac -b:a 192k -r $(FPS) \
		-t $(LENGTH) -y $@

git.log: mkrepo.py query_result create_mfnf_git.py
	python3 mkrepo.py query_result > $@

logo.png: logo.svg
	convert $< -resize x50 $@

last_frame.jpg: video.mp4
	ffmpeg -ss $(FRAME_TIME) -i $< -frames:v 1 -s $(SIZE) $@

.PHONY: clean
clean:
	git clean -f -X
