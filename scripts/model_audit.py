"""Audit ranking fairness, matchup consistency and conference evidence."""
import argparse,collections,json
from pathlib import Path

WEIGHTS={"schedule_strength":.4,"result_quality":.3,"win_percentage":.2,"conference_strength":.1}
def analyze(folder):
 folder=Path(folder);report={"status":"EXPERIMENTAL_NOT_OFFICIAL","divisions":{}}
 for division in ("fbs","fcs"):
  data=json.loads((folder/(division+".json")).read_text())
  teams=data["teams"];by_name={t["name"]:t for t in teams}
  if len(by_name)!=len(teams):raise ValueError("Duplicate team names in "+division)
  if [t["rank"] for t in teams]!=list(range(1,len(teams)+1)):raise ValueError("Invalid ranks in "+division)
  integrity=[];head_to_head=[];undefeated=[];conferences={}
  for t in teams:
   expected=sum(WEIGHTS[k]*t["components"][k] for k in WEIGHTS)
   if abs(expected-t["merit_score"])>.002:integrity.append({"team":t["name"],"issue":"score components do not reconcile"})
   if len(t["games"])!=t["wins"]+t["losses"]+t.get("ties",0):integrity.append({"team":t["name"],"issue":"game count differs from record"})
   conferences.setdefault(t["conference"],{"strength":t["components"]["conference_strength"],"observations":t.get("conference_sample_size",0),"teams":0})["teams"]+=1
   for g in t["games"]:
    opp=by_name.get(g["opponent"])
    if opp and t["rank"]>opp["rank"] and g["result"]=="W":
     head_to_head.append({"winner":t["name"],"winner_rank":t["rank"],"loser":opp["name"],"loser_rank":opp["rank"],"date":g["date"],"note":"Head-to-head result alone does not determine national merit order"})
   if t["losses"]==1:
    for u in teams:
     if u["losses"]==0 and u["wins"]>=3 and t["rank"]<u["rank"]:
      undefeated.append({"higher_ranked":t["name"],"higher_rank":t["rank"],"undefeated":u["name"],"undefeated_rank":u["rank"],"score_gap":round(t["merit_score"]-u["merit_score"],4),"weighted_components":{k:round(WEIGHTS[k]*(t["components"][k]-u["components"][k]),3) for k in WEIGHTS}})
  conf_list=[{"name":name,**values,"evidence":"limited" if values["observations"]<10 else "moderate" if values["observations"]<30 else "larger sample"} for name,values in conferences.items()]
  conf_list.sort(key=lambda c:(-c["strength"],c["name"]))
  report["divisions"][division]={"as_of":data["as_of"],"team_count":len(teams),"integrity_issues":integrity,"head_to_head_inversions":head_to_head,"one_loss_above_undefeated":undefeated,"conference_evidence":conf_list}
 return report

def html(report):
 import html as h
 esc=lambda s:h.escape(str(s),quote=True)
 out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Model Audit | College Football Merit Poll</title><style>body{background:#101923;color:#f2f6fc;font:16px/1.5 system-ui;max-width:1150px;margin:30px auto;padding:0 18px}a{color:#9bd0ff}table{border-collapse:collapse;width:100%}th,td{padding:9px;border-bottom:1px solid #3b4d60;text-align:left}section{border:1px solid #455a71;border-radius:12px;padding:18px;margin:20px 0}.scroll{overflow-x:auto}.muted{color:#bac9d8}</style><p><a href="index.html">Home</a> · <a href="releases.html">Releases</a></p><h1>Independent Model Audit</h1><p>EXPERIMENTAL — NOT AN OFFICIAL POLL. These are automated review flags, not evidence of incorrect rankings. A head-to-head winner can rank lower when its entire season is weaker.</p>']
 for div,d in report["divisions"].items():
  out.append('<section><h2>'+div.upper()+' · '+esc(d["as_of"])+'</h2><p>'+str(d["team_count"])+' teams · '+str(len(d["integrity_issues"]))+' integrity flags · '+str(len(d["head_to_head_inversions"]))+' head-to-head inversions · '+str(len(d["one_loss_above_undefeated"]))+' one-loss-over-undefeated comparisons</p>')
  if d["integrity_issues"]:out.append('<h3>Data integrity flags</h3><ul>'+''.join('<li>'+esc(x["team"])+': '+esc(x["issue"])+'</li>' for x in d["integrity_issues"])+'</ul>')
  out.append('<h3>Conference strength evidence</h3><div class="scroll"><table><tr><th>Conference</th><th>Strength</th><th>Interconference observations</th><th>Evidence</th></tr>')
  for c in d["conference_evidence"]:out.append('<tr><td>'+esc(c["name"])+'</td><td>'+esc(round(c["strength"],2))+'</td><td>'+esc(c["observations"])+'</td><td>'+esc(c["evidence"])+'</td></tr>')
  out.append('</table></div><h3>Head-to-head inversions (first 50)</h3><p class="muted">A lower-ranked team defeated a higher-ranked team. Review whole-season opponent quality before drawing conclusions.</p><ul>')
  for x in d["head_to_head_inversions"][:50]:out.append('<li>#'+esc(x["winner_rank"])+' '+esc(x["winner"])+' beat #'+esc(x["loser_rank"])+' '+esc(x["loser"])+' ('+esc(x["date"])+')</li>')
  out.append('</ul><h3>One-loss teams ranked above undefeated teams (first 50)</h3><ul>')
  for x in d["one_loss_above_undefeated"][:50]:out.append('<li>#'+esc(x["higher_rank"])+' '+esc(x["higher_ranked"])+' above #'+esc(x["undefeated_rank"])+' '+esc(x["undefeated"])+' · score gap '+esc(x["score_gap"])+' · weighted SOS '+esc(x["weighted_components"]["schedule_strength"])+'; results '+esc(x["weighted_components"]["result_quality"])+'; win% '+esc(x["weighted_components"]["win_percentage"])+'; conference '+esc(x["weighted_components"]["conference_strength"])+'</li>')
  out.append('</ul></section>')
 out.append('<p>Conference evidence categories describe sample size only; they are not confidence intervals or proof of calibration. <a href="https://github.com/calixthecreator25-netizen/Top-25/blob/main/METHOD.md">Methodology</a></p></html>')
 return ''.join(out)

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source",default="data/experimental");p.add_argument("--output",default="site")
 a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True);report=analyze(a.source)
 (out/"model-audit.json").write_text(json.dumps(report,indent=2))
 (out/"model-audit.html").write_text(html(report))
 for div,d in report["divisions"].items():
  print(div.upper(),d["team_count"],"teams",len(d["integrity_issues"]),"integrity flags",len(d["head_to_head_inversions"]),"head-to-head inversions")
  if d["integrity_issues"]:raise ValueError(div+" has data integrity errors")
