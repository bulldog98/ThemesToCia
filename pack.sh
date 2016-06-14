#!/usr/bin/env bash

# reverse a array
function reverse()
{
  local arrayname=${1:?Array name required} array revarray e
  eval "array=( \"\${$arrayname[@]}\" )"
  for e in "${array[@]}"
  do
    revarray=( "$e" "${revarray[@]}" )
  done
  eval "$arrayname=( \"\${revarray[@]}\" )"
}

if [[ -z "$(which makerom)" ]]; then
  echo "Make sure makerom is in your" '$PATH'
  exit 0
fi
if [[ -z "$(which convert)" ]]; then
  echo "imagemagick is a dependency, install it and make sure it is in your PATH!!!"
  exit 0
fi
if [[ -z "$(which ffmpeg)" ]]; then
  echo "ffmpeg is a dependency, install it and makre sure it is in your PATH!!!"
  exit 0
fi
if [[ $# -ne 1 ]] && [[ $# -ne 2 ]]; then
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

order="-r"
if [[ $# -eq 2 ]];then
  case $2 in
    "-r")
      order=""
      ;;
    *)
      echo "Only sorting allowed is -r or non at all"
      ;;
    esac
fi

themes=()
cd Themes
for FILE in *; do
    # If the file is a directory add it to the array. ("&&" is shorthand for
    # if/then.)
    [[ -d $FILE ]] && themes+=("$FILE")
done
cd ..
case $order in
  "")
    reverse themes
    ;;
  "-r")
    #Nothing to do here
    ;;
  *)
    echo "Invalid order"
    ;;
esac
costummakerom="makerom -target t"
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
  tmptheme=${themes[$i]}
  echo $tmptheme
  if test -n "$(find Themes/${tmptheme}/ -maxdepth 1 -name 'icon.*' -print -quit)"; then
    convert Themes/${tmptheme}/icon.* -resize 48x48 -background black -gravity center -extent 48x48 icons/${next}.png
    ffmpeg -hide_banner -loglevel panic -vcodec png -i icons/${next}.png -vcodec rawvideo -f rawvideo -pix_fmt rgb565 icons/${next}.icn
  else
    #FIXME: handle default icon
    touch icons/$next.icn
    echo "Do stuff with default icon"
  fi
  cp icons/$next.icn Themes/${tmptheme}/
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
