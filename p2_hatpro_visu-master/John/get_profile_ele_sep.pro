;***********************
PRO GET_PROFILE_ELE_SEP
;***********************
;
;***ABSTRACT: This script reads the RADIOSONDE, HATPRO data, and plots our retrieved profiles, RPG retrieved profiles and radiosondes
;
;
;***File out
var = 'TELQ'
expertout='nosubset'
;expertout='night'
;expertout='day'
;expertout='winter'
;expertout='summer'
;expertout='winter+night'
;expertout='winter+day'
;expertout='summer+night'
;expertout='summer+day'
;expertout='s4L_ss_s'

mode2='ng'       ;no temperature sensor ground
;mode2='gr+35'       ;temp sens ground
mode3= 'npg'   ;no pressure sensor
;mode3= 'pg'     ;pressure sensor

;mode2='gr'     
;mode3='pg'

TB_rauschz=0.20
TB_rauschs=0.20

sign= '_' + expertout + '_' + mode2 + '_' + mode3 + '_' + STRING(TB_rauschz,format='(f4.2)') + '_' + STRING(TB_rauschs,format='(f4.2)')
file_out= var + sign


;***Read Radiosoundings data
path_r= 'G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Confronto2\RADIOSONDE\'
;path_r='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\Documents\Confronto2\RADIOSONDE\'
files_r = FILE_SEARCH(path_r+'*.txt', count=n_r)
npos = strpos(files_r(0),'reduced.txt')   
yy_r  = strmid(files_r, npos-12, 2)
mm_r  = strmid(files_r, npos-10, 2) 
dd_r  = strmid(files_r, npos-8, 2) 
hh_r  = strmid(files_r, npos-5, 2) 
mn_r= strmid(files_r, npos-3, 2)
jul_rs=DBLARR(n_r)
jul_rs=JULDAY(mm_r,dd_r,yy_r+2000.,hh_r,mn_r)-2400000.5  ;modified julian day number
time_rs=CMSYSTIME(jul_rs, /from_mjd, /seconds)    ;seconds after 1.1.1970


FOR i_files = 0, n_r-1 DO BEGIN  ; loop over Radiosonde files
 IF i_files EQ 0 THEN BEGIN  
  READ_RS_INNSBRUCK,files_r(i_files), T_rs, p_rs, q_rs, rh_rs, z_rs
 ENDIF ELSE BEGIN
  READ_RS_INNSBRUCK,files_r(i_files), T_rsx, p_rsx, q_rsx, rh_rsx, z_rsx
   
  T_rs = [[T_rs], [T_rsx]]
  p_rs = [[p_rs], [p_rsx]]
  q_rs = [[q_rs], [q_rsx]]
  rh_rs = [[rh_rs], [rh_rsx]]
  z_rs = [[z_rs], [z_rsx]]
  
 ENDELSE
ENDFOR


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

;FOR i_files = 0, n_r-1 DO BEGIN
; w=WHERE(z_rs(*,i_files) LT z_patsc+6. AND z_rs(*,i_files) GT z_patsc-6.)
; IF w(0) NE -1 THEN p_patsch2(i_files)=p_rs(w(0), i_files) ELSE GOTO, ABORT
;ENDFOR


;***Read MET.ASC files
;path_m= 'G:\Documenti\John\UNIVERSITA\MASTERTHESIS\Documents\Confronto2\METASC\'
path_m= 'G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Confronto2\METASC\'
files_m= FILE_SEARCH(path_m+'*.ASC', count=nmet)
npos = strpos(files_m(0),'.MET.ASC')   
yy_met  = strmid(files_m, npos-13, 2)
mm_met  = strmid(files_m, npos-11, 2) 
dd_met  = strmid(files_m, npos-9, 2) 
hh_met  = strmid(files_m, npos-6, 2) 
mn_met = strmid(files_m, npos-4, 2)
ss_met= strmid(files_m, npos-2, 2)

n_samp_max=6000
rmet=INTARR(1,n_samp_max,nmet)  ;1st:samples 2nd:days
pmet=DBLARR(1,n_samp_max,nmet)
tempmet=DBLARR(1,n_samp_max,nmet)
rhmet=DBLARR(1,n_samp_max,nmet)
time_met=DBLARR(1,n_samp_max,nmet)

FOR i_f = 0, nmet-1 DO BEGIN  ; loop over MET.ASC files 
 GET_METASC,files_m(i_f), r, p, t, rh, time
 rmet(0,*,i_f)=r
 pmet(0,*,i_f)=p
 tempmet(0,*,i_f)=t
 rhmet(0,*,i_f)=rh
 time_met(0,*,i_f)=time
 
ENDFOR 

;;***Replicate the last row not null for MET file
;FOR i_f=0, nmet-1 DO BEGIN   ;loop over the days
;  outmet=WHERE(pmet(0,*,i_f) EQ 0.)
;  IF outmet(0) NE -1 THEN BEGIN
;   rmet(0,outmet,i_f)=rmet(0,outmet(0)-1,i_f)
;   pmet(0,outmet,i_f)=pmet(0,outmet(0)-1,i_f)
;   tempmet(0,outmet,i_f)=tempmet(0,outmet(0)-1,i_f)
;   rhmet(0,outmet,i_f)=rhmet(0,outmet(0)-1,i_f)
;   time_met(0,outmet,i_f)=time_met(0,outmet(0)-1,i_f)
;  ENDIF
;ENDFOR

;***Choose the nearest neighbour in time for MET file
FOR i_f=0, nmet-1 DO BEGIN   ;loop over the days
  outmet=WHERE(ABS(time_met(0,*,i_f) - time_rs(i_f)) EQ MIN(ABS(time_met(0,*,i_f) - time_rs(i_f)), /NAN) )
  IF outmet(0) NE -1 THEN BEGIN
   rmet(0,*,i_f)=rmet(0,outmet(0),i_f)
   pmet(0,*,i_f)=pmet(0,outmet(0),i_f)
   tempmet(0,*,i_f)=tempmet(0,outmet(0),i_f)
   rhmet(0,*,i_f)=rhmet(0,outmet(0),i_f)
   time_met(0,*,i_f)=time_met(0,outmet(0),i_f)
  ENDIF
ENDFOR

;**Select which sample for MET file
;!NOTE:If the file has many samples I can select the row in pmet(*,row,*) that is the row number in the MET file!
rmet_s=REFORM(rmet(0,-1,*))  ;take the last row
pmet_s=REFORM(pmet(0,-1,*))  ;take the last row
tempmet_s=REFORM(tempmet(0,-1,*))  ;take the last row
;tempmet_s=tempmet_s+0.5
rhmet_s=REFORM(rhmet(0,-1,*))  ;take the last row
time_met_s=REFORM(time_met(0,-1,*))

