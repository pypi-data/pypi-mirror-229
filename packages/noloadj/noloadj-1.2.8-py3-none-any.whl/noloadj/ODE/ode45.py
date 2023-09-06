import jax.numpy as np
from jax.lax import *
from jax import custom_jvp,jvp
from functools import partial
from noloadj.ODE.ode44 import rk44_step_der

def odeint45(f,x0,t,*P,T=0.,h0=1e-5,tol=1.48e-8):
    return _odeint45(f,h0,tol,x0,t,T,*P)


def rk_step(x_prev, t_prev, h,f,*P):
    k1=f(x_prev, t_prev,*P)
    k2 = f(x_prev + h*0.2 * k1, t_prev + 0.2 * h,*P)
    k3 = f(x_prev + h*(3 * k1 + 9 * k2) / 40,t_prev + 3 * h / 10,*P)
    k4 = f(x_prev + h*(44 * k1 / 45 - 56 * k2 / 15 + 32 * k3 / 9),t_prev +
           4 * h / 5,*P)
    k5 = f(x_prev + h*(19372 * k1 / 6561 - 25360 * k2 / 2187 +
            64448 * k3 / 6561- 212 * k4 / 729),
           t_prev + 8 * h / 9,*P)
    k6 = f(x_prev + h*(9017 * k1 / 3168 - 355 * k2 / 33 + 46732 * k3 / 5247+
            49 * k4 / 176 - 5103 * k5 / 18656),t_prev + h,*P)
    k7 = f(x_prev + h*(35 * k1 / 384 + 500 * k3 / 1113 +
            125 * k4 / 192 -2187 * k5 / 6784 + 11 * k6 / 84),t_prev + h,*P)

    x = x_prev + h *(35 * k1 / 384 + 500 * k3 / 1113 + 125 * k4 / 192
             -2187 * k5 / 6784 + 11 * k6 / 84)
    xest = x_prev + h *(5179 * k1 / 57600 + 7571* k3 / 16695 + 393 * k4 /640
            - 92097 * k5 / 339200 + 187 * k6 / 2100 + k7 / 40)
    t_now = t_prev + h
    return x, xest, t_now


def optimal_step(x,xest,h,tol,x_prev):
    e=np.sqrt(np.sum(((x-xest)/
                      (tol+tol*np.maximum(np.abs(x),np.abs(x_prev))))**2))
    hopt=h*(e)**(-1/5)
    hnew=np.minimum(1.5*h,0.9*hopt)
    return hnew

def interpolation(x_prev,y_prev,t_prev,x,y,t_now,tchoc):
    xchoc=(x_prev-x)*tchoc/(t_prev-t_now)+(t_prev*x-t_now*x_prev)/(t_prev-t_now)
    ychoc=(y_prev-y)*tchoc/(t_prev-t_now)+(t_prev*y-t_now*y_prev)/(t_prev-t_now)
    return xchoc,ychoc

def compute_new_point(state):
    x,h,x_prev,t_prev,t_now,y_prev,y,var_seuil,var_seuil_prev=state
    tchoc=(-t_prev*var_seuil+t_now*var_seuil_prev)/(var_seuil_prev-var_seuil)
    h=tchoc-t_prev
    xchoc,ychoc=interpolation(x_prev,y_prev,t_prev,x,y,t_now,tchoc)
    return xchoc,h,x_prev,t_prev,tchoc,y_prev,ychoc,var_seuil,var_seuil_prev

def interp_state_chgt(x_prev,y_prev,yb,t_prev,x,y,t_now,f,i,h,c,cnew):
    ind=np.where(np.array_equiv(y,yb),-1,np.argmax(np.abs(y-yb)))
    val_seuil=yb[ind]
    condition = np.bitwise_and(np.sign(x[ind]-val_seuil)!=np.sign(
            x_prev[ind]-val_seuil),np.not_equal(ind,-1))
    condition=np.bitwise_and(condition,np.bitwise_not(np.allclose(
            x_prev[ind]-val_seuil,0.)))
    x,h,_,_,t_now,_,y,_,_=cond(condition,compute_new_point,
                lambda state:state,(x,h,x_prev,t_prev,t_now,y_prev,y,
                                    x[ind]-val_seuil,x_prev[ind]-val_seuil))
    if hasattr(f,'commande'):
        _,x,y=f.update(x,y,t_now,i,cnew)
    else:
        _,x,y=f.update(x,y,t_now,i)
    return x,y,h,t_now

