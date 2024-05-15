import experiments as meas
import config

def make_tof(soc, expt_path, cfg_file, qubit_i):

    tof = meas.ToFCalibrationExperiment(soccfg=soc,
    path=expt_path,
    prefix=f"adc_trig_offset_calibration_qubit{qubit_i}",
    config_file=cfg_file)

    tof.cfg.expt = dict(pulse_length=0.5, # [us]
    readout_length=1.0, # [us]
    trig_offset=0, # [clock ticks]
    gain=30000, # blast the power just for the RFSoC calibration
    frequency=tof.cfg.device.readout.frequency[qubit_i], # [MHz]
    reps=1000, # Number of averages per point
    qubit=qubit_i) 

    tof.cfg.device.readout.relax_delay[qubit_i]=0.1 # wait time between experiments [us]
    return tof

def make_rspec_coarse(soc, expt_path, cfg_file, qubit_i, start=7000, span=250, reps=800, npts=5000):
    rspec = meas.ResonatorSpectroscopyExperiment(
    soccfg=soc,
    path=expt_path,
    prefix=f"resonator_spectroscopy_coarse",
    config_file=cfg_file,   
    )

    rspec.cfg.expt = dict(
        start = start, #Lowest resontaor frequency
        step=span/npts, # min step ~1 Hz
        expts=npts, # Number experiments stepping from start
        reps= reps, # Number averages per point 
        pulse_e=False, # add ge pi pulse prior to measurement
        pulse_f=False, # add ef pi pulse prior to measurement
        qubit=qubit_i,
    )

    rspec.cfg.device.readout.relax_delay = 5 # Wait time between experiments [us]
    return rspec

def make_rspec_fine(soc, expt_path, cfg_file, qubit_i, j, im=None, center=None, span=5, reps=500, smart=True):
    
    rspec = meas.ResonatorSpectroscopyExperiment(
    soccfg=soc,
    path=expt_path,
    prefix=f"resonator_spectroscopy_res{j}",
    config_file=cfg_file,  
    im=im
    )
    npts = 1000 

    if center==None: 
        center = rspec.cfg.device.readout.frequency[qubit_i]

    rspec.cfg.expt = dict(
        start = center-span/2, #Lowest resontaor frequency
        step=span/npts, # min step ~1 Hz
        smart=smart,
        kappa=0.35,
        expts=npts, # Number experiments stepping from start
        reps= reps, # Number averages per point 
        pulse_e=False, # add ge pi pulse prior to measurement
        pulse_f=False, # add ef pi pulse prior to measurement
        qubit=qubit_i,
    )

    rspec.cfg.device.readout.relax_delay = 5 # Wait time between experiments [us]
    return rspec

def make_rpowspec(soc, expt_path, cfg_file, qubit_i, res_freq, span_f=5, npts_f=250, span_gain=27000, start_gain=5000, npts_gain=10, reps=500, smart=False):

    rpowspec = meas.ResonatorPowerSweepSpectroscopyExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"ResonatorPowerSweepSpectroscopyExperiment_qubit{qubit_i}",
        config_file=cfg_file,
    )

    rpowspec.cfg.expt = dict(
        start_f = res_freq-span_f/2, # resonator frequency to be mixed up [MHz]
        step_f = span_f/npts_f, # min step ~1 Hz, 
        smart = smart, 
        expts_f=npts_f, # Number experiments stepping freq from start
        start_gain=start_gain,
        step_gain=int(span_gain/npts_gain), # Gain step size
        expts_gain=npts_gain+1, # Number experiments stepping gain from start
        reps= reps, # Number averages per point
        pulse_e=False, # add ge pi pulse before measurement
        pulse_f=False, # add ef pi pulse before measurement
        qubit=qubit_i,  
    ) 

    rpowspec.cfg.device.readout.relax_delay = 5 # Wait time between experiments [us]    
    rpowspec.cfg.device.readout.readout_length = 5
    return rpowspec