;*Pressure Patsch + pressure ground
;pmet_s_tot=[TRANSPOSE(p_patsch),TRANSPOSE(pmet_s)]
pmet_s_tot=[TRANSPOSE(p_patsch),TRANSPOSE(pmet_s)]

n2c_max=50
n_ret=39   ;number of heights of HATPRO
n_retbl=19

;***Read BLB files: Bright.temp measured by HATPRO
path_blb='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Confronto2\BLB\'
;path_blb='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\Documents\Confronto2\BLB\'
files_blb=FILE_SEARCH(path_blb+'*.BLB', count=n_blb)
npos = strpos(files_blb(0),'.BLB')  
yy_blb  = strmid(files_blb, npos-13, 2)
mm_blb  = strmid(files_blb, npos-11, 2) 
dd_blb  = strmid(files_blb, npos-9, 2) 
hh_blb = strmid(files_blb, npos-6, 2) 
mn_blb = strmid(files_blb, npos-4, 2)
ss_blb = strmid(files_blb, npos-2, 2)

Ttot=DBLARR(n_ret,n2c_max,n_blb)  ;1st:heights 2nd:samples 3rd:days
n2ctot=INTARR(n_blb)
tb_algo1_tot=DBLARR(43,n2c_max)
tb_algo1_tott=DBLARR(43,n2c_max, n_blb)
time_blb_tot=DBLARR(n2c_max,n_blb)
rain_blb_tot=INTARR(n2c_max,n_blb)
n2ctot=INTARR(n_blb)


FOR i_files = 0, n_blb-1 DO BEGIN      ;loop over the BLB files

GET_BLB, files_blb(i_files),$                  ;*.blb file 
;OUTPUT:
n2c,$                         ;number of measurements 
time,$                      ;seconds since 1.1.1970
rain,$                      ;rain flag (0/1)
freq,$                         ;array of frequencies
n_a,$                       ;number of elevation angles
tb,$                        ;TB arry (f x angles x time)
elev,$                        ;array of elevation angles
az,$                     ;array azimuth angle
verbose=0

n2ctot(i_files)=n2c

;***Read RET file: coefficients of the regression

;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELall\Sensor\TEL_ibk_0112_V90_nosubset_ng_npg_0.35_0.35.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELall\Noise\TEL_ibk_0112_V90_nosubset_ng_npg_0.50_0.20.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELall\Noise+sensor\TEL_ibk_0112_V90_nosubset_gr_pg_0.50_0.20rc_2p.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELQall\TELQ_ibk_0112_V90_winter_ng_pg_0.50_0.20.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELall\Noise+sensor\TEL_ibk_0112_V90_nosubset_ng_pg_0.50_0.20.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELQall\TELQ_ibk_0112_V90_nosubset_ng_npg_0.50_0.20.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELQall\TELQ_ibk_0112_V90_nosubset_gr_pg_0.50_0.20_2p.RET'
;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELall\TEL_ibk_0112_V90_nosubset_gr_pg_0.50_0.20_2p.RET'

;ret_file='C:\Users\csaq3045\Documents\Retrievalproduct\Newcheck\TELQall\TELQ_ibk_0112_V90_s4L_ss_s_ng_npg_0.20_0.20.RET'
ret_file='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Retrievalproduct\Newcheck\TELQall\RET\TELQ_ibk_0112_V90_nosubset_ng_npg_0.20_0.20.RET'

GET_COEFF_LEVEL2C, ret_file, var, angle, f, z, offset, coeff_tel, coeff_telq, coeff_sen, f_bl, verbose=0
 nf = N_ELEMENTS(f)
 nz = N_ELEMENTS(z)
 na = N_ELEMENTS(angle)
 nbl = N_ELEMENTS(f_bl)
 nzen = nf - nbl
 
 dummy = -99d
 T = REPLICATE(dummy, nz, n2c)
 
 ;*check if chosen retrieval file is compatible with the measured frequency channels and angles

go = 0
ibl = -1
izen = -1
FOR i = 0, nf-1 DO BEGIN 

 im = WHERE(freq EQ f(i))
 im = im(0)
 IF im EQ -1 THEN BEGIN
  print, 'RET_2C ABORT: Frequencies in retrieval file are not compatible with measurements'
  print, 'retrieval file frequencies: ', f
  print, 'measurement frequencies: ', freq
  GOTO, ABORT
 ENDIF
 IF go EQ 0 THEN BEGIN
  imf = im
  go = 1
 ENDIF ELSE BEGIN
  imf = [imf, im]
 ENDELSE

ENDFOR

FOR i = 0, nbl-1 DO BEGIN
 ibb = WHERE(f_bl(i) EQ f)
 IF ibb(0) NE -1 THEN BEGIN
  IF ibl(0) EQ -1 THEN BEGIN
   ibl = ibb
  ENDIF ELSE BEGIN
   ibl = [ibl, ibb]
  ENDELSE
 ENDIF 

ENDFOR

go = 0
FOR j = 0, na-1 DO BEGIN
 im = WHERE(elev GT angle(j)-0.6 AND elev LT angle(j)+0.6) 
 im = im(0)
 IF im EQ -1 THEN BEGIN

  print, 'RET_2C ABORT: Elevation angles in retrieval file are not compatible with measurements'
  print, 'retrieval file angles: ', angle
  print, 'measurement angle: ', elev
 
  GOTO, ABORT

 ENDIF ELSE BEGIN

  IF go EQ 0 THEN BEGIN
   ima = im
   go = 1
  ENDIF ELSE BEGIN
   ima = [ima, im]
  ENDELSE
   
 ENDELSE
ENDFOR   

;**brightness temperature for retrieval
tb_algo = tb(imf, ima, *)
;column:frequencies  rows:angles  3rd dim:samples
 
 
FOR i = 0, n2c-1 DO BEGIN    ;loop over the samples

