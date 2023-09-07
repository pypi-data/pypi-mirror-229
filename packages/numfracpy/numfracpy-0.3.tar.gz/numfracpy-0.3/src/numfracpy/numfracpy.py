import math
import numpy as np
from scipy import integrate
import scipy.special as special


#=============================================================================
# This Calculates the Riemann-Liouville Integral of order alpha
#=============================================================================

def RL_integral(f,a,t,alpha):
    if alpha <= 0: #alpha has to be greater than zero
        return "alpha cannot be less or equal than zero"
    if a == t: #There are issues with quad command if a = t
        return 0

    x2 = lambda s: ((t-s)**(alpha-1))*f(s)/special.gamma(alpha)
    return integrate.quad(x2, a, t)[0]


#=============================================================================
# This Calculates the Caputo Derivative for 0 < alpha < 1 by L1 Method
#=============================================================================

def Caputo_der1(f,t,dt,alpha):
    if alpha <= 0: #alpha has to be greater than zero
        return "alpha cannot be less or equal than zero"
    if alpha >= 1: #alpha has to be less than one
        return "alpha cannot be greater or equal than one"

    #We need to adjust that t = tn be equal to n*dt. Ideally, we always should
    #have n = t/dt is an integer
    n = int(t/dt)
    t = n*dt

    def b(k): #It is assumed k is an integer
        bk = (dt**(-alpha))*((k+1)**(1-alpha) - k**(1-alpha))/special.gamma(2-alpha)
        return bk

    suma = 0
    for k in range(0,n):
        suma += b(n-k-1)*(f((k+1)*dt) - f(k*dt))

    Cap_Der1 = suma

    return Cap_Der1


#=============================================================================
# This Calculates the Caputo Derivative for 1 < alpha < 2 by L2 Method
#=============================================================================

def Caputo_der2(f,t,dt,alpha):
    if alpha <= 1: #alpha has to be greater than one
        return "alpha cannot be less or equal than one"
    if alpha >= 2: #alpha has to be less than two
        return "alpha cannot be greater or equal than two"

    #We need to adjust that t = tn be equal to n*dt. Ideally, we always should
    #have n = t/dt is an integer
    n = int(t/dt)
    t = n*dt

    def w(k): #It is assumed k is an integer
        if k==-1:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*1
        elif k==0:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*(2**(2-alpha)-3)
        elif 1<=k and k<=n-2:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*(((k+2)**(2-alpha))-(3*((k+1)**(2-alpha)))+3*(k**(2-alpha))-((k-1)**(2-alpha)))
        elif k==n-1:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*(-2*(n**(2-alpha))+3*((n-1)**(2-alpha))-((n-2)**(2-alpha)))
        elif k==n:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*((n**(2-alpha))-((n-1)**(2-alpha)))

        return wk

    suma = 0
    for k in range(-1,n+1):
        suma += w(k)*f((n-k)*dt)

    Cap_Der2 =  suma

    return Cap_Der2


#=============================================================================
# This Calculates the Riemann-Liouville Derivative for 0 < alpha < 1
#=============================================================================

def RL_der1(f,t,dt,alpha):
    if alpha <= 0: #alpha has to be greater than zero
        return "alpha cannot be less or equal than zero"
    if alpha >= 1: #alpha has to be less than one
        return "alpha cannot be greater or equal than one"
    #We need to adjust that t = tn be equal to n*dt. Ideally, we always should
    #have n = t/dt is an integer
    n = int(t/dt)
    t = n*dt

    def b(k): #It is assumed k is an integer
        bk = (dt**(-alpha))*((k+1)**(1-alpha) - k**(1-alpha))/special.gamma(2-alpha)
        return bk

    suma = 0
    for k in range(0,n):
        suma += b(n-k-1)*(f((k+1)*dt) - f(k*dt))

    RLDer1 = f(0)*(t**(-alpha))/special.gamma(1-alpha) + suma

    return RLDer1


#=================================================================================
# This Calculates the Riemann-Liouville Derivative for 1 < alpha < 2 by L2 Method
#=================================================================================

