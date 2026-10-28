#!/usr/bin/env python3
"""Render the supplied DemoCaP results as standalone horizontal-bar SVG charts.

Run from any directory: python3 scripts/build_results.py
Source data: static/data/results.json (generalization/ablation transcribed from
supplied figures); method comparison independently parsed from the supplied TeX.
"""
from pathlib import Path
import csv, json, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'static/plots';OUT.mkdir(exist_ok=True)
DATA=ROOT/'static/data/results.json'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none',
                     'axes.labelcolor':'#514a44','text.color':'#29231f','xtick.color':'#70665f',
                     'ytick.color':'#29231f','axes.edgecolor':'#b9afa6','axes.linewidth':.7,
                     'savefig.facecolor':'white','pdf.fonttype':42})
ACCENT='#b64b08';BASE='#7d858d';GRID='#e8e2dc'

def base_axes(fig,left=.34,bottom=.17,top=.96):
    ax=fig.add_axes([left,bottom,.90-left,top-bottom]);ax.set_xlim(0,100)
    ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Success rate (%)',labelpad=8)
    ax.grid(axis='x',color=GRID,linewidth=.8);ax.set_axisbelow(True)
    ax.tick_params(axis='y',length=0,pad=9);ax.tick_params(axis='x',length=3)
    for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    return ax

def single_chart(methods,values,reported):
    fig=plt.figure(figsize=(7.0,4.0));ax=base_axes(fig,left=.38,bottom=.16,top=.97)
    colors=['#a8b0b8','#8d98a5','#6f7f91','#6e859b','#465c70',BASE,ACCENT]
    ys=list(range(len(methods)));ax.barh(ys,values,height=.60,color=colors,edgecolor='none')
    ax.set_yticks(ys,methods);ax.invert_yaxis();ax.set_ylim(len(methods)-.5,-.65)
    for y,v,dagger in zip(ys,values,reported):
        if v==0:ax.plot(0,y,'|',color=colors[y],markersize=8,markeredgewidth=1.4)
        ax.text(v+1.4,y,f'{v}%'+('†' if dagger else ''),va='center',ha='left',fontsize=11,
                color=ACCENT if y==len(methods)-1 else '#29231f',fontweight='bold' if y==len(methods)-1 else 'normal')
    ax.get_yticklabels()[-1].set_color(ACCENT);ax.get_yticklabels()[-1].set_fontweight('bold')
    return fig

def paired_chart(labels,base,demo,baseline_label='CaP++',ablation=False):
    fig=plt.figure(figsize=(8.3, max(4.7,len(labels)*.74+1.1)))
    ax=base_axes(fig,left=.37 if not ablation else .25,bottom=.14,top=.88)
    ys=list(range(len(labels)));shift=.18
    ax.barh([y-shift for y in ys],base,height=.30,color=BASE,label=baseline_label)
    ax.barh([y+shift for y in ys],demo,height=.30,color=ACCENT,label='DemoCaP')
    ax.set_yticks(ys,labels);ax.invert_yaxis();ax.set_ylim(len(labels)-.35,-.6)
    for y,b,d in zip(ys,base,demo):
        ax.text(b+1.3,y-shift,f'{b}%',va='center',fontsize=11,color='#514a44')
        ax.text(d+1.3,y+shift,f'{d}%',va='center',fontsize=11,color=ACCENT,fontweight='bold')
    handles,text=ax.get_legend_handles_labels()
    fig.legend(handles,text,loc='upper left',bbox_to_anchor=(.37 if not ablation else .25,.995),
               frameon=False,ncol=2,fontsize=11,handlelength=1.5,columnspacing=1.4)
    return fig

def main():
    data=json.loads(DATA.read_text())
    # The source table is the authority for all 84 method-comparison values.
    rows=[]
    for line in (ROOT/'static/data/method-comparison-source.tex').read_text().splitlines():
        if not line.startswith(('OpenVLA &','$\\pi_0$ &','$\\pi_{0.5}$ &','CaP-X (','CaP++ &','DemoCaP &')):continue
        cells=line.split('&');name=cells[0].strip();name={'$\\pi_0$':'π₀','$\\pi_{0.5}$':'π₀.₅'}.get(name,name)
        vals=[];reported=[]
        for cell in cells[1:]:
            reported.append('dagger' in cell)
            clean=re.sub(r'\\textsuperscript\{\$\\dagger\$\}','',cell)
            vals.append(int(re.search(r'\d+',clean).group()))
        assert len(vals)==12
        rows.append(dict(method=name,values=vals,reported_by_capx=reported))
    assert len(rows)==7
    data['method_comparison']['rows']=rows;DATA.write_text(json.dumps(data,indent=2)+'\n')
    methods=[r['method'] for r in rows];suites=data['suites'];conditions=data['method_comparison']['conditions']
    export=[]
    with PdfPages(OUT/'democap-results.pdf') as pdf:
        for condition_index,condition in enumerate(conditions):
            for suite_index,suite in enumerate(suites):
                index=suite_index*3+condition_index;values=[r['values'][index] for r in rows]
                reported=[r['reported_by_capx'][index] for r in rows]
                fig=single_chart(methods,values,reported)
                fig.savefig(OUT/f'method-{condition["id"]}-{suite["id"]}.svg')
                fig.suptitle(f'{suite["label"]} — {condition["label"]}',fontsize=14,y=1.04)
                pdf.savefig(fig,bbox_inches='tight');plt.close(fig)
                export.extend(dict(experiment='Method comparison',suite=suite['label'],condition=condition['label'],method=m,success_percent=v,n='',reported_by_capx=dagger) for m,v,dagger in zip(methods,values,reported))
        for suite in suites:
            entries=data['generalization'][suite['id']]
            labels=[f'{e["condition"]}  (n={e["n"]})' for e in entries]
            fig=paired_chart(labels,[e['cappp'] for e in entries],[e['democap'] for e in entries])
            fig.savefig(OUT/f'generalization-{suite["id"]}.svg')
            fig.suptitle(suite['label']+' — generalization',fontsize=14,y=1.03)
            pdf.savefig(fig,bbox_inches='tight');plt.close(fig)
            for e in entries:
                for method,key in [('CaP++','cappp'),('DemoCaP','democap')]:export.append(dict(experiment='Generalization',suite=suite['label'],condition=e['condition'],method=method,success_percent=e[key],n=e['n'],reported_by_capx=False))
        ab=data['direct_demo_ablation'];fig=paired_chart([s['label'] for s in suites],ab['direct_democap'],ab['democap'],baseline_label='Direct-DemoCaP',ablation=True)
        fig.savefig(OUT/'direct-demo-ablation.svg');fig.suptitle('Direct demonstration conditioning ablation',fontsize=14,y=1.03);pdf.savefig(fig,bbox_inches='tight');plt.close(fig)
        for suite_index,suite in enumerate(suites):
            for method,key in [('DemoCaP','democap'),('Direct-DemoCaP','direct_democap')]:export.append(dict(experiment='Direct-demo ablation',suite=suite['label'],condition='Original',method=method,success_percent=ab[key][suite_index],n='',reported_by_capx=False))
    with (ROOT/'static/data/results.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(export[0]),lineterminator='\n');w.writeheader();w.writerows(export)
    for path in OUT.glob('*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    print(f'Rendered 17 SVG charts and a PDF collection; exported {len(export)} values.')

if __name__=='__main__':main()
