import jax.numpy as np
from jax.lax import *
from jax import custom_jvp,jvp
from functools import partial

def odeint44(f,x0,t,*P):
    return _odeint44(f,x0,t,*P)


def rk_step(x_prev, t_prev, h,f,*P):
    k1 = f(x_prev, t_prev,*P)
    k2 = f(x_prev + h*0.5 * k1, t_prev + 0.5 * h,*P)
    k3 = f(x_prev + h*0.5 * k2, t_prev + 0.5 * h,*P)
    k4 = f(x_prev + h*k3, t_prev + h,*P)

    x = x_prev + h *(k1 + 2 * k2 + 2 * k3 + k4) / 6
    t_now = t_prev + h
    return x,t_now


def next_step_simulation(x_prev,t_prev,h,f,*P):
    x,t_now=rk_step(x_prev,t_prev,h,f.derivative,*P)
    y=f.output(x,t_now,*P)
    return x,t_now,y

@partial(custom_jvp,nondiff_argnums=(0,))
def _odeint44(f,x0,t,*P):
    h=t[1]-t[0]

    def scan_fun(state,t):

        x_prev,t_prev,y_prev=state

        x,t_now,y=next_step_simulation(x_prev,t_prev,h,f,*P)

        return (x,t_now,y),(x,y)


    y0=f.output(x0,0.,*P)
    vect,(xs,ys)=scan(scan_fun,(x0,t[0],y0),t[1:])

    xs=np.transpose(np.concatenate((x0[None], xs)))
    ys=np.transpose(np.concatenate((y0[None], ys)))

    return xs,ys


@_odeint44.defjvp
def _odeint44_jvp(f, primals, tangents):
    x0, t, *P = primals
    delta_x0, _, *dP = tangents
    nPdP = len(P)

    def f_aug(x,delta_x, t, *P_and_dP):
        P, dP = P_and_dP[:nPdP], P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x, t, *P), (delta_x,
                                                    0., *dP))
        return tangent_dot

    xs,xs_dot,ys,ys_dot = odeint44_etendu(f,f_aug,nPdP,x0,delta_x0,t, *P, *dP)
    return (xs,ys),(xs_dot,ys_dot)

def rk44_step_der(x_prev, t_prev, delta_x_prev,h,f_aug,f,nPdP,*P_and_dP):
    P,_ = P_and_dP[:nPdP],P_and_dP[nPdP:]
    k1 = f.derivative(x_prev, t_prev,*P)
    k2 = f.derivative(x_prev + h*0.5 * k1, t_prev + 0.5 * h,*P)
    k3 = f.derivative(x_prev + h*0.5 * k2, t_prev + 0.5 * h,*P)
    k4 = f.derivative(x_prev + h*k3, t_prev + h,*P)

    dk1 = f_aug(x_prev, delta_x_prev, t_prev, *P_and_dP)
    dk2 = f_aug(x_prev + h*0.5 * k1, delta_x_prev + h * 0.5 * dk1,t_prev +
                0.5 * h,*P_and_dP)
    dk3 = f_aug(x_prev + h*0.5 * k2, delta_x_prev + h * 0.5 * dk2,t_prev +
                0.5 * h,*P_and_dP)
    dk4 = f_aug(x_prev + h * k3,delta_x_prev + h * dk3, t_prev + h,*P_and_dP)

    x = x_prev + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    delta_x = delta_x_prev + h *(dk1 + 2 * dk2 + 2 * dk3 + dk4) / 6
    return delta_x,x

def next_der_step_simulation(x_prev,t_prev,delta_x_prev,h,f_aug,f,
                             nPdP,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]
    delta_x,x = rk44_step_der(x_prev, t_prev, delta_x_prev,h,f_aug,f,nPdP,
                              *P_and_dP)
    t_now=t_prev+h
    y=f.output(x,t_now,*P)
    delta_y = jvp(f.output, (x, t_now, *P), (delta_x, 0., *dP))[1]
    return delta_x,delta_y,x,y,t_now

def odeint44_etendu(f,f_aug,nPdP,x0,delta_x0,t,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]
    h=t[1]-t[0]

    def scan_fun(state, t):

        x_prev,delta_x_prev,y_prev,delta_y_prev,t_prev=state

        delta_x,delta_y,x,y,t_now=next_der_step_simulation(x_prev,t_prev,
                            delta_x_prev, h,f_aug,f,nPdP,*P_and_dP)

        return (x,delta_x,y,delta_y,t_now), (x,delta_x,y,delta_y)

    for element in f.__dict__.keys(): # pour eviter erreurs de code
        if hasattr(f.__dict__[element],'primal'):
            f.__dict__[element]=f.__dict__[element].primal

    y0=f.output(x0,0.,*P)
    delta_y0=jvp(f.output,(x0,0.,*P),(delta_x0,0.,*dP))[1]
    vect,(xs,delta_xs,ys,delta_ys)=scan(scan_fun,(x0,delta_x0,y0,delta_y0,
                        t[0]),t[1:])

    xs=np.transpose(np.concatenate((x0[None], xs)))
    ys=np.transpose(np.concatenate((y0[None], ys)))
    delta_xs=np.transpose(np.concatenate((delta_x0[None], delta_xs)))
    delta_ys = np.transpose(np.concatenate((delta_y0[None], delta_ys)))

    return xs,delta_xs,ys,delta_ys


def get_indice(names,valeur,output):
    if len(output)==1:
        return valeur[names.index(output[0])]
    else:
        return (valeur[names.index(i)] for i in output)
