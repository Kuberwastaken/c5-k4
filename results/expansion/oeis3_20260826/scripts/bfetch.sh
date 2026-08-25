#!/bin/zsh
UA="OpenAI File Downloader, XaiImageApiFetch/1.0"
BASE="/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis3_20260826"
IDS=(109905 105801 108866 115366 34693 113258 113271 113609 100800 114362 114137 100475 102847 108301 109671 113010 114216 945 100434 103662 104320 105020 105210 109845 110566 113250 113252 113255 11545 1157 232174 239957 280831 281976 287616 303656 308734 357513 37274)
for i in $IDS; do
  Anum=$(printf '%06d' $i)
  [ -s "$BASE/bfiles/b$Anum.txt" ] || curl -sS --retry 3 -A "$UA" -o "$BASE/bfiles/b$Anum.txt" "https://oeis.org/A$Anum/b$Anum.txt"
  if head -c 20 "$BASE/bfiles/b$Anum.txt" | grep -q "<"; then echo "HTML $i"; else echo "ok $i $(wc -l < "$BASE/bfiles/b$Anum.txt") lines"; fi
  sleep 0.7
done