def RL_der2(f,t,dt,alpha):
    if alpha <= 1: #alpha has to be greater than one
        return "alpha cannot be less or equal than one"
    if alpha >= 2: #alpha has to be less than two
        return "alpha cannot be greater or equal than two"
    #We need to adjust that t = tn be equal to n*dt. Ideally, we always should
    #have n = t/dt is an integer
    n = int(t/dt)
    t = n*dt

    def w(k): #It is assumed k is an integer
        if k==-1:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*1
        elif k==0:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*(2**(2-alpha)-3)
        elif 1<=k and k<=n-2:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*(((k+2)**(2-alpha))-(3*((k+1)**(2-alpha)))+3*(k**(2-alpha))-((k-1)**(2-alpha)))
        elif k==n-1:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*(-2*(n**(2-alpha))+3*((n-1)**(2-alpha))-((n-2)**(2-alpha)))
        elif k==n:
            wk = ((dt**(-alpha))/special.gamma(3-alpha))*((n**(2-alpha))-((n-1)**(2-alpha)))

        return wk

    suma = 0
    for k in range(-1,n+1):
        suma += w(k)*f((n-k)*dt)

    der = (f(dt)-f(0))/dt

    RLDer2 = f(0)*(t**(-alpha))/special.gamma(1-alpha) + der*(t**(1-alpha))/special.gamma(2-alpha) + suma

    return RLDer2


#===============================================================================
# This Calculates the Grunwald-Letnikov derivative of order  0 < alpha < 1
#===============================================================================

def GLDer1(f,t,dt,alpha):
    if alpha <= 0: #alpha has to be greater than zero
        return "alpha cannot be less or equal than zero"
    if alpha >= 1: #alpha has to be less than one
        return "alpha cannot be greater or equal than one"

    #We need to adjust that t = tn be equal to n*dt. Ideally, we always should
    #have n = t/dt is an integer
    n = int(t/dt)
    t = n*dt

    #This calculates w_{j}^{(alpha)} by a recurrence relation
    W_Alpha = [1]
    for j in range(0,n):
        w_j_1 = W_Alpha[-1]*(j-alpha)/(j+1)
        W_Alpha.append(w_j_1)

    suma = 0
    for j in range(0,n+1):
        suma += W_Alpha[j]*f((n-j)*dt)
    GL1result = suma/(dt**(alpha))

    return GL1result

#===============================================================================
# This Calculates the Grunwald-Letnikov derivative of order  1 < alpha < 2
#==============================================================================

def GLDer2(f,t,dt,alpha):
    if alpha <= 1: #alpha has to be greater than one
        return "alpha cannot be less or equal than one"
    if alpha >= 2: #alpha has to be less than two
        return "alpha cannot be greater or equal than two"

    #We need to adjust that t = tn be equal to n*dt. Ideally, we always should
    #have n = t/dt is an integer
    n = int(t/dt)
    t = n*dt

    p = 1
    #This calculates w_{j}^{(alpha)} by a recurrence relation
    W_Alpha = [1]
    for j in range(0,n+p):
        w_j_1 = W_Alpha[-1]*(j-alpha)/(j+1)
        W_Alpha.append(w_j_1)

    suma = 0
    for j in range(0,n+p+1):
        suma += W_Alpha[j]*f((n-j+p)*dt)
    GL2result = suma/(dt**(alpha))

    return GL2result


#=================================================================================
# This solves a Frac. Dif. Eq. of the form: {C}_D^{alpha}u(t) = f(t,u(t))
#
# INPUT f = f(t,u(t))
#       Initial = [f(0),f'(0),f''(0),...]
#       [Interv[0],Interv[1]] = [a,b]
#       dx: step on the independent variable
#       alpha: Derivative order
#=================================================================================