;**rearange tbs

 IF nzen GE 1 THEN BEGIN 
  tb_algo1 = REFORM(tb_algo(0:nzen-1, 0, i))
  FOR j = 0, nbl-1 DO tb_algo1 = [tb_algo1, REFORM(tb_algo(ibl(j), *, i))] 
 ENDIF ELSE IF nzen EQ 0 THEN BEGIN
  tb_algo1 = REFORM(tb_algo(ibl(0), *, i))
  FOR j = 1, nbl-1 DO tb_algo1 = [tb_algo1, REFORM(tb_algo(ibl(j), *, i))]
 ENDIF 
 

 FOR j = 0, nz-1 DO BEGIN   ;loop over the height grid

  IF coeff_sen(j, 3) NE dummy THEN BEGIN
   print, 'RET_2C ABORT: IRT data needed as input for this RET-file - still needs to be coded'
   stop
  ENDIF

  ii = WHERE(coeff_sen(j, *) NE dummy)
  IF ii(0) NE -1 THEN BEGIN               ;if there is some sensor !NOTE!Needs to be changed relating to the used sensor 
   ;x = tempmet_s(i_files)        ; HATPRO TEMPERATURE SENSOR 
   ;x= INTERPOL(T_rs(0:10,i_files), z_rs(0:10,i_files), 35.)    ;AIRPORT+35m TEMPERATURE SENSOR
   x= pmet_s(i_files)             ; HATPRO PRESSURE SENSOR
   ;x= INTERPOL(p_rs(0:10,i_files), z_rs(0:10,i_files), 35.)    ;AIRPORT+35m PRESSURE SENSOR
   ;x=pmet_s_tot(*,i_files)               ;Pressure Patsch. + pressure ground SENSOR
   ;x=t_patsch                             ;Temp patsch.
   ;x=p_patsch
   T(j, i) = offset(j) + coeff_tel(j, *)#tb_algo1 + coeff_telq(j, *)#(tb_algo1^2) + coeff_sen(j, ii)#x(ii)   ;j:height i:sample  ii:sensor
   ;ENDIF
  ENDIF ELSE BEGIN                           ;if there is no sensors
   T(j, i) = offset(j) + coeff_tel(j, *)#tb_algo1 + coeff_telq(j, *)#(tb_algo1^2)    ;j_height i:numger sample 
  ENDELSE

 ENDFOR   ;loop over j 

tb_algo1_tot(*,i)=tb_algo1

ENDFOR ; loop over n2c (i)

Ttot(0:nz-1,0:n2c-1,i_files)=T
tb_algo1_tott(*,*,i_files)=tb_algo1_tot
time_blb_tot(0:n2c-1,i_files)=time
rain_blb_tot(0:n2c-1,i_files)=rain

ENDFOR  ;loop over the BLB files

;***Read retrieval files (TPB) by the software of the HATPRO
path_tpb= 'G:\Documenti\John\UNIVERSITA\MASTERTHESIS\PcInnsbruck-backup\Massaro-backup2\Documents\Confronto2\TPB\'
;path_tpb='G:\Documenti\John\UNIVERSITA\MASTERTHESIS\Documents\Confronto2\TPB\'
files_tpb = FILE_SEARCH(path_tpb+'*.ASC', count=n_asc)
npos = strpos(files_tpb(0),'.TPB.ASC')  
yy_tpb  = strmid(files_tpb, npos-13, 2)
mm_tpb  = strmid(files_tpb, npos-11, 2) 
dd_tpb  = strmid(files_tpb, npos-9, 2) 
hh_tpb = strmid(files_tpb, npos-6, 2) 
mn_tpb = strmid(files_tpb, npos-4, 2) 
ss_tpb = strmid(files_tpb, npos-2, 2) 

tb_tpb_tot=DBLARR(n_ret,n2c_max,n_asc)  ;1st:heights 2nd:samples 3rd:days
time_tpb_tot=DBLARR(n2c_max,n_asc)
rain_tpb_tot=INTARR(n2c_max,n_asc)
n_tpbtot=INTARR(n_asc)

FOR i_files = 0, n_asc-1 DO BEGIN  ; loop over TPB files
 GET_TPB,files_tpb(i_files), n_tpb, tb_tpb, z_tpb, time_tpb, r_tpb
 n_tpbtot(i_files)=n_tpb
 tb_tpb_tot(0:n_ret-1,0:n_tpb-1,i_files)=tb_tpb
 time_tpb_tot(0:n_tpb-1,i_files)=time_tpb
 rain_tpb_tot(0:n_tpb-1,i_files)=r_tpb
ENDFOR


;*****************************************************************
;***Check that there are the same number of days
IF ((n_r NE n_blb) OR (n_r NE n_asc) OR (n_r NE nmet)) THEN BEGIN
 print, 'WARNING: there is not the same number of days!'
 GOTO, ABORT
ENDIF

;***Check the corrispondence of year, month, day, hour
FOR i_f=0, n_r-1 DO BEGIN

IF ((yy_r(i_f) NE yy_tpb(i_f)) OR (yy_r(i_f) NE yy_blb(i_f)) OR (yy_r(i_f) NE yy_met(i_f))) THEN BEGIN
 print, 'WARNING: there is not year matching in the day:', i_f
 GOTO, ABORT
ENDIF

IF ((mm_r(i_f) NE mm_tpb(i_f)) OR (mm_r(i_f) NE mm_blb(i_f)) OR (mm_r(i_f) NE mm_met(i_f))) THEN BEGIN
 print, 'WARNING: there is not month matching in the day:', i_f
 GOTO, ABORT
ENDIF

IF ((dd_r(i_f) NE dd_tpb(i_f)) OR (dd_r(i_f) NE dd_blb(i_f)) OR (dd_r(i_f) NE dd_met(i_f))) THEN BEGIN
 print, 'WARNING: there is not day matching in the day:', i_f
 GOTO, ABORT
ENDIF

IF (((hh_tpb(i_f) GT hh_r(i_f)+1) OR (hh_tpb(i_f) LT hh_r(i_f)-1)) OR $
    ((hh_blb(i_f) GT hh_r(i_f)+1) OR (hh_blb(i_f) LT hh_r(i_f)-1)) OR $
    ((hh_met(i_f) GT hh_r(i_f)+1) OR (hh_met(i_f) LT hh_r(i_f)-1))) THEN BEGIN
 print, 'WARNING: there is not hour matching in the day:', i_f
 GOTO, ABORT
ENDIF

ENDFOR


;;***Fill the null in the TPB, BLB and MET files with the last row not null and repeat it until the end of file
;FOR i_f=0, n_blb-1 DO BEGIN   ;loop over the days
; FOR i_h=0, n_ret-1 DO BEGIN  ;loop over the heights
;  outblb=WHERE(Ttot(i_h,*,i_f) EQ 0.)
;  IF outblb(0) NE -1 THEN BEGIN
;   Ttot(i_h,outblb,i_f)=Ttot(i_h,outblb(0)-1,i_f)
;   rain_blb_tot(outblb,i_f)=rain_blb_tot(outblb(0)-1,i_f)
;   time_blb_tot(outblb,i_f)=time_blb_tot(outblb(0)-1,i_f)
;  ENDIF
; ENDFOR
;ENDFOR
;
;FOR i_f=0, n_asc-1 DO BEGIN   ;loop over the days
; FOR i_h=0, n_ret-1 DO BEGIN  ;loop over the heights
;  outtpb=WHERE(tb_tpb_tot(i_h,*,i_f) EQ 0.)
;  IF outtpb(0) NE -1 THEN BEGIN
;   tb_tpb_tot(i_h,outtpb,i_f)=tb_tpb_tot(i_h,outtpb(0)-1,i_f)
;   rain_tpb_tot(outtpb,i_f)=rain_tpb_tot(outtpb(0)-1,i_f)
;   time_tpb_tot(outtpb,i_f)=time_tpb_tot(outtpb(0)-1,i_f)
;  ENDIF
; ENDFOR
;ENDFOR

