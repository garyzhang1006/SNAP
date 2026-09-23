import numpy as np
S=np.array([[1.5434e-05,2.8509e-05,-1.5923e-05,6.3360e-05,3.2814e-07,1.1676e-05,1.4808e-05,-4.0919e-07,2.5973e-05,4.4317e-07],
 [2.8509e-05,8.2182e-05,-5.3772e-05,1.3961e-04,8.1074e-07,2.3456e-05,2.8577e-05,1.1207e-06,5.7357e-05,2.8235e-07],
 [-1.5923e-05,-5.3772e-05,1.4337e-03,-7.7178e-05,-2.4860e-06,-9.4041e-06,1.7853e-05,3.5287e-07,-1.9656e-05,-3.3875e-06],
 [6.3360e-05,1.3961e-04,-7.7178e-05,4.3401e-04,1.9061e-06,4.8008e-05,6.9736e-05,-1.1707e-07,1.6556e-04,-1.0158e-06],
 [3.2814e-07,8.1074e-07,-2.4860e-06,1.9061e-06,6.7365e-07,3.9806e-07,1.8321e-07,8.2570e-08,9.8076e-08,-2.3876e-09],
 [1.1676e-05,2.3456e-05,-9.4041e-06,4.8008e-05,3.9806e-07,1.4210e-05,1.0622e-05,-1.8317e-07,1.8578e-05,-8.8690e-08],
 [1.4808e-05,2.8577e-05,1.7853e-05,6.9736e-05,1.8321e-07,1.0622e-05,3.2552e-05,5.6932e-07,3.1616e-05,6.6854e-08],
 [-4.0919e-07,1.1207e-06,3.5287e-07,-1.1707e-07,8.2570e-08,-1.8317e-07,5.6932e-07,7.5772e-07,2.5154e-07,8.4758e-08],
 [2.5973e-05,5.7357e-05,-1.9656e-05,1.6556e-04,9.8076e-08,1.8578e-05,3.1616e-05,2.5154e-07,9.8193e-05,-9.0688e-07],
 [4.4317e-07,2.8235e-07,-3.3875e-06,-1.0158e-06,-2.3876e-09,-8.8690e-08,6.6854e-08,8.4758e-08,-9.0688e-07,1.5477e-07]])
rel=np.array([0.927, 0.584, 0.993, 0.93, 0.757, 0.86, 0.392, 0.273, 0.888, 0.5])
v=np.clip(np.diag(S),1e-9,None); noise=v*(1-rel)/rel  # per-half item-noise variance of a trait mean
S=(S+S.T)/2; w_,V_=np.linalg.eigh(S); w_=np.clip(w_,0,None); S=(V_*w_)@V_.T; L=V_*np.sqrt(w_)
true=np.sqrt(S.sum()/np.trace(S))
# snap-r2-r1-18b: r1_power.py's rule-one pass rate, with and without recentring the
# remaining seeds inside the delete-one-seed jackknife. Lines above are r1_power.py
# verbatim; one() below keeps its draws and adds the recentred jackknife that
# SNAP compute2/analysis/estimates.seed_jackknife computes (estimate on sub_runs).
import json
def one(rng,scale=1.0,sizes=5,R=9,Lm=None):
    Lm=L if Lm is None else Lm
    TA=np.zeros((sizes,R)); UA=np.zeros((sizes,R)); As=[]; Bs=[]
    for c in range(sizes):
        e=(Lm@rng.normal(size=(10,R))).T*scale
        a=e+rng.normal(size=(R,10))*np.sqrt(2*noise); b=e+rng.normal(size=(R,10))*np.sqrt(2*noise)
        As.append(a.copy()); Bs.append(b.copy())
        a-=a.mean(0); b-=b.mean(0)
        TA[c]=a.sum(1)*b.sum(1); UA[c]=(a*b).sum(1)
    theta=TA.sum()/UA.sum()
    loo=np.array([(TA.sum()-TA[:,r].sum())/(UA.sum()-UA[:,r].sum()) for r in range(R)])
    se=np.sqrt((R-1)/R*((loo-loo.mean())**2).sum()); lo=theta-2.306*se
    A=np.array(As); B=np.array(Bs)
    def th(A,B):
        d=A-A.mean(1,keepdims=True); f=B-B.mean(1,keepdims=True)
        return (d.sum(-1)*f.sum(-1)).sum()/(d*f).sum()
    loo2=np.array([th(np.delete(A,r,1),np.delete(B,r,1)) for r in range(R)])
    se2=np.sqrt((R-1)/R*((loo2-loo2.mean())**2).sum()); lo2=theta-2.306*se2
    return np.sqrt(max(theta,0)), (np.sqrt(lo) if lo>0 else 0.0), (np.sqrt(lo2) if lo2>0 else 0.0), se, se2
rng=np.random.default_rng(20260923)
res=np.array([one(rng) for _ in range(4000)])
L_ind=np.diag(np.sqrt(np.diag(S)))
res0=np.array([one(rng,Lm=L_ind) for _ in range(4000)])
out={"true":float(true),"median_lambda":float(np.median(res[:,0])),"p5_p95":[float(x) for x in np.percentile(res[:,0],[5,95])],
     "pass_rate_r1_power_jackknife":float((res[:,1]>1).mean()),"pass_rate_recentred_jackknife":float((res[:,2]>1).mean()),
     "median_se_theta_r1_power":float(np.median(res[:,3])),"median_se_theta_recentred":float(np.median(res[:,4])),
     "null_diagonal_sigma":{"median_lambda":float(np.median(res0[:,0])),"pass_rate_r1_power_jackknife":float((res0[:,1]>1).mean()),
                            "pass_rate_recentred_jackknife":float((res0[:,2]>1).mean())},
     "note":"null here uses diagonal Sigma_E with rng continued; RESULT.txt's null used an independent-seed covariance whose construction is not in r1_power.py"}
print(json.dumps(out,indent=1))
open("/kaggle/working/r1_18b_jackknife_recentring.json","w").write(json.dumps(out,indent=1))