def next_step_simulation(x_prev,t_prev,y_prev,i,c,h,f,tol,T,*P):
    if hasattr(f,'etat'):
        f.etat=i
    x,xest,t_now=rk_step(x_prev,t_prev,h,f.derivative,*P)
    if hasattr(f,'computeotherX'):
        x=f.computeotherX(x,t_now,*P)
        xest=f.computeotherX(xest,t_now,*P)
    y=f.output(x,t_now,*P)
    hopt,cnew,tpdi=0.,0,0.
    if hasattr(f,'update'):
        if hasattr(f,'commande'):
            tpdi,cnew=f.commande(t_now,T)
            inew,_,yb=f.update(x,y,t_now,i,cnew)
        else:
            cnew=c
            inew,_,yb=f.update(x,y,t_now,i)
        x,y,h,t_now=cond(np.bitwise_not(np.allclose(i,inew)),lambda state:
            interp_state_chgt(x_prev,y_prev,yb,t_prev,x,y,t_now,f,i,h,c,cnew),
                         lambda state:state,(x,y,h,t_now))

        y=f.output(x,t_now,*P)
        hopt = optimal_step(x,xest, h, tol,x_prev)
        if hasattr(f,'commande'):
            hopt=np.minimum(tpdi-t_now,hopt)
        hopt=np.where(np.bitwise_not(np.allclose(i,inew)),1e-8,hopt) # pour accelerer code
    else:
        inew=i
        cnew=c
    if hasattr(f,'event'):
        for e in f.event:
            name,signe_str,seuil,name2,chgt_etat=e
            var_seuil,var_seuil_prev=get_indice(f.xnames,x,[name]),\
                            get_indice(f.xnames,x_prev,[name])
            signe=np.where(signe_str=='<',-1,1)
            condition = np.bitwise_and(np.sign(var_seuil-seuil)==signe,
                       np.bitwise_not(np.allclose(var_seuil_prev-seuil,0.)))
            hopt = optimal_step(x, xest, h, tol,x_prev)
            x,h,_,_,t_now,_,y,_,_=cond(condition,compute_new_point,
                lambda state:state,(x,h,x_prev,t_prev,t_now,y_prev,y,
                                    var_seuil-seuil,var_seuil_prev-seuil))
            xevent=cond(condition,chgt_etat,lambda state:state,
                                        get_indice(f.xnames,x,[name2]))
            x=x.at[f.xnames.index(name2)].set(xevent)
            y=f.output(x,t_now,*P)
    elif not hasattr(f,'event') and not hasattr(f,'update'):
        hopt = optimal_step(x, xest, h, tol,x_prev)
    return x,t_now,y,hopt,inew,cnew