def make_chi(soc, expt_path, cfg_file, qubit_i, go=False, span=3, npts=151, reps=500):
    # This adds an e pulse first 

    span = span # MHz
    npts = npts
    
    rspec_chi = meas.ResonatorSpectroscopyExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"resonator_spectroscopy_chi_qubit{qubit_i}",
        config_file=cfg_file,
        )

    rspec_chi.cfg.expt = dict(
        start=rspec_chi.cfg.device.readout.frequency[qubit_i]-span/2, # MHz
        # start=rspec_chi.cfg.device.readout.frequency[qubit_i]-rspec_chi.cfg.device.readout.lo_sideband[qubit_i]*span, # MHz
        step=span/npts,
        expts=npts,
        reps=reps,
        pulse_e=True, # add ge pi pulse prior to measurement
        pulse_f=False, # add ef pi pulse prior to measurement
        qubit=qubit_i,
    )
    # rspec_chi.cfg.device.readout.relax_delay = 100 # Wait time between experiments [us]
    if go: 
        rspec_chi.go(analyze=True, display=True, progress=True, save=True)
    
    return rspec_chi

def make_qspec(soc, expt_path, cfg_file, qubit_i, im=None, span=None, npts=1500, reps=50, rounds=20, gain=None, coarse=False, ef=False):
# This one may need a bunch of options. 
# coarse: wide span, medium gain, centered at ge freq
# ef: coarse: medium span, extra high gain, centered at the ef frequency  
# otherwise, narrow span, low gain, centered at ge frequency 

    if coarse and span is None:
        span=800 
        prefix = f"qubit_spectroscopy_coarse_qubit{qubit_i}"
    elif span is None:
        span=3
        prefix = f"qubit_spectroscopy_fine_qubit{qubit_i}"
    else:
        prefix = f"qubit_spectroscopy_qubit{qubit_i}"

    if coarse is True and gain is None:
        gain=500
    elif gain is None:
        gain=100

    qspec = meas.PulseProbeSpectroscopyExperiment(
    soccfg=soc,
    path = expt_path, 
    prefix = f"qubit_spectroscopy_coarse_qubit{qubit_i}",
    config_file=cfg_file,
    im=im
    )
    
    if ef:
        freq = qspec.cfg.device.qubit.f_ef[qubit_i]
        if coarse:
            prefix = f"qubit_spectroscopy_qubit_coarse_ef{qubit_i}"
            span=450
        else:
            prefix = f"qubit_spectroscopy_qubit_fine_ef{qubit_i}"
    else:
        freq = qspec.cfg.device.qubit.f_ge[qubit_i]

    
    qspec.cfg.expt = dict(
        start= freq-span/2, # qubit frequency to be mixed up [MHz]
        step = span/npts, # min step ~1 Hz
        expts = npts, # Number experiments stepping from start
        reps = reps, # Number averages per point
        rounds = rounds, #Number of start to finish sweeps to average over 
        length = 50, # qubit probe constant pulse length [us]
        gain = gain, #qubit pulse gain  
        pulse_type = 'const', 
        #pulse_type = 'gauss',  
        qubit = qubit_i,
    ) 

    qspec.cfg.device.readout.relax_delay = 10 # Wait time between experiments [us]
    return qspec

def make_lengthrabi(soc, expt_path, cfg_file, qubit_i, im=None, npts = 100, reps = 500, gain = 2000, num_pulses = 1):
    lengthrabi = meas.LengthRabiExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"length_rabi_qubit{qubit_i}",
        config_file=cfg_file,
        im=im
    )

    lengthrabi.cfg.expt = dict(
        start =  0.0025, 
        step=  soc.cycles2us(1), # [us] this is the samllest possible step size (size of clock cycle)
        expts= npts, 
        reps= reps,
        gain =  gain, #qubit gain [DAC units]
        #gain=lengthrabi.cfg.device.qubit.pulses.pi_ge.gain[qubit_i],
        pulse_type='gauss',
        # pulse_type='const',
        checkZZ=False,
        checkEF=False, 
        qubits=[qubit_i],
        num_pulses = 1, #number of pulses to play, must be an odd number 
    )

    return lengthrabi

