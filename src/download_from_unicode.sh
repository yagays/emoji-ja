# $ sh src/download_from_unicode.sh

mkdir -p data/unicode

wget https://unicode.org/repos/cldr/tags/latest/common/annotations/ja.xml -O data/unicode/ja.xml
wget http://unicode.org/Public/emoji/11.0/emoji-test.txt -O data/unicode/emoji-test.txt
