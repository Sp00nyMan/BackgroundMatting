tmp_folder=/tmp/sp00nyman/bgm

if mkdir $tmp_folder/ -p ; then
  if mv .buildozer bin $tmp_folder/ && echo moved buildozer files to $tmp_folder ; then
      rm -r * && echo removed old files
  else
      echo "Failed to move buildozer files to $tmp_folder"
  fi
else
  echo "failed to create dir $tmp_folder"
  exit
fi

cp /media/sf_Diploma/BackgroundMatting/app/. . -r && echo copied the latests files

if mv $tmp_folder/.buildozer $tmp_folder/bin .; then
  echo "Restored buildozer files from $tmp_folder"
else
  echo "Couldn't restore buildozer files"
fi

buildozer android debug deploy run logcat