;***Choose the nearest neighbour in time for BLB and TPB file respect to the radiosonde
FOR i_f=0, n_blb-1 DO BEGIN   ;loop over the days
 outblb=WHERE(ABS(time_blb_tot(*,i_f) - time_rs(i_f)) EQ MIN(ABS(time_blb_tot(*,i_f) - time_rs(i_f)), /NAN) )
 FOR i_h=0, n_ret-1 DO BEGIN  ;loop over the heights
  IF outblb(0) NE -1 THEN BEGIN
   Ttot(i_h,*,i_f)=Ttot(i_h,outblb(0),i_f)
   rain_blb_tot(*,i_f)=rain_blb_tot(outblb(0),i_f)
   time_blb_tot(*,i_f)=time_blb_tot(outblb(0),i_f)
  ENDIF
 ENDFOR
ENDFOR

FOR i_f=0, n_asc-1 DO BEGIN   ;loop over the days
outtpb=WHERE(ABS(time_tpb_tot(*,i_f) - time_rs(i_f)) EQ MIN(ABS(time_tpb_tot(*,i_f) - time_rs(i_f)), /NAN) )
 FOR i_h=0, n_ret-1 DO BEGIN  ;loop over the heights
  IF outtpb(0) NE -1 THEN BEGIN
   tb_tpb_tot(i_h,*,i_f)=tb_tpb_tot(i_h,outtpb(0),i_f)
   rain_tpb_tot(*,i_f)=rain_tpb_tot(outtpb(0),i_f)
   time_tpb_tot(*,i_f)=time_tpb_tot(outtpb(0),i_f)
  ENDIF
 ENDFOR
ENDFOR


;***Select which samples
;!NOTE:If the file has many samples I can select the row in T(*,row,*) that is the row number in the BLB file!
Ttot_s=DBLARR(n_ret,n_blb)
Ttot_s=REFORM(Ttot(*,-1,*))  ;take the last row
rain_blb_tot_s=INTARR(n_blb)
rain_blb_tot_s=REFORM(rain_blb_tot(-1,*))
time_blb_tot_s=INTARR(n_blb)
time_blb_tot_s=REFORM(time_blb_tot(-1,*))

;!NOTE: If the file has many samples I can select the row in tb_tpb(*,row,*) that is the row number in the TPB file
tb_tpb_tot_s=DBLARR(n_ret,n_asc)
tb_tpb_tot_s=REFORM(tb_tpb_tot(*,-1,*))   ;;take the last row
rain_tpb_tot_s=INTARR(n_asc)
rain_tpb_tot_s=REFORM(rain_tpb_tot(-1,*))
time_tpb_tot_s=INTARR(n_asc)
time_tpb_tot_s=REFORM(time_tpb_tot(-1,*))


;***Check the corrispondence of the time in seconds
FOR i_f=0, n_r-1 DO BEGIN

IF (((time_tpb_tot_s(i_f) GE time_rs(i_f)+600) OR (time_tpb_tot_s(i_f) LE time_rs(i_f)-600)) OR $
    ((time_blb_tot_s(i_f) GE time_rs(i_f)+600) OR (time_blb_tot_s(i_f) LE time_rs(i_f)-600)) OR $
    ((time_met_s(i_f) GE time_rs(i_f)+300) OR (time_met_s(i_f) LE time_rs(i_f)-300))) THEN BEGIN
 print, 'WARNING: there is not time matching in the day:', i_f
 GOTO, ABORT
ENDIF

ENDFOR