def FODE(f,Initial,Interv,dx,alpha):
    m = math.ceil(alpha)

    if len(Initial) != m:
        print("The number of initial conditions is wrong!")

    #discretization of independent variable
    N_ = int((Interv[1]-Interv[0])/dx)
    x = np.linspace(Interv[0],Interv[1],N_+1)
    #Initial setup for dependent variable
    y = np.zeros(len(x))
    y[0] = Initial[0]

    def b(j,n):
        return ((n-j)**alpha - (n - 1 - j)**alpha)/special.gamma(alpha+1)

    def a(j,n):
        factor = (dx**alpha)/special.gamma(alpha + 2)
        if j == 0:
            return factor*((n-1)**(alpha+1) - (n-1-alpha)*(n**alpha))
        elif (1 <= j) and (j <= n-1):
            return factor*((n-j+1)**(alpha+1) - 2*(n-j)**(alpha+1) + (n-1-j)**(alpha+1))
        elif j == n:
            return factor
        else:
            print("Something went wrong in calculation for a(j,n)")

    #Calculation of the Numerical Solution
    for n in range(0,N_):

        #Predictor u_{n+1}^P
        sum1 = 0
        for j in range(0,m):
            sum1 += (x[n+1]**j)*Initial[j]/math.factorial(j)
        sum2 = 0
        for j in range(0,n+1):
            sum2 += (dx**alpha)*b(j,n+1)*f(x[j],y[j])
        uP = sum1 + sum2

        #Approximation for u_{n+1}
        sum3 = 0
        for j in range(0,n+1):
            sum3 += a(j,n+1)*f(x[j],y[j])

        y[n+1] = sum1 + sum3 + a(n+1,n+1)*f(x[n+1],uP) #Adams Predictor-Corrector

    return (x,y)


#=================================================================================
# This solves a System of Frac. Dif. Eqs. of the form: ...
#
# INPUT f = [f1(t,[u]),f2(t,[u]),...]
#       Initial = [u1(0),u2(0),...]
#       [Interv[0],Interv[1]] = [a,b]
#       dx: step on the independent variable
#       alpha = [alpha1,alpha2,...]
#=================================================================================

def SystemFODEs(f,Initial,Interv,dx,alpha):

    if len(f) != len(Initial):
        print("f and Initial have differente size.")

    #discretization of independent variable
    N_ = int((Interv[1]-Interv[0])/dx); print("N_ = ",N_)
    x = np.linspace(Interv[0],Interv[1],N_+1)
    #Initial setup for dependent variables
    num = len(f) #Number of functions
    ysol = []
    for i in range(0,num):
        y = [0]*len(x)
        ysol.append(y)
        ysol[i][0] = Initial[i]

    def b(j,n,alpha):
        return ((n-j)**alpha - (n - 1 - j)**alpha)/special.gamma(alpha+1)

    def a(j,n,alpha):
        factor = (dx**alpha)/special.gamma(alpha + 2)
        if j == 0:
            return factor*((n-1)**(alpha+1) - (n-1-alpha)*(n**alpha))
        elif (1 <= j) and (j <= n-1):
            return factor*((n-j+1)**(alpha+1) - 2*(n-j)**(alpha+1) + (n-1-j)**(alpha+1))
        elif j == n:
            return factor
        else:
            print("Something went wrong in calculation for a(j,n)")

    #Calculation of the Numerical Solution
    for n in range(0,N_):
        #print("n = ",n)
        #Predictors [u_{n+1}^P]
        for eq in range(0,num):
            uP = [0]*num

            sum1 = Initial[eq]
            sum2 = 0
            for j in range(0,n+1):
                yj_state = []
                xj = x[j]
                for eq1 in range(0,num):
                    valuej = ysol[eq1][j]
                    yj_state.append(valuej)
                yj_state.insert(0,xj)
                sum2 += b(j,n+1,alpha[eq])*f[eq](yj_state)

            uP[eq] = sum1 + (dx**alpha[eq])*sum2
            #print("uP[",eq,"] = ",uP[eq])

        #Approximation for u_{n+1}
        x_n_1 = x[n+1]
        uP.insert(0,x_n_1)

        for eq in range(0,num):
            sum1 = Initial[eq]
            sum3 = 0
            for j in range(0,n+1):
                yj_state = []
                xj = x[j]
                for eq1 in range(0,num):
                    valuej = ysol[eq1][j]
                    yj_state.append(valuej)
                yj_state.insert(0,xj)
                sum3 += a(j,n+1,alpha[eq])*f[eq](yj_state)

            ysol[eq][n+1] = sum1 + sum3 + a(n+1,n+1,alpha[eq])*f[eq](uP) #Adams Predictor-Corrector

    return (x,ysol)