def make_amprabi(soc, expt_path, cfg_file, qubit_i, im=None, go=False, npts = 100, reps = 500, rounds=1, gain=15000):
    #auto_cfg.device.qubit.pulses.pi_ge.gain[qubit_i]
    amprabi = meas.AmplitudeRabiExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"amp_rabi_qubit{qubit_i}",
        config_file=cfg_file,
        im=im
        )
    auto_cfg = config.load(cfg_file)
    span = 2*gain
    amprabi.cfg.expt = dict(     
        start=0,
        step=int(span/npts), # [dac level]
        expts=npts,
        reps=reps,
        rounds=rounds,
        sigma_test= auto_cfg.device.qubit.pulses.pi_ge.sigma[qubit_i], # gaussian sigma for pulse length - overrides config [us]
        checkZZ=False,
        checkEF=False, 
        qubits=[qubit_i],
        pulse_type='gauss',
        # pulse_type='const',
        num_pulses = 1, #number of pulses to play, must be an odd number in order to achieve a pi rotation at pi length/ num_pulses 
    )

    if go: 
        amprabi.go(analyze=True, display=True, progress=True, save=True)

    return amprabi

def make_amprabi_chevron(soc, expt_path, cfg_file, qubit_i, im=None, span_gain=20000, npts_gain=25, start_gain=10000, span_f=20, npts_f=40, reps=100, rounds=10, sigma=0.1):
    amprabichev = meas.AmplitudeRabiChevronExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"amp_rabi_qubit_chevron{qubit_i}",
        config_file=cfg_file,
        im=im
    )

    span_gain = span_gain
    npts_gain = npts_gain

    span_f = span_f
    npts_f = npts_f

    amprabichev.cfg.expt = dict(
        start_f=amprabichev.cfg.device.qubit.f_ge[qubit_i]-span_f/2,
        step_f=span_f/(npts_f-1),
        expts_f=npts_f,
        start_gain=start_gain,
        step_gain=int(span_gain/npts_gain), # [dac level]
        expts_gain=npts_gain,
        reps=reps,
        rounds=rounds,
        sigma_test=sigma, # gaussian sigma for pulse length - overrides config [us]
        checkZZ=False,
        checkEF=False, 
        pulse_ge=False,
        qubits=[qubit_i],
        pulse_type='gauss',
        num_pulses=1
        # pulse_type='adiabatic',
        # mu=6, # dimensionless
        # beta=4, # dimensionless
        # sigma_test=0.120*4, # us
    )

    # amprabichev.cfg.device.readout.relax_delay = 50 # Wait time between experiments [us]
    return amprabichev

def make_t2r(soc, expt_path, cfg_file, qubit_i, im=None, go=False, npts = 300, reps = 200, rounds=2, step=0.5, ramsey_freq=0.1):
    t2r = meas.RamseyExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"ramsey_qubit{qubit_i}",
        config_file=cfg_file,
        im=im
    )

    t2r.cfg.expt = dict(
        start=0, # wait time tau [us]
        #step=soc.cycles2us(10), # [us] make sure nyquist freq = 0.5 * (1/step) > ramsey (signal) freq!
        step= step, # [us]
        expts=npts,
        ramsey_freq=ramsey_freq, # [MHz]
        reps=reps,
        rounds=rounds, # set this = 1 (computer asking for 20 rounds --> faster if I don't have to communicate between computer and board)
        qubits=[qubit_i],
        checkZZ=False,
        checkEF=False,
    )
    if go:
        t2r.go(analyze=True, display=True, progress=True, save=True)


    return t2r

def make_t2e(soc, expt_path, cfg_file, qubit_i, im=None, go=False, npts = 201, reps = 100, rounds=2, ramsey_freq=2.0, step=0.1):

    t2e = meas.RamseyEchoExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"echo_qubit{qubit_i}",
        config_file=cfg_file,
        im=im
        )

    t2e.cfg.expt = dict(
        start=1, #soc.cycles2us(150), # total wait time b/w the two pi/2 pulses [us]
        step=step, #step,
        expts=npts,
        ramsey_freq=ramsey_freq, # frequency by which to advance phase [MHz]
        num_pi=1, # number of pi pulses
        cpmg=False, # set either cp or cpmg to True
        cp=True, # set either cp or cpmg to True
        reps=reps,
        rounds=rounds,
        qubit=qubit_i,
    )
    if go: 
        t2e.go(analyze=True, display=True, progress=True, save=True)
    return t2e

