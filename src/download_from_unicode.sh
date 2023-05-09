# $ sh src/download_from_unicode.sh

mkdir -p data/unicode

wget https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/ja.xml -O data/unicode/ja.xml
wget http://unicode.org/Public/emoji/15.0/emoji-test.txt -O data/unicode/emoji-test.txt
