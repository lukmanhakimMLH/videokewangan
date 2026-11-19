#!/usr/bin/env bash
# Bina web app luar talian (PWA) dalam folder app/ daripada app.html.
# Library dimuatkan dari app/lib supaya app berfungsi tanpa internet.
set -euo pipefail
cd "$(dirname "$0")"
SRC=app.html
OUT=app/index.html

VERSION="$(cat "$SRC" app/lib/*.js app/sw.template.js | sha1sum | cut -c1-10)"

{
  printf '<!doctype html>\n<html lang="ms">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="theme-color" content="#ea580c">\n'
  printf '<meta name="apple-mobile-web-app-capable" content="yes">\n'
  printf '<meta name="mobile-web-app-capable" content="yes">\n'
  printf '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
  printf '<meta name="apple-mobile-web-app-title" content="Harta Pusaka">\n'
  printf '<link rel="manifest" href="manifest.webmanifest">\n'
  printf '<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">\n'
  printf '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
  sed -n '1,/^<\/style>/p' "$SRC"
  printf '</head>\n<body>\n'
  sed '1,/^<\/style>/d' "$SRC" \
    | sed -E 's#https://cdnjs\.cloudflare\.com/ajax/libs/[^"]*/([^/"]+\.js)#lib/\1#'
  cat <<'EOF'
<script>
if('serviceWorker' in navigator && location.protocol !== 'file:'){
  window.addEventListener('load', function(){ navigator.serviceWorker.register('sw.js').catch(function(){}); });
}
</script>
</body>
</html>
EOF
} > "$OUT"

sed "s/__VERSION__/$VERSION/" app/sw.template.js > app/sw.js

if grep -q 'cdnjs.cloudflare.com' "$OUT"; then echo "Ralat: masih ada pautan CDN dalam $OUT" >&2; exit 1; fi
echo "Siap: $OUT (versi $VERSION)"
