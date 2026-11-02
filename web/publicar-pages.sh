#!/usr/bin/env bash
# Publica web/dist no GitHub Pages (branch gh-pages). Uso: cd web && npm run build && bash publicar-pages.sh
set -e
D=$(mktemp -d); cp -r dist/. "$D/"; cd "$D"
echo "radar.lucasnegrelli.com" > CNAME; touch .nojekyll; cp index.html 404.html
git init -q -b gh-pages; git add -A
git -c user.name="radar-publico-bot" -c user.email="actions@users.noreply.github.com" commit -q -m "deploy $(date +%F)"
git remote add origin https://github.com/lucasnegrelli/radar-publico.git
git push -q -f origin gh-pages
echo "publicado no GitHub Pages"
