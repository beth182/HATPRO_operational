;***********************
PRO GET_PROFILE_ELE_SEP
;***********************
;
;***ABSTRACT: This script reads the RADIOSONDE, HATPRO data, and plots our retrieved profiles, RPG retrieved profiles and radiosondes
;***File out
var = 'TELQ'
expertout='nosubset'

mode2='ng'       ;no temperature sensor ground
mode3= 'npg'   ;no pressure sensor

;*** Some noise levels as Iva told
TB_rauschz=0.20
TB_rauschs=0.20


;***RS --------------------------------------------------------------------------------------
;***Rs       FIRST OF ALL READING SOME PATSCHERKOFEL OBSERVATION DATA HERE (p, T) 
;***RS --------------------------------------------------------------------------------------

;*Set the height of Patschekofel
z_patsc=2246-577.
p_patsch=DBLARR(n_r)
t_patsch=DBLARR(n_r)

;*Pressure of radiosonde at the height of Patsch.
FOR i_files = 0, n_r-1 DO BEGIN
 p_patsch(i_files)=INTERPOL(p_rs(0:500,i_files), z_rs(0:500,i_files), z_patsc)   
ENDFOR

;*Pressure of radiosonde at the height of Patsch.
FOR i_files = 0, n_r-1 DO BEGIN
 t_patsch(i_files)=INTERPOL(t_rs(0:500,i_files), z_rs(0:500,i_files), z_patsc)   
ENDFOR


;***RS --------------------------------------------------------------------------------------
;***Rs       SECOND READING ALL .MET FILES OF THE HATPRO ITSELF TO EXTRACT r,rh,T,p,... 
;***RS --------------------------------------------------------------------------------------

;***Read MET.ASC files
path_m= 'G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Confronto2\METASC\'
files_m= FILE_SEARCH(path_m+'*.ASC', count=nmet)
npos = strpos(files_m(0),'.MET.ASC')   
;***RS Those are the ASCII versions of the binary .TPB files i have,
;***RS named like: ZENIT_140101_103912.TPB
;***RS extracting Year, Month, Day, Hour, Minute and Second 
;***RS and store the return values in new vectors
yy_met  = strmid(files_m, npos-13, 2)
mm_met  = strmid(files_m, npos-11, 2) 
dd_met  = strmid(files_m, npos-9, 2) 
hh_met  = strmid(files_m, npos-6, 2) 
mn_met = strmid(files_m, npos-4, 2)
ss_met= strmid(files_m, npos-2, 2)

n_samp_max=6000
;***RS create integer and double float arrays with length 6000 (why 6000?)
rmet=INTARR(1,n_samp_max,nmet)  ;1st:samples 2nd:days
pmet=DBLARR(1,n_samp_max,nmet)
tempmet=DBLARR(1,n_samp_max,nmet)
rhmet=DBLARR(1,n_samp_max,nmet)
time_met=DBLARR(1,n_samp_max,nmet)