def make_t1(soc, expt_path, cfg_file, qubit_i, im=None, go=False, span=600, npts=200, reps=500, rounds=1):

    span = span 
    npts = npts
    
    t1 = meas.T1Experiment(
      soccfg=soc,
      path=expt_path,
      prefix=f"t1_qubit{qubit_i}",
      config_file= cfg_file,
      im=im
    )

    t1.cfg.expt = dict(
        start=0, # wait time [us]
        step=int(span/npts), 
        expts=npts,
        reps=reps, # number of times we repeat a time point 
        rounds=rounds, # number of start to finish sweeps to average over
        qubit=qubit_i,
        length_scan = span, # length of the scan in us
    )

    if go:
        t1.go(analyze=True, display=True, progress=True, save=True)

    return t1

def make_t1_2d(soc, expt_path, cfg_file, qubit_i, im=None, go=False, span=600, npts=200, reps=500, rounds=1, sweep_pts=100):

    span = span 
    npts = npts
    
    t1 = meas.T1_2D(
      soccfg=soc,
      path=expt_path,
      prefix=f"t1_2d_qubit{qubit_i}",
      config_file= cfg_file,
      im=im
    )

    t1.cfg.expt = dict(
        start=0, # wait time [us]
        step=int(span/npts), 
        expts=npts,
        reps=reps, # number of times we repeat a time point 
        rounds=rounds, # number of start to finish sweeps to average over
        qubit=qubit_i,
        length_scan = span, # length of the scan in us
        sweep_pts = sweep_pts, # number of points to sweep over,
    )

    if go:
        t1.go(analyze=True, display=True, progress=True, save=True)

    return t1

def make_t1doub(soc, expt_path, cfg_file, qubit_i, im=None, go=False, delay_time=150, npts=1, reps=1000, rounds=1):

    t1 = meas.T1ContinuousDoub(
      soccfg=soc,
      path=expt_path,
      prefix=f"t1cont2_qubit{qubit_i}",
      config_file= cfg_file,
      im=im
    )

    t1.cfg.expt = dict(
        start=0, # wait time [us]
        step=delay_time/npts, 
        expts=npts,
        reps=reps, # number of times we repeat a time point 
        rounds=rounds, # number of start to finish sweeps to average over
        qubit=qubit_i,
        length_scan = delay_time, # length of the scan in us
        num_saved_points = 10, # number of points to save for the T1 continuous scan 
    )

    if go:
        t1.go(analyze=False, display=False, progress=True, save=True)


    return t1    

def make_t1_cont(soc, expt_path, cfg_file, qubit_i, reps=2000000, norm=False, delay_time=150, rounds=1):
    if norm:
        prefix = f"t1_continuous_qubit_norm{qubit_i}"
    else:
        f"t1_continuous_qubit{qubit_i}"
    t1_cont = meas.T1Continuous(
        soccfg=soc,
        path=expt_path,
        prefix=prefix,
        config_file=cfg_file,
    )

    npts = 1
    if norm: 
        t1_cont.cfg.expt = dict(
            start=0,  # wait time [us]
            step=delay_time,
            expts=2,
            reps=reps,  # number of times we repeat a time point
            rounds=rounds,  # number of start to finish sweeps to average over
            qubit=qubit_i,
            )
           
    else:
        t1_cont.cfg.expt = dict(
        start=delay_time,  # wait time [us]
        step=0,
        expts=npts,
        reps= reps,  # number of times we repeat a time point
        rounds=1,  # number of start to finish sweeps to average over
        qubit=qubit_i,
        )
        


    return t1_cont

def make_singleshot(soc, expt_path, cfg_file, qubit_i, im=None, go=False, reps=10000):

    shot = meas.HistogramExperiment(
    soccfg=soc,
    path=expt_path,
    prefix=f"single_shot_qubit{qubit_i}",
    config_file= cfg_file,
    im=im,
    )

    shot.cfg.expt = dict(
        reps=reps,
        check_e = True, 
        check_f=False,
        qubit=qubit_i,
    )

    if go:
        shot.go(analyze=True, display=True, progress=True, save=True)


    return shot

