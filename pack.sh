#!/usr/bin/env bash

if [[ -z "$(which makerom)" ]]; then
  echo "Make sure makerom is in" '$PATH'
  exit 0
fi

costummakerom="makerom -target t"

themes="`ls Themes`"

for theme in ${themes[@]}
do
  #FIXME: first check if such an icon.* exists
  if test -n "$(find Themes/$theme -maxdepth 1 -name 'icon.*' -print -quit)"; then
    convert Themes/$theme/icon.* -resize 48x48 -background black -gravity center -extent 48x48 icons/$theme.png
    ffmpeg -vcodec png -i icons/$theme.png -vcodec rawvideo -f rawvideo -pix_fmt rgb565 icons/$theme.icn
  else
    #FIXME: handle default icon
    echo "Do stuff with default icon"
  fi
done
# FIXME: generate icns & cfa per Theme

# FIXME: generate correct .app, depending on language this needs the icons in
# tools\${LANG}\rom\icons\

#FIXME: generate final cia

#FIXME: clean up
