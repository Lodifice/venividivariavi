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

VIDEO_LENGTH := 233

.PHONY: all
all: final.mp4 final.webm

final.mp4: video.mp4
	ffmpeg -i video.mp4 -t $(VIDEO_LENGTH) final.mp4

final.webm: video.webm
	ffmpeg -i video.webm -t $(VIDEO_LENGTH) final.webm

video.webm: video.ppm audio.mp3
	ffmpeg -y -r 30 -f image2pipe -vcodec ppm -i $< \
		-codec:v libvpx -quality best -cpu-used 0 -b:v 1M \
		-qmin 10 -qmax 42 -maxrate 2M -bufsize 2M -threads 4 \
		-an -pass 1 -f webm /dev/null
	ffmpeg -y -r 30 -f image2pipe -vcodec ppm -i $< -i $(word 2, $^) \
		-codec:v libvpx -quality best -cpu-used 0 -b:v 1M -qmin 10 \
		-qmax 42 -maxrate 2M -bufsize 2M -threads 4 \
		-codec:a libvorbis -b:a 164k -pass 2 -f webm $@

video.mp4: video.ppm audio.mp3
	ffmpeg -y -r 30 -f image2pipe -vcodec ppm -i $< -i $(word 2, $^) \
		-c:v libx264 -preset veryslow -crf 22 -f mp4 -movflags +faststart \
		-c:a aac -b:a 192k $@

git.log: mkrepo.py query_result create_mfnf_git.py
	python3 mkrepo.py query_result > $@

video.ppm: git.log gource.conf logo.png
	gource --load-config gource.conf -r 30 -o video.ppm \
		-1280x720 git.log

logo.png: logo.svg
	convert $< -resize x50 $@

.PHONY: clean
clean:
	rm -rf git
	git clean -f -X