@partial(custom_jvp,nondiff_argnums=(0,1,2))
def _odeint45(f,h0,tol,x0,t,T,*P):

    def scan_fun(state,t):

        def cond_fn(state):
            _,_,_,x_prev,t_prev,_,_,h,_,_=state
            return (t_prev<t) & (h>0)

        def body_fn(state):
            _,_,_,x_prev,t_prev,y_prev,_,h,i,c=state

            x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                    i,c,h,f,tol,T,*P)

            return x_prev,t_prev,y_prev,x,t_now,y,h,hopt,inew,cnew

        x_prev,t_prev,y_prev,x_now,t_now,y_now,h,hopt,i,c = while_loop(cond_fn,
                                                                  body_fn,state)
        #interpolation lineaire
        x,y=interpolation(x_prev,y_prev,t_prev,x_now,y_now,t_now,t)
        if hasattr(f,'update'):
            hnew=1e-8
        else:
            hnew=h0
        return (x_prev,t_prev,y_prev,x,t,y,h,hnew,i,c),(x,y,i)

    if hasattr(f,'etat'):
        i0=f.etat
    else:
        i0=0
    if hasattr(f,'commande'):
        _,c0=f.commande(t[0],T)
    else:
        c0=0
    y0=f.output(x0,0.,*P)
    vect,(xs,ys,etats)=scan(scan_fun,(x0,t[0],y0,x0,t[0],y0,h0,h0,i0,c0),t[1:])
    if hasattr(f,'etat'):
        f.etat=vect[8]
    xs=np.transpose(np.concatenate((x0[None], xs)))
    ys=np.transpose(np.concatenate((y0[None], ys)))
    if hasattr(f,'etat'):
        if isinstance(i0,int):
            etats=np.insert(etats,0,i0)
        else:
            etats=np.transpose(np.concatenate((i0[None], etats)))
        return xs,ys,etats
    else:
        return xs,ys


@_odeint45.defjvp
def _odeint45_jvp(f,h0,tol, primals, tangents):
    x0, t,T, *P = primals
    delta_x0, _,_, *dP = tangents
    nPdP = len(P)

    def f_aug(x,delta_x, t, *P_and_dP):
        P, dP = P_and_dP[:nPdP], P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x, t, *P), (delta_x,
                                                    0., *dP))
        return tangent_dot
    if hasattr(f,'etat'):
        xs,xs_dot,ys,ys_dot,etats=odeint45_etendu(f,f_aug,nPdP,h0,tol,x0,
                                                  delta_x0, t,T, *P, *dP)
        return (xs,ys,etats),(xs_dot,ys_dot,etats)
    else:
        xs,xs_dot,ys,ys_dot = odeint45_etendu(f,f_aug,nPdP,h0,tol, x0,delta_x0,
                                        t,T, *P, *dP)
        return (xs,ys),(xs_dot,ys_dot)


def rk45_step_der(x_prev, t_prev, delta_x_prev,h,f_aug,f,nPdP,*P_and_dP):
    dk1 = f_aug(x_prev, delta_x_prev, t_prev, *P_and_dP)
    dk2 = f_aug(x_prev, delta_x_prev + h * 0.2 * dk1,t_prev +
                0.2 * h , *P_and_dP)
    dk3 = f_aug(x_prev, delta_x_prev + h * (3 * dk1
                + 9 * dk2) / 40,t_prev+3 * h / 10, *P_and_dP)
    dk4 = f_aug(x_prev,delta_x_prev +
         h*(44 * dk1 / 45 - 56 * dk2 /15+32*dk3/9),t_prev + 4 * h / 5,*P_and_dP)
    dk5 = f_aug(x_prev, delta_x_prev + h *
        (19372 * dk1 / 6561 - 25360*dk2/2187+ 64448 * dk3 / 6561 - 212 * dk4
            / 729),t_prev + 8 * h / 9, *P_and_dP)
    dk6 = f_aug(x_prev,delta_x_prev+h*(9017 *
            dk1 / 3168 -355 *dk2/33 +46732*dk3
            / 5247 + 49 * dk4 / 176 - 5103 * dk5 / 18656),t_prev + h, *P_and_dP)
    delta_x = delta_x_prev + h *(35 * dk1 / 384 + 500 * dk3 / 1113 +
            125 * dk4 / 192 - 2187 * dk5 / 6784 + 11 * dk6 / 84)
    return delta_x,x_prev

def next_der_step_simulation(x_prev,t_prev,delta_x_prev,x,t_now,h,f_aug,f,
                             nPdP,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]
    if hasattr(f,'update'):
        delta_x,X=rk45_step_der(x_prev,t_prev,delta_x_prev,h,f_aug,f,nPdP,
                                *P_and_dP)
    else:
        delta_x,X=rk44_step_der(x_prev,t_prev,delta_x_prev,h,f_aug,f,nPdP,
                                *P_and_dP)
    if hasattr(f, 'computeotherX'):
        delta_x = jvp(f.computeotherX, (x, t_now, *P), (delta_x, 0., *dP))[1]
    delta_y = jvp(f.output, (x, t_now, *P), (delta_x, 0., *dP))[1]
    return delta_x,delta_y,X