;***RS reading .MET files, again the ascii version (note that I have had
;***RS problems reading those files, they do not correspond with the
;***RS documentation (Appendix A of the HATPRO)
FOR i_f = 0, nmet-1 DO BEGIN  ; loop over MET.ASC files 
 GET_METASC,files_m(i_f), r, p, t, rh, time
 rmet(0,*,i_f)=r
 pmet(0,*,i_f)=p
 tempmet(0,*,i_f)=t
 rhmet(0,*,i_f)=rh
 time_met(0,*,i_f)=time
ENDFOR 


;***RS --------------------------------------------------------------------------------------
;***Rs          SEARCHING FOR NEAREST OBSERVATION TO THE RADIO SOUNDING (*_rs). 
;***RS            I THINK ALSO TOTALLY UNNECESSARY FOR AN OPERATIONAL MODE 
;***RS --------------------------------------------------------------------------------------

;***Choose the nearest neighbour in time for MET file
;***RS seems to search the nearest .MET observation for the radio sonde.
;***RS necessary for the operational algorithm?
;***RS nmet is the number of .MET files found on disc
FOR i_f=0, nmet-1 DO BEGIN   ;loop over the days
  ;***RS             met time          sounding time            met time           sounding time
  outmet=WHERE(ABS(time_met(0,*,i_f) - time_rs(i_f)) EQ MIN(ABS(time_met(0,*,i_f) - time_rs(i_f)), /NAN) )
  ;***RS take nearest neighbor r..? (rmet), pressure (pmet), temperature (tempmet), relative hum (rhmet) and time
  IF outmet(0) NE -1 THEN BEGIN
   rmet(0,*,i_f)=rmet(0,outmet(0),i_f)
   pmet(0,*,i_f)=pmet(0,outmet(0),i_f)
   tempmet(0,*,i_f)=tempmet(0,outmet(0),i_f)
   rhmet(0,*,i_f)=rhmet(0,outmet(0),i_f)
   time_met(0,*,i_f)=time_met(0,outmet(0),i_f)
  ENDIF
ENDFOR


;***RS --------------------------------------------------------------------------------------
;***RS                              RESHAPING SOME ELEMENTS 
;***RS --------------------------------------------------------------------------------------

;**Select which sample for MET file
;!NOTE:If the file has many samples I can select the row in pmet(*,row,*) that is the row number in the MET file!
;***RS The REFORM function changes the dimensions of an array without changing the total number of elements.
rmet_s=REFORM(rmet(0,-1,*))  ;take the last row
pmet_s=REFORM(pmet(0,-1,*))  ;take the last row
tempmet_s=REFORM(tempmet(0,-1,*))  ;take the last row
rhmet_s=REFORM(rhmet(0,-1,*))  ;take the last row
time_met_s=REFORM(time_met(0,-1,*))

;*Pressure Patsch + pressure ground
pmet_s_tot=[TRANSPOSE(p_patsch),TRANSPOSE(pmet_s)]


;***RS --------------------------------------------------------------------------------------
;***RS        THIRD STEP: READING THE BLB FILES CONTAINING BRIGHTNESS TEMPERATURES
;***RS --------------------------------------------------------------------------------------

n2c_max=50 ;***RS Number of samples
n_ret=39   ;number of heights of HATPRO
n_retbl=19 ;***RS seems to be the number of brightness temperatures of the hatpro

;***Read BLB files: Bright.temp measured by HATPRO
;***RS Reading the measured brightness temperatures <<<---- this is the base of the algorithm
path_blb='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Confronto2\BLB\'
files_blb=FILE_SEARCH(path_blb+'*.BLB', count=n_blb)
npos = strpos(files_blb(0),'.BLB')  
yy_blb  = strmid(files_blb, npos-13, 2)
mm_blb  = strmid(files_blb, npos-11, 2) 
dd_blb  = strmid(files_blb, npos-9, 2) 
hh_blb = strmid(files_blb, npos-6, 2) 
mn_blb = strmid(files_blb, npos-4, 2)
ss_blb = strmid(files_blb, npos-2, 2)

;***RS Create some of the result-arrays/matrizes
;***RS n_blb Number of .BLB files
;***RS n_ret number of heights
;***RS n2c_max number of samples
Ttot=DBLARR(n_ret,n2c_max,n_blb)  ;1st:heights 2nd:samples 3rd:days
n2ctot=INTARR(n_blb)
tb_algo1_tot=DBLARR(43,n2c_max)
tb_algo1_tott=DBLARR(43,n2c_max, n_blb)
time_blb_tot=DBLARR(n2c_max,n_blb)
rain_blb_tot=INTARR(n2c_max,n_blb)
n2ctot=INTARR(n_blb)

;***RS --------------------------------------------------------------------------------------
;***RS        STILL STEP 3 BUT THIS SEEMS TO BE THE MAIN PART OF WHAT GOES ON.
;***RS          READING ONE BLB FILE AFTER ANOTHER AND MODIFY IT USING THE 
;***RS               COEFFICIENTS STORED IN THE .RET FILE (ret_file) 
;***RS --------------------------------------------------------------------------------------

FOR i_files = 0, n_blb-1 DO BEGIN      ;loop over the BLB files

    ;***RS Reading the BLB file content, simply
    ;***RS A:   n2c         ;number of measurements 
    ;***RS B:   time        ;seconds since 1.1.1970
    ;***RS C:   rain        ;rain flag (0/1)
    ;***RS D:   freq        ;array of frequencies
    ;***RS E:   n_a         ;number of elevation angles
    ;***RS F:   tb          ;TB arry (f x angles x time)
    ;***RS G:   elev        ;array of elevation angles
    ;***RS H:   az          ;array azimuth angle
    ;***RS     input file         A     B    C     D    E    F    G    H
    GET_BLB, files_blb(i_files), n2c, time, rain, freq, n_a, tb, elev, az, verbose=0
    n2ctot(i_files)=n2c
    
    ;***Read RET file: coefficients of the regression
    ;***RS static file, why reading it n_blb times?
    ret_file='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Retrievalproduct\Newcheck\TELQall\RET\TELQ_ibk_0112_V90_nosubset_ng_npg_0.20_0.20.RET'
    
    ;***RS   A:    var = 'TELQ' defined in the head of this script. Linear Quadratic mode (as Iva told)
    ;***RS   B:    angles                 ;elevation angles
    ;***RS   C:    f                      ;frequency array in GHz
    ;***RS   D:    z                      ;height grid in m
    ;***RS   E:    offset                 ;MLR offset (n_z)
    ;***RS   F:    coeff_tel              ;linear retrieval coefficients (n_z x (n_f + n_bl*n_ang-1))
    ;***RS   G:    coeff_telq             ;quadratic retrieval coefficients 
    ;***RS   H:    coeff_sen              ;retrieval coefficients for additional sensors (T_gr, q_gr, p_gr, TB_ir) (n_z)
    ;***RS   I:    f_bl                   ;freqeuncies used for BL scanning
    ;***RS              .RET      A     B    C  D    E        F           G          H         I
    GET_COEFF_LEVEL2C, ret_file, var, angle, f, z, offset, coeff_tel, coeff_telq, coeff_sen, f_bl, verbose=0
    
    ;***RS   length of the different arrays read by the GET_COEFF_LEVEL2C method.
    ;***RS   nf: number of frequencies, nz: number of altitudes, na: nr. angles,
    ;***RS   nbl number of freqs used for BL scanning
    ;***RS   = nzen number of zenit angles? what is the zen here?
    nf = N_ELEMENTS(f)
    nz = N_ELEMENTS(z)
    na = N_ELEMENTS(angle)
    nbl = N_ELEMENTS(f_bl)
    nzen = nf - nbl
    
    dummy = -99d
    ;***RS Looks like a matrix size nz (levels) times n2c (number of measurements)
    ;***RS Seems to be the result T matrix
    T = REPLICATE(dummy, nz, n2c)
     
    ;*check if chosen retrieval file is compatible with the measured frequency channels and angles
    go = 0
    ibl = -1
    izen = -1
    ;***RS looping over all the different frequencies
    FOR i = 0, nf-1 DO BEGIN 
    
        im = WHERE(freq EQ f(i)); RS indizes of frequence?
        im = im(0);               RS take first, if not found seems to return -1: ABORT
        IF im EQ -1 THEN BEGIN
            print, 'RET_2C ABORT: Frequencies in retrieval file are not compatible with measurements'
            print, 'retrieval file frequencies: ', f
            print, 'measurement frequencies: ', freq
            GOTO, ABORT
        ENDIF
        ;***RS step by step adding im to imf (imf: indizes vector)
        IF go EQ 0 THEN BEGIN
            imf = im
            go = 1
        ENDIF ELSE BEGIN
            imf = [imf, im]
        ENDELSE
    
    ENDFOR
    
    ;***RS looping over all freqs used for BL scanning, do the
    ;***RS the same as done above with the frequencies. Store the position indizes
    ;***RS of each of those frequencies. 
    FOR i = 0, nbl-1 DO BEGIN
        ibb = WHERE(f_bl(i) EQ f)
        IF ibb(0) NE -1 THEN BEGIN
            ;***RS: store the indizes
            IF ibl(0) EQ -1 THEN BEGIN
                ibl = ibb
            ENDIF ELSE BEGIN
                ibl = [ibl, ibb]
            ENDELSE
        ENDIF 
    ENDFOR
    
    ;***RS looping over all angles, again store indizes 
    go = 0
    ;***RS na is number of angles
    FOR j = 0, na-1 DO BEGIN
        im = WHERE(elev GT angle(j)-0.6 AND elev LT angle(j)+0.6) 
        im = im(0)
        IF im EQ -1 THEN BEGIN
            print, 'RET_2C ABORT: Elevation angles in retrieval file are not compatible with measurements'
            print, 'retrieval file angles: ', angle
            print, 'measurement angle: ', elev
            
            GOTO, ABORT
        ENDIF ELSE BEGIN
            ;***RS: store the indizes
            IF go EQ 0 THEN BEGIN
                ima = im
                go = 1
            ENDIF ELSE BEGIN
                ima = [ima, im]
            ENDELSE
        ENDELSE
    ENDFOR   
    
    ;**brightness temperature for retrieval
    ;***RS As written above:     TB arry (f x angles x time)
    ;***RS Takes out all "good" frequencies times all "good" angles for all the times (*)
    ;***RS Looks like "brightness temperature for the algorythm ---> result?
    ;***RS looks like imf and ima is always *
    tb_algo = tb(imf, ima, *)
    ;column:frequencies  rows:angles  3rd dim:samples
     
     
    ;***RS looping over n2c which is the number of measurements
    FOR i = 0, n2c-1 DO BEGIN    ;loop over the samples
    
        ;**rearange tbs
        ;***RS seems to take out a 2D matrix out of the 3D matrix tb_algo containing
        ;***RS different samples in the third dimension.
        ;***RS if tbl(j) is equal to freq or f, then this really is only tb_algo(*,*,i)
        ;***RS probably transposed.
        IF nzen GE 1 THEN BEGIN 
            tb_algo1 = REFORM(tb_algo(0:nzen-1, 0, i))
            FOR j = 0, nbl-1 DO tb_algo1 = [tb_algo1, REFORM(tb_algo(ibl(j), *, i))] 
        ENDIF ELSE IF nzen EQ 0 THEN BEGIN
            tb_algo1 = REFORM(tb_algo(ibl(0), *, i))
            FOR j = 1, nbl-1 DO tb_algo1 = [tb_algo1, REFORM(tb_algo(ibl(j), *, i))]
        ENDIF 
        
    
        ;***RS as written: looping over the height grid. Or in other words:
        ;***RS add the regression to each of the levels of the hatpro
        FOR j = 0, nz-1 DO BEGIN   ;loop over the height grid
    
            IF coeff_sen(j, 3) NE dummy THEN BEGIN
                print, 'RET_2C ABORT: IRT data needed as input for this RET-file - still needs to be coded'
                stop
            ENDIF

            ;***RS take non-dummy variable indizes 
            ii = WHERE(coeff_sen(j, *) NE dummy)

            ;***RS --------------------------------------------------------------------------
            ;***RS                       DOING THE REGRESSION
            ;***RS --------------------------------------------------------------------------
            ;***RS This is where the regression coefficients take place, 
            ;***RS at least for the temperature profile (?)
            IF ii(0) NE -1 THEN BEGIN               ;if there is some sensor !NOTE!Needs to be changed relating to the used sensor 
                x= pmet_s(i_files)             ; HATPRO PRESSURE SENSOR
                 ;***RS veri veri tutto bene importante
                T(j, i) = offset(j) + coeff_tel(j, *)#tb_algo1 + coeff_telq(j, *)#(tb_algo1^2) + coeff_sen(j, ii)#x(ii)   ;j:height i:sample  ii:sensor
            ENDIF ELSE BEGIN                           ;if there is no sensors
                ; from below:
                ; tb_algo1 is a vector with 43 elements!!!!
                ; this corresponds to the coefficients which are exactly 43 and
                ; the matrix multiplication here is nothing else than elementwise
                ; vector multiplicatoin.
                T(j, i) = offset(j) + coeff_tel(j, *)#tb_algo1 + coeff_telq(j, *)#(tb_algo1^2)    ;j_height i:numger sample 
            ENDELSE
    
        ENDFOR   ;loop over j 
    
        ; i is the sample index.
        ; and size of tot: tb_algo1_tot=DBLARR(43,n2c_max)
        ; does this really work? 43 only works if we have
        ; this setup!!
        ; number of frequencies:    7
        ; number of angles;         10
        ; 3 of the freqs only have 1 coefficient!!
        ; 4 of them do have 10 coefficients. In sum 3+40=43
        tb_algo1_tot(*,i)=tb_algo1
    
    ENDFOR ; loop over n2c (i)
    
    ;***RS seems that he stores the final results to some total variables
    ; means that we store Ttot( all levels, all samples, fileindex )
    ; so sum over (0,*,0) gives us mean result temperature on level  0 for file 0
    Ttot(0:nz-1,0:n2c-1,i_files)=T
    ; store tb_algo_tot on 3th dimension of files
    tb_algo1_tott(*,*,i_files)=tb_algo1_tot
    ; store time and rain for each of the samples
    time_blb_tot(0:n2c-1,i_files)=time
    rain_blb_tot(0:n2c-1,i_files)=rain

ENDFOR  ;loop over the BLB files

