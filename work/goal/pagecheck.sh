#!/bin/zsh
# Builds every rule-one/rule-two outcome variant in the scratchpad and prints the page the main text ends on.
#   zsh work/goal/pagecheck.sh <scratch dir>
setopt nullglob
ROOT="${0:A:h:h:h}"; S=$1
for v in "0 0" "2 1" "2 2" "2 3" "1 1" "1 2" "1 3" "real"; do
  d=$S/pc-${v// /}; rm -rf $d; mkdir -p $d
  cp $ROOT/deliverables/*.tex $ROOT/deliverables/*.sty $ROOT/deliverables/supplement_extended.aux $d/ 2>/dev/null
  cp -R $ROOT/deliverables/figures $d/
  if [ "$v" != real ]; then
    rm -f $d/pythia_values.tex
    set -- ${=v}
    sed -i '' -e "s/\\\\newcommand{\\\\Ronecase}{0}/\\\\newcommand{\\\\Ronecase}{$1}/" -e "s/\\\\newcommand{\\\\Rtwocase}{0}/\\\\newcommand{\\\\Rtwocase}{$2}/" $d/main.tex
  fi
  (cd $d && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1); rc=$?
  pg=$(grep -o 'newlabel{maintext:end}{{[^}]*}{[0-9]*' $d/main.aux | grep -o '[0-9]*$')
  und=$(grep -c 'undefined' $d/main.log)
  echo "variant $v: rc=$rc main text ends p$pg, undefined-warnings=$und"
done
