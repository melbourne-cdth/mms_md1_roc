import numpy as np
import numpy.random as ra
from cdsutils.mutils import *
import pandas as pd
import hvplot.pandas
import holoviews as hv
import panel as pn
import param



def pop2(l1,l2,n):
    return ra.normal(l1,l2,n)

def pop3(p1, p2, n):
    return ra.rayleigh(p1,n)

def num_class(data, _class):
    return data[data["Class"] == _class].shape[0]

def num_pos(data, _class, threshold):
    return data[(data["Class"] == _class) & (data["Value"] >= threshold)].shape[0]

def num_neg(data, _class, threshold):
    return data[(data["Class"] == _class) & (data["Value"] < threshold)].shape[0]

 
def pf(data, _class, threshold):
    return num_pos(data, _class, threshold)/num_class(data, _class)
def pops_min(data):
    return data["Value"].min()
def pops_max(data):
    return data["Value"].max()

def trace_roc(data, num=100, delta=0.1):
    mint = pops_min(data)
    maxt = pops_max(data)
    
    return ([pf(data, "-", t) for t in np.linspace(maxt+delta, mint-delta, num=num)],
            [pf(data, "+", t) for t in np.linspace(maxt+delta, mint-delta, num=num)]
        )
    

def auc_(fpf, tpf):
    auc = 0.0
    for i in range(len(fpf)-1):
        dx = fpf[i+1]-fpf[i]
        y2 = tpf[i+1]
        y1 = tpf[i]
        auc = auc + dx*y1

    return auc
def auc(data):
    fs, ts = trace_roc(data)
    return auc_(fs, ts)


def ppv(data, t):
    try:
        np = num_pos(data, "+", t)
        return np/(np+num_pos(data, "-", t))
    except ZeroDivisionError:
        return 1.0
def npv(data, t):
    try:
        nn = num_neg(data, "-", t)
        return nn/(nn+num_neg(data, "+", t))
    except ZeroDivisionError:
        return 1.0


def _compute_stats(data, t):
    
    nap = num_class(data, "+")
    nan = num_class(data, "-")

    tpf = pf(data, "+", t)
    sens = tpf
    fpf = pf(data, "-", t)
    spec = 1-fpf
    ntp = num_pos(data, "+", t)
    nfn = nap - ntp
    ntn = num_neg(data, "-", t)
    nfp = nan - ntn
    acc = (ntp+ntn) / (nap + nan)
    _rslts = {"threshold":"% 3.2f"%t}
    _rslts["PPV"] = "%3.2f"%(ppv(data, t))
    _rslts["NPV"] = "%3.2f"%(npv(data, t))
    _rslts["Sensitivity (TPF)"] = "%3.2f"%tpf
    _rslts["Specificity (1-FPF)"] = "%3.2f"%(1 -fpf)
    _rslts["Accuracy"] = "%3.2f"%(acc)
    _rslts["Area Under the Curve (AUC)"] = "%3.2f"%(auc(data))
    return ddict(_rslts, template=dt1)

def generate_data(np, nn, mean_p, mean_n, std_p, std_n):
    neg = pd.DataFrame(ra.normal(mean_n, std_n, nn), columns=["Value"])
    pos = pd.DataFrame(ra.normal(mean_p, std_p, np), columns=["Value"])

    neg["Class"] = "-"
    pos["Class"] = "+"
    return pd.concat([neg, pos], ignore_index=True)

def generate_roc_data(df):
    pos = df[df.Class == "+"]["Value"]
    neg = df[df.Class == "-"]["Value"]
    fpf, tpf = trace_roc(df)
    rocd = pd.DataFrame(zip(fpf, tpf), columns=["FPF", "TPF"])
    return rocd

def get_fpf_tpf(df, t, np, nn):
    tpf = df[(df["Value"] >= t)& (df["Class"] == "+")].shape[0]/ np
    fpf = df[(df["Value"] >= t)& (df["Class"] == "-")].shape[0]/ nn
    return fpf,tpf
    

    
def func1(t):
    return t


class Decisions(param.Parameterized):
    np    = param.Integer(default=1000, bounds=(10, 1000))
    nn    = param.Integer(default=1000, bounds=(100, 10000))
    std_p     = param.Number(default=1, bounds=(0.5, 5))
    std_n     = param.Number(default=1, bounds=(0.5, 5))
    mean_p     = param.Number(default=0, bounds=(-2, 2))
    mean_n     = param.Number(default=0, bounds=(-2, 2))
    thresh = param.Number(default=0, bounds=(-5,5))
    
    results = pn.pane.HTML("<h2>Hello</h2>")
    
    def f1(self):
        
        self.rocd = generate_roc_data(self.data)
        return self.rocd.hvplot.area(x="FPF", y="TPF", aspect="equal", xlim=(0, 1), ylim=(0, 1))

    def get_params(self):
        return (self.np, self.nn, self.mean_p, self.mean_n, self.std_p, self.std_n)
    def view(self):
        self.data = generate_data(self.np, self.nn, self.mean_p, self.mean_n, self.std_p, self.std_n)
        self.params = self.get_params()
        return  self.data.hvplot.kde(by="Class"), self.f1()
    def view2(self):
        if not hasattr(self, "data") or self.get_params() != self.params:
            p1, p2 = self.view()
        else:
            p1 = self.data.hvplot.kde(by="Class")
            p2 = self.rocd.hvplot.area(x="FPF", y="TPF", aspect="equal", xlim=(0, 1), ylim=(0, 1))
        t = self.thresh
        fpf, tpf = get_fpf_tpf(self.data, t, self.np, self.nn)
        self.results.object = _compute_stats(self.data, t)
        return hv.Layout(p1*hv.VLine(t) + p2*hv.Ellipse(fpf, tpf, 0.1)).cols(1)