#=====================================================================================
# This Calculates the Mittag-Leffler functions
#=====================================================================================

def LTInversion(t,Lambda,alpha,beta,gama,log_epsilon):
    # Evaluation of the relevant poles
    theta = np.angle(Lambda)
    kmin = np.ceil(-alpha/2.0 - theta/(2*np.pi))
    kmax = np.floor(alpha/2.0 - theta/(2*np.pi))
    k_vett = np.arange(kmin, kmax+1)
    s_star = np.abs(Lambda)**(1.0/alpha) * np.exp(1j*(theta+2*k_vett*np.pi)/alpha)


    # Evaluation of phi(s_star) for each pole
    phi_s_star = (np.real(s_star)+np.abs(s_star))/2
    # Sorting of the poles according to the value of phi(s_star)
    index_s_star = np.argsort(phi_s_star)
    phi_s_star = phi_s_star.take(index_s_star)
    s_star = s_star.take(index_s_star)


    # Deleting possible poles with phi_s_star=0
    index_save = phi_s_star > 1.00e-15
    s_star = s_star.repeat(index_save)
    phi_s_star = phi_s_star.repeat(index_save)
    # Inserting the origin in the set of the singularities
    s_star = np.hstack([[0], s_star])
    phi_s_star = np.hstack([[0], phi_s_star])
    J1 = len(s_star)
    J = J1 - 1


    # Strength of the singularities
    p = gama*np.ones((J1,), float)
    p[0] = max(0,-2*(alpha*gama-beta+1))
    q = gama*np.ones((J1,), float)
    q[-1] = float('inf')
    phi_s_star = np.hstack([phi_s_star, [float('inf')]])
    # Looking for the admissible regions with respect to round-off errors
    admissible_regions = \
       np.nonzero(np.bitwise_and(
           (phi_s_star[:-1] < (log_epsilon - np.log(np.finfo(np.float64).eps))/t),
           (phi_s_star[:-1] < phi_s_star[1:])))[0]
    #print(phi_s_star)

    # Initializing vectors for optimal parameters
    JJ1 = admissible_regions[-1]
    mu_vett = np.ones((JJ1+1,), float)*float('inf')
    N_vett = np.ones((JJ1+1,), float)*float('inf')
    h_vett = np.ones((JJ1+1,), float)*float('inf')
    #print(admissible_regions)


    # Evaluation of parameters for inversion of LT in each admissible region
    find_region = False
    while not find_region:
        for j1 in admissible_regions:
            if j1 < J1-1:
                muj, hj, Nj = OptimalParam_RB(t, phi_s_star[j1], phi_s_star[j1+1], p[j1], q[j1], log_epsilon)
                #print("I am in if.")
            else:
                muj, hj, Nj = OptimalParam_RU(t, phi_s_star[j1], p[j1], log_epsilon)
                #print("I am in else.")
            mu_vett[j1] = muj
            h_vett[j1] = hj
            N_vett[j1] = Nj
            #print("muj = ",muj,"  hj = ",hj,"  Nj = ",Nj)
        if N_vett.min() > 200: #500
            log_epsilon = log_epsilon + np.log(10)
        else:
            find_region = True
    # Selection of the admissible region for integration which
    # involves the minimum number of nodes
    iN = np.argmin(N_vett)
    N = N_vett[iN]
    mu = mu_vett[iN]
    h = h_vett[iN]


    # Evaluation of the inverse Laplace transform
    k = np.arange(-N, N+1)
    u = h*k
    z = mu*(1j*u+1.0)**2
    zd = -2.0*mu*u + 2j*mu
    zexp = np.exp(z*t)
    F = z**(alpha*gama-beta)/(z**alpha - Lambda)**gama*zd
    S = zexp*F ;
    Integral = h*np.sum(S)/(2.0*np.pi*1j)
    # Evaluation of residues
    ss_star = s_star[iN+1:]
    Residues = np.sum(1.0/alpha*(ss_star)**(1-beta)*np.exp(t*ss_star))
    # Evaluation of the ML function
    E = Integral + Residues
    if np.imag(Lambda) == 0.:
        E = np.real(E)
    return E

