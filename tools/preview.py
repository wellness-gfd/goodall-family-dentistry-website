"""Build an interactive preview copy of the site for the Claude artifact viewer.

    python3 tools/preview.py      # writes preview/index.html

The live site uses real addresses (/dental-implants). The artifact viewer can only
switch pages with #page links and loads files by relative path, so this copy:
  - uses relative image/video paths (images/... instead of /images/...)
  - switches pages with #page in place of real addresses
Everything else (content, styles, scripts) is identical to src/index.html.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "src", "index.html"), encoding="utf-8").read()
s = src


def R(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, f"expected {count}x, found {n}: {old[:70]}"
    s = s.replace(old, new)


# relative asset paths
s = re.sub(r'(?<=["\'(`\s])/(images|videos)/', r'\1/', s)

# hash routing
R('  if(r==="smile-plan"&&qs) return "/smile-plan#"+qs;', '  if(r==="smile-plan"&&qs) return "#smile-plan?"+qs;')
R('  return (r==="home"?"/":"/"+r)+(qs?"?"+qs:"")+anchor;', '  return "#"+r+(qs?"?"+qs:"");')
i = s.index("function curKey(){")
j = s.index("\n", i)
s = s[:i] + 'function curKey(){let k=decodeURIComponent(location.hash.slice(1).split("?")[0])||"home";if(ROUTE_ANCHORS[k])k=ROUTE_ANCHORS[k];return k;}' + s[j:]
R('  if(location.hash&&curKey()==="home"){const p=pathFor(location.hash.slice(1));if(p)history.replaceState(null,"",p);}\n', '')
R('history.replaceState(null,"","/"+key+location.search+location.hash);', 'history.replaceState(null,"","#"+key);')
R('  if(key==="smile-plan"&&location.search){history.replaceState(null,"","/smile-plan#"+location.search.slice(1));}\n', '')
R('new URLSearchParams(key==="smile-plan"?location.hash.slice(1):location.search)', 'new URLSearchParams(location.hash.split("?")[1]||"")')
R('const anc=key==="smile-plan"?"":location.hash.slice(1), el=anc&&document.getElementById(anc);', 'const anc="", el=null;')

# click handling: every internal link becomes a #page change
i = s.index('/* Same-site links load instantly without a full page reload */')
j = s.index('/* Links added later')
s = s[:i] + '''/* Preview copy: internal links switch pages with #page */
document.addEventListener("click",e=>{
  if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey) return;
  const a=e.target.closest&&e.target.closest("a[href]"); if(!a||(a.target&&a.target!=="_self")) return;
  const href=a.getAttribute("href"); let p=null;
  if(href[0]==="#") p=pathFor(href.slice(1));
  else if(href[0]==="/"&&!/\\.[a-z0-9]{2,5}$/i.test(href.split(/[?#]/)[0])){
    const u=new URL(href,"https://x.invalid");
    const qs=u.search?u.search.slice(1):(u.pathname==="/smile-plan"&&u.hash?u.hash.slice(1):"");
    p=pathFor((u.pathname.slice(1)||"home")+(qs?"?"+qs:""));
  }
  if(!p) return;
  e.preventDefault(); closeDrawer();
  if(location.hash===p) window.scrollTo({top:0,behavior:"smooth"}); else location.hash=p;
});
window.addEventListener("hashchange",route);
''' + s[j:]

os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
open(os.path.join(ROOT, "preview", "index.html"), "w", encoding="utf-8").write(s)
print("wrote preview/index.html", len(s))
