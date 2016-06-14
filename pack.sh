#!/usr/bin/env bash

if [[ -z "$(which makerom)" ]]; then
  echo "Make sure makerom is in" '$PATH'
  exit 0
fi
if [[ -z "$(which convert)" ]]; then
  echo "imagemagic is a dependecy install it!!!"
  exit 0
fi
if [[ -z "$(which ffmpeg)" ]]; then
  echo "ffmpeg is a dependecy install it!!!"
  exit 0
fi
if [[ $# -ne 1 ]]; then
    echo "Illegal number of parameters"
fi

#FIXME: all regions
region=""

case $1 in
    "-E")
        region="EUR"
        ;;
    "-U")
        region="USA"
        ;;
    "-J")
	      region="JPN"
	      ;;
    *)
        echo "This is not supported"
        exit 0
        ;;
esac

costummakerom="makerom -target t"

themes="`ls Themes`"
numthemes=${#themes[@]}

#FIXME: a bin works as follows input is $themesshortend[${i}]
# dd conv=notrunc of=tools\${region}\rom\ContentInfoArchive_${region}_${lang}.bin bs=1 seek=$((8+(${i}+1)*200))

for (( i=0; i<${numthemes}; i++ ));
do
  themesshortend[$i]=$(echo ${themes[$i]}|cut -c1-64)
done

for (( i=0; i<${numthemes}; i++ ));
do
  #FIXME: first check if such an icon.* exists
  next=$(($i + 1))
  if test -n "$(find Themes/${themes[$i]} -maxdepth 1 -name 'icon.*' -print -quit)"; then
    convert Themes/${themes[$i]}/icon.* -resize 48x48 -background black -gravity center -extent 48x48 icons/${next}.png
    ffmpeg -hide_banner -loglevel panic -vcodec png -i icons/${next}.png -vcodec rawvideo -f rawvideo -pix_fmt rgb565 icons/${next}.icn
  else
    #FIXME: handle default icon
    touch icons/$next.icn
    echo "Do stuff with default icon"
  fi
  cp icons/$next.icn Themes/${themes[$i]}/
done
# FIXME: generate icns & cfa per Theme

# FIXME: generate correct .app, depending on language this needs the icons in
# tools\${LANG}\rom\icons\

#FIXME: generate final cia

#FIXME: clean up
if test -n "$(find icons -maxdepth 1 -name '*' -print -quit)"; then
  rm icons/*
fi
if test -n "$(find . -maxdepth 1 -name '*.cfa' -print -quit)"; then
  rm *.cfa
fi