# ============================================================================
# Finding optimal parameters in a right-bounded region
# ============================================================================

def OptimalParam_RB(t, phi_s_star_j, phi_s_star_j1, pj, qj, log_epsilon):
    # Definition of some constants
    log_eps = -36.043653389117154 # log(eps)
    fac = 1.01
    conservative_error_analysis = False
    # Maximum value of fbar as the ration between tolerance and round-off unit
    f_max = np.exp(log_epsilon - log_eps)
    # Evaluation of the starting values for sq_phi_star_j and sq_phi_star_j1
    sq_phi_star_j = np.sqrt(phi_s_star_j)
    threshold = 2.0*np.sqrt((log_epsilon - log_eps)/t)
    #print(log_epsilon); print(log_eps)

    sq_phi_star_j1 = min(np.sqrt(phi_s_star_j1), threshold - sq_phi_star_j)
    #print("sq_phi_star_j = ",sq_phi_star_j,"  threshold = ",threshold,"  sq_phi_star_j1 = ",sq_phi_star_j1)

    # Zero or negative values of pj and qj
    if pj < 1.0e-14 and qj < 1.0e-14:
        sq_phibar_star_j = sq_phi_star_j
        sq_phibar_star_j1 = sq_phi_star_j1
        adm_region = 1

    # Zero or negative values of just pj
    if pj < 1.0e-14 and qj >= 1.0e-14:
        sq_phibar_star_j = sq_phi_star_j
        if sq_phi_star_j > 0:
            f_min = fac*(sq_phi_star_j/(sq_phi_star_j1-sq_phi_star_j))**qj
        else:
            f_min = fac
        if f_min < f_max:
            f_bar = f_min + f_min/f_max*(f_max-f_min)
            fq = f_bar**(-1/qj)
            sq_phibar_star_j1 = (2*sq_phi_star_j1-fq*sq_phi_star_j)/(2+fq)
            adm_region = True
        else:
            adm_region = False

    # Zero or negative values of just qj
    if pj >= 1.0e-14 and qj < 1.0e-14:
        sq_phibar_star_j1 = sq_phi_star_j1
        f_min = fac*(sq_phi_star_j1/(sq_phi_star_j1-sq_phi_star_j))**pj
        if f_min < f_max:
            f_bar = f_min + f_min/f_max*(f_max-f_min)
            fp = f_bar**(-1.0/pj)
            sq_phibar_star_j = (2.0*sq_phi_star_j+fp*sq_phi_star_j1)/(2-fp)
            adm_region = True
        else:
            adm_region = False
    # Positive values of both pj and qj
    if pj >= 1.0e-14 and qj >= 1.0e-14:
        f_min = fac*(sq_phi_star_j+sq_phi_star_j1) / \
                (sq_phi_star_j1-sq_phi_star_j)**max(pj, qj)
        if f_min < f_max:
            f_min = max(f_min,1.5)
            f_bar = f_min + f_min/f_max*(f_max-f_min)
            fp = f_bar**(-1/pj)
            fq = f_bar**(-1/qj)
            if ~conservative_error_analysis:
                w = -phi_s_star_j1*t/log_epsilon
            else:
                w = -2.0*phi_s_star_j1*t/(log_epsilon-phi_s_star_j1*t)
            den = 2+w - (1+w)*fp + fq
            sq_phibar_star_j = ((2+w+fq)*sq_phi_star_j + fp*sq_phi_star_j1)/den
            sq_phibar_star_j1 = (-(1.+w)*fq*sq_phi_star_j + (2.0+w-(1.+w)*fp)*sq_phi_star_j1)/den
            adm_region = True
        else:
            adm_region = False
    if adm_region:
        log_epsilon = log_epsilon  - np.log(f_bar)
        if not conservative_error_analysis:
            w = -sq_phibar_star_j1**2*t/log_epsilon
        else:
            w = -2.0*sq_phibar_star_j1**2*t/(log_epsilon-sq_phibar_star_j1**2*t)
        muj = (((1.+w)*sq_phibar_star_j + sq_phibar_star_j1)/(2.0+w))**2
        hj = -2.0*np.pi/log_epsilon*(sq_phibar_star_j1-sq_phibar_star_j) \
             / ((1.+w)*sq_phibar_star_j + sq_phibar_star_j1)
        Nj = np.ceil(np.sqrt(1-log_epsilon/t/muj)/hj)
    else:
        muj = 0
        hj = 0
        Nj = float('inf')
    return muj, hj, Nj