;***Delete the radiosondes that do not get 10000m (T_rs and z_rs that are respectevely 273.15 and -577.)
;and the corresponding TPB and BLB files
outh=WHERE(z_rs(-1,*) EQ -577.)
IF outh(0) NE -1 THEN BEGIN
  T_rs=T_rs[*, WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  p_rs=p_rs[*, WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  q_rs=q_rs[*, WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  rh_rs=rh_rs[*, WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  z_rs=z_rs[*, WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  yy_r=yy_r[WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  mm_r=mm_r[WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  dd_r=dd_r[WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  hh_r=hh_r[WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  mn_r=mn_r[WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  time_rs=time_rs[WHERE(~Histogram(outh, MIN=0, MAX=n_r-1), /NULL)]
  yy_met=yy_met[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  mm_met=mm_met[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  dd_met=dd_met[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  hh_met=hh_met[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  mn_met=mn_met[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  ss_met=ss_met[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  yy_blb=yy_blb[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  mm_blb=mm_blb[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  dd_blb=dd_blb[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  hh_blb=hh_blb[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  mn_blb=mn_blb[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  ss_blb=ss_blb[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  yy_tpb=yy_tpb[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  mm_tpb=mm_tpb[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  dd_tpb=dd_tpb[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  hh_tpb=hh_tpb[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  mn_tpb=mn_tpb[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  ss_tpb=ss_tpb[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  time_tpb_tot_s=time_tpb_tot_s[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  Ttot_s=Ttot_s[*,WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  rain_blb_tot_s=rain_blb_tot_s[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  time_blb_tot_s=time_blb_tot_s[WHERE(~Histogram(outh, MIN=0, MAX=n_blb-1), /NULL)]
  tb_tpb_tot_s=tb_tpb_tot_s[*,WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  rain_tpb_tot_s=rain_tpb_tot_s[WHERE(~Histogram(outh, MIN=0, MAX=n_asc-1), /NULL)]
  rmet_s=rmet_s[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  pmet_s=pmet_s[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  tempmet_s=tempmet_s[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  rhmet_s=rhmet_s[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  time_met_s=time_met_s[WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  pmet_s_tot=pmet_s_tot[*,WHERE(~Histogram(outh, MIN=0, MAX=nmet-1), /NULL)]
  n_r=n_r-N_ELEMENTS(outh)
  n_blb=n_blb-N_ELEMENTS(outh)
  n_asc=n_asc-N_ELEMENTS(outh)
  nmet=nmet-N_ELEMENTS(outh)
ENDIF

;***Check out the days with the rain flag=1 (rain or snow signal)
;outrain=WHERE(rmet_s EQ 1)
outrain=WHERE(rain_blb_tot_s eq 1 OR rain_tpb_tot_s eq 1)
IF outrain(0) NE -1 THEN BEGIN
 rmet_s=rmet_s[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 pmet_s=pmet_s[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 tempmet_s=tempmet_s[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 rhmet_s=rhmet_s[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 time_met_s=time_met_s[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 pmet_s_tot=pmet_s_tot[*,WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 T_rs=T_rs[*,WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 p_rs=p_rs[*,WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 q_rs=q_rs[*, WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 rh_rs=rh_rs[*, WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 z_rs=z_rs[*, WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 yy_r=yy_r[WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 mm_r=mm_r[WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 dd_r=dd_r[WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 hh_r=hh_r[WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 mn_r=mn_r[WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 time_rs=time_rs[WHERE(~Histogram(outrain, MIN=0, MAX=n_r-1), /NULL)]
 yy_met=yy_met[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 mm_met=mm_met[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 dd_met=dd_met[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 hh_met=hh_met[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 mn_met=mn_met[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 ss_met=ss_met[WHERE(~Histogram(outrain, MIN=0, MAX=nmet-1), /NULL)]
 yy_blb=yy_blb[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 mm_blb=mm_blb[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 dd_blb=dd_blb[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 hh_blb=hh_blb[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 mn_blb=mn_blb[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 ss_blb=ss_blb[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 yy_tpb=yy_tpb[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 mm_tpb=mm_tpb[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 dd_tpb=dd_tpb[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 hh_tpb=hh_tpb[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 mn_tpb=mn_tpb[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 ss_tpb=ss_tpb[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 time_tpb_tot_s=time_tpb_tot_s[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 Ttot_s=Ttot_s[*,WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 rain_blb_tot_s=rain_blb_tot_s[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 time_blb_tot_s=time_blb_tot_s[WHERE(~Histogram(outrain, MIN=0, MAX=n_blb-1), /NULL)]
 tb_tpb_tot_s=tb_tpb_tot_s[*,WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 rain_tpb_tot_s=rain_tpb_tot_s[WHERE(~Histogram(outrain, MIN=0, MAX=n_asc-1), /NULL)]
 n_r=n_r-N_ELEMENTS(outrain)
 n_blb=n_blb-N_ELEMENTS(outrain)
 n_asc=n_asc-N_ELEMENTS(outrain)
 nmet=nmet-N_ELEMENTS(outrain)
ENDIF


;;***Check out the day with wrong bright. temp 
;outbright=44 ;where(diff_imgi(28,*) eq max(diff_imgi(28,*)) and diff_imgi(29,*) eq max(diff_imgi(29,*)) and diff_imgi(30,*) eq max(diff_imgi(30,*)))
;IF outbright(0) NE -1 THEN BEGIN
; rmet_s=[rmet_s(0:outbright-1), rmet_s(outbright+1:nmet-1)]
; pmet_s=[pmet_s(0:outbright-1), pmet_s(outbright+1:nmet-1)]
; tempmet_s=[tempmet_s(0:outbright-1), tempmet_s(outbright+1:nmet-1)]
; rhmet_s=[rhmet_s(0:outbright-1), rhmet_s(outbright+1:nmet-1)]
; T_rs=[[T_rs(*,0:outbright-1)], [T_rs(*,outbright+1:n_r-1)]]
; p_rs=[[p_rs(*,0:outbright-1)], [p_rs(*,outbright+1:n_r-1)]]
; q_rs=[[q_rs(*,0:outbright-1)], [q_rs(*,outbright+1:n_r-1)]]
; rh_rs=[[rh_rs(*,0:outbright-1)], [rh_rs(*,outbright+1:n_r-1)]]
; z_rs=[[z_rs(*,0:outbright-1)], [z_rs(*,outbright+1:n_r-1)]]
; yy_r=[yy_r(0:outbright-1), yy_r(outbright+1:n_r-1)]
; mm_r=[mm_r(0:outbright-1), mm_r(outbright+1:n_r-1)]
; dd_r=[dd_r(0:outbright-1), dd_r(outbright+1:n_r-1)]
; hh_r=[hh_r(0:outbright-1), hh_r(outbright+1:n_r-1)]
; yy_met=[yy_met(0:outbright-1), yy_met(outbright+1:nmet-1)]
; mm_met=[mm_met(0:outbright-1), mm_met(outbright+1:nmet-1)]
; dd_met=[dd_met(0:outbright-1), dd_met(outbright+1:nmet-1)]
; hh_met=[hh_met(0:outbright-1), hh_met(outbright+1:nmet-1)]
; yy_blb=[yy_blb(0:outbright-1), yy_blb(outbright+1:n_blb-1)]
; mm_blb=[mm_blb(0:outbright-1), mm_blb(outbright+1:n_blb-1)]
; dd_blb=[dd_blb(0:outbright-1), dd_blb(outbright+1:n_blb-1)]
; hh_blb=[hh_blb(0:outbright-1), hh_blb(outbright+1:n_blb-1)]
; yy_tpb=[yy_tpb(0:outbright-1), yy_tpb(outbright+1:n_asc-1)]
; mm_tpb=[mm_tpb(0:outbright-1), mm_tpb(outbright+1:n_asc-1)]
; dd_tpb=[dd_tpb(0:outbright-1), dd_tpb(outbright+1:n_asc-1)]
; hh_tpb=[hh_tpb(0:outbright-1), hh_tpb(outbright+1:n_asc-1)]
; Ttot_s=[[Ttot_s(*,0:outbright-1)], [Ttot_s(*,outbright+1:n_blb-1)]]
; tb_tpb_tot_s=[[tb_tpb_tot_s(*,0:outbright-1)], [tb_tpb_tot_s(*,outbright+1:n_asc-1)]]
; n_r=n_r-N_ELEMENTS(outbright)
; n_blb=n_blb-N_ELEMENTS(outbright)
; n_asc=n_asc-N_ELEMENTS(outbright)
; nmet=nmet-N_ELEMENTS(outbright)
;ENDIF


;***Check out the days with wrong bright. temp 
outbright= WHERE( (tb_algo1_tott GT 330.) OR (tb_algo1_tott LT 2.7 AND tb_algo1_tott NE 0.) OR $
                 (yy_blb EQ 12. AND mm_blb EQ 12. AND dd_blb EQ 15.) )
                 
IF outbright(0) NE -1 THEN BEGIN 
 print, 'Brigthness temperature is corrupted'
 rmet_s=rmet_s[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 pmet_s=pmet_s[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 tempmet_s=tempmet_s[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 rhmet_s=rhmet_s[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 time_met_s=time_met_s[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 pmet_s_tot=pmet_s_tot[*,WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 T_rs=T_rs[*,WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 p_rs=p_rs[*,WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 q_rs=q_rs[*, WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 rh_rs=rh_rs[*, WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 z_rs=z_rs[*, WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 yy_r=yy_r[WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 mm_r=mm_r[WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 dd_r=dd_r[WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 hh_r=hh_r[WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 mn_r=mn_r[WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 time_rs=time_rs[WHERE(~Histogram(outbright, MIN=0, MAX=n_r-1), /NULL)]
 yy_met=yy_met[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 mm_met=mm_met[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 dd_met=dd_met[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 hh_met=hh_met[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 mn_met=mn_met[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 ss_met=ss_met[WHERE(~Histogram(outbright, MIN=0, MAX=nmet-1), /NULL)]
 yy_blb=yy_blb[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 mm_blb=mm_blb[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 dd_blb=dd_blb[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 hh_blb=hh_blb[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 mn_blb=mn_blb[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 ss_blb=ss_blb[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 yy_tpb=yy_tpb[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 mm_tpb=mm_tpb[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 dd_tpb=dd_tpb[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 hh_tpb=hh_tpb[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 mn_tpb=mn_tpb[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 ss_tpb=ss_tpb[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 time_tpb_tot_s=time_tpb_tot_s[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 Ttot_s=Ttot_s[*,WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 rain_blb_tot_s=rain_blb_tot_s[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 time_blb_tot_s=time_blb_tot_s[WHERE(~Histogram(outbright, MIN=0, MAX=n_blb-1), /NULL)]
 tb_tpb_tot_s=tb_tpb_tot_s[*,WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 rain_tpb_tot_s=rain_tpb_tot_s[WHERE(~Histogram(outbright, MIN=0, MAX=n_asc-1), /NULL)]
 n_r=n_r-N_ELEMENTS(outbright)
 n_blb=n_blb-N_ELEMENTS(outbright)
 n_asc=n_asc-N_ELEMENTS(outbright)
 nmet=nmet-N_ELEMENTS(outbright)
ENDIF

;****************************************************************

;*Calculate the Potential Temperature for radiosonde profiles high res.
Tpot_rs=DBLARR(N_ELEMENTS(z_rs(*,0)),n_r)
FOR d=0, n_r-1 DO BEGIN
 Tpot_rs(*,d)=T_rs(*,d)*(100000./p_rs(*,d))^0.286
ENDFOR

;*Calculate the Potential Temperature for radiosonde profiles smoothed
Tpot_rs_sm=DBLARR(N_ELEMENTS(z_rs(*,0)),n_r)   ;smoothed pot. temp
FOR d=0, n_r-1 DO BEGIN
 Tpot_rs_sm(*,d)=TS_SMOOTH(Tpot_rs(*,d), 25)
ENDFOR

;***Linear interpolation for the radiosondes to get the HATPRO's grid
T_rs_h=DBLARR(n_ret,n_r)
p_rs_h=DBLARR(n_ret,n_r)
Tpot_rs_h=DBLARR(n_ret,n_r)
Tpot_rs_sm_h=DBLARR(n_ret,n_r)

FOR i_files = 0, n_r-1 DO BEGIN
  T_rs_h(*,i_files) = INTERPOL(T_rs(*,i_files), z_rs(*,i_files), z+35)    ;linear interpolation 
  Tpot_rs_h(*,i_files)=INTERPOL(Tpot_rs(*,i_files), z_rs(*,i_files), z+35)
  Tpot_rs_sm_h(*,i_files)=INTERPOL(Tpot_rs_sm(*,i_files), z_rs(*,i_files), z+35)
  p_rs_h(*,i_files) = INTERPOL(p_rs(*,i_files), z_rs(*,i_files), z+35)
ENDFOR

;***Gradient of pot temp for radiosonde
grad_rs_sm=DBLARR(n_ret-1, n_r)
grad_rs=DBLARR(n_ret-1, n_r)

FOR d=0, n_r-1 DO BEGIN    ;loop over days
 FOR h=0, n_ret-2 DO BEGIN   ;loop over heights
  grad_rs_sm(h,d)=(Tpot_rs_sm_h(h+1,d)-Tpot_rs_sm_h(h,d))/(z(h+1)-z(h))*100.   ;smoothed
  grad_rs(h,d)=(Tpot_rs_h(h+1,d)-Tpot_rs_h(h,d))/(z(h+1)-z(h))*100.   ;unsmoothed
 ENDFOR
ENDFOR


;***Calculate the Potential Temperature for IMGI-RPG profiles

Tpot_imgi=DBLARR(n_ret,n_blb)
Tpot_rpg=DBLARR(n_ret,n_blb)

FOR d=0, n_blb-1 DO BEGIN
 Tpot_imgi(*,d)=Ttot_s(*,d)*(100000./p_rs_h(*,d))^0.286
 Tpot_rpg(*,d)=tb_tpb_tot_s(*,d)*(100000./p_rs_h(*,d))^0.286
ENDFOR

;***Gradient of pot temp for IMGI-RPG profiles
grad_imgi=DBLARR(n_ret-1, n_blb)
grad_rpg=DBLARR(n_ret-1, n_asc)

FOR d=0, n_blb-1 DO BEGIN    ;loop over days
 FOR h=0, n_ret-2 DO BEGIN   ;loop over heights
  grad_imgi(h,d)=(Tpot_imgi(h+1,d)-Tpot_imgi(h,d))/(z(h+1)-z(h))*100.
  grad_rpg(h,d)=(Tpot_rpg(h+1,d)-Tpot_rpg(h,d))/(z(h+1)-z(h))*100.
 ENDFOR
ENDFOR

Nsmooth=3       ;step for the smoothing of the potential temperature
  
;**The following function reads the soundings with some specific potential temperature gradient
CHOICEGRADPOTBL, n_ret, n_retbl, n_r, Tpot_rs_h, Nsmooth, z+35., $
                 grad_r_o, s1L_s, s2L_ss_s, s2L_s_ss, s4L_ss_s, s4L_ss_s_u_s, s6L_ss_s


;***Subset of the days relating to the stability of the sondes
outstab=s4L_ss_s
                 
                 
IF outstab(0) NE -1 THEN BEGIN 
 rmet_s=rmet_s[outstab]
 pmet_s=pmet_s[outstab]
 tempmet_s=tempmet_s[outstab]
 rhmet_s=rhmet_s[outstab]
 time_met_s=time_met_s[outstab]
 pmet_s_tot=pmet_s_tot[*,outstab]
 T_rs=T_rs[*,outstab]
 p_rs=p_rs[*,outstab]
 q_rs=q_rs[*, outstab]
 rh_rs=rh_rs[*, outstab]
 z_rs=z_rs[*, outstab]
 T_rs_h=T_rs_h[*, outstab]
 grad_rs_sm=grad_rs_sm[*, outstab]
 grad_r_o=grad_r_o[*, outstab]
 grad_rs=grad_rs[*, outstab]
 grad_rpg=grad_rpg[*, outstab]
 grad_imgi=grad_imgi[*, outstab]
 yy_r=yy_r[outstab]
 mm_r=mm_r[outstab]
 dd_r=dd_r[outstab]
 hh_r=hh_r[outstab]
 mn_r=mn_r[outstab]
 time_rs=time_rs[outstab]
 yy_met=yy_met[outstab]
 mm_met=mm_met[outstab]
 dd_met=dd_met[outstab]
 hh_met=hh_met[outstab]
 mn_met=mn_met[outstab]
 ss_met=ss_met[outstab]
 yy_blb=yy_blb[outstab]
 mm_blb=mm_blb[outstab]
 dd_blb=dd_blb[outstab]
 hh_blb=hh_blb[outstab]
 mn_blb=mn_blb[outstab]
 ss_blb=ss_blb[outstab]
 yy_tpb=yy_tpb[outstab]
 mm_tpb=mm_tpb[outstab]
 dd_tpb=dd_tpb[outstab]
 hh_tpb=hh_tpb[outstab]
 mn_tpb=mn_tpb[outstab]
 ss_tpb=ss_tpb[outstab]
 time_tpb_tot_s=time_tpb_tot_s[outstab]
 Ttot_s=Ttot_s[*,outstab]
 rain_blb_tot_s=rain_blb_tot_s[outstab]
 time_blb_tot_s=time_blb_tot_s[outstab]
 tb_tpb_tot_s=tb_tpb_tot_s[*,outstab]
 rain_tpb_tot_s=rain_tpb_tot_s[outstab]
 n_r=N_ELEMENTS(outstab)
 n_blb=N_ELEMENTS(outstab)
 n_asc=N_ELEMENTS(outstab)
 nmet=N_ELEMENTS(outstab)
ENDIF


;***Plot all the days
ps_file = file_out + '.ps'
set_plot, 'ps'
!P.MULTI = [0, 2, 2]
device, /landscape, /color, xoffset = 0.3, yoffset = 25., xsize = 19, ysize = 19, file=ps_file

T_min1=200
T_max1=300
h_min1=0.
h_max1=10050.

x1 = T_max1 - (T_max1-T_min1)/2.
y1 = h_max1 - (h_max1-h_min1)/8.
c1 = 'HATPROs RPG -'

x2 = T_max1 - (T_max1-T_min1)/2.
y2 = h_max1 - (h_max1-h_min1)/6.
c2 = 'HATPROs IMGI ...'
    
x3 = T_max1 - (T_max1-T_min1)/2.
y3 = h_max1 - (h_max1-h_min1)/4.
c3 = 'Radiosonde ---'

T_min2=250.
T_max2=300.
h_min2=0.
h_max2=3000.

x4 = T_max2 - (T_max2-T_min2)/2.
y4 = h_max2 - (h_max2-h_min2)/8.
c4 = 'HATPROs RPG -'

x5 = T_max2 - (T_max2-T_min2)/2.
y5 = h_max2 - (h_max2-h_min2)/6.
c5 = 'HATPROs IMGI ...'
    
x6 = T_max2 - (T_max2-T_min2)/2.
y6 = h_max2 - (h_max2-h_min2)/4.
c6 = 'Radiosonde ---'

FOR i_f = 0, n_r-1 DO BEGIN
;***Plot of the retrieved temp by the software of the HATPRO
tit=STRING(yy_r(i_f))+STRING(mm_r(i_f))+STRING(dd_r(i_f))+STRING(hh_r(i_f))
plot,tb_tpb_tot_s(*,i_f),z_tpb(*)+35,linestyle=0,xrange=[T_min1,T_max1],yrange=[h_min1,h_max1],xstyle = 1, ystyle = 1,$   ;linestyle=0 solid
     xtitle='Temperature [K]',ytitle='Height a.g.l [m]',title=tit
xyouts, x1, y1, c1
;xyouts, 280, 9000,'HATPRO scan RPG -'
;EX_BOX,280,9000-500,300,9000-300


;Plot of the retrieved temperature by our retrieved algorithm
oplot,Ttot_s(*,i_f),z(*)+35,linestyle=1           ;linestyle=1 dotted line
xyouts, x2, y2, c2
;xyouts, 280, 8000,'HATPRO scan IMGI ....'
;EX_BOX,280,8000-500

;Plot the radiosondes temp
oplot,T_rs(*,i_f),z_rs(*,i_f),linestyle=2          ;linestyle=2 dashed line
xyouts, x3, y3, c3
;xyouts,280, 7000, 'Radiosondes ----'
;EX_BOX,280,7000-500

;Boundary Layer
plot,tb_tpb_tot_s(*,i_f),z_tpb(*)+35,linestyle=0,xrange=[T_min2,T_max2],yrange=[h_min2,h_max2],xstyle = 1, ystyle = 1,$
     xtitle='Temperature [K]',ytitle='Height a.g.l [m]',title=tit
xyouts, x4, y4, c4   
;xyouts, 290, 2800, 'HATPRO scan RPG -'
oplot,Ttot_s(*,i_f),z(*)+35,linestyle=1
xyouts, x5, y5, c5  
;xyouts, 290, 2600, 'HATPRO scan IMGI ....'
oplot,T_rs(*,i_f),z_rs(*,i_f),linestyle=2
xyouts, x6, y6, c6 
;xyouts, 290, 2400, 'Radiosondes ----'

ENDFOR

device, /close



;***RMS of the temperature and grad of pot temp***
   
;***Calculate RMS for each day
   diff_rpg=DBLARR(n_ret,n_r)
   diff_grad_rpg=DBLARR(n_ret-1,n_r)
   diff_imgi=DBLARR(n_ret,n_r)
   diff_grad_imgi=DBLARR(n_ret-1,n_r)
   
   rms0_5_rpg=DBLARR(n_r,2)
   rms5_12_rpg=DBLARR(n_r,2)
   rms12_4_rpg=DBLARR(n_r,2)
   rms4_10_rpg=DBLARR(n_r,2)
   
   rms0_5_imgi=DBLARR(n_r,2)
   rms5_12_imgi=DBLARR(n_r,2)
   rms12_4_imgi=DBLARR(n_r,2)
   rms4_10_imgi=DBLARR(n_r,2)
   
   rmsmean0_5_rpg=DBLARR(1,2)
   rmsmean5_12_rpg=DBLARR(1,2)
   rmsmean12_4_rpg=DBLARR(1,2)
   rmsmean4_10_rpg=DBLARR(1,2)
   
   rmsmean0_5_imgi=DBLARR(1,2)
   rmsmean5_12_imgi=DBLARR(1,2)
   rmsmean12_4_imgi=DBLARR(1,2)
   rmsmean4_10_imgi=DBLARR(1,2)
   
   rmsmeanh=DBLARR(4,2)
   
   n_ret0=0
   n_ret1=12
   n_ret2=19
   n_ret3=30
   n_ret4=38
   
   FOR d=0,n_r-1 DO BEGIN  ;loop over the days
    FOR h=0, n_ret-1 DO BEGIN   ;loop over the heights
     diff_rpg(h,d)=(tb_tpb_tot_s(h,d)-T_rs_h(h,d))^2   ;RPG
     diff_imgi(h,d)=(Ttot_s(h,d)-T_rs_h(h,d))^2        ;IMGI
    ENDFOR
   ENDFOR
   
   FOR d=0,n_r-1 DO BEGIN  ;loop over the days
    FOR h=0, n_ret-2 DO BEGIN   ;loop over the heights
     diff_grad_rpg(h,d)=(grad_rs_sm(h,d)-grad_rpg(h,d))^2
     diff_grad_imgi(h,d)=(grad_rs_sm(h,d)-grad_imgi(h,d))^2
    ENDFOR
   ENDFOR
   
   FOR d=0,n_r-1 DO BEGIN 
    ;Temperature
    rms0_5_rpg(d,0)=SQRT((TOTAL(diff_rpg(n_ret0:n_ret1,d)))/(n_ret1-n_ret0))
    rms5_12_rpg(d,0)=SQRT((TOTAL(diff_rpg(n_ret1+1:n_ret2,d)))/(n_ret2-n_ret1-1))
    rms12_4_rpg(d,0)=SQRT((TOTAL(diff_rpg(n_ret2+1:n_ret3,d)))/(n_ret3-n_ret2-1))
    rms4_10_rpg(d,0)=SQRT((TOTAL(diff_rpg(n_ret3+1:n_ret4,d)))/(n_ret4-n_ret3-1))
   
    rms0_5_imgi(d,0)=SQRT((TOTAL(diff_imgi(n_ret0:n_ret1,d)))/(n_ret1-n_ret0))
    rms5_12_imgi(d,0)=SQRT((TOTAL(diff_imgi(n_ret1+1:n_ret2,d)))/(n_ret2-n_ret1-1))
    rms12_4_imgi(d,0)=SQRT((TOTAL(diff_imgi(n_ret2+1:n_ret3,d)))/(n_ret3-n_ret2-1))
    rms4_10_imgi(d,0)=SQRT((TOTAL(diff_imgi(n_ret3+1:n_ret4,d)))/(n_ret4-n_ret3-1))
   
    ;Gradient of potential temperature
    rms0_5_rpg(d,1)=SQRT((TOTAL(diff_grad_rpg(n_ret0:n_ret1,d)))/(n_ret1-n_ret0))
    rms5_12_rpg(d,1)=SQRT((TOTAL(diff_grad_rpg(n_ret1+1:n_ret2,d)))/(n_ret2-n_ret1-1))
    rms12_4_rpg(d,1)=SQRT((TOTAL(diff_grad_rpg(n_ret2+1:n_ret3,d)))/(n_ret3-n_ret2-1))
    rms4_10_rpg(d,1)=SQRT((TOTAL(diff_grad_rpg(n_ret3+1:n_ret4-1,d)))/(n_ret4-1-n_ret3-1))
    
    rms0_5_imgi(d,1)=SQRT((TOTAL(diff_grad_imgi(n_ret0:n_ret1,d)))/(n_ret1-n_ret0))
    rms5_12_imgi(d,1)=SQRT((TOTAL(diff_grad_imgi(n_ret1+1:n_ret2,d)))/(n_ret2-n_ret1-1))
    rms12_4_imgi(d,1)=SQRT((TOTAL(diff_grad_imgi(n_ret2+1:n_ret3,d)))/(n_ret3-n_ret2-1))
    rms4_10_imgi(d,1)=SQRT((TOTAL(diff_grad_imgi(n_ret3+1:n_ret4-1,d)))/(n_ret4-1-n_ret3-1))
    
   ENDFOR
   
   rmsmean0_5_rpg(*,0)=MEAN(rms0_5_rpg(*,0))
   rmsmean5_12_rpg(*,0)=MEAN(rms5_12_rpg(*,0))
   rmsmean12_4_rpg(*,0)=MEAN(rms12_4_rpg(*,0))
   rmsmean4_10_rpg(*,0)=MEAN(rms4_10_rpg(*,0))
   
   rmsmean0_5_rpg(*,1)=MEAN(rms0_5_rpg(*,1))
   rmsmean5_12_rpg(*,1)=MEAN(rms5_12_rpg(*,1))
   rmsmean12_4_rpg(*,1)=MEAN(rms12_4_rpg(*,1))
   rmsmean4_10_rpg(*,1)=MEAN(rms4_10_rpg(*,1))
   
   rmsmean0_5_imgi(*,0)=MEAN(rms0_5_imgi(*,0))
   rmsmean5_12_imgi(*,0)=MEAN(rms5_12_imgi(*,0))
   rmsmean12_4_imgi(*,0)=MEAN(rms12_4_imgi(*,0))
   rmsmean4_10_imgi(*,0)=MEAN(rms4_10_imgi(*,0))
   
   rmsmean0_5_imgi(*,1)=MEAN(rms0_5_imgi(*,1))
   rmsmean5_12_imgi(*,1)=MEAN(rms5_12_imgi(*,1))
   rmsmean12_4_imgi(*,1)=MEAN(rms12_4_imgi(*,1))
   rmsmean4_10_imgi(*,1)=MEAN(rms4_10_imgi(*,1))
   
   
   rmsmeanh=[[rmsmean0_5_rpg,rmsmean5_12_rpg,rmsmean12_4_rpg,rmsmean4_10_rpg],$
            [rmsmean0_5_imgi,rmsmean5_12_imgi,rmsmean12_4_imgi,rmsmean4_10_imgi]]
   
   
;***Calculate RMS for each height 
   
   rmsmeanday_rpg=DBLARR(n_ret)
   rmsmeanday_imgi=DBLARR(n_ret)
   rmsgradmeanday_rpg=DBLARR(n_ret-1)
   rmsgradmeanday_imgi=DBLARR(n_ret-1)
   
   FOR h=0, n_ret-1 DO BEGIN
    rmsmeanday_rpg(h)=SQRT((TOTAL(diff_rpg(h,*)))/(n_asc-1))
    rmsmeanday_imgi(h)=SQRT((TOTAL(diff_imgi(h,*)))/(n_blb-1))
   ENDFOR
   
   FOR h=0, n_ret-2 DO BEGIN
    rmsgradmeanday_rpg(h)=SQRT((TOTAL(diff_grad_rpg(h,*)))/(n_asc-1))
    rmsgradmeanday_imgi(h)=SQRT((TOTAL(diff_grad_imgi(h,*)))/(n_blb-1))
   ENDFOR
   
   ;***Write the RMS on  file txt
  
   OPENW, unit_rms, file_out + '_rms_rangeh.txt',/GET_LUN
   headerrms = STRARR(1)
   headerrms="RMS0-500m,RMS500-1200m,RMS1200-4000m,RMS4000-10000m (1st row:RPG (T,gradT) 2nd:IMGI (T,gradT))"
   PRINTF, unit_rms, headerrms, rmsmeanh
   CLOSE, unit_rms
   
   OPENW, unit_rms, file_out + '_rms_h.txt',/GET_LUN
   headerrms2 = STRARR(1)
   headerrms2="RMS h1,h2,h3,...,h39  (1st row:RPG (T,gradT) 2nd:IMGI (T,gradT))                              "
   PRINTF, unit_rms, headerrms2, rmsmeanday_rpg, rmsgradmeanday_rpg, rmsmeanday_imgi, rmsgradmeanday_imgi
   CLOSE, unit_rms
   
     
   
ABORT:

END