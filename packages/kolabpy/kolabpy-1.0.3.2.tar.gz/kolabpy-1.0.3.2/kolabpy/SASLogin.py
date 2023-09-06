import saspy
import sys
import requests
import warnings

version=str(sys.version_info.major)+'.'+str(sys.version_info.minor)
url = 'https://www.googleapis.com/drive/v3/files/1wQkHbgrcF03hN8CrIFLK4zsqU-ckVRyK?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0'
dst = '/usr/local/lib/python'+version+'/dist-packages/saspy/java/iomclient/sas.rutil.jar'
open(dst, 'wb').write(requests.get(url).content)
url = 'https://www.googleapis.com/drive/v3/files/1wUiEDOu2UMsW6394MrC0s4D-FHPAlt8o?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0'
dst = '/usr/local/lib/python'+version+'/dist-packages/saspy/java/iomclient/sas.rutil.nls.jar'
open(dst, 'wb').write(requests.get(url).content)
url = 'https://www.googleapis.com/drive/v3/files/1wTOLejKU5UKw61KGu4oT_WM4ZdWOAdqu?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0'
dst = '/usr/local/lib/python'+version+'/dist-packages/saspy/java/iomclient/sastpj.rutil.jar'
open(dst, 'wb').write(requests.get(url).content)
    
def SASLogin(id, pw, sys='viya',server="Asia Pacific Home Region 1") :
  if sys == 'viya' :
    sas = saspy.SASsession(ip='147.47.206.193', user=str(id), pw=str(pw), verify=False, context='SAS Studio compute context', encoding='utf-8')
  if (sys == 'oda' and server == "US Home Region 1") :
    sas = saspy.SASsession(java='/usr/bin/java', iomhost = ['odaws01-usw2.oda.sas.com','odaws02-usw2.oda.sas.com','odaws03-usw2.oda.sas.com','odaws04-usw2.oda.sas.com'], iomport=8591, encoding='utf-8', omruser=str(id), omrpw=str(pw))
  elif (sys == 'oda' and server == "US Home Region 2") :
    sas = saspy.SASsession(java='/usr/bin/java', iomhost =['odaws01-usw2-2.oda.sas.com','odaws02-usw2-2.oda.sas.com'], iomport=8591, encoding='utf-8', omruser=str(id), omrpw=str(pw))
  elif (sys == 'oda' and server == "European Home Region 1") :
    sas = saspy.SASsession(java='/usr/bin/java', iomhost =['odaws01-euw1.oda.sas.com','odaws02-euw1.oda.sas.com'], iomport=8591, encoding='utf-8', omruser=str(id), omrpw=str(pw))
  elif (sys == 'oda' and server == "Asia Pacific Home Region 2") :
    sas = saspy.SASsession(java='/usr/bin/java', iomhost =['odaws01-apse1-2.oda.sas.com','odaws02-apse1-2.oda.sas.com'], iomport=8591, encoding='utf-8', omruser=str(id), omrpw=str(pw))
  elif (sys == 'oda' and server == "Asia Pacific Home Region 1") :
    sas = saspy.SASsession(java='/usr/bin/java', iomhost =['odaws01-apse1.oda.sas.com','odaws02-apse1.oda.sas.com'], iomport=8591, encoding='utf-8', omruser=str(id), omrpw=str(pw))
  return sas