# ============================================================================
# Finding optimal parameters in a right-unbounded region
# ============================================================================

def OptimalParam_RU(t, phi_s_star_j, pj, log_epsilon):
    # Evaluation of the starting values for sq_phi_star_j
    sq_phi_s_star_j = np.sqrt(phi_s_star_j)
    if phi_s_star_j > 0:
        phibar_star_j = phi_s_star_j*1.01
    else:
        phibar_star_j = 0.01
    sq_phibar_star_j = np.sqrt(phibar_star_j)
    # Definition of some constants
    f_min = 1;    f_max = 10;    f_tar = 5
    # Iterative process to look for fbar in [f_min,f_max]
    while True:
        phi_t = phibar_star_j*t
        log_eps_phi_t = log_epsilon/phi_t
        Nj = np.ceil(phi_t/np.pi*(1.0 - 3*log_eps_phi_t/2 + np.sqrt(1-2*log_eps_phi_t)))
        A = np.pi*Nj/phi_t
        sq_muj = sq_phibar_star_j*np.abs(4-A)/np.abs(7-np.sqrt(1+12*A))
        fbar = ((sq_phibar_star_j-sq_phi_s_star_j)/sq_muj)**(-pj)
        if (pj < 1.0e-14) or (f_min < fbar and fbar < f_max):
            break
        sq_phibar_star_j = f_tar**(-1./pj)*sq_muj + sq_phi_s_star_j
        phibar_star_j = sq_phibar_star_j**2
    muj = sq_muj**2
    hj = (-3*A - 2 + 2*np.sqrt(1+12*A))/(4-A)/Nj
    # Adjusting integration parameters to keep round-off errors under control
    log_eps = np.log(np.finfo(np.float64).eps)
    threshold = (log_epsilon - log_eps)/t
    if muj > threshold:
        if abs(pj) < 1.0e-14:
            Q = 0
        else:
            Q = f_tar**(-1/pj)*np.sqrt(muj)
        phibar_star_j = (Q + np.sqrt(phi_s_star_j))**2
        if phibar_star_j < threshold:
            w = np.sqrt(log_eps/(log_eps-log_epsilon))
            u = np.sqrt(-phibar_star_j*t/log_eps)
            muj = threshold
            Nj = np.ceil(w*log_epsilon/2/np.pi/(u*w-1))
            hj = np.sqrt(log_eps/(log_eps - log_epsilon))/Nj
        else:
            Nj =float('inf')
            hj = 0
    return muj, hj, Nj

#############################################################################
#(t,Lambd a,alpha,beta,gama,log_epsilon)
epsilon = 1e-15
log_epsilon = np.log(epsilon)
def Mittag_Leffler_one(z,alpha):
    return LTInversion(1,z,alpha,1,1,np.log(1e-15))

def Mittag_Leffler_two(z,alpha,beta):
    return LTInversion(1,z,alpha,beta,1,np.log(1e-15))

def Mittag_Leffler_three(z,alpha,beta,gamma):
    return LTInversion(1,z,alpha,beta,gamma,np.log(1e-15))

def MittagLeffler_one_fsum(z,alpha,Nmax):
    out=0
    for n in range(Nmax+1):
        out+=z**n/special.gamma(alpha*n+1)
    return out

def MittagLeffler_two_fsum(z,alpha,beta,Nmax):
    out=0
    for n in range(Nmax+1):
        out+=z**n/special.gamma(alpha*n+beta)
    return out

##############################################################################
