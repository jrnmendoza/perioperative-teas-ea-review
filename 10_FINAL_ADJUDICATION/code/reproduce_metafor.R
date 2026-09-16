.libPaths(c(Sys.getenv('ASTRA_R_LIBRARY','/tmp/astra-r-library'),.libPaths()))
library(metafor)
d<-read.csv('10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv',stringsAsFactors=FALSE)
results<-list()
for(id in unique(d$model_id)) {
 x<-d[d$model_id==id,];k<-nrow(x); measure<-x$measure[1]
 if(measure=='RR') z<-escalc(measure='RR',ai=events_i,bi=n_i-events_i,ci=events_c,di=n_c-events_c,data=x,add=.5,to='only0',drop00=TRUE)
 if(measure=='MD') z<-escalc(measure='MD',m1i=mean_i,sd1i=sd_i,n1i=n_i,m2i=mean_c,sd2i=sd_c,n2i=n_c,data=x)
 if(measure=='SMD') z<-escalc(measure='SMD',m1i=mean_i,sd1i=sd_i,n1i=n_i,m2i=mean_c,sd2i=sd_c,n2i=n_c,data=x,vtype='LS')
 fit<-rma.uni(yi=z$yi,vi=z$vi,method=if(k>1)'REML' else 'EE',test=if(k>1)'adhoc' else 'z',control=list(threshold=1e-10,maxiter=10000))
 pi.lo<-NA;pi.hi<-NA
 if(k>=5){pr<-predict(fit);pi.lo<-pr$pi.lb;pi.hi<-pr$pi.ub}
 results[[id]]<-data.frame(model_id=id,k=k,N=sum(x$n_i+x$n_c),effect=as.numeric(fit$b),se=fit$se,ci_low=fit$ci.lb,ci_high=fit$ci.ub,p=fit$pval,tau2=fit$tau2,I2=if(k>1)fit$I2 else NA,pi_low=pi.lo,pi_high=pi.hi,max_effect_input_difference=max(abs(x$yi-z$yi)),max_variance_input_difference=max(abs(x$vi-z$vi)))
}
write.csv(do.call(rbind,results),'10_FINAL_ADJUDICATION/05_REPRODUCTION/metafor_outputs.csv',row.names=FALSE)
capture.output(sessionInfo(),file='10_FINAL_ADJUDICATION/05_REPRODUCTION/R_session.txt')