def make_singleshot_opt(soc, expt_path, cfg_file, qubit_i, go=False, im=None, reps=10000, start_f = None, span_f=0.5, npts_f =5, start_gain=None, span_gain=25000, npts_gain=5, start_len=None, span_len=25.0, npts_len=5):

    shotopt = meas.SingleShotOptExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"single_shot_opt_qubit{qubit_i}",
        config_file=cfg_file, 
        im=im
    )

    if npts_f==1 and start_f is None:
        start_f = shotopt.cfg.device.readout.frequency[qubit_i]
    elif start_f is None:
        start_f = shotopt.cfg.device.readout.frequency[qubit_i] - 0.5*span_f

    if npts_gain==1 and start_gain is None:
        start_gain = shotopt.cfg.device.readout.gain[qubit_i]
    elif start_gain is None:
        start_gain = 1000

    if npts_len==1 and start_len is None:
        start_len = shotopt.cfg.device.readout.readout_length[qubit_i]
    elif start_len is None:
        start_len = 2

    if npts_f == 1:
        step_f =0 
    else:
        step_f = span_f/(npts_f-1)

    if npts_gain == 1:
        step_gain =0 
    else:
        step_gain = span_gain/(npts_gain-1)

    if npts_len == 1:
        step_len =0 
    else:
        step_len = span_len/(npts_len-1)


    shotopt.cfg.expt = dict(
        reps=reps,
        qubit=qubit_i,
        start_f=start_f,
        step_f=step_f,
        expts_f=npts_f,
        start_gain=start_gain,#start_gain=1000,
        step_gain=step_gain,
        expts_gain=npts_gain,
        start_len=start_len,
        step_len=step_len,
        expts_len=npts_len,
    )

    if go:
        shotopt.go(analyze=True, display=True, progress=True, save=True)

    return shotopt

def make_amprabiEF(soc, expt_path, cfg_file, qubit_i, im=None, go=False, span=30000, npts=101, reps=200, rounds=2, pulse_ge=True):
    if pulse_ge:
        prefix = "amp_rabi_EF_ge" +f"_qubit{qubit_i}"
    else:
        prefix ="amp_rabi_EF"+f"_qubit{qubit_i}"

    amprabiEF = meas.AmplitudeRabiExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=prefix,
        config_file=cfg_file,        
        im=im
    )

    amprabiEF.cfg.expt = dict(
        start=0, # qubit gain [dac level]
        step=int(span/npts), # [dac level]
        expts=npts,
        reps=reps,
        rounds=rounds,
        pulse_type='gauss',
        qubits=[qubit_i],
        # sigma_test=0.013, # gaussian sigma for pulse length - default from cfg [us]
        checkZZ=False,
        checkEF=True, 
        num_pulses=1,
        pulse_ge=pulse_ge)

    if go:
        amprabiEF.go(analyze=True, display=True, progress=True, save=True)
    return amprabiEF

def make_acstark(soc, expt_path, cfg_file, qubit_i, span_f=100, npts_f=300, span_gain=10000, npts_gain=25):
    acspec = meas.ACStarkShiftPulseProbeExperiment(
        soccfg=soc,
        path=expt_path,
        prefix=f"ac_stark_shift_qubit{qubit_i}",
        config_file=cfg_file,
    )

    pump_params=dict(
    ch=1,
    type='full',
    nyquist=2,
    )

    acspec.cfg.expt = dict(        
        start_f=acspec.cfg.device.qubit.f_ge[qubit_i]-0.25*span_f, # Pulse frequency [MHz]
        step_f=span_f/npts_f,
        expts_f=npts_f,
        start_gain=0, 
        step_gain=int(span_gain/npts_gain),
        expts_gain=npts_gain+1,
        pump_params=pump_params,
    
        pump_freq=acspec.cfg.device.qubit.f_ge[qubit_i]-20,
        # pump_freq=acspec.cfg.device.qubit.f_EgGf[2],
        pump_length=10, # [us]
        qubit_length=1, # [us]
        qubit_gain=2814,
        pulse_type='const',
        reps=100,
        rounds=10, # Number averages per point
        qubit=qubit_i,
    )
    acspec.cfg.device.readout.relax_delay = 25
    return acspec
