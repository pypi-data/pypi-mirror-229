from noloadj.ODE.ode45_fft import odeint45_fft,odeint45_fft_etendu
from noloadj.ODE.ode_tools import *
from jax.lax import while_loop
from noloadj.ODE.ode45_extract import _odeint45,odeint45_etendu

def odeint45_extract_fft(f,x0,*P,M,T=0.,h0=1e-5,tol=1.48e-8):
    return _odeint45_extract_fft(f,h0,tol,M,x0,T,*P)


@partial(custom_jvp,nondiff_argnums=(0,1,2,3))
def _odeint45_extract_fft(f,h0,tol,M,x0,T,*P):

    freq_cstr=dict(zip(list(f.freq_constraints.keys()),
                                [0.] * len(f.freq_constraints)))

    ts,xf,yf,cstr,ifinal=_odeint45(f,h0,T/M,tol,x0,T,*P)
    f.etat=ifinal
    _,_,module,phase=odeint45_fft(f,xf,np.linspace(ts,ts+T,M),*P,
                                    M=M,T=T,h0=h0)

    vect_freq=np.where(M//2==0,np.linspace(0.,(M/2-1)/T,M//2),
                          np.linspace(0.,(M-1)/(2*T),M//2))
    if hasattr(f,'freq_constraints'):
        for i in f.freq_constraints.keys():
            expression,_,name=f.freq_constraints[i]
            ind = f.xnames.index(name)
            freq_cstr[i]=expression(module[ind],phase[ind],vect_freq,1/T)

    return (ts,xf,yf,cstr,freq_cstr)


@_odeint45_extract_fft.defjvp
def _odeint45_fft_jvp(f,h0,tol,M, primals, tangents):
    x0,T, *P = primals
    delta_x0,dT, *dP = tangents
    nPdP = len(P)

    def f_aug(x0,delta_x0, t, *P_and_dP):
        P,dP =P_and_dP[:nPdP],P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x0, t, *P), (delta_x0,
                                                            0., *dP))
        return tangent_dot

    xf,yf,cstr,freq_cstr,ts,dts,xf_dot,yf_dot,cstr_dot,freq_cstr_dot=\
        odeint45_extract_fft_etendu(f,f_aug,nPdP,h0,tol,M,x0,delta_x0,T,dT,
                                    *P,*dP)
    return (ts,xf,yf,cstr,freq_cstr),(dts,xf_dot,yf_dot,cstr_dot,freq_cstr_dot)


def odeint45_extract_fft_etendu(f,f_aug,nPdP,h0,tol,M,x0,delta_x0,T,dT,*P_and_dP):

    freq_cstr=dict(zip(list(f.freq_constraints.keys()),
                       [0.]*len(f.freq_constraints)))
    freq_delta_cstr=dict(zip(list(f.freq_constraints.keys()),
                             [0.]*len(f.freq_constraints)))

    xf,yf,cstr,ts,dts,delta_xf,delta_yf,delta_cstr,ifinal=odeint45_etendu(f,
                            f_aug,nPdP,h0,T/M,tol,x0,delta_x0,T,dT,*P_and_dP)
    f.etat=ifinal
    _,_,module,phase,_,_,dmodule,dphase=odeint45_fft_etendu(f,f_aug,nPdP,h0,
                     tol,M,xf,delta_xf,np.linspace(ts,ts+T,M),T,*P_and_dP)


    vect_freq=np.where(M//2==0,np.linspace(0.,(M/2-1)/T,M//2),
                          np.linspace(0.,(M-1)/(2*T),M//2))
    if hasattr(f,'freq_constraints'):
        for i in f.freq_constraints.keys():
            _,der_expression,name=f.freq_constraints[i]
            ind = f.xnames.index(name)
            freq_cstr[i],freq_delta_cstr[i]=der_expression(module[ind],
                phase[ind],dmodule[ind], dphase[ind],vect_freq,1//T)

    return xf,yf,cstr,freq_cstr,ts,dts,delta_xf,delta_yf,delta_cstr,\
           freq_delta_cstr


################################################################################

def Module_0Hz(name):
    def expression(module,phase,vect_freq,f):
        res=module[0]
        return res
    def der_expression(module,phase,dmodule,dphase,vect_freq,f):
        res=module[0]
        dres=dmodule[0]
        return res,dres
    return expression,der_expression,name

def Module_Fondamental(name):
    def expression(module,phase,vect_freq,f):
        indf=np.argmin(np.abs(vect_freq-f))
        res=module[indf]
        return res
    def der_expression(module,phase,dmodule,dphase,vect_freq,f):
        indf=np.argmin(np.abs(vect_freq-f))
        res=module[indf]
        dres=dmodule[indf]
        return res,dres
    return expression,der_expression,name

def Module_Harmoniques(name,number):
    def expression(module,phase,vect_freq,f):
        res=np.zeros(number)
        for j in range(len(res)):
            indf=np.argmin(np.abs(vect_freq-(j+2)*f))
            res=res.at[j].set(module[indf])
        return res
    def der_expression(module,phase,dmodule,dphase,vect_freq,f):
        res = np.zeros(number)
        dres=np.zeros(number)
        for j in range(len(res)):
            indf=np.argmin(np.abs(vect_freq-(j+2)*f))
            res=res.at[j].set(module[indf])
            dres=dres.at[j].set(dmodule[indf])
        return res,dres
    return expression,der_expression,name
