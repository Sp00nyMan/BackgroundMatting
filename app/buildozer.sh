tmp_folder=/tmp/sp00nyman/bgm
mkdir $tmp_folder/ -p
mv .buildozer bin $tmp_folder/ && echo moved buildozer files to $tmp_folder
rm -r * && echo removed old files
cp /media/sf_Diploma/BackgroundMatting/app/. . -r && echo copied the latests files
mv $tmp_folder/.buildozer $tmp_folder/bin . && echo restored buildozer files from $tmp_folder
buildozer android debug deploy run logcat