def odeint45_etendu(f,f_aug,nPdP,h0,tol,x0,delta_x0,t,T,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]
    dh=t[1]-t[0]

    def scan_fun(state, t):

        def cond_fn(state):
            _,_,_,x_prev,y_prev,t_prev,_,h,_,_,_=state
            return (t_prev < t) & (h > 0)

        def body_fn(state):
            _,_,_,x_prev,y_prev,t_prev,_,h,_,i,c=state

            x,t_now,y,hopt,inew,cnew=next_step_simulation(x_prev,t_prev,y_prev,
                                                        i,c,h,f,tol,T,*P)

            return x_prev,y_prev,t_prev,x,y,t_now,h,hopt,i,inew,cnew

        x_prev2,_,y_prev2,_,t_prev2,x_prev1,delta_x_prev,y_prev1,delta_y_prev,\
                    t_prev1,h,hopt,i,inew,c,T_prev,X_prev=state
        x_prev,y_prev,t_prev,x_now,y_now,t_now,h,hopt,i,inew,c = while_loop(
            cond_fn,body_fn, (x_prev2,y_prev2,t_prev2,x_prev1,y_prev1,t_prev1,h,
                              hopt,i,inew,c))
        # interpolation lineaire
        x,y=interpolation(x_prev,y_prev,t_prev,x_now,y_now,t_now,t)

        if hasattr(f,'etat'):
            f.etat=i
        if hasattr(f,'update'):
            delta_x,delta_y,X=next_der_step_simulation(x_prev1,t_prev1,
                                delta_x_prev,x,t,dh,f_aug,f,nPdP,*P_and_dP)
        else:
            delta_x,delta_y,X=next_der_step_simulation(X_prev,T_prev,
                                delta_x_prev,x,t,dh,f_aug,f,nPdP,*P_and_dP)

        if hasattr(f,'update'):
            hnew=1e-8
        else:
            hnew=h0
        return (x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev,x,delta_x,y,
            delta_y,t,h,hnew,i,inew,c,T_prev+dh,X),(x,delta_x,y,delta_y,inew)

    for element in f.__dict__.keys(): # pour eviter erreurs de code
        if hasattr(f.__dict__[element],'primal'):
            f.__dict__[element]=f.__dict__[element].primal
    if hasattr(f,'etat'):
        i0=f.etat
    else:
        i0=0
    if hasattr(f,'commande'):
        _,c0=f.commande(t[0],T)
    else:
        c0=0
    y0=f.output(x0,0.,*P)
    delta_y0=jvp(f.output,(x0,0.,*P),(delta_x0,0.,*dP))[1]
    vect,(xs,delta_xs,ys,delta_ys,etats)=scan(scan_fun,(x0,delta_x0,y0,delta_y0,
             t[0],x0,delta_x0,y0,delta_y0,t[0],h0,h0,i0,i0,c0,t[0],x0),t[1:])
    if hasattr(f,'etat'):
        f.etat=vect[13]
    xs=np.transpose(np.concatenate((x0[None], xs)))
    ys=np.transpose(np.concatenate((y0[None], ys)))
    delta_xs=np.transpose(np.concatenate((delta_x0[None], delta_xs)))
    delta_ys = np.transpose(np.concatenate((delta_y0[None], delta_ys)))
    if hasattr(f,'etat'):
        if isinstance(i0,int):
            etats=np.insert(etats,0,i0)
        else:
            etats=np.transpose(np.concatenate((i0[None], etats)))
        return xs,delta_xs,ys,delta_ys,etats
    else:
        return xs,delta_xs,ys,delta_ys


def get_indice(names,valeur,output):
    if len(output)==1:
        return valeur[names.index(output[0])]
    else:
        return (valeur[names.index(i)] for i in output)
