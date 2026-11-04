#!/usr/bin/env bash
# Publica web/dist no GitHub Pages (branch gh-pages). Uso: cd web && npm run build && bash publicar-pages.sh
set -e
D=$(mktemp -d); cp -r dist/. "$D/"; cd "$D"
echo "radar.lucasnegrelli.com" > CNAME; touch .nojekyll; cp index.html 404.html
git init -q -b gh-pages; git add -A
git -c user.name="radar-publico-bot" -c user.email="actions@users.noreply.github.com" commit -q -m "deploy $(date +%F)"
git remote add origin "https://${GH_TOKEN:+x-access-token:$GH_TOKEN@}github.com/lucasnegrelli/radar-publico.git"
for i in 1 2 3 4; do git push -q -f origin gh-pages && break; echo "push falhou, tentativa $i"; sleep $((20*i)); done; git ls-remote origin gh-pages >/dev/null
echo "publicado no GitHub Pages"
